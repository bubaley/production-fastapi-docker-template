from datetime import datetime

from pydantic import BaseModel, Field

from app.core.fields.email_field import LoginEmail, NormalizedEmail
from app.core.fields.password_field import NewPassword
from app.domains.auth.services.token_service import TokenPair
from app.domains.organization.models import Organization
from app.domains.organization.schemas import OrganizationCreateSchema, OrganizationReadSchema
from app.domains.user.models import User
from app.domains.user.schemas import UserReadSchema


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: LoginEmail
    password: str = Field(max_length=128)


class SessionExpirySchema(BaseModel):
    """When the session cookies expire. The tokens themselves never leave the HttpOnly cookies."""

    access_expires_at: datetime
    refresh_expires_at: datetime

    @classmethod
    def from_pair(cls, pair: TokenPair) -> SessionExpirySchema:
        return cls(access_expires_at=pair.access.expires_at, refresh_expires_at=pair.refresh.expires_at)


class MeSchema(BaseModel):
    """What a client needs to bootstrap: the user (with `is_superuser`) and the organizations they belong to."""

    user: UserReadSchema
    organizations: list[OrganizationReadSchema]

    @classmethod
    async def for_user(cls, user: User) -> MeSchema:
        organizations = Organization.filter(org_users__user_id=user.id).order_by('created_at', 'id')
        return cls(
            user=await UserReadSchema.from_tortoise_orm(user),
            organizations=await OrganizationReadSchema.from_queryset(organizations),
        )


class SessionSchema(MeSchema, SessionExpirySchema):
    """Login response: the bootstrap data plus cookie expiry."""

    @classmethod
    async def build(cls, user: User, pair: TokenPair) -> SessionSchema:
        me = await MeSchema.for_user(user)
        return cls(user=me.user, organizations=me.organizations, **SessionExpirySchema.from_pair(pair).model_dump())


class SetupStatusSchema(BaseModel):
    """First-run state: `needs_setup` while the database has no users; then setup is closed for good."""

    needs_setup: bool
    # `POST /setup` needs `setup_token` (the server's SETUP_TOKEN); only meaningful while `needs_setup`.
    token_required: bool


class SetupRequest(BaseModel):
    """The first user (created as a superuser) and, optionally, the first organization they become a member of."""

    email: NormalizedEmail
    first_name: str = Field(min_length=1, max_length=128)
    last_name: str = Field(min_length=1, max_length=128)
    password: NewPassword
    organization: OrganizationCreateSchema | None = None
    setup_token: str | None = Field(None, max_length=256)
