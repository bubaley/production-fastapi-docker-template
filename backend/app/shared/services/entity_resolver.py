from typing import Any, Callable, Generic, TypedDict, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel as PydanticBaseModel
from tortoise.expressions import Q

from app.core.models import BaseModel

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)
PydanticBaseModelT = TypeVar('PydanticBaseModelT', bound=PydanticBaseModel)


class EntityResolverGetData(TypedDict):
    key: str
    value: Any


class EntityResolverKeyData(TypedDict):
    model_key: str
    schema_key: str


ResolverGetDataType = list[EntityResolverGetData] | EntityResolverGetData


class EntityResolver(Generic[BaseModelT]):
    def __init__(
        self,
        model: type[BaseModelT],
        queryset_filter: Q,
        not_found_msg: str,
        keys_data: list[EntityResolverKeyData],
        collect_only_requested_values: bool = True,
    ):
        self.model = model
        self.queryset_filter = queryset_filter
        self.not_found_msg = not_found_msg
        self.collect_only_requested_values = collect_only_requested_values

        self.keys_data = keys_data
        self._keys_values: dict[str, list[Any]] = {}
        self._keys_entities: dict[str, dict[Any, list[BaseModelT]]] = {}

    async def resolve(self, items: list[PydanticBaseModelT]):
        self._keys_values = {v['model_key']: [] for v in self.keys_data}
        self._keys_entities = {v['model_key']: {} for v in self.keys_data}

        for item in items:
            for key_data in self.keys_data:
                value = getattr(item, key_data['schema_key'])
                if value:
                    self._keys_values.setdefault(key_data['model_key'], []).append(value)
        _values_filter = Q()
        for model_key, values in self._keys_values.items():
            if values:
                _values_filter |= Q(**{f'{model_key}__in': set(values)})  # type: ignore
        if _values_filter == Q():
            return self
        entities = await self.model.filter(_values_filter).filter(self.queryset_filter)

        for entity in entities:
            for key_data in self.keys_data:
                value = getattr(entity, key_data['model_key'])
                skip_collect = (
                    self.collect_only_requested_values and value not in self._keys_values[key_data['model_key']]
                )
                if not skip_collect:
                    model_key_data = self._keys_entities.setdefault(key_data['model_key'], {})
                    model_key_data.setdefault(value, []).append(entity)
        return self

    def __get_entity(self, data: EntityResolverGetData, extra_filter: Callable[[BaseModelT], bool] | None = None):
        values = self._keys_entities.get(data['key'], {}).get(data['value'], [])
        if extra_filter:
            values = [v for v in values if extra_filter(v)]
        return values[0] if values else None

    def get(self, data: ResolverGetDataType, extra_filter: Callable[[BaseModelT], bool] | None = None):
        _data = data if isinstance(data, list) else [data]
        return next((self.__get_entity(v, extra_filter) for v in _data), None)

    def validate_and_get(self, data: ResolverGetDataType, extra_filter: Callable[[BaseModelT], bool] | None = None):
        _data = data if isinstance(data, list) else [data]
        entity = self.get(data, extra_filter)
        if not entity and any(v.get('value') for v in _data):
            raise HTTPException(400, self.not_found_msg)
        return entity

    def get_flat_entities(self) -> list[BaseModelT]:
        values: dict[Any, BaseModelT] = {}
        for el in self._keys_entities.values():
            for entities in el.values():
                values.update({entity.pk: entity for entity in entities})
        return list(values.values())

    def get_values_by_key(self, key: str):
        if key not in self._keys_values:
            raise ValueError(f'Key {key} not found in values')
        return set(self._keys_values[key])

    def get_entities_by_key(self, key: str) -> dict[Any, list[BaseModelT]]:
        if key not in self._keys_entities:
            raise ValueError(f'Key {key} not found in entities')
        return self._keys_entities[key]

    def is_all_entities_found_by_key(self, key: str) -> bool:
        entities_by_key = self.get_entities_by_key(key)
        values_by_key = self.get_values_by_key(key)
        return all(v in entities_by_key for v in values_by_key)

    def is_all_entities_found(self) -> bool:
        return all(self.is_all_entities_found_by_key(key) for key in self._keys_values)
