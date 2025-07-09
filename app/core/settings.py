# https://github.com/bubaley/production-fastapi-docker-template
# version: 0.0.0 | Increase the version after changes from the template, this will make

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'Production FastAPI Docker Example'

    debug: bool = Field(True)
    database_url: str = Field('sqlite://db.sqlite3')
    secret_key: str = Field('secret-key-change-me')


settings = Settings()
