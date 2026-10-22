"""How auth tokens travel (HttpOnly cookies, Authorization header). The token lifecycle itself lives in AuthService."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from fastapi import Response
from starlette.requests import HTTPConnection

from app.core.settings import settings
from app.domains.auth.services.token_service import IssuedToken, TokenPair, TokenType

ACCESS_COOKIE = 'access_token'
REFRESH_COOKIE = 'refresh_token'


def _cookie_path(token_type: TokenType) -> str:
    # The refresh cookie is sent only to the auth endpoints, never with ordinary API requests.
    return settings.refresh_cookie_path if token_type == TokenType.REFRESH else '/'


def _cookie_key(token_type: TokenType) -> str:
    return REFRESH_COOKIE if token_type == TokenType.REFRESH else ACCESS_COOKIE


def _set_cookie(response: Response, token: IssuedToken) -> None:
    response.set_cookie(
        key=_cookie_key(token.type),
        value=token.token,
        max_age=max(0, int((token.expires_at - datetime.now(tz=UTC)).total_seconds())),
        path=_cookie_path(token.type),
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _delete_cookie(response: Response, key: str, path: str) -> None:
    response.delete_cookie(
        key=key,
        path=path,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def _delete_legacy_refresh_cookie(response: Response) -> None:
    # Refresh cookies issued before the path was narrowed live on '/'.
    if settings.refresh_cookie_path != '/':
        _delete_cookie(response, REFRESH_COOKIE, '/')


def set_auth_cookies(response: Response, pair: TokenPair) -> None:
    _delete_legacy_refresh_cookie(response)
    _set_cookie(response, pair.access)
    _set_cookie(response, pair.refresh)


def clear_auth_cookies(response: Response) -> None:
    _delete_legacy_refresh_cookie(response)
    _delete_cookie(response, ACCESS_COOKIE, _cookie_path(TokenType.ACCESS))
    _delete_cookie(response, REFRESH_COOKIE, _cookie_path(TokenType.REFRESH))


class CredentialKind(StrEnum):
    COOKIE = 'cookie'  # access JWT in the HttpOnly access cookie (browsers, SSR with the forwarded Cookie header)
    API_TOKEN = 'token'  # API token in `Authorization: Token ...` (integrations)
    BEARER = 'bearer'  # access JWT in `Authorization: Bearer ...` (tests, server-side scripts)


@dataclass(frozen=True)
class Credential:
    kind: CredentialKind
    value: str


def read_credentials(connection: HTTPConnection) -> list[Credential]:
    """Every credential the connection carries, in resolution order: access cookie, then Authorization header."""
    credentials: list[Credential] = []
    if cookie := connection.cookies.get(ACCESS_COOKIE):
        credentials.append(Credential(kind=CredentialKind.COOKIE, value=cookie))
    auth_header = connection.headers.get('Authorization')
    if auth_header:
        scheme, _, value = auth_header.strip().partition(' ')
        value = value.strip()
        kinds = {'token': CredentialKind.API_TOKEN, 'bearer': CredentialKind.BEARER}
        if (kind := kinds.get(scheme.lower())) and value:
            credentials.append(Credential(kind=kind, value=value))
    return credentials


def has_auth_cookie(connection: HTTPConnection) -> bool:
    return ACCESS_COOKIE in connection.cookies or REFRESH_COOKIE in connection.cookies


def read_access_token(connection: HTTPConnection) -> str | None:
    """The access JWT from the cookie or a Bearer header (never an API token)."""
    return next(
        (
            credential.value
            for credential in read_credentials(connection)
            if credential.kind != CredentialKind.API_TOKEN
        ),
        None,
    )


def read_refresh_token(connection: HTTPConnection) -> str | None:
    return connection.cookies.get(REFRESH_COOKIE)
