from pydantic import BaseModel, Field

from app.core.fields.email_field import LoginEmail
from app.domains.auth.services.token_service import TokenPair


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: LoginEmail
    password: str = Field(max_length=128)


class RefreshTokenRequest(BaseModel):
    """Refresh token in the body; without it the refresh cookie is used."""

    refresh_token: str | None = None


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    type: str = 'bearer'

    @classmethod
    def from_pair(cls, pair: TokenPair) -> TokenResponse:
        return cls(access_token=pair.access.token, refresh_token=pair.refresh.token)
