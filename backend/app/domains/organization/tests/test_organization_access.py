from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import AppException
from app.domains.auth.services.auth_service import AuthService
from app.domains.organization.models import Organization, OrganizationUser
from app.domains.organization.services.organization_service import OrganizationService


@pytest.mark.asyncio
async def test_member_can_add_remove_and_duplicate_is_reported(api_client, user_factory):
    actor = await user_factory()
    added = await user_factory()
    organization = await Organization.create(name='Org', key='org')
    await OrganizationUser.create(organization=organization, user=actor)
    headers = {
        'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}',
        'Organization-Key': organization.key,
    }
    response = await api_client.post('/api/v1/organization-users', headers=headers, json={'user_id': str(added.id)})
    assert response.status_code == 201
    membership_id = response.json()['id']
    duplicate = await api_client.post('/api/v1/organization-users', headers=headers, json={'user_id': str(added.id)})
    assert duplicate.status_code == 400
    assert await OrganizationUser.filter(organization=organization, user=added).count() == 1
    response = await api_client.delete(f'/api/v1/organization-users/{membership_id}', headers=headers)
    assert response.status_code == 204
    assert not await OrganizationUser.filter(organization=organization, user=added).exists()


@pytest.mark.asyncio
async def test_member_cannot_remove_foreign_organization_membership(api_client, user_factory):
    actor = await user_factory()
    foreign_user = await user_factory()
    organization = await Organization.create(name='Other', key='other')
    membership = await OrganizationUser.create(organization=organization, user=foreign_user)
    headers = {'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}'}
    response = await api_client.delete(f'/api/v1/organization-users/{membership.id}', headers=headers)
    assert response.status_code == 404
    assert await OrganizationUser.filter(id=membership.id).exists()
    response = await api_client.post(
        '/api/v1/organization-users',
        headers={**headers, 'Organization-Key': organization.key},
        json={'user_id': str(actor.id)},
    )
    assert response.status_code == 400
    assert not await OrganizationUser.filter(organization=organization, user=actor).exists()


@pytest.mark.asyncio
async def test_service_rejects_membership_changes_by_outsider(db, user_factory):
    actor = await user_factory()
    owner = await user_factory()
    organization = await Organization.create(name='Other', key='other')
    membership = await OrganizationUser.create(organization=organization, user=owner)
    with pytest.raises(AppException) as error:
        await OrganizationService.remove_member(membership, actor)
    assert error.value.status_code == 403
    assert await OrganizationUser.filter(id=membership.id).exists()


@pytest.mark.asyncio
async def test_superuser_can_remove_membership(api_client, user_factory):
    admin = await user_factory(is_superuser=True)
    member = await user_factory()
    organization = await Organization.create(name='Org', key='org')
    membership = await OrganizationUser.create(organization=organization, user=member)
    response = await api_client.delete(
        f'/api/v1/organization-users/{membership.id}',
        headers={'Authorization': f'Bearer {(await AuthService.start_session(admin)).access.token}'},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_created_organization_includes_actor(api_client, user_factory):
    actor = await user_factory()
    response = await api_client.post(
        '/api/v1/organizations',
        headers={'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}'},
        json={'name': 'New', 'key': 'new'},
    )
    assert response.status_code == 201
    assert await OrganizationUser.filter(organization_id=response.json()['id'], user=actor).exists()


@pytest.mark.asyncio
async def test_organization_creation_rolls_back_when_membership_fails(db, user_factory, monkeypatch):
    actor = await user_factory()
    monkeypatch.setattr(OrganizationUser, 'create', AsyncMock(side_effect=RuntimeError('Membership failed')))
    with pytest.raises(RuntimeError, match='Membership failed'):
        await OrganizationService.create(Organization(name='Rollback', key='rollback'), actor)
    assert not await Organization.filter(key='rollback').exists()


@pytest.mark.asyncio
@pytest.mark.parametrize('method', ['patch', 'put'])
async def test_membership_user_cannot_be_changed(api_client, user_factory, method):
    actor = await user_factory()
    member = await user_factory()
    organization = await Organization.create(name='Org', key='org')
    await OrganizationUser.create(organization=organization, user=actor)
    membership = await OrganizationUser.create(organization=organization, user=member)
    headers = {
        'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}',
        'Organization-Key': organization.key,
    }
    response = await getattr(api_client, method)(
        f'/api/v1/organization-users/{membership.id}', headers=headers, json={'user_id': str(actor.id)}
    )
    assert response.status_code == 422
    assert (await OrganizationUser.get(id=membership.id)).user_id == member.id


@pytest.mark.asyncio
async def test_membership_update_keeps_organization(api_client, user_factory):
    actor = await user_factory()
    organization = await Organization.create(name='Org', key='org')
    other = await Organization.create(name='Other', key='other')
    membership = await OrganizationUser.create(organization=organization, user=actor)
    await OrganizationUser.create(organization=other, user=actor)
    response = await api_client.patch(
        f'/api/v1/organization-users/{membership.id}',
        headers={
            'Authorization': f'Bearer {(await AuthService.start_session(actor)).access.token}',
            'Organization-Key': 'other',
        },
        json={},
    )
    assert response.status_code == 200
    assert (await OrganizationUser.get(id=membership.id)).organization_id == organization.id


@pytest.mark.asyncio
async def test_service_rejects_membership_update_by_outsider(db, user_factory):
    actor = await user_factory()
    owner = await user_factory()
    organization = await Organization.create(name='Other', key='other')
    membership = await OrganizationUser.create(organization=organization, user=owner)
    with pytest.raises(AppException) as error:
        await OrganizationService.update_member(membership, actor)
    assert error.value.status_code == 403
