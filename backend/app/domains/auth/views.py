from fastapi import APIRouter, Request, Response
from fastapi_ronin.decorators import action, viewset
from fastapi_ronin.permissions import IsAuthenticated

from app.core.exceptions import AppException
from app.core.schemas import ErrorCode
from app.core.viewsets import BaseGenericViewSet
from app.domains.auth.schemas import LoginRequest, MeSchema, SessionExpirySchema, SessionSchema
from app.domains.auth.services.auth_service import AuthService
from app.domains.auth.transport import clear_auth_cookies, read_access_token, read_refresh_token, set_auth_cookies
from app.domains.user.models import User
from app.domains.user.schemas import UserReadSchema

auth_router = APIRouter(prefix='/auth', tags=['auth'])
routers = (auth_router,)


def _client_ip(request: Request) -> str:
    # Behind Caddy this is the real client only when uvicorn runs with --proxy-headers.
    return request.client.host if request.client else 'unknown'


@viewset(auth_router)
class AuthViewSet(BaseGenericViewSet):
    """
    Session endpoints. Tokens travel only in HttpOnly cookies (`domains/auth/transport.py`); response bodies carry
    the user and cookie expiry, never a token.
    """

    model = User
    read_schema = UserReadSchema

    def get_permissions(self):
        if self.action in ['login', 'refresh', 'logout']:
            return []
        return [IsAuthenticated()]

    @action(methods=['POST'])
    async def login(self, request: Request, response: Response, data: LoginRequest) -> SessionSchema:
        """Check the password and start a session: sets the `access_token` and `refresh_token` cookies."""
        session = await AuthService.login(data.email, data.password, client_ip=_client_ip(request))
        set_auth_cookies(response, session.tokens)
        return await SessionSchema.build(session.user, session.tokens)

    @action(methods=['POST'])
    async def refresh(self, request: Request, response: Response) -> SessionExpirySchema:
        """Rotate the session from the `refresh_token` cookie; both cookies are replaced."""
        refresh_token = read_refresh_token(request)
        if not refresh_token:
            raise AppException.from_attrs(ErrorCode.UNAUTHORIZED, 'Refresh token not found')
        pair = await AuthService.refresh(refresh_token)
        set_auth_cookies(response, pair)
        return SessionExpirySchema.from_pair(pair)

    @action(methods=['POST'], status_code=204)
    async def logout(self, request: Request, response: Response) -> None:
        """End the current session (works with expired credentials): revoke it and clear the auth cookies."""
        await AuthService.logout(refresh_token=read_refresh_token(request), access_token=read_access_token(request))
        clear_auth_cookies(response)

    @action(methods=['POST'], status_code=204)
    async def logout_all(self, response: Response) -> None:
        """End every session of the current user and clear the auth cookies."""
        await AuthService.invalidate_user_tokens(self.user)
        clear_auth_cookies(response)

    @action(methods=['GET'])
    async def me(self) -> MeSchema:
        """The current user and their organizations."""
        return await MeSchema.for_user(self.user)
