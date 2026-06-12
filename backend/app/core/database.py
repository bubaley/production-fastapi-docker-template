import asyncio

from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.context import TortoiseContext
from tortoise.contrib.fastapi import register_tortoise

from app.core.settings import settings

MODELS = [
    'app.domains.organization.models',
    'app.domains.user.models',
]


TORTOISE_ORM = {
    'connections': {'default': settings.database_url},
    'apps': {
        'models': {
            'models': MODELS,
            'default_connection': 'default',
            'migrations': 'migrations.models',
        }
    },
}


def register_database(app: FastAPI):
    register_tortoise(
        app,
        db_url=settings.database_url,
        modules={'models': MODELS},
        generate_schemas=False,
        add_exception_handlers=True,
    )


Tortoise.init_models(MODELS, 'models')


class DatabaseConnection:
    _instance = None
    _tortoise_instance: TortoiseContext | None = None
    _initialized = False
    TORTOISE_KWARGS = {'config': TORTOISE_ORM, 'use_tz': False}

    @property
    def tortoise_instance(self):
        if not self._initialized:
            raise Exception(
                'Tortoise ORM is not initialized. Use "async with DatabaseConnection():" or call "await DatabaseConnection().tortoise_init()" first.'
            )
        return self._tortoise_instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def tortoise_init(self):
        if not self._initialized:
            self._tortoise_instance = await Tortoise.init(**self.TORTOISE_KWARGS)
            self._initialized = True

    def __enter__(self):
        asyncio.run(self.tortoise_init())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.run(Tortoise.close_connections())
        self._initialized = False

    async def __aenter__(self):
        await self.tortoise_init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await Tortoise.close_connections()
        self._initialized = False
