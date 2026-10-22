import hashlib
from datetime import datetime, timedelta

import pytest
from httpx2 import ASGITransport, AsyncClient

from app.conftest import TEST_ORIGIN, TEST_PASSWORD
from app.core.settings import Settings, settings
from app.core.utils.date_utils import utcnow
from app.domains.auth.services.auth_service import AuthService
from app.domains.organization.models import Organization, OrganizationUser
from app.domains.user.models import User, UserToken
from app.main import app

LOGIN = '/api/v1/auth/login'
REFRESH = '/api/v1/auth/refresh'
LOGOUT = '/api/v1/auth/logout'
ME = '/api/v1/auth/me'
FOREIGN_ORIGIN = 'https://evil.example'


async def _login(client: AsyncClient, user: User):
    response = await client.post(LOGIN, json={'email': user.email, 'password': TEST_PASSWORD})
    assert response.status_code == 200, response.text
    return response


def _set_cookie_headers(response) -> dict[str, str]:
    return {header.split('=', 1)[0]: header for header in response.headers.get_list('set-cookie')}


async def _api_token(user: User, value: str = 'integration-token-value') -> str:
    await UserToken.create(
        user=user, name='Integration', value_hash=hashlib.sha256(value.encode()).hexdigest(), value_preview='***'
    )
    return value


# LOGIN / ME


@pytest.mark.asyncio
async def test_login_sets_http_only_cookies_and_returns_no_tokens(api_client, user_factory):
    user = await user_factory()
    organization = await Organization.create(name='Org', key='org')
    await OrganizationUser.create(organization=organization, user=user)

    response = await _login(api_client, user)

    body = response.json()
    assert set(body) == {'user', 'organizations', 'access_expires_at', 'refresh_expires_at'}
    assert body['user']['id'] == str(user.id)
    assert [org['id'] for org in body['organizations']] == [str(organization.id)]
    assert 'token' not in response.text
    access_expires_at = datetime.fromisoformat(body['access_expires_at'])
    assert timedelta(minutes=14) < access_expires_at - utcnow() <= timedelta(minutes=15)
    cookies = _set_cookie_headers(response)
    access = cookies['access_token'].lower()
    assert 'httponly' in access and 'samesite=lax' in access and 'path=/;' in access
    refreshes = [header.lower() for header in response.headers.get_list('set-cookie') if 'refresh_token=' in header]
    assert any('path=/api/v1/auth' in header and 'httponly' in header for header in refreshes)


def test_access_token_lifetime_defaults_to_15_minutes():
    assert Settings.model_fields['jwt_access_token_expire_minutes'].default == 15
    assert Settings.model_fields['jwt_refresh_token_expire_minutes'].default == 60 * 24 * 30


@pytest.mark.asyncio
async def test_me_returns_user_and_organizations(api_client, user_factory, organization_factory):
    user = await user_factory(is_superuser=True)
    first = await organization_factory(members=(user,))
    second = await organization_factory(members=(user,))
    await organization_factory()  # not a member: not listed, even for a superuser
    await _login(api_client, user)

    response = await api_client.get(ME)

    assert response.status_code == 200
    body = response.json()
    assert body['user']['is_superuser'] is True
    assert [org['id'] for org in body['organizations']] == [str(first.id), str(second.id)]


@pytest.mark.asyncio
async def test_session_lifecycle_through_cookies_only(api_client, user_factory):
    user = await user_factory()
    await _login(api_client, user)
    assert (await api_client.get(ME)).status_code == 200

    refreshed = await api_client.post(REFRESH)
    assert refreshed.status_code == 200
    assert set(_set_cookie_headers(refreshed)) >= {'access_token', 'refresh_token'}
    assert (await api_client.get(ME)).status_code == 200

    logout = await api_client.post(LOGOUT)
    assert logout.status_code == 204
    assert (await api_client.get(ME)).status_code == 401
    assert (await api_client.post(REFRESH)).status_code == 401


# CSRF


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'headers, expected',
    [
        ({}, 403),
        ({'Origin': FOREIGN_ORIGIN}, 403),
        ({'Origin': 'null'}, 403),
        ({'Referer': f'{FOREIGN_ORIGIN}/page'}, 403),
        ({'Referer': f'{TEST_ORIGIN}/settings/profile'}, 201),
        ({'Origin': TEST_ORIGIN}, 201),
        ({'Origin': settings.cors_origins[0]}, 201),
    ],
)
async def test_cookie_authenticated_unsafe_requests_need_trusted_origin(db, user_factory, headers, expected):
    user = await user_factory()
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_ORIGIN) as client:
        await _login(client, user)
        response = await client.post('/api/v1/organizations', headers=headers, json={'name': 'Org', 'key': 'org'})
    assert response.status_code == expected, response.text
    if expected == 403:
        assert response.json()['error'] == {'code': 'FORBIDDEN', 'message': 'Origin not allowed', 'details': {}}
        assert not await Organization.exists(key='org')


@pytest.mark.asyncio
async def test_safe_cookie_requests_do_not_need_origin(db, user_factory):
    """SSR: Nitro forwards the browser's Cookie header server-to-server, without an Origin."""
    user = await user_factory()
    pair = await AuthService.start_session(user)
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://127.0.0.1:8000') as client:
        response = await client.get(ME, headers={'Cookie': f'access_token={pair.access.token}'})
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize('path', [REFRESH, LOGOUT])
async def test_public_cookie_endpoints_check_origin(api_client, user_factory, path):
    await _login(api_client, await user_factory())
    response = await api_client.post(path, headers={'Origin': FOREIGN_ORIGIN})
    assert response.status_code == 403
    assert (await api_client.get(ME)).status_code == 200


@pytest.mark.asyncio
async def test_header_credentials_are_exempt_from_origin_check(db, user_factory):
    user = await user_factory()
    token = await _api_token(user)
    bearer = (await AuthService.start_session(user)).access.token
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_ORIGIN) as client:
        for authorization in (f'Token {token}', f'Bearer {bearer}'):
            response = await client.post(
                '/api/v1/organizations',
                headers={'Authorization': authorization, 'Origin': FOREIGN_ORIGIN},
                json={'name': 'Org', 'key': f'org-{authorization[:5].lower().strip()}'},
            )
            assert response.status_code == 201, response.text


# CREDENTIAL ORDER


@pytest.mark.asyncio
async def test_cookie_wins_over_header_and_brings_the_origin_check(api_client, user_factory):
    cookie_user = await user_factory()
    header_user = await user_factory()
    await _login(api_client, cookie_user)
    token = await _api_token(header_user)
    me = await api_client.get(ME, headers={'Authorization': f'Token {token}'})
    assert me.json()['user']['id'] == str(cookie_user.id)
    response = await api_client.post(
        '/api/v1/organizations',
        headers={'Authorization': f'Token {token}', 'Origin': FOREIGN_ORIGIN},
        json={'name': 'Org', 'key': 'org'},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invalid_cookie_falls_back_to_api_token(api_client, user_factory):
    user = await user_factory()
    token = await _api_token(user)
    response = await api_client.get(ME, headers={'Cookie': 'access_token=expired', 'Authorization': f'Token {token}'})
    assert response.status_code == 200
    assert response.json()['user']['id'] == str(user.id)
