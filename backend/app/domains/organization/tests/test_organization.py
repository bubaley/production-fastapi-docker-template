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
