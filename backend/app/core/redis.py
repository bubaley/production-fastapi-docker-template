import asyncio

from loguru import logger
from redis.asyncio import Redis

from app.core.settings import settings

_client: Redis | None = None


def get_redis() -> Redis:
    """Shared client for the app Redis (`REDIS_URL`, falls back to `BROKER_REDIS_URL`). Connects lazily."""
    global _client
    if _client is None:
        _client = Redis.from_url(
            settings.app_redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=5,
            health_check_interval=30,
        )
    return _client


async def ping_redis(timeout: float = 1.0) -> bool:
    try:
        return bool(await asyncio.wait_for(get_redis().ping(), timeout=timeout))
    except Exception as e:
        logger.warning('Redis ping failed: {}', e)
        return False


async def close_redis() -> None:
    global _client
    if _client is not None:
        client, _client = _client, None
        await client.aclose()
