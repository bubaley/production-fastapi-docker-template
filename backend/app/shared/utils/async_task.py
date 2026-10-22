import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from loguru import logger

# The event loop keeps only weak references to tasks; hold them until they finish.
_background_tasks: set[asyncio.Task[Any]] = set()


def _on_task_done(task: asyncio.Task[Any]) -> None:
    _background_tasks.discard(task)
    if task.cancelled():
        return
    if exc := task.exception():
        logger.opt(exception=exc).error('Background task {} failed', task.get_name())


def async_task[**P](func: Callable[P, Coroutine[Any, Any, Any]]) -> Callable[P, Coroutine[Any, Any, None]]:
    """
    Decorator that runs an async function as a fire-and-forget background task.
    The caller does not wait for the result; failures are logged.
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        task = asyncio.create_task(func(*args, **kwargs), name=getattr(func, '__qualname__', None))
        _background_tasks.add(task)
        task.add_done_callback(_on_task_done)

    return wrapper
