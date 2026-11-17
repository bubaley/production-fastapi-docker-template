import asyncio
from collections.abc import Iterator
from typing import Any

import pytest
from httpx2 import AsyncClient

from app.conftest import TEST_PASSWORD
from app.core.settings import settings
from app.domains.auth.services.setup_service import SetupService
from app.domains.organization.models import Organization, OrganizationUser
from app.domains.user.models import User

STATUS = '/api/v1/setup/status'
SETUP = '/api/v1/setup'
ME = '/api/v1/auth/me'


@pytest.fixture(autouse=True)
def _fresh_setup_state() -> Iterator[None]:
    """The "complete" flag is cached per process; each test starts from its own database state."""
    SetupService._complete = False
    yield
    SetupService._complete = False


def _body(**extra: Any) -> dict[str, Any]:
    return {
        'email': 'Owner@Example.test',
        'first_name': 'Ada',
        'last_name': 'Owner',
        'password': TEST_PASSWORD,
        **extra,
    }


@pytest.mark.asyncio
async def test_empty_database_runs_setup_once_and_signs_in(api_client: AsyncClient):
    assert (await api_client.get(STATUS)).json() == {'needs_setup': True, 'token_required': False}

    response = await api_client.post(SETUP, json=_body(organization={'name': 'Acme', 'key': 'acme'}))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body['user']['email'] == 'owner@example.test'
    assert body['user']['is_superuser'] is True
    assert [org['key'] for org in body['organizations']] == ['acme']
    assert 'token' not in response.text
    me = await api_client.get(ME)  # the setup response set the auth cookies
    assert me.status_code == 200
    user = await User.get(email='owner@example.test')
    assert await user.verify_password_async(TEST_PASSWORD)
    assert await OrganizationUser.filter(user=user, organization__key='acme').exists()

    assert (await api_client.get(STATUS)).json()['needs_setup'] is False
    again = await api_client.post(SETUP, json=_body(email='second@example.test'))
    assert again.status_code == 409
    assert again.json()['error']['code'] == 'CONFLICT'
    assert await User.all().count() == 1


@pytest.mark.asyncio
async def test_setup_without_organization(api_client: AsyncClient):
    response = await api_client.post(SETUP, json=_body())
    assert response.status_code == 200, response.text
    assert response.json()['organizations'] == []
    assert not await Organization.exists()


@pytest.mark.asyncio
async def test_existing_users_close_setup(api_client: AsyncClient, user_factory):
    await user_factory()
    assert (await api_client.get(STATUS)).json()['needs_setup'] is False
    response = await api_client.post(SETUP, json=_body())
    assert response.status_code == 409
    assert not await User.filter(email='owner@example.test').exists()


@pytest.mark.asyncio
async def test_concurrent_setups_create_exactly_one_user(api_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    """Every request passes the early check; the transaction lock lets only the first one create a user."""
    set_password = User.set_password_async

    async def slow_set_password(user: User, password: str) -> None:
        await asyncio.sleep(0.05)  # inside the transaction, after the "no users yet" check: the others catch up
        await set_password(user, password)

    monkeypatch.setattr(User, 'set_password_async', slow_set_password)
    responses = await asyncio.gather(
        *(api_client.post(SETUP, json=_body(email=f'owner{index}@example.test')) for index in range(4))
    )
    assert sorted(response.status_code for response in responses) == [200, 409, 409, 409]
    assert await User.all().count() == 1


@pytest.mark.asyncio
async def test_setup_validates_password_and_organization_key(api_client: AsyncClient):
    short = await api_client.post(SETUP, json=_body(password='short'))
    assert short.status_code == 422
    bad_key = await api_client.post(SETUP, json=_body(organization={'name': 'Acme', 'key': ' acme'}))
    assert bad_key.status_code == 422
    assert not await User.exists()


@pytest.mark.asyncio
async def test_setup_token_is_required_when_configured(api_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, 'setup_token', 'first-run-secret')
    assert (await api_client.get(STATUS)).json() == {'needs_setup': True, 'token_required': True}

    missing = await api_client.post(SETUP, json=_body())
    wrong = await api_client.post(SETUP, json=_body(setup_token='guess'))
    assert missing.status_code == wrong.status_code == 403
    assert not await User.exists()

    response = await api_client.post(SETUP, json=_body(setup_token='first-run-secret'))
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_failed_setup_attempts_are_rate_limited(api_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, 'setup_token', 'first-run-secret')
    monkeypatch.setattr(settings, 'login_rate_limit_attempts', 2)
    for _ in range(2):
        assert (await api_client.post(SETUP, json=_body(setup_token='guess'))).status_code == 403
    limited = await api_client.post(SETUP, json=_body(setup_token='first-run-secret'))
    assert limited.status_code == 429
    assert limited.headers['Retry-After']
