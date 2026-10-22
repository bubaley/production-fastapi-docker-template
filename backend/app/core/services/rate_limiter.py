import hashlib
import math
import time
from collections.abc import Callable

from loguru import logger

from app.core.redis import get_redis
from app.core.settings import settings


class _MemoryWindows:
    """Per-process fixed windows: used in tests and as a fallback while Redis is unavailable."""

    def __init__(self) -> None:
        self._windows: dict[str, tuple[int, float]] = {}

    def _current(self, key: str) -> tuple[int, float] | None:
        window = self._windows.get(key)
        if window and window[1] <= time.monotonic():
            del self._windows[key]
            return None
        return window

    def count(self, key: str) -> tuple[int, int]:
        window = self._current(key)
        if not window:
            return 0, 0
        return window[0], max(1, math.ceil(window[1] - time.monotonic()))

    def hit(self, key: str, window_seconds: int) -> None:
        window = self._current(key)
        if window:
            self._windows[key] = (window[0] + 1, window[1])
        else:
            self._windows[key] = (1, time.monotonic() + window_seconds)

    def reset(self, key: str) -> None:
        self._windows.pop(key, None)

    def clear(self) -> None:
        self._windows.clear()


class RateLimiter:
    """
    Fixed-window counter of failed attempts. `retry_after()` returns seconds to wait once the limit is reached.
    Redis-backed so limits hold across workers; falls back to process memory if Redis fails.
    """

    def __init__(self, namespace: str, limit: Callable[[], int], window_seconds: Callable[[], int]):
        self.namespace = namespace
        self._limit = limit
        self._window_seconds = window_seconds
        self.memory = _MemoryWindows()

    def _key(self, *parts: str) -> str:
        digest = hashlib.sha256('|'.join(parts).encode()).hexdigest()
        return f'ratelimit:{self.namespace}:{digest}'

    @staticmethod
    def _use_redis() -> bool:
        return not settings.testing

    async def retry_after(self, *parts: str) -> int | None:
        key = self._key(*parts)
        count, ttl = await self._count(key)
        return ttl if count >= self._limit() else None

    async def _count(self, key: str) -> tuple[int, int]:
        if self._use_redis():
            try:
                redis = get_redis()
                async with redis.pipeline(transaction=False) as pipe:
                    pipe.get(key)
                    pipe.ttl(key)
                    raw, ttl = await pipe.execute()
                return int(raw or 0), max(1, int(ttl))
            except Exception as e:
                logger.warning('Rate limiter falls back to memory: {}', e)
        return self.memory.count(key)

    async def hit(self, *parts: str) -> None:
        key = self._key(*parts)
        window = self._window_seconds()
        if self._use_redis():
            try:
                redis = get_redis()
                async with redis.pipeline(transaction=True) as pipe:
                    pipe.incr(key)
                    pipe.expire(key, window, nx=True)
                    await pipe.execute()
                return
            except Exception as e:
                logger.warning('Rate limiter falls back to memory: {}', e)
        self.memory.hit(key, window)

    async def reset(self, *parts: str) -> None:
        key = self._key(*parts)
        self.memory.reset(key)
        if self._use_redis():
            try:
                await get_redis().delete(key)
            except Exception as e:
                logger.warning('Rate limiter reset failed: {}', e)


login_rate_limiter = RateLimiter(
    'login',
    limit=lambda: settings.login_rate_limit_attempts,
    window_seconds=lambda: settings.login_rate_limit_window_seconds,
)
