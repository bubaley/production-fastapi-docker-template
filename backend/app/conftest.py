import pytest
from tortoise.contrib.test import tortoise_test_context

from app.core.database import MODELS


@pytest.fixture
async def db():
    async with tortoise_test_context(MODELS, use_tz=False) as ctx:
        yield ctx
