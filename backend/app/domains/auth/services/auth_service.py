from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from loguru import logger
from tortoise.expressions import F
from tortoise.transactions import in_transaction

from app.core.exceptions import AppException
from app.core.schemas import ErrorCode
from app.core.services.crypto_service import CryptoService
from app.core.services.rate_limiter import login_rate_limiter
from app.core.settings import settings
from app.core.utils.date_utils import as_utc, utcnow
from app.domains.auth.models import RefreshSession
from app.domains.auth.services.token_service import TokenClaims, TokenPair, TokenService, TokenType
from app.domains.user.models import User, UserToken

INVALID_CREDENTIALS = 'Invalid email or password'
INVALID_REFRESH_TOKEN = 'Invalid refresh token'


class AuthMethod(StrEnum):
    JWT = 'jwt'
    API_TOKEN = 'api_token'


@dataclass(frozen=True)
class Authentication:
    user: User
    method: AuthMethod
    # When the credential stops being valid; None for API tokens without expiry.
    expires_at: datetime | None = None


@dataclass(frozen=True)
class Session:
    """A started session: the user and the tokens the transport hands out (as cookies)."""

    user: User
    tokens: TokenPair


def _unauthorized(message: str) -> AppException:
    return AppException.from_attrs(ErrorCode.UNAUTHORIZED, message)


