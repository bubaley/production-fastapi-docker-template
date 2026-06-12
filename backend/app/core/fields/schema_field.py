from typing import TypeVar

from pydantic import BaseModel
from tortoise import fields
from tortoise.exceptions import FieldError
from tortoise.fields.data import JSON_DUMPS, JSON_LOADS

SchemaType = TypeVar('SchemaType', bound=BaseModel)


ResultType = TypeVar('ResultType')


class SchemaField(fields.JSONField[ResultType]):
    def to_db_value(
        self,
        value,
        instance,
    ) -> str | None:
        self.validate(value)
        if value is None:
            return None
        if isinstance(value, (str, bytes)):
            try:
                self.decoder(value)
            except Exception:
                raise FieldError(f'Value {value!r} is invalid json value.')
            if isinstance(value, bytes):
                return value.decode()
            return value

        return self.encoder(value)

    def __init__(self, schema: type[SchemaType], *args, **kwargs):
        def decoder(x):
            if x is None:
                return None
            instance = JSON_LOADS(x)
            if isinstance(instance, list):
                return [schema.model_validate(v) for v in instance]
            return schema.model_validate(instance)

        def encoder(x):
            if x is None:
                return None
            if isinstance(x, list):
                data = [v.model_dump(mode='json') for v in x]
            else:
                data = x.model_dump(mode='json')
            return JSON_DUMPS(data)

        kwargs['decoder'] = decoder
        kwargs['encoder'] = encoder
        super().__init__(*args, **kwargs)
