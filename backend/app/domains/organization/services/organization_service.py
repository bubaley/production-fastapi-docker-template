from fastapi import HTTPException, Request

from app.domains.organization.models import Organization
from app.domains.user.models import User


class OrganizationService:
    @staticmethod
    def get_organization_key_from_request(request: Request) -> str | None:
        organization_key = request.query_params.get('organization_key')
        organization_key = organization_key or request.headers.get('X-Organization-Key')
        return organization_key

    @staticmethod
    async def get_organization_by_id(organization_id: int, user: User) -> Organization:
        return await OrganizationService._find_organization(organization_filter={'id': organization_id}, user=user)

    @staticmethod
    async def get_organization_by_key(organization_key: str, user: User) -> Organization:
        return await OrganizationService._find_organization(
            organization_filter={'organization_key': organization_key}, user=user
        )

    @staticmethod
    async def get_organization_from_request(
        request: Request,
        user: User,
    ) -> Organization:
        organization_key = OrganizationService.get_organization_key_from_request(request)
        if not organization_key:
            raise HTTPException(
                status_code=400,
                detail='organization_key is required in query params or X-Organization-Key header',
            )

        return await OrganizationService.get_organization_by_key(
            organization_key=organization_key,
            user=user,
        )

    @staticmethod
    async def _find_organization(organization_filter: dict, user: User) -> Organization:
        _filter = organization_filter
        if not user.is_superuser:
            _filter['users'] = user
        organization = await Organization.filter(**_filter).first()
        if not organization:
            raise HTTPException(status_code=404, detail='Organization not found or access denied')
        return organization
