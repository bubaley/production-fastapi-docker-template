from datetime import datetime
from uuid import UUID

from fastapi_ronin.decorators import schema
from pydantic import Field

from app.core.models import BaseCreateSchema, BaseReadSchema
from app.domains.user.models import User, UserToken


@schema(model=User)
class UserCreateSchema(BaseCreateSchema):
    email: str
    first_name: str
    last_name: str
    password: str = Field(min_length=1, max_length=128)
    is_superuser: bool = False


@schema(model=User)
class UserReadSchema(BaseReadSchema):
    email: str
    first_name: str
    last_name: str
    is_superuser: bool


@schema(model=User)
class UserUpdateSchema(BaseCreateSchema):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = Field(default=None, max_length=128)
    is_superuser: bool | None = None


# USER_TOKEN_SCHEMAS


@schema(model=UserToken)
class UserTokenCreateSchema(BaseCreateSchema):
    user_id: UUID | None = None
    name: str


@schema(model=UserToken)
class UserTokenUpdateSchema(BaseCreateSchema):
    name: str


@schema(model=UserToken)
class UserTokenReadSchema(BaseReadSchema):
    user_id: UUID
    value_preview: str
    last_used_at: datetime | None
    name: str


@schema(model=UserToken)
class UserTokenCreatedReadSchema(UserTokenReadSchema):
    value: str
