from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Optional

import bcrypt
from fastapi import Response
from jose import JWTError, jwt

from app.core.settings import settings

if TYPE_CHECKING:
    from app.domains.user.models import User


class TokenType(StrEnum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class Token:
    """Helper class to represent a JWT token with type and expiry."""

    def __init__(self, token: str, token_type: TokenType, expires: Optional[datetime] = None):
        self.token = token
        self.type = token_type
        self.expires = expires

    def remove_cookie(self, response: Response, path: str = '/'):
        """Remove the token as an HTTP-only cookie in the response."""
        AuthService.remove_cookie(response, self.type, path)

    def set_cookie(self, response: Response, path: str = '/'):
        """Set the token as an HTTP-only cookie in the response."""
        AuthService.set_cookie(response, self.type, self.token, self.expires, path)

    @property
    def cookie_key(self) -> str:
        return AuthService.get_cookie_key(self.type)


class AuthService:
    """Service for handling authentication operations including password hashing and JWT tokens."""

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_access_token(user: 'User') -> Token:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        payload: dict[str, Any] = {'id': str(user.id), 'type': TokenType.ACCESS, 'exp': expire}
        encoded_jwt = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
        return Token(token=encoded_jwt, token_type=TokenType.ACCESS, expires=expire)  # nosec B106

    @staticmethod
    def create_refresh_token(user: 'User') -> Token:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_refresh_token_expire_minutes)
        payload: dict[str, Any] = {'id': str(user.id), 'type': TokenType.REFRESH, 'exp': expire}
        encoded_jwt = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
        return Token(token=encoded_jwt, token_type=TokenType.REFRESH, expires=expire)  # nosec B106

    @staticmethod
    def verify_token(token: str) -> Optional[dict[str, Any]]:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError:
            return None

    @staticmethod
    def set_token_cookie(response: Response, token: Token):
        """Set a JWT token in HTTP-only cookie."""
        token.set_cookie(response)

    @staticmethod
    def remove_cookie(response: Response, token_type: TokenType, path: str = '/'):
        """Remove the token as an HTTP-only cookie in the response."""
        response.delete_cookie(key=token_type.value, path=path, httponly=settings.cookie_httponly)

    @staticmethod
    def set_cookie(
        response: Response, token_type: TokenType, token: str, expires: Optional[datetime] = None, path: str = '/'
    ):
        """Set the token as an HTTP-only cookie in the response."""
        max_age = None
        if expires:
            max_age = int((expires - datetime.now(tz=timezone.utc)).total_seconds())
        response.set_cookie(
            key=AuthService.get_cookie_key(token_type),
            value=token,
            max_age=max_age,
            path=path,
            httponly=settings.cookie_httponly,
            secure=settings.cookie_secure,
            samesite=settings.cookie_samesite,
        )

    @staticmethod
    def get_cookie_key(token_type: TokenType) -> str:
        return f'{token_type.value}_token'
