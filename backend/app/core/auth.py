from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi_ronin.state import BaseStateManager
from pydantic import BaseModel, ConfigDict, ValidationError

from app.core.services.crypto_service import CryptoService
from app.domains.auth.services.auth_service import AuthService
from app.domains.organization.models import Organization
from app.domains.user.models import User, UserToken
from app.shared.services.owned_data_provider import OwnedDataProvider, OwnedDataResult


class AuthState(BaseModel):
    user: User | None = None
    organization: Organization | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def user_id(self) -> UUID | None:
        return self.user.id if self.user else None

    @property
    def organization_id(self) -> UUID | None:
        return self.organization.id if self.organization else None


async def _user_from_api_token(value: str) -> Optional[User]:
    digest = CryptoService.hash_value(value)
    token = await UserToken.filter(value_hash=digest).select_related('user').first()
    if not token:
        return None
    token.last_used_at = datetime.now(timezone.utc)
    await token.save(update_fields=['last_used_at'])
    return token.user


async def _user_from_jwt_token(value: str) -> Optional[User]:
    payload: Optional[dict[str, Any]] = AuthService.verify_token(token=value)
    if not payload:
        return None
    try:
        return await User.filter(id=payload.get('id')).first()
    except Exception:
        return None


def is_public_route(request: Request) -> bool:
    available_routes = ['auth/login', 'auth/register', 'auth/refresh']
    return any(v in request.url.path for v in available_routes)


async def get_user(request: Request):
    auth_header = request.headers.get('Authorization')
    cookie_value = request.cookies.get('access_token')

    if not auth_header and not cookie_value:
        return None

    user: User | None = None

    if auth_header:
        parts = auth_header.split(None, 1)
        if len(parts) == 2:
            scheme, credential = parts[0].lower(), parts[1].strip()
            if scheme == 'token':
                user = await _user_from_api_token(credential)
            elif scheme == 'bearer':
                user = await _user_from_jwt_token(credential)
    elif cookie_value:
        user = await _user_from_jwt_token(cookie_value)

    BaseStateManager.set_user(user)

    if not is_public_route(request) and not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    return user


async def get_auth_state(request: Request, user: User = Depends(get_user)):
    data = OwnedDataResult()
    if user:
        try:
            data = await OwnedDataProvider.process_request_headers(request, user)
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors()[0]['msg'])
    auth_state = AuthState(user=user, organization=data.organization)
    state = BaseStateManager.get_state()
    state.set('auth_state', auth_state)
    return auth_state
