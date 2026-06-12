from taskiq import TaskiqScheduler
from taskiq.events import TaskiqEvents
from taskiq_redis import ListQueueBroker, ListRedisScheduleSource, RedisAsyncResultBackend
from tortoise import Tortoise

from app.core.database import TORTOISE_ORM
from app.core.settings import settings

broker = ListQueueBroker(settings.broker_redis_url).with_result_backend(
    RedisAsyncResultBackend(settings.broker_redis_url)
)
redis_schedule_source = ListRedisScheduleSource(settings.broker_redis_url)
scheduler = TaskiqScheduler(broker=broker, sources=[redis_schedule_source])


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(_) -> None:
    await Tortoise.init(config=TORTOISE_ORM)


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(_) -> None:
    await Tortoise.close_connections()
