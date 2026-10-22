from taskiq import AsyncBroker, InMemoryBroker, TaskiqScheduler
from taskiq.events import TaskiqEvents
from taskiq_redis import ListRedisScheduleSource, RedisAsyncResultBackend, RedisStreamBroker
from tortoise import Tortoise

from app.core.database import TORTOISE_ORM
from app.core.logging import setup_logging
from app.core.redis import close_redis
from app.core.settings import settings


def _build_broker() -> AsyncBroker:
    if settings.testing:
        # Tasks run in the calling event loop; `await task.wait_result()` returns immediately.
        return InMemoryBroker()
    # Redis Streams with consumer groups: a message is acknowledged after the task runs, so a crashed worker
    # does not lose it. Results expire after TASKIQ_RESULT_TTL_SECONDS.
    return RedisStreamBroker(settings.broker_redis_url).with_result_backend(
        RedisAsyncResultBackend(settings.broker_redis_url, result_ex_time=settings.taskiq_result_ttl_seconds)
    )


broker = _build_broker()
redis_schedule_source = ListRedisScheduleSource(settings.broker_redis_url)
scheduler = TaskiqScheduler(broker=broker, sources=[redis_schedule_source])


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(_) -> None:
    if settings.testing:
        return
    setup_logging()
    await Tortoise.init(config=TORTOISE_ORM, use_tz=False)


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(_) -> None:
    if settings.testing:
        return
    await Tortoise.close_connections()
    await close_redis()
