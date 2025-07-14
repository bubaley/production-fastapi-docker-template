# https://github.com/bubaley/production-fastapi-docker-template
# version: 0.0.0 | Increase the version after changes from the template, this will make

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'Production FastAPI Docker Example'

    debug: bool = Field(default=True)
    database_url: str = Field(default='sqlite://db.sqlite3')
    secret_key: str = Field(default='secret-key-change-me')


settings = Settings()
