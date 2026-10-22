from uuid import UUID

from tortoise import fields

from app.core.models import BaseModel
from app.core.scope import Scope


class RefreshSession(BaseModel):
    """
    One issued refresh token. A login starts a family (`family_id`); every refresh revokes the presented
    token and issues the next one in the same family. Presenting a revoked token again (reuse) revokes the
    whole family, so a stolen refresh token dies together with the legitimate session.
    """

    user = fields.ForeignKeyField('models.User', related_name='refresh_sessions', on_delete=fields.CASCADE)
    user_id: UUID
    jti = fields.CharField(max_length=64, unique=True)
    family_id = fields.UUIDField(db_index=True)
    expires_at = fields.DatetimeField()
    revoked_at = fields.DatetimeField(null=True)
    # jti of the token issued when this one was rotated; empty when revoked by logout or reuse detection
    replaced_by = fields.CharField(max_length=64, null=True)

    tenant_scope = Scope(user='user_id')

    class Meta:
        table = 'refresh_session'
        ordering = ('created_at',)
