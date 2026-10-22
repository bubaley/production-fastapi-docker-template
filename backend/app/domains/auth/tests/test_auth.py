from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
import pytest
from fastapi import Request

from app.core.auth import is_public_route
from app.core.settings import settings
from app.domains.auth.services.auth_service import AuthService
from app.domains.auth.services.token_service import TokenService, TokenType
from app.domains.user.models import User

# Issued by python-jose (HS256) before the PyJWT migration; must keep validating.
LEGACY_SECRET_KEY = 'legacy-jose-compat-secret-key-' + 'x' * 40
LEGACY_JOSE_TOKEN = (
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
    'eyJpZCI6IjVmMGM2YjhlLTJmNGUtNGMxYS05ZDNiLThhN2U2ZjVkNGMzYiIsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjQxMDI0NDQ4MDB9.'
    'NwFyI6811GK5aSU9w7LF1pBQDEOk30oEgy5W9LYPFqw'
)


def _legacy_token(user: User, token_type: str = 'access', expires_in: timedelta = timedelta(hours=1)) -> str:
    """Token shape issued before claim versioning: `id`, `type`, `exp` only."""
    payload = {'id': str(user.id), 'type': token_type, 'exp': datetime.now(UTC) + expires_in}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def _bearer(token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {token}'}


def _refresh_cookie(token: str) -> dict[str, str]:
    return {'Cookie': f'refresh_token={token}'}


def test_tokens_issued_by_python_jose_still_validate(monkeypatch):
    monkeypatch.setattr(settings, 'secret_key', LEGACY_SECRET_KEY)
    claims = TokenService.decode(LEGACY_JOSE_TOKEN, TokenType.ACCESS)
    assert claims is not None
    assert claims.legacy
    assert claims.user_id == UUID('5f0c6b8e-2f4e-4c1a-9d3b-8a7e6f5d4c3b')
    assert claims.version == 0
    assert claims.jti is None


def test_token_claims_and_rejections(monkeypatch):
    user = User(id=uuid4(), token_version=3)
    session_id = uuid4()
    token = TokenService.issue(user, TokenType.REFRESH, session_id)
    payload = TokenService.decode_payload(token.token)
    assert payload is not None
    assert set(payload) == {'sub', 'type', 'iat', 'exp', 'jti', 'ver', 'sid'}
    assert payload['sub'] == str(user.id)
    assert payload['type'] == 'refresh'
    assert payload['ver'] == 3
    assert payload['jti'] == token.jti
    assert payload['sid'] == str(session_id)
    assert TokenService.decode(token.token, TokenType.ACCESS) is None
    assert TokenService.decode('not-a-token', TokenType.ACCESS) is None
    assert TokenService.decode(LEGACY_JOSE_TOKEN, TokenType.ACCESS) is None  # other secret
    monkeypatch.setattr(settings, 'jwt_access_token_expire_minutes', -1)
    assert TokenService.decode(TokenService.issue(user, TokenType.ACCESS, session_id).token, TokenType.ACCESS) is None


@pytest.mark.asyncio
@pytest.mark.parametrize('token_type, expected_status', [('access', 200), ('refresh', 401)])
async def test_only_access_jwt_authenticates_api(api_client, user_factory, token_type, expected_status):
    user = await user_factory()
    pair = await AuthService.start_session(user)
    token = pair.access if token_type == 'access' else pair.refresh
    response = await api_client.get('/api/v1/auth/me', headers=_bearer(token.token))
    assert response.status_code == expected_status


@pytest.mark.asyncio
@pytest.mark.parametrize('accept_legacy, expected_status', [(True, 200), (False, 401)])
async def test_legacy_id_claim_is_accepted_during_grace_period(
    api_client, user_factory, monkeypatch, accept_legacy, expected_status
):
    monkeypatch.setattr(settings, 'jwt_accept_legacy_tokens', accept_legacy)
    user = await user_factory()
    response = await api_client.get('/api/v1/auth/me', headers=_bearer(_legacy_token(user)))
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_legacy_refresh_token_is_exchanged_once(api_client, user_factory, monkeypatch):
    monkeypatch.setattr(settings, 'refresh_reuse_leeway_seconds', 0)
    user = await user_factory()
    legacy = _legacy_token(user, 'refresh')
    first = await api_client.post('/api/v1/auth/refresh', headers=_refresh_cookie(legacy))
    assert first.status_code == 200
    rotated = first.cookies['refresh_token']
    claims = TokenService.decode(rotated, TokenType.REFRESH)
    assert claims is not None
    assert claims.jti is not None
    # Replaying the legacy token is reuse: the session it started is revoked.
    assert (await api_client.post('/api/v1/auth/refresh', headers=_refresh_cookie(legacy))).status_code == 401
    assert (await api_client.post('/api/v1/auth/refresh', headers=_refresh_cookie(rotated))).status_code == 401


@pytest.mark.asyncio
async def test_expired_tokens_are_rejected(api_client, user_factory, monkeypatch):
    user = await user_factory()
    monkeypatch.setattr(settings, 'jwt_access_token_expire_minutes', -1)
    monkeypatch.setattr(settings, 'jwt_refresh_token_expire_minutes', -1)
    pair = await AuthService.start_session(user)
    assert (await api_client.get('/api/v1/auth/me', headers=_bearer(pair.access.token))).status_code == 401
    response = await api_client.post('/api/v1/auth/refresh', headers=_refresh_cookie(pair.refresh.token))
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_does_not_depend_on_selected_organization(api_client, user_factory):
    user = await user_factory()
    pair = await AuthService.start_session(user)
    response = await api_client.post(
        '/api/v1/auth/logout',
        headers={**_bearer(pair.access.token), 'Organization-Key': 'no-longer-accessible'},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_accepts_expired_or_invalid_credentials(api_client):
    response = await api_client.post('/api/v1/auth/logout', headers={'Authorization': 'Bearer invalid'})
    assert response.status_code == 204


@pytest.mark.parametrize(
    'path, public',
    [
        ('/api/v1/auth/login', True),
        ('/api/v1/auth/refresh/', True),
        ('/api/v1/auth/logout', True),
        ('/api/v1/auth/logout-all', False),
        ('/api/v1/auth/me', False),
        ('/api/v1/something/auth/login', False),
    ],
)
def test_public_routes_match_exactly(path, public):
    assert is_public_route(Request({'type': 'http', 'path': path, 'headers': []})) is public