class AuthService:
    """
    Token lifecycle. Transport-agnostic: `domains/auth/transport.py` puts the tokens into HttpOnly cookies.

    - login: verify password (rate limited per IP + email) and start a refresh-session family
    - refresh: rotate the refresh token; reuse of a rotated token revokes the whole family
    - logout: revoke the family of the presented token
    - invalidate_user_tokens: bump `token_version` and revoke every session (password change, logout-all,
      deactivation); every JWT issued before stops working
    """

    # LOGIN

    @staticmethod
    async def login(email: str, password: str, client_ip: str) -> Session:
        if retry_after := await login_rate_limiter.retry_after(client_ip, email):
            raise AppException.from_attrs(
                ErrorCode.RATE_LIMITED, 'Too many login attempts', headers={'Retry-After': str(retry_after)}
            )
        # iexact also matches accounts stored before emails were normalized to lowercase.
        user = await User.filter(email__iexact=email).first()
        if not user:
            await User.verify_dummy_password(password)
        if not user or not await user.verify_password_async(password) or not user.is_active:
            await login_rate_limiter.hit(client_ip, email)
            raise _unauthorized(INVALID_CREDENTIALS)
        await login_rate_limiter.reset(client_ip, email)
        return Session(user=user, tokens=await AuthService.start_session(user))

    @staticmethod
    async def start_session(user: User) -> TokenPair:
        pair = TokenService.issue_pair(user, session_id=uuid4())
        await RefreshSession.create(
            user=user, jti=pair.refresh.jti, family_id=pair.session_id, expires_at=pair.refresh.expires_at
        )
        return pair

    # REFRESH

    @staticmethod
    async def refresh(refresh_token: str) -> TokenPair:
        claims = TokenService.decode(refresh_token, TokenType.REFRESH)
        user = await AuthService._user_for_claims(claims) if claims else None
        if not claims or not user:
            raise _unauthorized(INVALID_REFRESH_TOKEN)

        session = await AuthService._session_for_refresh(refresh_token, claims, user)
        now = utcnow()
        if session.revoked_at is not None:
            await AuthService._handle_reuse(session)
        if as_utc(session.expires_at) <= now:
            raise _unauthorized(INVALID_REFRESH_TOKEN)

        pair = TokenService.issue_pair(user, session_id=session.family_id)
        async with in_transaction():
            rotated = await RefreshSession.filter(id=session.id, revoked_at=None).update(
                revoked_at=now, replaced_by=pair.refresh.jti
            )
            if not rotated:
                # A parallel request rotated the same token a moment ago.
                raise _unauthorized('Refresh token already used')
            await RefreshSession.create(
                user=user, jti=pair.refresh.jti, family_id=session.family_id, expires_at=pair.refresh.expires_at
            )
        return pair

    @staticmethod
    async def _session_for_refresh(refresh_token: str, claims: TokenClaims, user: User) -> RefreshSession:
        if claims.jti is not None:
            session = await RefreshSession.get_or_none(jti=claims.jti, user_id=user.id)
            if not session:
                raise _unauthorized(INVALID_REFRESH_TOKEN)
            return session
        # Legacy refresh token (no jti): it becomes the root of a new family, keyed by its digest, so it can
        # be exchanged exactly once.
        digest = CryptoService.hash_value(refresh_token)
        session = await RefreshSession.get_or_none(jti=digest, user_id=user.id)
        if session is None:
            session = await RefreshSession.create(
                user=user, jti=digest, family_id=uuid4(), expires_at=claims.expires_at
            )
        return session

    @staticmethod
    async def _handle_reuse(session: RefreshSession) -> None:
        leeway = timedelta(seconds=settings.refresh_reuse_leeway_seconds)
        revoked_at = as_utc(session.revoked_at) if session.revoked_at else None
        if session.replaced_by and revoked_at and utcnow() - revoked_at <= leeway:
            raise _unauthorized('Refresh token already used')
        revoked = await AuthService.revoke_family(session.family_id)
        logger.warning(
            'Refresh token reuse detected for user {}: revoked {} session(s) of family {}',
            session.user_id,
            revoked,
            session.family_id,
        )
        raise _unauthorized(INVALID_REFRESH_TOKEN)

    # LOGOUT

    @staticmethod
    async def logout(refresh_token: str | None = None, access_token: str | None = None) -> None:
        """Revoke the session family of the presented token. Invalid or expired tokens are ignored."""
        family_id: UUID | None = None
        if refresh_token and (claims := TokenService.decode(refresh_token, TokenType.REFRESH)):
            jti = claims.jti or CryptoService.hash_value(refresh_token)
            session = await RefreshSession.get_or_none(jti=jti, user_id=claims.user_id)
            family_id = session.family_id if session else claims.session_id
        if family_id is None and access_token and (claims := TokenService.decode(access_token, TokenType.ACCESS)):
            family_id = claims.session_id
        if family_id is not None:
            await AuthService.revoke_family(family_id)

    @staticmethod
    async def revoke_family(family_id: UUID) -> int:
        return await RefreshSession.filter(family_id=family_id, revoked_at=None).update(revoked_at=utcnow())

    @staticmethod
    async def invalidate_user_tokens(user: User) -> None:
        """Every JWT issued to the user stops working; refresh sessions are revoked. API tokens are kept."""
        await User.filter(id=user.id).update(token_version=F('token_version') + 1)
        await user.refresh_from_db(fields=['token_version'])
        await RefreshSession.filter(user_id=user.id, revoked_at=None).update(revoked_at=utcnow())

    # AUTHENTICATION

    @staticmethod
    async def _user_for_claims(claims: TokenClaims) -> User | None:
        user = await User.get_or_none(id=claims.user_id)
        if not user or not user.is_active or user.token_version != claims.version:
            return None
        return user

    @staticmethod
    async def authenticate_access_token(token: str) -> Authentication | None:
        claims = TokenService.decode(token, TokenType.ACCESS)
        user = await AuthService._user_for_claims(claims) if claims else None
        if not claims or not user:
            return None
        return Authentication(user=user, method=AuthMethod.JWT, expires_at=claims.expires_at)

    @staticmethod
    async def authenticate_api_token(value: str) -> Authentication | None:
        token = await UserToken.filter(value_hash=CryptoService.hash_value(value)).select_related('user').first()
        if not token or not token.user.is_active:
            return None
        now = utcnow()
        expires_at = as_utc(token.expires_at) if token.expires_at else None
        if expires_at and expires_at <= now:
            return None
        touch_interval = timedelta(seconds=settings.api_token_touch_interval_seconds)
        if token.last_used_at is None or now - as_utc(token.last_used_at) >= touch_interval:
            await UserToken.filter(id=token.id).update(last_used_at=now)
        return Authentication(user=token.user, method=AuthMethod.API_TOKEN, expires_at=expires_at)
