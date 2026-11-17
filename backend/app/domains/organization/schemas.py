from unicodedata import category
from uuid import UUID

from fastapi_ronin.decorators import schema
from pydantic import ConfigDict, field_validator

from app.core.models import BaseCreateSchema, BaseReadSchema
from app.domains.organization.models import ORGANIZATION_KEY_MAX_LENGTH, Organization, OrganizationUser
from app.domains.user.schemas import UserReadSchema


class OrganizationFields(BaseCreateSchema):
    """Fields shared by the create and read schemas."""

    name: str
    key: str


@schema(model=Organization)
class OrganizationCreateSchema(OrganizationFields):
    @field_validator('key')
    @classmethod
    def validate_key(cls, key: str) -> str:
        """The key travels in the `Organization-Key` header: no edge whitespace (trimmed in transit), no control chars."""
        if (
            not 1 <= len(key) <= ORGANIZATION_KEY_MAX_LENGTH
            or key != key.strip()
            or any(category(c) in ('Cc', 'Cs') for c in key)
        ):
            raise ValueError(
                f'Organization key must contain 1 to {ORGANIZATION_KEY_MAX_LENGTH} characters without edge whitespace or control characters'
            )
        return key


@schema(model=Organization)
class OrganizationUpdateSchema(BaseCreateSchema):
    name: str


# Not derived from the create schema: stored keys are read back without the create-time validation.
@schema(model=Organization)
class OrganizationReadSchema(BaseReadSchema, OrganizationFields):
    pass


@schema(model=OrganizationUser)
class OrganizationUserCreateSchema(BaseCreateSchema):
    """The organization is explicit (not `Organization-Key`): members are managed from the organization's page."""

    organization_id: UUID
    user_id: UUID


@schema(model=OrganizationUser)
class OrganizationUserUpdateSchema(BaseCreateSchema):
    """A membership has no mutable fields yet: user and organization are fixed after creation."""

    model_config = ConfigDict(extra='forbid')


@schema(model=OrganizationUser)
class OrganizationUserReadSchema(BaseReadSchema, OrganizationUserCreateSchema):
    user: UserReadSchema
