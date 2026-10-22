import pytest

from app.domains.auth.services.auth_service import AuthService
from app.domains.user.models import User, UserToken


@pytest.mark.asyncio
@pytest.mark.parametrize('method', ['patch', 'put'])
async def test_token_owner_cannot_be_changed(api_client, user_factory, method):
    actor = await user_factory()
    admin = await user_factory(is_superuser=True)
    headers = {'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}'}
    created = await api_client.post('/api/v1/user-tokens', headers=headers, json={'name': 'Own token'})
    assert created.status_code == 200
    token = created.json()
    response = await getattr(api_client, method)(
        f'/api/v1/user-tokens/{token["id"]}', headers=headers, json={'name': 'Changed', 'user_id': str(admin.id)}
    )
    assert response.status_code == 422
    stored = await UserToken.get(id=token['id'])
    assert stored.user_id == actor.id
    response = await api_client.get('/api/v1/auth/me', headers={'Authorization': f'Token {token["value"]}'})
    assert response.status_code == 200
    assert response.json()['user']['id'] == str(actor.id)
    assert response.json()['user']['is_superuser'] is False


@pytest.mark.asyncio
async def test_owner_can_rename_token_without_exposing_secret(api_client, user_factory):
    actor = await user_factory()
    headers = {'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}'}
    created = await api_client.post('/api/v1/user-tokens', headers=headers, json={'name': 'Original'})
    token = created.json()
    response = await api_client.patch(f'/api/v1/user-tokens/{token["id"]}', headers=headers, json={'name': 'Renamed'})
    assert response.status_code == 200
    assert response.json()['name'] == 'Renamed'
    assert 'value' not in response.json()
    assert (await UserToken.get(id=token['id'])).user_id == actor.id


@pytest.mark.asyncio
async def test_other_users_cannot_access_or_modify_tokens(api_client, user_factory):
    owner = await user_factory()
    actor = await user_factory()
    owner_headers = {'Authorization': f'Bearer {(await AuthService.start_session(owner)).access.token}'}
    token = (await api_client.post('/api/v1/user-tokens', headers=owner_headers, json={'name': 'Private'})).json()
    headers = {'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}'}
    path = f'/api/v1/user-tokens/{token["id"]}'
    assert (await api_client.get(path, headers=headers)).status_code == 404
    assert (await api_client.patch(path, headers=headers, json={'name': 'Changed'})).status_code == 404
    assert (await api_client.delete(path, headers=headers)).status_code == 404
    assert (
        await api_client.post(
            '/api/v1/user-tokens', headers=headers, json={'name': 'Impersonate', 'user_id': str(owner.id)}
        )
    ).status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize('admin, expected_status', [(False, 403), (True, 201)])
async def test_only_superuser_creates_users(api_client, user_factory, admin, expected_status):
    actor = await user_factory(is_superuser=admin)
    response = await api_client.post(
        '/api/v1/users',
        headers={'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}'},
        json={'email': 'new@example.test', 'first_name': 'New', 'last_name': 'User', 'password': 'new-password'},
    )
    assert response.status_code == expected_status
    assert await User.filter(email='new@example.test').exists() is admin


@pytest.mark.asyncio
async def test_profile_is_available_without_organization_membership(api_client, user_factory):
    actor = await user_factory()
    headers = {'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}'}
    response = await api_client.get(f'/api/v1/users/{actor.id}', headers=headers)
    assert response.status_code == 200
    assert response.json()['id'] == str(actor.id)
