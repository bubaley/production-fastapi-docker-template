from fastapi import Request
from fastapi_ronin.generics import GenericViewSet
from fastapi_ronin.permissions import BasePermission

from app.domains.user.models import User


class IsSuperUser(BasePermission):
    async def has_permission(self, request: Request, view: GenericViewSet):
        user: User | None = view.user
        if user and user.is_superuser:
            return True
        return False
