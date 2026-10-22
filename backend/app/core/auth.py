from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi_ronin.state import BaseStateManager
from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.requests import HTTPConnection

from app.domains.auth.services.auth_service import Authentication, AuthMethod, AuthService
from app.domains.auth.transport import CredentialKind, read_credential
from app.domains.organization.models import Organization
from app.domains.user.models import User
from app.shared.services.owned_data_provider import OwnedDataProvider, OwnedDataResult


class AuthState(BaseModel):
    user: User | None = None
    organization: Organization | None = None
    # How the user authenticated; e.g. API tokens cannot mint new API tokens.
    auth_method: AuthMethod | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def user_id(self) -> UUID | None:
        return self.user.id if self.user else None

    @property
    def organization_id(self) -> UUID | None:
        return self.organization.id if self.organization else None


def is_public_route(request: Request) -> bool:
    available_routes = {'/api/v1/auth/login', '/api/v1/auth/refresh', '/api/v1/auth/logout'}
    return request.url.path.rstrip('/') in available_routes


async def authenticate_connection(connection: HTTPConnection) -> Authentication | None:
    """Resolve the credential of an HTTP request or websocket handshake."""
    credential = read_credential(connection)
    if credential is None:
        return None
    if credential.kind == CredentialKind.API_TOKEN:
        return await AuthService.authenticate_api_token(credential.value)
    return await AuthService.authenticate_access_token(credential.value)


async def resolve_connection_user(connection: HTTPConnection) -> User | None:
    authentication = await authenticate_connection(connection)
    return authentication.user if authentication else None


async def get_authentication(request: Request) -> Authentication | None:
    authentication = await authenticate_connection(request)
    BaseStateManager.set_user(authentication.user if authentication else None)

    if not is_public_route(request) and not authentication:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    return authentication


async def get_auth_state(
    request: Request, authentication: Annotated[Authentication | None, Depends(get_authentication)]
) -> AuthState:
    user = authentication.user if authentication else None
    data = OwnedDataResult()
    if user and not is_public_route(request):
        try:
            data = await OwnedDataProvider.process_request_headers(request, user)
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors()[0]['msg'])
    auth_state = AuthState(
        user=user,
        organization=data.organization,
        auth_method=authentication.method if authentication else None,
    )
    state = BaseStateManager.get_state()
    state.set('auth_state', auth_state)
    return auth_state


def get_current_auth_state() -> AuthState:
    return BaseStateManager.get_state().get('auth_state') or AuthState()
