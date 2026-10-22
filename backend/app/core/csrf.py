"""
Origin checks for cookie-authenticated requests.

Browsers attach cookies to cross-site requests, so every unsafe request that relies on the auth cookies must
come from a trusted origin: the API's own host or one of `CORS_ORIGINS`. `SameSite=Lax` already keeps the cookies
off cross-site POSTs; this check also covers same-site attackers (sibling subdomains) and old browsers.
Requests authenticated by an `Authorization` header are exempt: a cross-site page cannot set that header.
Safe methods are never checked, so SSR can forward the browser's `Cookie` header on GETs without an Origin.
"""

from urllib.parse import urlsplit

from starlette.requests import HTTPConnection

from app.core.exceptions import AppException
from app.core.schemas import ErrorCode
from app.core.settings import settings

SAFE_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS', 'TRACE'})
CSRF_FAILED = 'Origin not allowed'


def request_origin(connection: HTTPConnection) -> str | None:
    """`Origin`, else the scheme and host of `Referer`. None when the client sent neither."""
    if origin := connection.headers.get('origin'):
        return origin
    referer = urlsplit(connection.headers.get('referer') or '')
    if referer.scheme and referer.netloc:
        return f'{referer.scheme}://{referer.netloc}'
    return None


def is_trusted_origin(origin: str, connection: HTTPConnection) -> bool:
    """Same host as the request or listed in `CORS_ORIGINS`. `Origin: null` (sandboxed frames) is never trusted."""
    if origin.rstrip('/') in {allowed.rstrip('/') for allowed in settings.cors_origins}:
        return True
    netloc = urlsplit(origin).netloc
    return bool(netloc) and netloc == connection.headers.get('host')


def enforce_trusted_origin(connection: HTTPConnection, method: str) -> None:
    """403 for an unsafe request without a trusted Origin/Referer. Call only for cookie-authenticated requests."""
    if method.upper() in SAFE_METHODS:
        return
    origin = request_origin(connection)
    if origin is None or not is_trusted_origin(origin, connection):
        raise AppException.from_attrs(ErrorCode.FORBIDDEN, CSRF_FAILED)
