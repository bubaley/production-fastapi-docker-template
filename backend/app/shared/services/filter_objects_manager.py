from dataclasses import dataclass
from typing import Any, Callable

from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from app.core.auth import AuthState
from app.core.models import BaseModel
from app.domains.organization.models import Organization, OrganizationUser
from app.domains.user.models import User

ScopeFilterType = str | None | Callable[[Any], Q]


@dataclass
class Scope:
    user: ScopeFilterType = None
    organization: ScopeFilterType = None


class FilterObjectsManager:
    models_data: dict[type[BaseModel], Scope] = {
        Organization: Scope(
            user='org_users__user_id',
        ),
        OrganizationUser: Scope(),
        User: Scope(),
    }

    @classmethod
    def filter(cls, queryset: QuerySet, auth_state: AuthState) -> QuerySet:
        model_data = cls.models_data.get(queryset.model)
        if not model_data:
            return queryset
        queryset = cls._process_filter(queryset, model_data.user, auth_state.user_id)
        if auth_state.organization_id:
            queryset = cls._process_filter(queryset, model_data.organization, auth_state.organization_id)
        return queryset

    @classmethod
    def _process_filter(cls, queryset: QuerySet, scope_filter: ScopeFilterType, value: Any) -> QuerySet:
        if callable(scope_filter):
            queryset = queryset.filter(scope_filter(value))
        if isinstance(scope_filter, str):
            queryset = queryset.filter(**{scope_filter: value})
        return queryset
