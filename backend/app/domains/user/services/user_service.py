import secrets
from datetime import datetime
from typing import Any
from uuid import UUID

from app.core.exceptions import AppException
from app.core.schemas import ErrorCode
from app.core.services.crypto_service import CryptoService
from app.core.utils.date_utils import as_utc, utcnow
from app.domains.auth.services.auth_service import AuthMethod, AuthService
from app.domains.auth.services.token_service import TokenPair
from app.domains.user.models import User, UserToken

# Fields only a superuser may set on any account, including their own.
SUPERUSER_ONLY_FIELDS = ('is_superuser', 'is_active')


class UserService:
    # PROFILE

    @staticmethod
    def validate_create(actor: User, is_superuser: bool) -> None:
        if is_superuser and not actor.is_superuser:
            raise AppException.from_attrs(ErrorCode.FORBIDDEN, 'Forbidden')

    @staticmethod
    def validate_update(actor: User, target_id: UUID | None, changes: dict[str, Any]) -> None:
        if not actor.is_superuser:
            forbidden = [field for field in SUPERUSER_ONLY_FIELDS if field in changes]
            if forbidden:
                raise AppException.from_attrs(ErrorCode.FORBIDDEN, f'Cannot change {", ".join(forbidden)}')
        if changes.get('is_active') is False and target_id == actor.id:
            raise AppException.from_attrs(ErrorCode.VALIDATION_ERROR, 'Cannot deactivate yourself')

    @staticmethod
    async def after_update(user: User, changes: dict[str, Any]) -> None:
        if changes.get('is_active') is False:
            await AuthService.invalidate_user_tokens(user)

    # PASSWORD

    @staticmethod
    async def validate_password_change(actor: User, user: User, current_password: str | None) -> None:
        if actor.is_superuser:
            return
        if actor.id != user.id:
            raise AppException.from_attrs(ErrorCode.FORBIDDEN, 'Forbidden')
        if not current_password or not await user.verify_password_async(current_password):
            raise AppException.from_attrs(ErrorCode.VALIDATION_ERROR, 'Invalid current password')

    @staticmethod
    async def change_password(actor: User, user: User, new_password: str) -> TokenPair | None:
        """
        Store the new password and invalidate every token of the user. When users change their own
        password, a fresh session is returned so the current client stays signed in.
        """
        await user.set_password_async(new_password)
        await user.save(update_fields=['password', 'updated_at'])
        await AuthService.invalidate_user_tokens(user)
        if actor.id == user.id:
            return await AuthService.start_session(user)
        return None

    # API TOKENS

    @staticmethod
    def validate_api_token_creation(
        actor: User, auth_method: AuthMethod | None, owner_id: UUID | None, expires_at: datetime | None
    ) -> UUID:
        """Return the owner id. An API token cannot mint new API tokens."""
        if auth_method == AuthMethod.API_TOKEN:
            raise AppException.from_attrs(ErrorCode.FORBIDDEN, 'API tokens cannot create API tokens')
        if owner_id and owner_id != actor.id and not actor.is_superuser:
            raise AppException.from_attrs(ErrorCode.FORBIDDEN, 'Forbidden')
        if expires_at and as_utc(expires_at) <= utcnow():
            raise AppException.from_attrs(ErrorCode.VALIDATION_ERROR, 'expires_at must be in the future')
        return owner_id or actor.id

    @staticmethod
    async def create_api_token(owner_id: UUID, name: str, expires_at: datetime | None) -> tuple[UserToken, str]:
        """Return the token and its secret value; only the hash is stored, the value is shown once."""
        value = secrets.token_urlsafe(64)
        token = await UserToken.create(
            user_id=owner_id,
            name=name,
            value_hash=CryptoService.hash_value(value),
            value_preview=f'***{value[-6:]}',
            expires_at=expires_at,
        )
        return token, value
