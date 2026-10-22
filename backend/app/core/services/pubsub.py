import asyncio
import contextlib
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Awaitable, Callable

from loguru import logger

from app.core.redis import get_redis
from app.core.settings import settings

Handler = Callable[[str], Awaitable[None]]


class PubSub(ABC):
    """Cross-process broadcast of text messages by topic. Handlers run in the subscribing process."""

    def __init__(self) -> None:
        self.handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Handler) -> None:
        if handler not in self.handlers[topic]:
            self.handlers[topic].append(handler)

    async def dispatch(self, topic: str, message: str) -> None:
        for handler in list(self.handlers.get(topic, ())):
            try:
                await handler(message)
            except Exception:
                logger.exception('Pub/sub handler for {} failed', topic)

    @abstractmethod
    async def publish(self, topic: str, message: str) -> None: ...

    async def start(self) -> None:
        return None

    async def stop(self) -> None:
        return None


class InMemoryPubSub(PubSub):
    """Single-process pub/sub for tests: publish calls the handlers directly."""

    async def publish(self, topic: str, message: str) -> None:
        await self.dispatch(topic, message)


class RedisPubSub(PubSub):
    """
    Redis pub/sub. Any process can publish (API workers, taskiq); processes that call `start()` receive.
    The listener reconnects with backoff, so Redis is not required at boot.
    """

    def __init__(self) -> None:
        super().__init__()
        self._task: asyncio.Task[None] | None = None

    async def publish(self, topic: str, message: str) -> None:
        await get_redis().publish(topic, message)

    async def start(self) -> None:
        if self._task is None and self.handlers:
            self._task = asyncio.create_task(self._listen(), name='redis-pubsub-listener')

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    async def _listen(self) -> None:
        backoff = 1.0
        while True:
            pubsub = get_redis().pubsub(ignore_subscribe_messages=True)
            try:
                await pubsub.subscribe(*self.handlers)
                backoff = 1.0
                while True:
                    message = await pubsub.get_message(timeout=1.0)
                    if message and message.get('type') == 'message':
                        await self.dispatch(message['channel'], message['data'])
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning('Redis pub/sub listener disconnected ({}); retrying in {}s', e, backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30.0)
            finally:
                with contextlib.suppress(Exception):
                    await pubsub.aclose()


_pubsub: PubSub | None = None


def get_pubsub() -> PubSub:
    global _pubsub
    if _pubsub is None:
        _pubsub = InMemoryPubSub() if settings.testing else RedisPubSub()
    return _pubsub
