from typing import Any, TypeVar

from fastapi import Depends, Query
from fastapi_ronin.generics import GenericViewSet
from fastapi_ronin.lookups import UUIDLookup
from fastapi_ronin.pagination import Pagination
from fastapi_ronin.permissions import IsAuthenticated
from fastapi_ronin.state import BaseStateManager
from fastapi_ronin.types import T
from fastapi_ronin.viewsets import ModelViewSet, ReadOnlyViewSet
from fastapi_ronin.wrappers import PaginatedResponseDataWrapper, PaginationType
from pypika_tortoise import Order
from tortoise.queryset import QuerySet

from app.core.auth import AuthState, organization_key_header
from app.core.models import BaseModel
from app.core.scope import Scope
from app.core.utils.process_state_to_model import process_state_to_model
from app.shared.services.filter_objects_manager import FilterObjectsManager

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)


def with_stable_ordering[BaseModelT: BaseModel](queryset: QuerySet[BaseModelT]) -> QuerySet[BaseModelT]:
    """
    Append `id` to the ordering (explicit `order_by` or the model's Meta.ordering) unless it is already there.
    Orderings such as `created_at` are not unique; without a tiebreaker rows can repeat or vanish between pages.
    """
    orderings = list(queryset._orderings) or list(queryset.model._meta.ordering)
    if any(field in ('id', 'pk') for field, _ in orderings):
        return queryset
    fields = [f'-{field}' if order == Order.desc else field for field, order in orderings]
    return queryset.order_by(*fields, 'id')


class LightPageNumberPagination(Pagination[BaseModelT]):
    """Page number based pagination."""

    page: int = 1
    page_size: int = 100
    has_next: bool = False

    @classmethod
    def build(
        cls,
        page: int = Query(1, ge=1, description='Page number'),
        page_size: int = Query(100, ge=1, le=500, description='Number of records per page'),
    ) -> LightPageNumberPagination:
        return cls(page=page, page_size=page_size)

    def _get_offset(self):
        return (self.page - 1) * self.page_size

    def paginate(self, queryset: QuerySet[BaseModelT]) -> QuerySet[BaseModelT]:
        return with_stable_ordering(queryset).offset(self._get_offset()).limit(self.page_size)

    async def fill_meta(self, queryset: QuerySet[BaseModelT], data: list[Any]) -> None:
        offset = self._get_offset()
        next_page_offset = offset + self.page_size
        self.has_next = bool(await queryset.offset(next_page_offset).limit(1).only('id').first())


class PageResponse(PaginatedResponseDataWrapper[T, PaginationType]):
    """`{data: [...], meta: {page, page_size, has_next}}`, named `<ReadSchema>Page` in OpenAPI."""

    @classmethod
    def model_parametrized_name(cls, params: tuple[Any, ...]) -> str:
        return f'{getattr(params[0], "__name__", params[0])}Page'


class BaseGenericViewSet(GenericViewSet[BaseModelT]):
    pagination = LightPageNumberPagination
    list_wrapper = PageResponse
    lookup_class = UUIDLookup
    permission_classes = [IsAuthenticated]  # noqa: RUF012 - ronin declares this attribute as a list
    # Declare the `Organization-Key` header on every route of the viewset. None: when the model is
    # organization-scoped or gets its `organization` from the header on create (`process_state_to_model`).
    organization_header: bool | None = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Routes are added during ronin's __init__, and a router copies its dependencies into each new route.
        if self.uses_organization_header() and not any(
            dependency.dependency is organization_key_header for dependency in self.router.dependencies
        ):
            self.router.dependencies.append(Depends(organization_key_header))
        super().__init__(*args, **kwargs)

    @classmethod
    def uses_organization_header(cls) -> bool:
        if cls.organization_header is not None:
            return cls.organization_header
        model = getattr(cls, 'model', None)
        if model is None:
            return False
        scope = getattr(model, 'tenant_scope', None)
        return (isinstance(scope, Scope) and scope.organization is not None) or 'organization' in model._meta.fields_map

    async def get_queryset(self) -> QuerySet[BaseModelT]:
        result: AuthState = BaseStateManager.get_state().get('auth_state') or AuthState(user=self.user)
        queryset = self.model.all()
        return FilterObjectsManager.filter(queryset=queryset, auth_state=result)

    async def before_save(self, obj: BaseModelT) -> None:
        # Ownership is assigned on create only, so an update cannot move a row to another organization.
        if not obj._saved_in_db:
            process_state_to_model(obj)

    async def bind_to_existing_object(self, obj: BaseModelT, params: dict[str, Any]) -> BaseModelT:
        if instance := await self.model.filter(**params).only('id', 'created_at', 'updated_at').first():
            obj.id = instance.id
            obj.created_at = instance.created_at
            obj.updated_at = instance.updated_at
            obj._saved_in_db = True
        return obj


class BaseReadOnlyViewSet(BaseGenericViewSet[BaseModelT], ReadOnlyViewSet[BaseModelT]):
    pass


class BaseModelViewSet(BaseGenericViewSet[BaseModelT], ModelViewSet[BaseModelT]):
    pass
