import pytest
from tortoise import Tortoise

from app.core.auth import AuthState
from app.core.exceptions import AppException
from app.core.scope import Scope, Unscoped
from app.domains.auth.services.auth_service import AuthService
from app.domains.organization.models import Organization, OrganizationUser
from app.shared.services.filter_objects_manager import FilterObjectsManager, ScopeConfigurationError


def _auth(user) -> dict[str, str]:
    return {'Authorization': f'Bearer {AuthService.create_access_token(user).token}'}


@pytest.fixture
async def tenants(user_factory):
    """`actor` belongs to `own` and `second`; `outsider` alone belongs to `foreign`."""
    actor = await user_factory()
    outsider = await user_factory()
    own = await Organization.create(name='Own', key='own')
    second = await Organization.create(name='Second', key='second')
    foreign = await Organization.create(name='Foreign', key='foreign')
    await OrganizationUser.create(organization=own, user=actor)
    await OrganizationUser.create(organization=second, user=actor)
    await OrganizationUser.create(organization=foreign, user=outsider)
    return {'actor': actor, 'outsider': outsider, 'own': own, 'second': second, 'foreign': foreign}


@pytest.fixture
def org_scoped_memberships(monkeypatch):
    """Turn OrganizationUser into an organization-scoped model to exercise the organization rule."""

    def apply(*, require_organization: bool = True):
        user_rule = OrganizationUser.tenant_scope
        assert isinstance(user_rule, Scope)
        scope = Scope(user=user_rule.user, organization='organization_id', require_organization=require_organization)
        monkeypatch.setattr(OrganizationUser, 'tenant_scope', scope)

    return apply


async def _organization_ids(state: AuthState) -> set:
    queryset = FilterObjectsManager.filter(OrganizationUser.all(), state)
    return set(await queryset.values_list('organization_id', flat=True))


@pytest.mark.asyncio
async def test_every_registered_model_declares_a_scope(db):
    for model in Tortoise.apps['models'].values():
        FilterObjectsManager.get_scope(model)


@pytest.mark.asyncio
async def test_model_without_scope_fails_closed(db, user_factory, monkeypatch):
    monkeypatch.delattr(Organization, 'tenant_scope')
    with pytest.raises(ScopeConfigurationError, match='Organization has no tenant_scope'):
        FilterObjectsManager.filter(Organization.all(), AuthState(user=await user_factory()))


@pytest.mark.asyncio
async def test_unscoped_model_is_returned_as_is(tenants, monkeypatch):
    monkeypatch.setattr(Organization, 'tenant_scope', Unscoped(reason='test'))
    queryset = FilterObjectsManager.filter(Organization.all(), AuthState(user=tenants['actor']))
    assert await queryset.count() == 3


@pytest.mark.asyncio
async def test_anonymous_state_is_rejected(tenants):
    with pytest.raises(AppException) as error:
        FilterObjectsManager.filter(Organization.all(), AuthState())
    assert error.value.status_code == 401


@pytest.mark.asyncio
async def test_users_see_only_their_organizations(api_client, tenants):
    response = await api_client.get('/api/v1/organizations', headers=_auth(tenants['actor']))
    assert response.status_code == 200
    assert {row['key'] for row in response.json()['data']} == {'own', 'second'}
    foreign_path = f'/api/v1/organizations/{tenants["foreign"].id}'
    assert (await api_client.get(foreign_path, headers=_auth(tenants['actor']))).status_code == 404
    assert (
        await api_client.patch(foreign_path, headers=_auth(tenants['actor']), json={'name': 'X'})
    ).status_code == 404


@pytest.mark.asyncio
async def test_memberships_of_foreign_organizations_are_hidden(api_client, tenants):
    response = await api_client.get('/api/v1/organization-users', headers=_auth(tenants['actor']))
    assert response.status_code == 200
    visible = {row['id'] for row in response.json()['data']}
    expected = await OrganizationUser.filter(organization_id__in=[tenants['own'].id, tenants['second'].id])
    assert visible == {str(membership.id) for membership in expected}


@pytest.mark.asyncio
async def test_organization_scope_narrows_to_selected_organization(tenants, org_scoped_memberships):
    org_scoped_memberships()
    state = AuthState(user=tenants['actor'], organization=tenants['own'])
    assert await _organization_ids(state) == {tenants['own'].id}


@pytest.mark.asyncio
async def test_organization_scope_requires_organization_header(tenants, org_scoped_memberships):
    org_scoped_memberships()
    with pytest.raises(AppException) as error:
        FilterObjectsManager.filter(OrganizationUser.all(), AuthState(user=tenants['actor']))
    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_optional_organization_scope_still_filters_by_user(tenants, org_scoped_memberships):
    org_scoped_memberships(require_organization=False)
    state = AuthState(user=tenants['actor'])
    assert await _organization_ids(state) == {tenants['own'].id, tenants['second'].id}


@pytest.mark.asyncio
async def test_user_filter_applies_even_with_foreign_organization(tenants, org_scoped_memberships):
    org_scoped_memberships()
    state = AuthState(user=tenants['actor'], organization=tenants['foreign'])
    assert await _organization_ids(state) == set()
