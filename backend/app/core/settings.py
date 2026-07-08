# https://github.com/bubaley/production-fastapi-docker-template
# version: 0.0.0 | Increase the version after changes from the template, this will make

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / '.env'


class Settings(BaseSettings):
    debug: bool = True

    # database settings
    sql_engine: str = 'asyncpg'
    sql_database: str = 'postgres'
    sql_user: str = 'postgres'
    sql_password: str = 'postgres'
    sql_host: str = 'localhost'
    sql_port: int = 5432

    # encryption settings
    secret_key: str = Field(None, validate_default=True, min_length=64)
    encryption_key: str = Field(None, validate_default=True, min_length=32, max_length=32)

    # cache settings
    cache_redis_url: str | None = None

    # broker settings
    broker_redis_url: str = 'redis://localhost:6379/0'

    # JWT settings
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire_minutes: int = 60 * 24 * 1  # 24 hour
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 30  # 7 days

    # cookie settings
    cookie_secure: bool = False
    cookie_samesite: Literal['lax', 'strict', 'none'] = 'lax'
    cookie_httponly: bool = True

    # CORS settings
    cors_origins: list[str] = [
        'http://[::1]:3000',
        'http://localhost:3000',  # React default
        'http://localhost:5173',  # Vite default
        'http://localhost:8080',  # Vue CLI default
        'http://localhost:9001',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:8080',
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ['*']
    cors_allow_headers: list[str] = ['*']

    # AWS S3 settings
    aws_access_key_id: str = ''
    aws_secret_access_key: str = ''
    aws_s3_region_name: str = 'us-east-1'
    aws_s3_endpoint_url: str | None = None
    aws_storage_bucket_name: str = ''

    @property
    def database_url(self) -> str:
        return f'{self.sql_engine}://{self.sql_user}:{self.sql_password}@{self.sql_host}:{self.sql_port}/{self.sql_database}'

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding='utf-8',
        extra='allow',
    )


settings = Settings()
