from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi_ronin.decorators import action, viewset
from fastapi_ronin.permissions import IsAuthenticated

from app.core.viewsets import BaseGenericViewSet
from app.domains.auth.schemas import LoginRequest, RefreshTokenRequest, TokenResponse
from app.domains.auth.services.auth_service import AuthService, TokenType
from app.domains.user.models import User
from app.domains.user.schemas import UserReadSchema

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@viewset(auth_router)
class AuthViewSet(BaseGenericViewSet):
    model = User
    read_schema = UserReadSchema

    def get_permissions(self):
        if self.action in ['login', 'refresh', 'logout', 'register']:
            return []
        return [IsAuthenticated()]

    @action(methods=['POST'], response_model=TokenResponse)
    async def login(self, response: Response, data: LoginRequest):
        """Authenticate user and return JWT token."""
        user = await User.filter(email=data.email).first()
        if not user or not user.verify_password(data.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
        access_token = AuthService.create_access_token(user)
        access_token.set_cookie(response)
        refresh_token = AuthService.create_refresh_token(user)
        refresh_token.set_cookie(response)
        result = TokenResponse(access_token=access_token.token, refresh_token=refresh_token.token)
        return result

    @action(methods=['POST'])
    async def logout(self, response: Response):
        """Logout user by clearing auth cookies."""
        AuthService.remove_cookie(response, TokenType.ACCESS)
        AuthService.remove_cookie(response, TokenType.REFRESH)
        result = {'success': True}
        return result

    @action(methods=['GET'], response_model=UserReadSchema)
    async def me(self):
        """Get current authenticated user information."""
        result = self.user
        return result

    # @action(methods=['POST'], response_model=UserSchema)
    # async def register(self, data: RegisterRequest):
    #     """Register a new user with hashed password."""
    #     user_data = data.model_dump(exclude={'password'})
    #     user = User(**user_data)
    #     user.set_password(data.password)
    #     await user.save()
    #     organization = await Organization.create(name='Основная', key='main')
    #     await organization.users.add(user)
    #     user.organization = organization
    #     await user.save()
    #     return user

    @action(methods=['POST'], response_model=TokenResponse)
    async def refresh(self, request: Request, response: Response, data: RefreshTokenRequest | None = None):
        """Refresh access and refresh tokens using a valid refresh token."""
        refresh_cookie_key = AuthService.get_cookie_key(TokenType.REFRESH)
        refresh_token = data.refresh_token if data else request.cookies.get(refresh_cookie_key)
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token not found')
        payload = AuthService.verify_token(refresh_token)
        if not payload or payload.get('type') != TokenType.REFRESH:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

        user_id = payload.get('id')
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token payload')

        user = await User.filter(id=user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

        access_token = AuthService.create_access_token(user)
        access_token.set_cookie(response)
        refresh_token = AuthService.create_refresh_token(user)
        refresh_token.set_cookie(response)

        result = TokenResponse(access_token=access_token.token, refresh_token=refresh_token.token)
        return result
