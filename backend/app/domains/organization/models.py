from uuid import UUID

from tortoise import fields
from tortoise.expressions import Q, Subquery

from app.core.models import BaseModel
from app.core.scope import Scope


def _memberships_of_user_organizations(user_id: UUID) -> Q:
    # A subquery instead of 'organization__org_users__user_id': Tortoise mis-aliases that self-join.
    member_org_ids = OrganizationUser.filter(user_id=user_id).values('organization_id')
    return Q(organization_id__in=Subquery(member_org_ids))


class OrganizationUser(BaseModel):
    organization = fields.ForeignKeyField(
        'models.Organization',
        related_name='org_users',
        on_delete=fields.CASCADE,
    )
    organization_id: UUID
    user = fields.ForeignKeyField('models.User', related_name='org_users', on_delete=fields.CASCADE)
    user_id: UUID

    tenant_scope = Scope(user=_memberships_of_user_organizations)

    class Meta:
        table = 'organization_user'
        unique_together = (('organization', 'user'),)
        ordering = ('created_at',)


class Organization(BaseModel):
    name = fields.CharField(max_length=128)
    key = fields.CharField(max_length=128, unique=True, db_index=True)

    tenant_scope = Scope(user='org_users__user_id')

    class Meta:
        ordering = ('created_at',)
        table = 'organization'
