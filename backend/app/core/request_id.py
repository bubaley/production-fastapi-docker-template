import re
from contextvars import ContextVar
from uuid import uuid4

from loguru import logger
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = 'X-Request-ID'
_HEADER_KEY = REQUEST_ID_HEADER.lower().encode('latin-1')
_VALID_REQUEST_ID = re.compile(r'^[A-Za-z0-9._:-]{8,128}$')

request_id_var: ContextVar[str | None] = ContextVar('request_id', default=None)


def get_request_id() -> str | None:
    return request_id_var.get()


def _incoming_request_id(scope: Scope) -> str | None:
    for key, value in scope.get('headers', ()):
        if key == _HEADER_KEY:
            candidate = value.decode('latin-1').strip()
            return candidate if _VALID_REQUEST_ID.match(candidate) else None
    return None


class RequestIdMiddleware:
    """
    Pure ASGI middleware: reuses a sane incoming `X-Request-ID` or generates one, exposes it through
    `request_id_var` (bound to every log line) and returns it on HTTP responses.

    It wraps the whole application, including Starlette's error middleware (see `app.main.App`), so the
    unhandled-exception handler logs with the request id and its 500 response carries the header.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in ('http', 'websocket'):
            await self.app(scope, receive, send)
            return

        request_id = _incoming_request_id(scope) or uuid4().hex
        token = request_id_var.set(request_id)
        response_started = False

        async def send_with_request_id(message: Message) -> None:
            nonlocal response_started
            if message['type'] == 'http.response.start':
                response_started = True
                headers = [(k, v) for k, v in message.get('headers', []) if k != _HEADER_KEY]
                headers.append((_HEADER_KEY, request_id.encode('latin-1')))
                message['headers'] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        except Exception:
            # Starlette's error middleware re-raises after the exception handler has logged the error and
            # sent the 500 response. Swallow it so the server does not log it a second time; log only what
            # no handler saw (websocket errors, failures before the response started).
            if not response_started:
                logger.exception('Unhandled error in {} {}', scope['type'], scope.get('path', ''))
        finally:
            request_id_var.reset(token)
