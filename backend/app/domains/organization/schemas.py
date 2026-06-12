from uuid import UUID

from fastapi_ronin.decorators import schema

from app.core.models import BaseCreateSchema, BaseReadSchema
from app.domains.organization.models import Organization, OrganizationUser
from app.domains.user.schemas import UserReadSchema


@schema(model=Organization)
class OrganizationCreateSchema(BaseCreateSchema):
    name: str
    key: str


@schema(model=Organization)
class OrganizationUpdateSchema(BaseCreateSchema):
    name: str


@schema(model=Organization)
class OrganizationReadSchema(BaseReadSchema, OrganizationCreateSchema):
    pass


@schema(model=OrganizationUser)
class OrganizationUserCreateSchema(BaseCreateSchema):
    user_id: UUID


@schema(model=OrganizationUser)
class OrganizationUserReadSchema(BaseReadSchema, OrganizationUserCreateSchema):
    user: UserReadSchema
