from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi_ronin.decorators import action, viewset
from fastapi_ronin.permissions import IsAuthenticated

from app.core.viewsets import BaseGenericViewSet
from app.domains.auth.schemas import LoginRequest, RefreshTokenRequest, TokenResponse
from app.domains.auth.services.auth_service import AuthService
from app.domains.auth.transport import clear_auth_cookies, read_access_token, read_refresh_token, set_auth_cookies
from app.domains.user.models import User
from app.domains.user.schemas import UserReadSchema

auth_router = APIRouter(prefix='/auth', tags=['auth'])


def _client_ip(request: Request) -> str:
    # Behind Caddy this is the real client only when uvicorn runs with --proxy-headers.
    return request.client.host if request.client else 'unknown'


@viewset(auth_router)
class AuthViewSet(BaseGenericViewSet):
    model = User
    read_schema = UserReadSchema

    def get_permissions(self):
        if self.action in ['login', 'refresh', 'logout']:
            return []
        return [IsAuthenticated()]

    @action(methods=['POST'], response_model=TokenResponse)
    async def login(self, request: Request, response: Response, data: LoginRequest):
        """Authenticate user and return JWT tokens (also set as cookies)."""
        pair = await AuthService.login(data.email, data.password, client_ip=_client_ip(request))
        set_auth_cookies(response, pair)
        return TokenResponse.from_pair(pair)

    @action(methods=['POST'])
    async def logout(self, request: Request, response: Response, data: RefreshTokenRequest | None = None):
        """End the current session: revoke its refresh tokens and clear auth cookies."""
        refresh_token = (data.refresh_token if data else None) or read_refresh_token(request)
        await AuthService.logout(refresh_token=refresh_token, access_token=read_access_token(request))
        clear_auth_cookies(response)
        return {'success': True}

    @action(methods=['POST'])
    async def logout_all(self, response: Response):
        """End every session of the current user: all issued JWTs stop working."""
        await AuthService.invalidate_user_tokens(self.user)
        clear_auth_cookies(response)
        return {'success': True}

    @action(methods=['GET'], response_model=UserReadSchema)
    async def me(self):
        """Get current authenticated user information."""
        return self.user

    @action(methods=['POST'], response_model=TokenResponse)
    async def refresh(self, request: Request, response: Response, data: RefreshTokenRequest | None = None):
        """Rotate the refresh token: returns a new pair; the presented refresh token stops working."""
        refresh_token = (data.refresh_token if data else None) or read_refresh_token(request)
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token not found')
        pair = await AuthService.refresh(refresh_token)
        set_auth_cookies(response, pair)
        return TokenResponse.from_pair(pair)
