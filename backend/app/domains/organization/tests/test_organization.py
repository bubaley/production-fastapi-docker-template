import pytest
from tortoise.exceptions import IntegrityError

from app.domains.organization.models import Organization


@pytest.mark.asyncio
async def test_create_organization(db):
    org = await Organization.create(name='Acme', key='acme')

    assert org.id is not None
    assert org.name == 'Acme'
    assert org.key == 'acme'
    assert org.created_at is not None
    assert org.updated_at is not None


@pytest.mark.asyncio
async def test_get_organization_by_key(db):
    created = await Organization.create(name='Acme', key='acme')

    org = await Organization.get(key='acme')

    assert org.id == created.id
    assert org.name == 'Acme'


@pytest.mark.asyncio
async def test_organization_key_must_be_unique(db):
    await Organization.create(name='Acme', key='acme')

    with pytest.raises(IntegrityError):
        await Organization.create(name='Other', key='acme')


@pytest.mark.asyncio
@pytest.mark.parametrize('key', [' acme', 'acme ', 'ac\nme', '', 'k' * 129])
async def test_organization_key_must_travel_in_a_header(api_client, user_factory, auth_headers, key):
    """Edge whitespace is trimmed in transit and control characters cannot be sent, so such a key never resolves."""
    headers = await auth_headers(await user_factory())
    response = await api_client.post('/api/v1/organizations', headers=headers, json={'name': 'Acme', 'key': key})
    assert response.status_code == 422
    assert not await Organization.filter(name='Acme').exists()
