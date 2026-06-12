from uuid import UUID

from tortoise import fields

from app.core.models import BaseModel
from app.domains.auth.services.auth_service import AuthService


class User(BaseModel):
    email = fields.CharField(max_length=128, unique=True)
    password = fields.CharField(max_length=128)
    first_name = fields.CharField(max_length=128)
    last_name = fields.CharField(max_length=128)
    is_superuser = fields.BooleanField(default=False)

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password = AuthService.hash_password(password)

    def verify_password(self, password: str) -> bool:
        """Verify the user's password against the stored hash."""
        return AuthService.verify_password(password, self.password)

    class Meta:
        ordering = ['-created_at']
        table = 'user'


class UserToken(BaseModel):
    user = fields.ForeignKeyField('models.User', related_name='user_tokens', on_delete=fields.CASCADE)
    user_id: UUID
    value_hash = fields.CharField(max_length=64, unique=True, db_index=True)
    value_preview = fields.CharField(max_length=64)
    last_used_at = fields.DatetimeField(null=True)

    class Meta:
        table = 'user_token'
        ordering = ['created_at']
