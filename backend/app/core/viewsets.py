from typing import Any, TypeVar

from fastapi import Query
from fastapi_ronin.generics import GenericViewSet
from fastapi_ronin.lookups import UUIDLookup
from fastapi_ronin.pagination import Pagination
from fastapi_ronin.permissions import IsAuthenticated
from fastapi_ronin.state import BaseStateManager
from fastapi_ronin.viewsets import ModelViewSet, ReadOnlyViewSet
from fastapi_ronin.wrappers import PaginatedResponseDataWrapper
from tortoise.queryset import QuerySet

from app.core.auth import AuthState
from app.core.models import BaseModel
from app.core.utils.process_state_to_model import process_state_to_model
from app.shared.services.filter_objects_manager import FilterObjectsManager

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)


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
    ) -> 'LightPageNumberPagination':
        return cls(page=page, page_size=page_size)

    def _get_offset(self):
        return (self.page - 1) * self.page_size

    def paginate(self, queryset: QuerySet[BaseModelT]) -> QuerySet[BaseModelT]:
        return queryset.offset(self._get_offset()).limit(self.page_size)

    async def fill_meta(self, queryset: QuerySet[BaseModelT], data: list[Any]) -> None:
        offset = self._get_offset()
        next_page_offset = offset + self.page_size
        self.has_next = bool(await queryset.offset(next_page_offset).limit(1).only('id').first())


class BaseGenericViewSet(GenericViewSet[BaseModelT]):
    pagination = LightPageNumberPagination
    list_wrapper = PaginatedResponseDataWrapper
    lookup_class = UUIDLookup
    permission_classes = [IsAuthenticated]

    async def get_queryset(self) -> QuerySet[BaseModelT]:
        result: AuthState = BaseStateManager.get_state().get('auth_state') or AuthState(user=self.user)
        queryset = self.model.all()
        return FilterObjectsManager.filter(queryset=queryset, auth_state=result)

    async def before_save(self, obj: BaseModelT) -> None:
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
