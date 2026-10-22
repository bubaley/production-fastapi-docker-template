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
    filterset_class = OrganizationUserFilterSet

    async def get_queryset(self):
        user: User = self.user
        if user.is_superuser:
            return OrganizationUser.all()

        org_ids = await OrganizationUser.filter(user_id=user.id).values_list('organization_id', flat=True)
        return OrganizationUser.filter(organization_id__in=org_ids)

    async def perform_create(self, obj: OrganizationUser) -> OrganizationUser:
        return await OrganizationService.add_member(obj, self.user)

    async def perform_destroy(self, obj: OrganizationUser) -> None:
        await OrganizationService.remove_member(obj, self.user)
