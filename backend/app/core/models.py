from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from fastapi_ronin.types import PydanticModel
from tortoise import fields
from tortoise.models import Model

from app.core.scope import TenantScope


class BaseModel(Model):
    id = fields.UUIDField(primary_key=True, default=uuid4)
    created_at = fields.DatetimeField(auto_now_add=True, db_index=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Required on every concrete model; read by FilterObjectsManager (see app/core/scope.py).
    tenant_scope: ClassVar[TenantScope]

    class Meta:
        abstract = True


BASE_FIELDS = ('id', 'created_at', 'updated_at')


class BaseSchema(PydanticModel):
    pass


class BaseReadSchema(PydanticModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class BaseCreateSchema(BaseSchema):
    pass
