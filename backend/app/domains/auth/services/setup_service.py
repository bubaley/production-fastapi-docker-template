import hmac

from loguru import logger
from tortoise.transactions import in_transaction

from app.core.exceptions import AppException
from app.core.schemas import ErrorCode
from app.core.services.rate_limiter import setup_rate_limiter
from app.core.settings import settings
from app.domains.auth.schemas import SetupRequest
from app.domains.auth.services.auth_service import AuthService, Session
from app.domains.organization.models import Organization
from app.domains.organization.services.organization_service import OrganizationService
from app.domains.user.models import User

# Any constant shared by every API process: `pg_advisory_xact_lock` serializes concurrent setup requests.
SETUP_LOCK_ID = 7_301_955_210_042
SETUP_COMPLETE = 'Setup is already complete'
INVALID_SETUP_TOKEN = 'Invalid setup token'


class SetupService:
    """
    First-run setup: while the database has no users, `POST /setup` creates the first superuser (and optionally the
    first organization) and signs them in. Once a user exists, setup is closed: the last user cannot delete
    themselves, so the user table only becomes empty again on a wiped database, which is a fresh deployment.
    """

    # Users never disappear through the API, so "complete" is cached per process; "needs setup" is always re-read.
    _complete = False

    @classmethod
    async def needs_setup(cls) -> bool:
        if not cls._complete:
            cls._complete = await User.exists()
        return not cls._complete

    @staticmethod
    def token_required() -> bool:
        return bool(settings.setup_token)

    @classmethod
    async def complete(cls, data: SetupRequest, client_ip: str) -> Session:
        """Create the first superuser in one locked transaction; a second or concurrent call gets 409."""
        if retry_after := await setup_rate_limiter.retry_after(client_ip):
            raise AppException.from_attrs(
                ErrorCode.RATE_LIMITED, 'Too many setup attempts', headers={'Retry-After': str(retry_after)}
            )
        if not await cls.needs_setup():
            await setup_rate_limiter.hit(client_ip)
            raise AppException.from_attrs(ErrorCode.CONFLICT, SETUP_COMPLETE)
        if cls.token_required() and not hmac.compare_digest(
            (data.setup_token or '').encode(), settings.setup_token.encode()
        ):
            await setup_rate_limiter.hit(client_ip)
            raise AppException.from_attrs(ErrorCode.FORBIDDEN, INVALID_SETUP_TOKEN)

        async with in_transaction() as connection:
            if connection.capabilities.dialect == 'postgres':
                await connection.execute_query('SELECT pg_advisory_xact_lock($1)', [SETUP_LOCK_ID])
            # SQLite (tests with --sqlite) serializes writers itself.
            if await User.exists():
                cls._complete = True
                raise AppException.from_attrs(ErrorCode.CONFLICT, SETUP_COMPLETE)
            user = User(email=data.email, first_name=data.first_name, last_name=data.last_name, is_superuser=True)
            await user.set_password_async(data.password)
            await user.save()
            if data.organization is not None:
                organization = Organization(name=data.organization.name, key=data.organization.key)
                await OrganizationService.create(organization, user)
        cls._complete = True
        logger.info('First-run setup complete: superuser {} created', user.id)
        return Session(user=user, tokens=await AuthService.start_session(user))

    @classmethod
    async def warn_if_open(cls) -> None:
        """Startup log line: an empty database means anyone who reaches the site can claim it."""
        try:
            if not await cls.needs_setup():
                return
        except Exception as e:
            logger.warning('Cannot check first-run setup state ({})', e)
            return
        how = 'with SETUP_TOKEN' if cls.token_required() else 'by anyone who reaches the site (no SETUP_TOKEN set)'
        logger.warning('No users yet: first-run setup at /setup is open {}; or run `manage.py create_superuser`', how)
