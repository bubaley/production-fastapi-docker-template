from fastapi import APIRouter, HTTPException
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
        obj = await super().perform_create(obj)
        await OrganizationUser.create(organization=obj, user=self.user)
        return obj


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
        if not self.user.is_superuser:
            allowed = await Organization.filter(id=obj.organization_id, users=self.user).exists()
            if not allowed:
                raise HTTPException(status_code=403, detail='Cannot modify this organization')
        existing = await OrganizationUser.get_or_none(organization_id=obj.organization_id, user_id=obj.user_id)
        if existing:
            raise HTTPException(status_code=400, detail='User is already in this organization')
        return await super().perform_create(obj)

    async def perform_destroy(self, obj: OrganizationUser) -> None:
        if not self.user.is_superuser:
            allowed = await Organization.filter(id=obj.organization_id, users=self.user).exists()
            if not allowed:
                raise HTTPException(status_code=403, detail='Cannot modify this organization')
        await obj.delete()
