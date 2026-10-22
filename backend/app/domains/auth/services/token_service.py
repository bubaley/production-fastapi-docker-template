from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import jwt

from app.core.settings import settings

if TYPE_CHECKING:
    from app.domains.user.models import User


class TokenType(StrEnum):
    ACCESS = 'access'
    REFRESH = 'refresh'


@dataclass(frozen=True)
class IssuedToken:
    token: str
    type: TokenType
    jti: str
    expires_at: datetime


@dataclass(frozen=True)
class TokenPair:
    access: IssuedToken
    refresh: IssuedToken
    session_id: UUID


@dataclass(frozen=True)
class TokenClaims:
    user_id: UUID
    type: TokenType
    version: int
    expires_at: datetime
    jti: str | None = None
    session_id: UUID | None = None
    # Issued before claim versioning: `id` instead of `sub`, no `jti`/`ver`.
    legacy: bool = False


class TokenService:
    """
    JWT encoding and claim validation only; no database access. Claims: `sub` (user id), `type`, `iat`, `exp`,
    `jti`, `ver` (the user's token_version), `sid` (refresh-session family). Tokens from before claim
    versioning carry `id` instead of `sub` and are accepted while `JWT_ACCEPT_LEGACY_TOKENS` is on.
    """

    @staticmethod
    def _lifetime(token_type: TokenType) -> timedelta:
        if token_type == TokenType.ACCESS:
            return timedelta(minutes=settings.jwt_access_token_expire_minutes)
        return timedelta(minutes=settings.jwt_refresh_token_expire_minutes)

    @staticmethod
    def issue(user: User, token_type: TokenType, session_id: UUID) -> IssuedToken:
        now = datetime.now(tz=UTC)
        expires_at = now + TokenService._lifetime(token_type)
        jti = uuid4().hex
        payload: dict[str, Any] = {
            'sub': str(user.id),
            'type': token_type.value,
            'iat': now,
            'exp': expires_at,
            'jti': jti,
            'ver': user.token_version,
            'sid': str(session_id),
        }
        encoded = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
        return IssuedToken(token=encoded, type=token_type, jti=jti, expires_at=expires_at)

    @staticmethod
    def issue_pair(user: User, session_id: UUID) -> TokenPair:
        return TokenPair(
            access=TokenService.issue(user, TokenType.ACCESS, session_id),
            refresh=TokenService.issue(user, TokenType.REFRESH, session_id),
            session_id=session_id,
        )

    @staticmethod
    def decode_payload(token: str) -> dict[str, Any] | None:
        """Signature and expiry check only."""
        try:
            return jwt.decode(
                token, settings.secret_key, algorithms=[settings.jwt_algorithm], options={'require': ['exp']}
            )
        except jwt.PyJWTError:
            return None

    @staticmethod
    def decode(token: str, expected_type: TokenType) -> TokenClaims | None:
        payload = TokenService.decode_payload(token)
        if not payload or payload.get('type') != expected_type.value:
            return None
        legacy = 'sub' not in payload
        if legacy and not settings.jwt_accept_legacy_tokens:
            return None
        try:
            user_id = UUID(str(payload['id'] if legacy else payload['sub']))
            session_id = UUID(str(payload['sid'])) if payload.get('sid') else None
        except KeyError, ValueError:
            return None
        version = payload.get('ver', 0)
        jti = payload.get('jti')
        if not isinstance(version, int) or (jti is not None and not isinstance(jti, str)):
            return None
        return TokenClaims(
            user_id=user_id,
            type=expected_type,
            version=version,
            expires_at=datetime.fromtimestamp(payload['exp'], tz=UTC),
            jti=jti,
            session_id=session_id,
            legacy=legacy,
        )
