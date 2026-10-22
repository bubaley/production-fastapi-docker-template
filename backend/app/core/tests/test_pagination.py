from datetime import datetime

import pytest

from app.core.viewsets import with_stable_ordering
from app.domains.organization.models import Organization


def _order_sql(queryset) -> str:
    return queryset.sql().split('ORDER BY', 1)[1]


@pytest.mark.asyncio
async def test_stable_ordering_appends_id_once(db):
    assert _order_sql(with_stable_ordering(Organization.all())).count('"id"') == 1
    assert '"created_at"' in _order_sql(with_stable_ordering(Organization.all()))
    explicit = with_stable_ordering(Organization.all().order_by('-name'))
    assert '"name" DESC' in _order_sql(explicit)
    assert '"id"' in _order_sql(explicit)
    already_unique = Organization.all().order_by('id')
    assert with_stable_ordering(already_unique) is already_unique


@pytest.mark.asyncio
async def test_pages_with_equal_sort_keys_neither_repeat_nor_skip(
    api_client, user_factory, organization_factory, auth_headers
):
    actor = await user_factory()
    organizations = [await organization_factory(members=(actor,)) for _ in range(7)]
    # Same created_at for every row: only the id tiebreaker makes the order deterministic.
    await Organization.filter(id__in=[org.id for org in organizations]).update(created_at=datetime(2026, 1, 1))
    headers = await auth_headers(actor)

    seen: list[str] = []
    page = 1
    while True:
        response = await api_client.get('/api/v1/organizations', headers=headers, params={'page': page, 'page_size': 3})
        assert response.status_code == 200
        body = response.json()
        seen.extend(row['id'] for row in body['data'])
        if not body['meta']['has_next']:
            break
        page += 1

    assert len(seen) == len(set(seen)) == 7
    assert seen == sorted(seen)


@pytest.mark.asyncio
async def test_organization_filters(api_client, user_factory, organization_factory, auth_headers):
    actor = await user_factory()
    await organization_factory(members=(actor,), name='Acme Corp')
    await organization_factory(members=(actor,), name='Globex')
    headers = await auth_headers(actor)
    response = await api_client.get('/api/v1/organizations', headers=headers, params={'name': 'acme'})
    assert response.status_code == 200
    assert [row['name'] for row in response.json()['data']] == ['Acme Corp']
