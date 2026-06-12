from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str | None = None


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    type: str = 'bearer'


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: str
    password: str
    first_name: str
    last_name: str
