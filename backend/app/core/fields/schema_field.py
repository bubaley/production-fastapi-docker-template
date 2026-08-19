from typing import Any, TypeVar

from pydantic import BaseModel, TypeAdapter
from tortoise import Model, fields
from tortoise.fields.data import JSON_DUMPS, JSON_LOADS

TModel = TypeVar('TModel', bound=BaseModel)


class SchemaField(fields.JSONField[TModel]):
    def __init__(self, schema: type[TModel] | None = None, **kwargs: Any):
        self._schema = schema
        kwargs['decoder'] = self.decode
        kwargs['encoder'] = self.encode
        super().__init__(**kwargs)

    def to_db_value(self, value: Any, instance: 'Model | type[Model]') -> str | None:
        self.validate(value)
        if value is None:
            return None
        model_instance = self.decode(value)
        return self.encode(model_instance)

    def decode(self, value: Any) -> TModel | None:
        assert self._schema is not None, 'Schema must be provided'
        if value is None:
            return None
        if isinstance(value, self._schema):
            return value
        if isinstance(value, (bytes, str)):
            if isinstance(value, bytes):
                value = value.decode()
            try:
                value = JSON_LOADS(value)
            except Exception as e:
                raise ValueError(f'Malformed JSON in {self.__class__.__name__}: {e}')
        if isinstance(value, dict):
            return self._schema.model_validate(value)
        if value is None:
            return None
        raise ValueError(
            f'Invalid type for {self._schema.__name__}: expected dict or {self._schema.__name__}, got {type(value)}'
        )

    def encode(self, value: TModel | None) -> str | None:
        if value is None:
            return None
        return JSON_DUMPS(value.model_dump(mode='json'))


class SchemaListField(fields.JSONField[list[TModel]]):
    def __init__(self, schema: type[TModel] | None = None, **kwargs: Any):
        self._schema = schema
        self._list_schema_adapter: TypeAdapter[list[TModel]] | None = None
        kwargs['decoder'] = self.decode
        kwargs['encoder'] = self.encode
        super().__init__(**kwargs)

    def _get_list_adapter(self) -> TypeAdapter[list[TModel]]:
        if self._list_schema_adapter is None:
            assert self._schema is not None, 'Schema must be provided before first use'
            self._list_schema_adapter = TypeAdapter(list[self._schema])
        return self._list_schema_adapter

    def to_db_value(self, value: Any, instance: 'Model | type[Model]') -> str | None:
        self.validate(value)
        assert self._schema is not None, 'Schema must be provided'
        if value is None:
            return None
        model_list = self.decode(value)
        return self.encode(model_list)

    def decode(self, value: Any) -> list[TModel] | None:
        assert self._schema is not None, 'Schema must be provided'
        if value is None:
            return None

        if isinstance(value, (bytes, str)):
            if isinstance(value, bytes):
                value = value.decode()
            try:
                value = JSON_LOADS(value)
            except Exception as e:
                raise ValueError(f'Malformed JSON in {self.__class__.__name__}: {e}')
        if isinstance(value, list):
            if value and isinstance(value[0], self._schema):
                return value
            return self._get_list_adapter().validate_python(value)
        if value is None:
            return None
        raise ValueError(f'Expected list for {self._schema.__name__} collection, got {type(value)}')

    def encode(self, value: list[TModel] | None) -> str | None:
        if value is None:
            return None
        data = self._get_list_adapter().dump_python(value, mode='json', exclude_unset=True)
        return JSON_DUMPS(data)
