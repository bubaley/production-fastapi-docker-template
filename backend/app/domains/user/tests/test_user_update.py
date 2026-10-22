import pytest

from app.core.settings import settings
from app.domains.user.models import User


def _user_payload(**overrides) -> dict:
    return {
        'email': 'new@example.test',
        'first_name': 'New',
        'last_name': 'User',
        'password': 'long-enough',
        **overrides,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize('field', ['is_superuser', 'is_active'])
async def test_regular_user_cannot_escalate_or_toggle_activity(api_client, user_factory, auth_headers, field):
    actor = await user_factory()
    value = field == 'is_superuser'  # escalate to superuser / deactivate
    response = await api_client.patch(
        f'/api/v1/users/{actor.id}', headers=await auth_headers(actor), json={field: value}
    )
    assert response.status_code == 403
    stored = await User.get(id=actor.id)
    assert stored.is_superuser is False
    assert stored.is_active is True


@pytest.mark.asyncio
async def test_regular_user_edits_own_profile(api_client, user_factory, auth_headers):
    actor = await user_factory()
    response = await api_client.patch(
        f'/api/v1/users/{actor.id}', headers=await auth_headers(actor), json={'first_name': 'Renamed'}
    )
    assert response.status_code == 200
    assert response.json()['first_name'] == 'Renamed'


@pytest.mark.asyncio
async def test_superuser_cannot_deactivate_themselves(api_client, user_factory, auth_headers):
    admin = await user_factory(is_superuser=True)
    response = await api_client.patch(
        f'/api/v1/users/{admin.id}', headers=await auth_headers(admin), json={'is_active': False}
    )
    assert response.status_code == 400
    assert (await User.get(id=admin.id)).is_active is True


@pytest.mark.asyncio
async def test_superuser_grants_superuser(api_client, user_factory, auth_headers):
    admin = await user_factory(is_superuser=True)
    user = await user_factory()
    response = await api_client.patch(
        f'/api/v1/users/{user.id}', headers=await auth_headers(admin), json={'is_superuser': True}
    )
    assert response.status_code == 200
    assert (await User.get(id=user.id)).is_superuser is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'payload, error_location',
    [
        (_user_payload(password='short'), 'body.password'),
        (_user_payload(email='not-an-email'), 'body.email'),
    ],
)
async def test_user_creation_validates_password_policy_and_email(
    api_client, user_factory, auth_headers, payload, error_location
):
    admin = await user_factory(is_superuser=True)
    response = await api_client.post('/api/v1/users', headers=await auth_headers(admin), json=payload)
    assert response.status_code == 422
    assert response.json()['error']['details']['errors'][0]['location'] == error_location
    assert not await User.filter(email='new@example.test').exists()


@pytest.mark.asyncio
async def test_password_policy_is_configurable(api_client, user_factory, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, 'password_min_length', 4)
    admin = await user_factory(is_superuser=True)
    response = await api_client.post(
        '/api/v1/users', headers=await auth_headers(admin), json=_user_payload(password='four')
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_change_password_enforces_policy_and_current_password(api_client, user_factory, auth_headers):
    user = await user_factory()
    headers = await auth_headers(user)
    path = f'/api/v1/users/{user.id}/change-password'
    short = await api_client.post(
        path, headers=headers, json={'current_password': 'test-password', 'new_password': 'x'}
    )
    assert short.status_code == 422
    wrong = await api_client.post(
        path, headers=headers, json={'current_password': 'wrong-password', 'new_password': 'long-enough'}
    )
    assert wrong.status_code == 400
    assert wrong.json()['error']['message'] == 'Invalid current password'


@pytest.mark.asyncio
async def test_user_cannot_change_someone_elses_password(api_client, user_factory, auth_headers):
    actor = await user_factory()
    other = await user_factory()
    response = await api_client.post(
        f'/api/v1/users/{other.id}/change-password',
        headers=await auth_headers(actor),
        json={'current_password': 'test-password', 'new_password': 'long-enough'},
    )
    # Not visible through the user scope.
    assert response.status_code == 404
