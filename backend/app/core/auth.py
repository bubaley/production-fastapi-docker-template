from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi_ronin.state import BaseStateManager
from pydantic import BaseModel, ConfigDict, ValidationError
from starlette.requests import HTTPConnection

from app.core.csrf import enforce_trusted_origin
from app.domains.auth.services.auth_service import Authentication, AuthMethod, AuthService
from app.domains.auth.transport import Credential, CredentialKind, has_auth_cookie, read_credentials
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


PUBLIC_PATHS = frozenset({'/api/v1/auth/login', '/api/v1/auth/refresh', '/api/v1/auth/logout'})


def is_public_route(request: Request) -> bool:
    return request.url.path.rstrip('/') in PUBLIC_PATHS


async def _authenticate(credential: Credential) -> Authentication | None:
    if credential.kind == CredentialKind.API_TOKEN:
        return await AuthService.authenticate_api_token(credential.value)
    return await AuthService.authenticate_access_token(credential.value)


async def resolve_connection(connection: HTTPConnection) -> tuple[Authentication, CredentialKind] | None:
    """
    The first valid credential in order: access cookie, `Authorization: Token`, `Authorization: Bearer`.
    An expired or revoked cookie does not hide a valid header credential.
    """
    for credential in read_credentials(connection):
        if authentication := await _authenticate(credential):
            return authentication, credential.kind
    return None


async def authenticate_connection(connection: HTTPConnection) -> Authentication | None:
    """Resolve the credential of an HTTP request or websocket handshake."""
    resolved = await resolve_connection(connection)
    return resolved[0] if resolved else None


async def get_authentication(request: Request) -> Authentication | None:
    resolved = await resolve_connection(request)
    authentication = resolved[0] if resolved else None
    # CSRF: unsafe requests that rely on the auth cookies need a trusted Origin; header credentials are exempt.
    relies_on_cookies = resolved[1] == CredentialKind.COOKIE if resolved else has_auth_cookie(request)
    if relies_on_cookies:
        enforce_trusted_origin(request, request.method)

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


def organization_key_header(
    organization_key: Annotated[
        str | None,
        Header(
            alias='Organization-Key',
            description='Key of the active organization; required by organization-scoped endpoints.',
        ),
    ] = None,
) -> str | None:
    """Declares `Organization-Key` in OpenAPI for the endpoints that use it; `get_auth_state` resolves it."""
    return organization_key


def get_current_auth_state() -> AuthState:
    return BaseStateManager.get_state().get('auth_state') or AuthState()
