from pydantic import BaseModel

from app.core.fields.email_field import NormalizedEmail


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: NormalizedEmail
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str | None = None


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    type: str = 'bearer'
