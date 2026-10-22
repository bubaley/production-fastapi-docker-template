from fastapi import APIRouter
from fastapi_ronin.decorators import viewset

from app.core.viewsets import BaseModelViewSet
from app.domains.organization.filters import OrganizationFilterSet, OrganizationUserFilterSet
from app.domains.organization.models import Organization, OrganizationUser
from app.domains.organization.schemas import (
    OrganizationCreateSchema,
    OrganizationReadSchema,
    OrganizationUpdateSchema,
    OrganizationUserCreateSchema,
    OrganizationUserReadSchema,
    OrganizationUserUpdateSchema,
)
from app.domains.organization.services.organization_service import OrganizationService
from app.domains.user.models import User

organizations_router = APIRouter(prefix='/organizations', tags=['organizations'])
organization_users_router = APIRouter(prefix='/organization-users', tags=['organization-users'])


@viewset(organizations_router)
class OrganizationViewSet(BaseModelViewSet[Organization]):
    model = Organization
    read_schema = OrganizationReadSchema
    create_schema = OrganizationCreateSchema
    update_schema = OrganizationUpdateSchema
    filterset_class = OrganizationFilterSet

    async def perform_create(self, obj: Organization) -> Organization:
        return await OrganizationService.create(obj, self.user)


@viewset(organization_users_router)
class OrganizationUserViewSet(BaseModelViewSet[OrganizationUser]):
    model = OrganizationUser
    read_schema = OrganizationUserReadSchema
    create_schema = OrganizationUserCreateSchema
    update_schema = OrganizationUserUpdateSchema
    filterset_class = OrganizationUserFilterSet
    # The organization comes from the body and is checked by OrganizationService, not from `Organization-Key`.
    organization_header = False

    async def get_queryset(self):
        user: User = self.user
        if user.is_superuser:
            return OrganizationUser.all()
        return await super().get_queryset()

    async def before_save(self, obj: OrganizationUser) -> None:
        pass

    async def perform_create(self, obj: OrganizationUser) -> OrganizationUser:
        return await OrganizationService.add_member(obj, self.user)

    async def perform_update(self, obj: OrganizationUser) -> OrganizationUser:
        return await OrganizationService.update_member(obj, self.user)

    async def perform_destroy(self, obj: OrganizationUser) -> None:
        await OrganizationService.remove_member(obj, self.user)
