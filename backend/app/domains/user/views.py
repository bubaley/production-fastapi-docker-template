from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from fastapi_ronin import mixins
from fastapi_ronin.decorators import action, viewset
from fastapi_ronin.types import PydanticModel
from pydantic import BaseModel

from app.core.auth import get_current_auth_state
from app.core.viewsets import BaseModelViewSet, BaseReadOnlyViewSet
from app.domains.auth.transport import set_auth_cookies
from app.domains.user.filters import UserTokenFilterSet
from app.domains.user.models import User, UserToken
from app.domains.user.schemas import (
    UserChangePasswordSchema,
    UserCreateSchema,
    UserReadSchema,
    UserTokenCreatedReadSchema,
    UserTokenCreateSchema,
    UserTokenReadSchema,
    UserTokenUpdateSchema,
    UserUpdateSchema,
)
from app.domains.user.services.user_service import UserService
from app.shared.permissions.is_superuser import IsSuperUser

users_router = APIRouter(prefix='/users', tags=['users'])
user_tokens_router = APIRouter(prefix='/user-tokens', tags=['user-tokens'])


@viewset(users_router)
class UserViewSet(BaseModelViewSet[User]):
    model = User
    read_schema = UserReadSchema
    create_schema = UserCreateSchema
    update_schema = UserUpdateSchema

    def get_permissions(self):
        permissions = [permission() for permission in self.permission_classes]
        if self.action in {'create', 'destroy'}:
            return [*permissions, IsSuperUser()]
        return permissions

    async def get_queryset(self):
        user: User = self.user
        if user.is_superuser:
            return User.all()
        return await super().get_queryset()

    async def validate_data(self, data: PydanticModel):
        if isinstance(data, UserCreateSchema):
            UserService.validate_create(self.user, data.is_superuser)
        return await super().validate_data(data)

    async def before_save(self, obj: User) -> None:
        v = self.state.validated_data
        if isinstance(v, BaseModel):
            raw = v.model_dump(exclude_unset=True)
            if raw.get('password'):
                await obj.set_password_async(raw['password'])

    async def perform_update(self, obj: User) -> User:
        changes = self._changes()
        UserService.validate_update(self.user, obj.id, changes)
        await obj.save()
        await UserService.after_update(obj, changes)
        return obj

    def _changes(self) -> dict:
        v = self.state.validated_data
        return v.model_dump(exclude_unset=True) if isinstance(v, BaseModel) else dict(v or {})

    async def perform_destroy(self, obj: User) -> None:
        if obj.id == self.user.id:
            raise HTTPException(status_code=400, detail='Cannot delete yourself')
        await obj.delete()

    @action(methods=['POST'], detail=True)
    async def change_password(
        self, item_id: UUID, data: UserChangePasswordSchema, response: Response
    ) -> UserReadSchema:
        """Change the password; every token of the user stops working. A self-change returns new auth cookies."""
        user = await self.get_object(item_id)
        await UserService.validate_password_change(self.user, user, data.current_password)
        pair = await UserService.change_password(self.user, user, data.new_password)
        if pair:
            set_auth_cookies(response, pair)
        return await UserReadSchema.from_tortoise_orm(user)


@viewset(user_tokens_router)
class UserTokenViewSet(
    BaseReadOnlyViewSet[UserToken],
    mixins.CreateMixin[UserToken],
    mixins.DestroyMixin[UserToken],
    mixins.UpdateMixin[UserToken],
):
    model = UserToken
    filterset_class = UserTokenFilterSet
    read_schema = UserTokenReadSchema
    create_schema = UserTokenCreateSchema
    update_schema = UserTokenUpdateSchema

    async def get_queryset(self):
        user: User = self.user
        if user.is_superuser:
            return UserToken.all()
        return await super().get_queryset()

    @action(methods=['POST'], detail=False, status_code=201)
    async def create(self, data: UserTokenCreateSchema) -> UserTokenCreatedReadSchema:
        owner_id = UserService.validate_api_token_creation(
            self.user, get_current_auth_state().auth_method, data.user_id, data.expires_at
        )
        token, value = await UserService.create_api_token(owner_id, data.name, data.expires_at)
        setattr(token, 'value', value)  # noqa: B010 - read schema field, not a model column
        return await UserTokenCreatedReadSchema.from_tortoise_orm(token)
