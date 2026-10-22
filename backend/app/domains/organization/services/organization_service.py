from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from app.core.exceptions import AppException
from app.core.schemas import ErrorCode
from app.domains.organization.models import Organization, OrganizationUser
from app.domains.user.models import User


class OrganizationService:
    @staticmethod
    async def create(organization: Organization, actor: User) -> Organization:
        async with in_transaction():
            await organization.save()
            await OrganizationUser.create(organization=organization, user=actor)
        return organization

    @staticmethod
    async def validate_membership_change(membership: OrganizationUser, actor: User) -> None:
        if actor.is_superuser:
            return
        allowed = await OrganizationUser.filter(organization_id=membership.organization_id, user_id=actor.id).exists()
        if not allowed:
            raise AppException.from_attrs(ErrorCode.FORBIDDEN, 'Cannot modify this organization')

    @staticmethod
    async def add_member(membership: OrganizationUser, actor: User) -> OrganizationUser:
        await OrganizationService.validate_membership_change(membership, actor)
        try:
            await membership.save()
        except IntegrityError:
            if await OrganizationUser.filter(
                organization_id=membership.organization_id, user_id=membership.user_id
            ).exists():
                raise AppException.from_attrs(ErrorCode.VALIDATION_ERROR, 'User is already in this organization')
            raise
        return membership

    @staticmethod
    async def remove_member(membership: OrganizationUser, actor: User) -> None:
        await OrganizationService.validate_membership_change(membership, actor)
        await membership.delete()
