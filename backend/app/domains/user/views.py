import hashlib
import secrets

from fastapi import APIRouter, HTTPException
from fastapi_ronin import mixins
from fastapi_ronin.decorators import action, viewset
from fastapi_ronin.types import PydanticModel
from pydantic import BaseModel

from app.core.viewsets import BaseModelViewSet, BaseReadOnlyViewSet
from app.domains.organization.models import OrganizationUser
from app.domains.user.filters import UserTokenFilterSet
from app.domains.user.models import User, UserToken
from app.domains.user.schemas import (
    UserCreateSchema,
    UserReadSchema,
    UserTokenCreatedReadSchema,
    UserTokenCreateSchema,
    UserTokenReadSchema,
    UserUpdateSchema,
)

users_router = APIRouter(prefix='/users', tags=['users'])
user_tokens_router = APIRouter(prefix='/user-tokens', tags=['user-tokens'])


@viewset(users_router)
class UserViewSet(BaseModelViewSet[User]):
    model = User
    read_schema = UserReadSchema
    create_schema = UserCreateSchema
    update_schema = UserUpdateSchema

    async def get_queryset(self):
        user: User = self.user
        if user.is_superuser:
            return User.all()

        user_ids = await OrganizationUser.filter(user_id=user.id).values_list('user_id', flat=True)
        return User.filter(id__in=user_ids)

    async def validate_data(self, data: PydanticModel):
        if isinstance(data, UserCreateSchema):
            if data.is_superuser and not self.user.is_superuser:
                raise HTTPException(status_code=403, detail='Forbidden')
        elif isinstance(data, UserUpdateSchema) and not self.user.is_superuser:
            payload = data.model_dump(exclude_unset=True)
            if 'is_superuser' in payload:
                raise HTTPException(status_code=403, detail='Cannot change superuser flag')
        return await super().validate_data(data)

    async def before_save(self, obj: User) -> None:
        v = self.state.validated_data
        if isinstance(v, BaseModel):
            raw = v.model_dump(exclude_unset=True)
            if raw.get('password'):
                obj.set_password(raw['password'])

    async def perform_destroy(self, obj: User) -> None:
        if obj.id == self.user.id:
            raise HTTPException(status_code=400, detail='Cannot delete yourself')
        await obj.delete()


@viewset(user_tokens_router)
class UserTokenViewSet(BaseReadOnlyViewSet[UserToken], mixins.CreateMixin[UserToken], mixins.DestroyMixin[UserToken]):
    model = UserToken
    filterset_class = UserTokenFilterSet
    read_schema = UserTokenReadSchema
    create_schema = UserTokenCreateSchema

    async def get_queryset(self):
        user: User = self.user
        if user.is_superuser:
            return UserToken.all()
        user_ids = await OrganizationUser.filter(user_id=user.id).values_list('user_id', flat=True)
        user_ids = list(set(user_ids) | {user.id})
        return UserToken.filter(user_id__in=user_ids)

    @action(methods=['POST'], detail=False)
    async def create(self, data: UserTokenCreateSchema) -> UserTokenCreatedReadSchema:
        user_token = UserToken().update_from_dict(data.model_dump(exclude_unset=True))
        value = secrets.token_urlsafe(32)
        user_token.value_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()
        user_token.value = value
        user_token.value_preview = f'***{value[-6:]}'
        await user_token.save()
        result = await UserTokenCreatedReadSchema.from_tortoise_orm(user_token)
        result.value = value
        return result
