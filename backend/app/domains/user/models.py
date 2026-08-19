from uuid import UUID

from tortoise import fields

from app.core.models import BaseModel
from app.core.settings import settings
from app.domains.auth.services.auth_service import AuthService


class User(BaseModel):
    email = fields.CharField(max_length=128, unique=True)
    password = fields.CharField(max_length=128)
    first_name = fields.CharField(max_length=128)
    last_name = fields.CharField(max_length=128)
    is_superuser = fields.BooleanField(default=False)

    def _password_extra_salt(self) -> str:
        return f'{self.id}{settings.secret_key}'

    def set_password(self, password: str) -> None:
        self.password = AuthService.hash_password(password, extra_salt=self._password_extra_salt())

    def verify_password(self, password: str) -> bool:
        return AuthService.verify_password(password, self.password, extra_salt=self._password_extra_salt())

    class Meta:
        ordering = ('-created_at',)
        table = 'user'


class UserToken(BaseModel):
    user = fields.ForeignKeyField('models.User', related_name='user_tokens', on_delete=fields.CASCADE)
    user_id: UUID
    name = fields.CharField(max_length=128)
    value_hash = fields.CharField(max_length=64, unique=True, db_index=True)
    value_preview = fields.CharField(max_length=64)
    last_used_at = fields.DatetimeField(null=True)

    class Meta:
        table = 'user_token'
        ordering = ('created_at',)
