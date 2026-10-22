import asyncio

import pytest
from loguru import logger

from app.shared.utils import async_task as async_task_module
from app.shared.utils.async_task import async_task


@pytest.mark.asyncio
async def test_background_task_is_referenced_until_done_and_failure_is_logged():
    release = asyncio.Event()
    messages: list[str] = []
    sink_id = logger.add(lambda message: messages.append(str(message)), level='ERROR')

    @async_task
    async def job():
        await release.wait()
        raise RuntimeError('boom')

    try:
        await job()
        assert len(async_task_module._background_tasks) == 1
        task = next(iter(async_task_module._background_tasks))
        release.set()
        with pytest.raises(RuntimeError):
            await task
        await asyncio.sleep(0)
    finally:
        logger.remove(sink_id)

    assert not async_task_module._background_tasks
    assert any('Background task' in message and 'boom' in message for message in messages)
