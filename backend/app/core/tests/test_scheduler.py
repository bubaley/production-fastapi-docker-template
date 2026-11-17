import pytest
from taskiq.schedule_sources import LabelScheduleSource

from app.core.broker import broker, scheduler


@pytest.mark.asyncio
async def test_scheduler_picks_up_cron_labels_declared_on_tasks():
    """`@broker.task(schedule=[{'cron': ...}])` is enough: the scheduler reads schedules from task labels."""

    @broker.task(task_name='tests.scheduled_probe', schedule=[{'cron': '*/5 * * * *', 'schedule_id': 'probe'}])
    async def scheduled_probe() -> None:
        pass

    source = next(source for source in scheduler.sources if isinstance(source, LabelScheduleSource))
    try:
        await source.startup()
        schedules = {schedule.schedule_id: schedule for schedule in await source.get_schedules()}
    finally:
        broker.local_task_registry.pop('tests.scheduled_probe', None)
        await source.startup()
    assert schedules['probe'].task_name == 'tests.scheduled_probe'
    assert schedules['probe'].cron == '*/5 * * * *'
