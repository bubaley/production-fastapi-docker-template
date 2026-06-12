from typing import TypeVar
from uuid import UUID

from fastapi import Request
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, model_validator
from pydantic_core import PydanticCustomError
from tortoise.expressions import Q

from app.core.models import BaseModel
from app.domains.organization.models import Organization
from app.domains.user.models import User
from app.shared.services.entity_resolver import EntityResolver, EntityResolverGetData

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)
OwnedDataT = TypeVar('OwnedDataT', bound='OwnedData')


class OwnedData(PydanticBaseModel):
    organization_id: UUID | None = None
    organization_key: str | None = None

    @model_validator(mode='after')
    def validate_resolutions(self) -> 'OwnedData':
        if self.organization_id is not None and self.organization_key is not None:
            raise PydanticCustomError('customer_error', 'Cannot provide both organization_key and organization_id')
        return self

    def get_organization_resolve_data(self) -> list[EntityResolverGetData]:
        return [
            {'key': 'key', 'value': self.organization_key},
            {'key': 'id', 'value': self.organization_id},
        ]


class OwnedDataResult(PydanticBaseModel):
    organization: Organization | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


NOT_FOUND_MSG_ORGANIZATION = 'Invalid organization_key or organization_id'


class OwnedDataProvider:
    @classmethod
    async def process_request_headers(cls, request: Request, user: User):
        data = cls._parse_request(request)
        results = await cls.resolve_owned_data([data], user)
        return results[0]

    @classmethod
    async def resolve_owned_data(cls, payloads: list[OwnedDataT], user: User):
        org_resolver = await EntityResolver[Organization](
            model=Organization,
            queryset_filter=Q(org_users__user_id=user.id),
            not_found_msg=NOT_FOUND_MSG_ORGANIZATION,
            keys_data=[
                {'model_key': 'key', 'schema_key': 'organization_key'},
                {'model_key': 'id', 'schema_key': 'organization_id'},
            ],
        ).resolve(items=payloads)

        results: list[OwnedDataResult] = []
        for el in payloads:
            organization = org_resolver.validate_and_get(el.get_organization_resolve_data())
            results.append(OwnedDataResult(organization=organization))
        return results

    @classmethod
    def _parse_request(cls, request: Request) -> OwnedData:
        data = {}
        for key in OwnedData.model_fields.keys():
            value = request.headers.get(f'{key.replace("_", "-")}')
            if value:
                data[key] = value
        return OwnedData.model_validate(data)
