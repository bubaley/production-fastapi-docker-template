import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger
from tortoise import connections

from app.core.redis import ping_redis
from app.core.settings import settings

health_router = APIRouter(include_in_schema=False)

CHECK_TIMEOUT_SECONDS = 2.0


@health_router.get('/health')
async def health():
    """Liveness: the process serves requests. Touches no dependencies."""
    return {'status': 'ok', 'version': settings.app_version, 'sha': settings.git_sha}


async def _check_database() -> bool:
    try:
        # Shielded: cancelling a query that is lazily creating the connection pool leaves the pool half-built and
        # every later query hangs. The probe gives up waiting; the query itself finishes in the background.
        query = connections.get('default').execute_query('SELECT 1')
        await asyncio.wait_for(asyncio.shield(query), timeout=CHECK_TIMEOUT_SECONDS)
        return True
    except Exception as e:
        logger.warning('Readiness: database check failed: {}', e)
        return False


async def warm_up_database() -> None:
    """Build the connection pool at startup instead of inside the first request (or readiness probe)."""
    try:
        await connections.get('default').execute_query('SELECT 1')
    except Exception as e:
        logger.warning('Database unavailable at startup ({}); /ready reports it', e)


@health_router.get('/ready')
async def ready():
    """Readiness: database and Redis answer within a short timeout. 503 otherwise."""
    database, redis = await asyncio.gather(_check_database(), ping_redis(timeout=CHECK_TIMEOUT_SECONDS))
    checks = {'database': 'ok' if database else 'error', 'redis': 'ok' if redis else 'error'}
    healthy = database and redis
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={'status': 'ok' if healthy else 'error', 'checks': checks},
    )
