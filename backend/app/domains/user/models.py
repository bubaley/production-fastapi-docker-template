from uuid import UUID, uuid4

from tortoise import fields

from app.core.models import BaseModel
from app.core.scope import Scope
from app.core.settings import settings
from app.domains.auth.services.auth_service import AuthService


class User(BaseModel):
    email = fields.CharField(max_length=128, unique=True)
    password = fields.CharField(max_length=128)
    first_name = fields.CharField(max_length=128)
    last_name = fields.CharField(max_length=128)
    is_superuser = fields.BooleanField(default=False)

    tenant_scope = Scope(user='id')

    @staticmethod
    def _password_peppers(user_id: UUID) -> tuple[str, str]:
        # Current pepper first. The legacy `{id}{SECRET_KEY}` pepper is only a verification fallback:
        # hashes created before PASSWORD_PEPPER existed keep working and are re-hashed on login.
        return settings.password_pepper, f'{user_id}{settings.secret_key}'

    def set_password(self, password: str) -> None:
        """Blocking bcrypt call; use `set_password_async` inside the event loop."""
        self.password = AuthService.hash_password(password, settings.password_pepper)

    async def set_password_async(self, password: str) -> None:
        self.password = await AuthService.hash_password_async(password, settings.password_pepper)

    def verify_password(self, password: str) -> bool:
        """Blocking bcrypt call that never upgrades legacy hashes; prefer `verify_password_async`."""
        return AuthService.match_pepper(password, self.password, self._password_peppers(self.id)) is not None

    async def verify_password_async(self, password: str) -> bool:
        """Verify the password; a legacy-format hash is re-hashed with the current pepper and saved."""
        match = await AuthService.match_pepper_async(password, self.password, self._password_peppers(self.id))
        if match is None:
            return False
        if match > 0:
            await self.set_password_async(password)
            await self.save(update_fields=['password'])
        return True

    @classmethod
    async def verify_dummy_password(cls, password: str) -> None:
        """Run a check that always fails, costing as much as a failed check for an existing user."""
        await AuthService.verify_dummy_password(password, cls._password_peppers(uuid4()))

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

    tenant_scope = Scope(user='user_id')

    class Meta:
        table = 'user_token'
        ordering = ('created_at',)
