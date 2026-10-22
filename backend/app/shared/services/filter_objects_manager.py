from typing import Any

from tortoise.models import Model
from tortoise.queryset import QuerySet

from app.core.auth import AuthState
from app.core.exceptions import AppException
from app.core.schemas import ErrorCode
from app.core.scope import Scope, ScopeFilter, TenantScope, Unscoped


class ScopeConfigurationError(RuntimeError):
    pass


class FilterObjectsManager:
    """Applies the model's `tenant_scope` to a queryset. Fails closed: a model without a scope cannot be queried."""

    @classmethod
    def get_scope(cls, model: type[Model]) -> TenantScope:
        scope = getattr(model, 'tenant_scope', None)
        if not isinstance(scope, Scope | Unscoped):
            raise ScopeConfigurationError(
                f'{model.__name__} has no tenant_scope. Declare `tenant_scope = Scope(user=...)` on the model, '
                'or `tenant_scope = Unscoped(reason=...)` if its rows are intentionally global.'
            )
        return scope

    @classmethod
    def filter(cls, queryset: QuerySet, auth_state: AuthState) -> QuerySet:
        scope = cls.get_scope(queryset.model)
        if isinstance(scope, Unscoped):
            return queryset
        if auth_state.user_id is None:
            raise AppException.from_attrs(ErrorCode.UNAUTHORIZED, 'Authentication required')
        queryset = cls._apply(queryset, scope.user, auth_state.user_id)
        if scope.organization is None:
            return queryset
        if auth_state.organization_id is not None:
            return cls._apply(queryset, scope.organization, auth_state.organization_id)
        if scope.require_organization:
            raise AppException.from_attrs(ErrorCode.VALIDATION_ERROR, 'Organization-Key header is required')
        return queryset

    @classmethod
    def _apply(cls, queryset: QuerySet, scope_filter: ScopeFilter, value: Any) -> QuerySet:
        if isinstance(scope_filter, str):
            return queryset.filter(**{scope_filter: value})
        return queryset.filter(scope_filter(value))
