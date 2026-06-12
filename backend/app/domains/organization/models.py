from uuid import UUID

from tortoise import fields

from app.core.models import BaseModel


class OrganizationUser(BaseModel):
    organization = fields.ForeignKeyField(
        'models.Organization',
        related_name='org_users',
        on_delete=fields.CASCADE,
    )
    organization_id: UUID
    user = fields.ForeignKeyField('models.User', related_name='org_users', on_delete=fields.CASCADE)
    user_id: UUID

    class Meta:
        table = 'organization_user'
        unique_together = (('organization', 'user'),)
        ordering = ['created_at']


class Organization(BaseModel):
    name = fields.CharField(max_length=128)
    key = fields.CharField(max_length=128, unique=True, db_index=True)

    class Meta:
        ordering = ['created_at']
        table = 'organization'
