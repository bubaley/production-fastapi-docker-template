import pytest
from fastapi import Request

from app.core.auth import is_public_route
from app.domains.auth.services.auth_service import AuthService


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
