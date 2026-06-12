import asyncio
from functools import wraps
from typing import Any, Callable


def async_task(func: Callable[..., Any]):
    """
    Decorator that wraps an async method to execute it as a background task.
    When the decorated method is called, it will be executed via asyncio.create_task.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        asyncio.create_task(func(*args, **kwargs))
        return None

    return wrapper
