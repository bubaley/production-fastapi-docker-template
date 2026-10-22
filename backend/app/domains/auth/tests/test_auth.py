from uuid import uuid4

import pytest
from fastapi import Request

from app.core.auth import is_public_route
from app.core.settings import settings
from app.domains.auth.services.auth_service import AuthService
from app.domains.user.models import User

# Issued by python-jose (HS256) before the PyJWT migration; must keep validating.
LEGACY_SECRET_KEY = 'legacy-jose-compat-secret-key-' + 'x' * 40
LEGACY_JOSE_TOKEN = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
    'eyJpZCI6IjVmMGM2YjhlLTJmNGUtNGMxYS05ZDNiLThhN2U2ZjVkNGMzYiIsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjQxMDI0NDQ4MDB9.'
    'NwFyI6811GK5aSU9w7LF1pBQDEOk30oEgy5W9LYPFqw'
)


def test_tokens_issued_by_python_jose_still_validate(monkeypatch):
    monkeypatch.setattr(settings, 'secret_key', LEGACY_SECRET_KEY)
    payload = AuthService.verify_token(LEGACY_JOSE_TOKEN)
    assert payload == {'id': '5f0c6b8e-2f4e-4c1a-9d3b-8a7e6f5d4c3b', 'type': 'access', 'exp': 4102444800}


def test_token_claims_and_rejections(monkeypatch):
    user = User(id=uuid4())
    payload = AuthService.verify_token(AuthService.create_refresh_token(user).token)
    assert payload is not None
    assert set(payload) == {'id', 'type', 'exp'}
    assert payload['id'] == str(user.id)
    assert payload['type'] == 'refresh'
    assert AuthService.verify_token('not-a-token') is None
    assert AuthService.verify_token(LEGACY_JOSE_TOKEN) is None
    monkeypatch.setattr(settings, 'jwt_access_token_expire_minutes', -1)
    assert AuthService.verify_token(AuthService.create_access_token(user).token) is None


@pytest.mark.asyncio
@pytest.mark.parametrize('token_type, expected_status', [('access', 200), ('refresh', 401)])
async def test_only_access_jwt_authenticates_api(api_client, user_factory, token_type, expected_status):
    user = await user_factory()
    create_token = AuthService.create_access_token if token_type == 'access' else AuthService.create_refresh_token
    response = await api_client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {create_token(user).token}'})
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_refresh_still_issues_new_tokens(api_client, user_factory):
    user = await user_factory()
    token = AuthService.create_refresh_token(user)
    response = await api_client.post('/api/v1/auth/refresh', json={'refresh_token': token.token})
    assert response.status_code == 200
    token_data = AuthService.verify_token(response.json()['access_token'])
    assert token_data is not None
    assert token_data['type'] == 'access'


@pytest.mark.asyncio
async def test_logout_clears_login_cookies(api_client, user_factory):
    user = await user_factory()
    response = await api_client.post('/api/v1/auth/login', json={'email': user.email, 'password': 'test-password'})
    assert response.status_code == 200
    assert api_client.cookies.get('access_token')
    assert api_client.cookies.get('refresh_token')
    assert (await api_client.get('/api/v1/auth/me')).status_code == 200
    response = await api_client.post('/api/v1/auth/logout')
    assert response.status_code == 200
    assert not api_client.cookies.get('access_token')
    assert not api_client.cookies.get('refresh_token')
    assert (await api_client.get('/api/v1/auth/me')).status_code == 401


@pytest.mark.asyncio
async def test_logout_accepts_expired_or_invalid_credentials(api_client):
    response = await api_client.post('/api/v1/auth/logout', headers={'Authorization': 'Bearer invalid'})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout_does_not_depend_on_selected_organization(api_client, user_factory):
    user = await user_factory()
    response = await api_client.post(
        '/api/v1/auth/logout',
        headers={
            'Authorization': f'Bearer {AuthService.create_access_token(user).token}',
            'Organization-Key': 'no-longer-accessible',
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'path, public',
    [
        ('/api/v1/auth/login', True),
        ('/api/v1/auth/refresh/', True),
        ('/api/v1/auth/logout', True),
        ('/api/v1/auth/me', False),
        ('/api/v1/something/auth/login', False),
    ],
)
def test_public_routes_match_exactly(path, public):
    assert is_public_route(Request({'type': 'http', 'path': path, 'headers': []})) is public
