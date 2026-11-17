import pytest
from fastapi import HTTPException

from app.domains.organization.models import Organization, OrganizationUser
from app.shared.services.owned_data_provider import OwnedData, OwnedDataProvider


@pytest.mark.asyncio
async def test_organization_id_and_key_resolve_the_same_membership(user_factory):
    """`Organization-Id` resolves by id under the same membership rule as `Organization-Key`."""
    member = await user_factory()
    organization = await Organization.create(name='Acme', key='acme')
    await OrganizationUser.create(organization=organization, user=member)

    by_id, by_key = await OwnedDataProvider.resolve_owned_data(
        [OwnedData(organization_id=organization.id), OwnedData(organization_key=organization.key)], member
    )
    assert by_id.organization is not None and by_id.organization.id == organization.id
    assert by_key.organization is not None and by_key.organization.id == organization.id


@pytest.mark.asyncio
@pytest.mark.parametrize('payload', ['id', 'key'])
async def test_foreign_organization_is_rejected_even_for_superusers(user_factory, payload):
    outsider = await user_factory(is_superuser=True)
    organization = await Organization.create(name='Acme', key='acme')
    await OrganizationUser.create(organization=organization, user=await user_factory())
    data = OwnedData(organization_id=organization.id) if payload == 'id' else OwnedData(organization_key='acme')

    with pytest.raises(HTTPException) as error:
        await OwnedDataProvider.resolve_owned_data([data], outsider)
    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_organization_id_header(api_client, user_factory, auth_headers):
    member = await user_factory()
    organization = await Organization.create(name='Acme', key='acme')
    other = await Organization.create(name='Other', key='other')
    await OrganizationUser.create(organization=organization, user=member)
    headers = await auth_headers(member)

    async def members(**extra: str) -> int:
        return (await api_client.get('/api/v1/organization-users', headers={**headers, **extra})).status_code

    assert await members(**{'Organization-Id': str(organization.id)}) == 200
    assert await members(**{'Organization-Id': str(other.id)}) == 400
    assert await members(**{'Organization-Id': str(organization.id), 'Organization-Key': 'acme'}) == 400
