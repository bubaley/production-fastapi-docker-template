import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
import pytest
from tortoise.context import TortoiseContext
from tortoise.contrib.test import truncate_all_models
from tortoise.migrations.api import migrate

from app.core.database import TORTOISE_ORM
from app.core.settings import settings

TEST_DATABASE_NAME = f'{settings.sql_database}_test'
TEST_DATABASE_URL = (
    f'{settings.sql_engine}://{settings.sql_user}:{settings.sql_password}'
    f'@{settings.sql_host}:{settings.sql_port}/{TEST_DATABASE_NAME}'
)


def pytest_addoption(parser: pytest.Parser):
    parser.addoption('--keepdb', action='store_true', default=False, help='Keep database between tests')


def _get_config():
    return {'connections': {'default': TEST_DATABASE_URL}, 'apps': TORTOISE_ORM['apps']}


@asynccontextmanager
async def _postgres_admin() -> AsyncGenerator[asyncpg.Connection, None]:
    conn: asyncpg.Connection = await asyncpg.connect(
        user=settings.sql_user,
        password=settings.sql_password,
        host=settings.sql_host,
        port=settings.sql_port,
        database='postgres',
    )
    try:
        yield conn
    finally:
        await conn.close()


async def _database_exists() -> bool:
    async with _postgres_admin() as conn:
        return await conn.fetchval('SELECT 1 FROM pg_database WHERE datname = $1', TEST_DATABASE_NAME) is not None


def _confirm_drop() -> bool:
    # Non-interactive runs (CI) recreate the database without prompting.
    if not sys.stdin.isatty():
        return True
    answer = input(f'Test database "{TEST_DATABASE_NAME}" already exists. Drop and recreate it? [y/N]: ')
    return answer.strip().lower() in ('y', 'yes')


async def _setup_database(*, recreate: bool) -> None:
    async with _postgres_admin() as conn:
        if recreate:
            await conn.fetch(
                'SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = $1 AND pid <> pg_backend_pid()',
                TEST_DATABASE_NAME,
            )
            await conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DATABASE_NAME}"')
        await conn.execute(f'CREATE DATABASE "{TEST_DATABASE_NAME}" OWNER "{settings.sql_user}"')


async def _ensure_test_database(keepdb: bool) -> None:
    exists = await _database_exists()
    if keepdb:
        if not exists:
            await _setup_database(recreate=False)
        return
    if exists and not _confirm_drop():
        pytest.exit(
            f'Test database "{TEST_DATABASE_NAME}" was not dropped. Re-run with --keepdb to reuse the existing database.'
        )
    await _setup_database(recreate=exists)


# FIXTURES


@pytest.fixture(scope='session', autouse=True)
async def setup_database(request: pytest.FixtureRequest):
    await _ensure_test_database(request.config.getoption('--keepdb'))
    await migrate(config=_get_config())
    yield


@pytest.fixture
async def db():
    ctx = TortoiseContext()
    async with ctx:
        await ctx.init(config=_get_config(), _create_db=False, use_tz=False)
        await truncate_all_models()
        yield ctx
