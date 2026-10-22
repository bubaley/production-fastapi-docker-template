import pytest

from app.conftest import TEST_PASSWORD
from app.core.settings import settings
from app.domains.auth.models import RefreshSession
from app.domains.auth.services.auth_service import AuthService
from app.domains.auth.services.token_service import TokenService, TokenType
from app.domains.user.models import User

LOGIN = '/api/v1/auth/login'
REFRESH = '/api/v1/auth/refresh'
ME = '/api/v1/auth/me'


def _bearer(token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {token}'}


async def _login(api_client, user: User) -> dict:
    response = await api_client.post(LOGIN, json={'email': user.email, 'password': TEST_PASSWORD})
    assert response.status_code == 200
    return response.json()


async def _refresh(api_client, refresh_token: str):
    return await api_client.post(REFRESH, json={'refresh_token': refresh_token})


# ROTATION


@pytest.mark.asyncio
async def test_refresh_rotates_the_pair(api_client, user_factory):
    user = await user_factory()
    tokens = await _login(api_client, user)
    response = await _refresh(api_client, tokens['refresh_token'])
    assert response.status_code == 200
    rotated = response.json()
    assert rotated['refresh_token'] != tokens['refresh_token']
    assert (await api_client.get(ME, headers=_bearer(rotated['access_token']))).status_code == 200
    old_claims = TokenService.decode(tokens['refresh_token'], TokenType.REFRESH)
    new_claims = TokenService.decode(rotated['refresh_token'], TokenType.REFRESH)
    assert old_claims is not None
    assert new_claims is not None
    old = await RefreshSession.get(jti=old_claims.jti)
    assert old.revoked_at is not None
    assert old.replaced_by == new_claims.jti
    assert new_claims.session_id == old.family_id


@pytest.mark.asyncio
async def test_reused_refresh_token_revokes_the_family(api_client, user_factory, monkeypatch):
    monkeypatch.setattr(settings, 'refresh_reuse_leeway_seconds', 0)
    user = await user_factory()
    stolen = (await _login(api_client, user))['refresh_token']
    legit = (await _refresh(api_client, stolen)).json()['refresh_token']
    other_session = (await _login(api_client, user))['refresh_token']

    assert (await _refresh(api_client, stolen)).status_code == 401
    # The legitimate continuation of the reused token dies with it; other logins are untouched.
    assert (await _refresh(api_client, legit)).status_code == 401
    assert (await _refresh(api_client, other_session)).status_code == 200


@pytest.mark.asyncio
async def test_reuse_within_leeway_does_not_revoke_the_family(api_client, user_factory):
    user = await user_factory()
    first = (await _login(api_client, user))['refresh_token']
    second = (await _refresh(api_client, first)).json()['refresh_token']
    # A parallel tab presenting the just-rotated token gets 401, but the session survives.
    assert (await _refresh(api_client, first)).status_code == 401
    assert (await _refresh(api_client, second)).status_code == 200


@pytest.mark.asyncio
async def test_refresh_uses_cookie_scoped_to_auth_path(api_client, user_factory):
    user = await user_factory()
    await _login(api_client, user)
    refresh_cookie = next(cookie for cookie in api_client.cookies.jar if cookie.name == 'refresh_token')
    assert refresh_cookie.path == settings.refresh_cookie_path == '/api/v1/auth'
    access_cookie = next(cookie for cookie in api_client.cookies.jar if cookie.name == 'access_token')
    assert access_cookie.path == '/'
    response = await api_client.post(REFRESH)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_without_token_is_rejected(api_client):
    response = await api_client.post(REFRESH)
    assert response.status_code == 401


# LOGOUT


@pytest.mark.asyncio
async def test_logout_clears_cookies_and_revokes_the_session(api_client, user_factory):
    user = await user_factory()
    tokens = await _login(api_client, user)
    assert api_client.cookies.get('access_token')
    assert (await api_client.get(ME)).status_code == 200
    response = await api_client.post('/api/v1/auth/logout')
    assert response.status_code == 200
    assert not api_client.cookies.get('access_token')
    assert not api_client.cookies.get('refresh_token')
    assert (await api_client.get(ME)).status_code == 401
    assert (await _refresh(api_client, tokens['refresh_token'])).status_code == 401


@pytest.mark.asyncio
async def test_logout_with_bearer_only_revokes_its_session(api_client, user_factory):
    user = await user_factory()
    pair = await AuthService.start_session(user)
    other = await AuthService.start_session(user)
    assert (await api_client.post('/api/v1/auth/logout', headers=_bearer(pair.access.token))).status_code == 200
    assert (await _refresh(api_client, pair.refresh.token)).status_code == 401
    assert (await _refresh(api_client, other.refresh.token)).status_code == 200


@pytest.mark.asyncio
async def test_logout_all_invalidates_every_token(api_client, user_factory):
    user = await user_factory()
    first = await AuthService.start_session(user)
    second = await AuthService.start_session(user)
    response = await api_client.post('/api/v1/auth/logout-all', headers=_bearer(first.access.token))
    assert response.status_code == 200
    for pair in (first, second):
        assert (await api_client.get(ME, headers=_bearer(pair.access.token))).status_code == 401
        assert (await _refresh(api_client, pair.refresh.token)).status_code == 401
    assert (await User.get(id=user.id)).token_version == 1


# PASSWORD CHANGE AND DEACTIVATION


@pytest.mark.asyncio
async def test_password_change_invalidates_other_sessions_and_keeps_the_caller(api_client, user_factory):
    user = await user_factory()
    other_device = await AuthService.start_session(user)
    await _login(api_client, user)
    response = await api_client.post(
        f'/api/v1/users/{user.id}/change-password',
        json={'current_password': TEST_PASSWORD, 'new_password': 'brand-new-password'},
    )
    assert response.status_code == 200
    assert (await api_client.get(ME, headers=_bearer(other_device.access.token))).status_code == 401
    assert (await _refresh(api_client, other_device.refresh.token)).status_code == 401
    # The response carried fresh cookies for the caller.
    assert (await api_client.get(ME)).status_code == 200


@pytest.mark.asyncio
async def test_admin_password_reset_invalidates_the_users_tokens(api_client, user_factory, auth_headers):
    admin = await user_factory(is_superuser=True)
    user = await user_factory()
    pair = await AuthService.start_session(user)
    response = await api_client.post(
        f'/api/v1/users/{user.id}/change-password',
        headers=await auth_headers(admin),
        json={'new_password': 'reset-by-admin'},
    )
    assert response.status_code == 200
    assert 'access_token' not in response.cookies
    assert (await api_client.get(ME, headers=_bearer(pair.access.token))).status_code == 401


@pytest.mark.asyncio
async def test_inactive_user_cannot_login_or_use_tokens(api_client, user_factory):
    user = await user_factory()
    pair = await AuthService.start_session(user)
    await User.filter(id=user.id).update(is_active=False)
    response = await api_client.post(LOGIN, json={'email': user.email, 'password': TEST_PASSWORD})
    assert response.status_code == 401
    assert response.json()['error']['message'] == 'Invalid email or password'
    assert (await api_client.get(ME, headers=_bearer(pair.access.token))).status_code == 401
    assert (await _refresh(api_client, pair.refresh.token)).status_code == 401


@pytest.mark.asyncio
async def test_deactivation_by_superuser_revokes_tokens(api_client, user_factory, auth_headers):
    admin = await user_factory(is_superuser=True)
    user = await user_factory()
    pair = await AuthService.start_session(user)
    response = await api_client.patch(
        f'/api/v1/users/{user.id}', headers=await auth_headers(admin), json={'is_active': False}
    )
    assert response.status_code == 200
    assert response.json()['is_active'] is False
    assert await RefreshSession.filter(user_id=user.id, revoked_at=None).count() == 0
    await User.filter(id=user.id).update(is_active=True)
    # Reactivation does not resurrect old tokens: token_version moved on.
    assert (await api_client.get(ME, headers=_bearer(pair.access.token))).status_code == 401


# LOGIN PROTECTION


@pytest.mark.asyncio
@pytest.mark.parametrize('email_known', [True, False])
async def test_login_failures_are_uniform(api_client, user_factory, email_known):
    user = await user_factory()
    email = user.email if email_known else 'nobody@example.test'
    response = await api_client.post(LOGIN, json={'email': email, 'password': 'wrong-password'})
    assert response.status_code == 401
    assert response.json()['error'] == {'code': 'UNAUTHORIZED', 'message': 'Invalid email or password', 'details': {}}
    assert 'access_token' not in response.cookies


@pytest.mark.asyncio
async def test_login_is_rate_limited_per_ip_and_email(api_client, user_factory, monkeypatch):
    monkeypatch.setattr(settings, 'login_rate_limit_attempts', 3)
    user = await user_factory()
    other = await user_factory()
    for _ in range(3):
        response = await api_client.post(LOGIN, json={'email': user.email, 'password': 'wrong'})
        assert response.status_code == 401
    blocked = await api_client.post(LOGIN, json={'email': user.email, 'password': TEST_PASSWORD})
    assert blocked.status_code == 429
    assert blocked.json()['error']['code'] == 'RATE_LIMITED'
    assert 0 < int(blocked.headers['Retry-After']) <= settings.login_rate_limit_window_seconds
    # Another account from the same IP is not blocked.
    assert (await api_client.post(LOGIN, json={'email': other.email, 'password': TEST_PASSWORD})).status_code == 200


@pytest.mark.asyncio
async def test_successful_login_resets_the_failure_counter(api_client, user_factory, monkeypatch):
    monkeypatch.setattr(settings, 'login_rate_limit_attempts', 2)
    user = await user_factory()
    await api_client.post(LOGIN, json={'email': user.email, 'password': 'wrong'})
    await _login(api_client, user)
    await api_client.post(LOGIN, json={'email': user.email, 'password': 'wrong'})
    await _login(api_client, user)
