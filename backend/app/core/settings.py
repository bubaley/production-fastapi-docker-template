from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / '.env'


class Settings(BaseSettings):
    debug: bool = True
    # Set by the test suite before the app is imported: in-memory broker, pub/sub and rate limiter, cheap bcrypt.
    testing: bool = False

    # release info, shown by /health
    app_version: str = '0.0.0-dev'
    git_sha: str | None = None

    # logging
    log_format: Literal['json', 'text'] = 'text'
    log_level: str = 'INFO'

    # OpenTelemetry: requires the `otel` extra; exporters are configured by the standard OTEL_* variables
    otel_enabled: bool = False

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
    # Optional secret mixed into password hashes; empty means no pepper. Choose it before users sign up
    # and never change it (empty -> value counts as a change): hashes made with another pepper stop verifying.
    # Hashes from before this setting existed depend on SECRET_KEY until the user logs in again and they are
    # re-hashed, so rotating SECRET_KEY locks out only users who have not logged in since the upgrade.
    password_pepper: str = ''
    password_min_length: int = 8
    bcrypt_rounds: int = 12

    # Redis for rate limits and websocket fan-out. Falls back to BROKER_REDIS_URL. CACHE_REDIS_URL is the old name.
    redis_url: str | None = Field(None, validation_alias=AliasChoices('redis_url', 'cache_redis_url'))

    # broker settings
    broker_redis_url: str = 'redis://localhost:6379/0'
    taskiq_result_ttl_seconds: int = 60 * 60

    # JWT settings
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire_minutes: int = 60 * 24  # 24 hours
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 30  # 30 days
    # Tokens issued before claim versioning (`id` instead of `sub`, no `jti`/`ver`). Disable once they have expired.
    jwt_accept_legacy_tokens: bool = True
    # A refresh token reused within this window right after its rotation (parallel tabs) is rejected
    # without revoking the session.
    refresh_reuse_leeway_seconds: int = 10

    # API tokens (`Authorization: Token ...`): minimum interval between `last_used_at` writes
    api_token_touch_interval_seconds: int = 60

    # login rate limit per client IP + email
    login_rate_limit_attempts: int = 10
    login_rate_limit_window_seconds: int = 15 * 60

    # cookie settings
    cookie_secure: bool = False
    cookie_samesite: Literal['lax', 'strict', 'none'] = 'lax'
    cookie_httponly: bool = True
    refresh_cookie_path: str = '/api/v1/auth'

    # websockets
    websocket_send_timeout_seconds: float = 5.0
    websocket_max_message_bytes: int = 64 * 1024
    websocket_auth_check_interval_seconds: int = 60

    # CORS settings: the Nuxt dev server (FRONTEND_PORT); production is same-origin behind Caddy
    cors_origins: list[str] = [
        'http://localhost:9001',
        'http://127.0.0.1:9001',
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
    # Base URL for public object links (CDN or bucket website); defaults to the endpoint/bucket URL
    aws_s3_public_url: str | None = None
    aws_s3_presign_expire_seconds: int = 60 * 60

    @property
    def database_url(self) -> str:
        return f'{self.sql_engine}://{self.sql_user}:{self.sql_password}@{self.sql_host}:{self.sql_port}/{self.sql_database}'

    @property
    def app_redis_url(self) -> str:
        return self.redis_url or self.broker_redis_url

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding='utf-8',
        extra='allow',
    )


settings = Settings()
