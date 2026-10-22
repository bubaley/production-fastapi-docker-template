from datetime import timedelta

import pytest

from app.core.settings import settings
from app.core.utils.date_utils import as_utc, utcnow
from app.domains.user.models import User, UserToken


async def _create_token(api_client, headers: dict, **payload) -> dict:
    response = await api_client.post('/api/v1/user-tokens', headers=headers, json={'name': 'Integration', **payload})
    assert response.status_code == 200, response.text
    return response.json()


def _token_header(value: str) -> dict[str, str]:
    return {'Authorization': f'Token {value}'}


@pytest.mark.asyncio
async def test_api_token_authenticates_until_it_expires(api_client, user_factory, auth_headers):
    user = await user_factory()
    expires_at = utcnow() + timedelta(hours=1)
    token = await _create_token(api_client, await auth_headers(user), expires_at=expires_at.isoformat())
    assert token['expires_at'] is not None
    assert (await api_client.get('/api/v1/auth/me', headers=_token_header(token['value']))).status_code == 200
    await UserToken.filter(id=token['id']).update(expires_at=utcnow() - timedelta(seconds=1))
    assert (await api_client.get('/api/v1/auth/me', headers=_token_header(token['value']))).status_code == 401


@pytest.mark.asyncio
async def test_api_token_expiry_must_be_in_the_future(api_client, user_factory, auth_headers):
    user = await user_factory()
    response = await api_client.post(
        '/api/v1/user-tokens',
        headers=await auth_headers(user),
        json={'name': 'Expired', 'expires_at': (utcnow() - timedelta(minutes=1)).isoformat()},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_api_token_of_inactive_user_is_rejected(api_client, user_factory, auth_headers):
    user = await user_factory()
    token = await _create_token(api_client, await auth_headers(user))
    await User.filter(id=user.id).update(is_active=False)
    assert (await api_client.get('/api/v1/auth/me', headers=_token_header(token['value']))).status_code == 401


@pytest.mark.asyncio
async def test_api_token_cannot_create_api_tokens(api_client, user_factory, auth_headers):
    user = await user_factory()
    token = await _create_token(api_client, await auth_headers(user))
    response = await api_client.post(
        '/api/v1/user-tokens', headers=_token_header(token['value']), json={'name': 'Minted by a token'}
    )
    assert response.status_code == 403
    assert await UserToken.filter(user_id=user.id).count() == 1


@pytest.mark.asyncio
async def test_last_used_at_writes_are_throttled(api_client, user_factory, auth_headers, monkeypatch):
    user = await user_factory()
    token = await _create_token(api_client, await auth_headers(user))
    await api_client.get('/api/v1/auth/me', headers=_token_header(token['value']))
    first_use = (await UserToken.get(id=token['id'])).last_used_at
    assert first_use is not None

    await api_client.get('/api/v1/auth/me', headers=_token_header(token['value']))
    assert (await UserToken.get(id=token['id'])).last_used_at == first_use

    monkeypatch.setattr(settings, 'api_token_touch_interval_seconds', 0)
    await api_client.get('/api/v1/auth/me', headers=_token_header(token['value']))
    last_used_at = (await UserToken.get(id=token['id'])).last_used_at
    assert last_used_at is not None
    assert as_utc(last_used_at) >= as_utc(first_use)
