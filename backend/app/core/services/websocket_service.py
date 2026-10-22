import asyncio
import contextlib
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, ClassVar
from urllib.parse import urlsplit

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from loguru import logger

from app.core.auth import authenticate_connection
from app.core.services.pubsub import get_pubsub
from app.core.settings import settings
from app.core.utils.date_utils import utcnow
from app.domains.auth.services.auth_service import Authentication

# Close codes after the handshake: the credential expired or was revoked / access to the channel is gone.
CLOSE_UNAUTHORIZED = 4401
CLOSE_FORBIDDEN = 4403
CLOSE_POLICY = 1008
CLOSE_TOO_BIG = 1009
CLOSE_TRY_AGAIN = 1013

_AUTH_STATE_KEY = 'ws_authentication'


@dataclass
class ChannelConfig:
    name: str
    is_detail: bool = False
    secure: bool = True


@dataclass
class WebSocketMessage:
    channel: ChannelConfig
    message_type: str
    data: Any
    recipient_id: str | None = None


def encode_message(message_type: str, data: Any) -> str:
    """JSON text for clients; UUIDs, datetimes and pydantic models are encoded like API responses."""
    return json.dumps(jsonable_encoder({'type': message_type, 'data': data}))


def is_allowed_origin(websocket: WebSocket) -> bool:
    """Browsers always send Origin: allow same-origin and CORS origins. Clients without Origin are not browsers."""
    origin = websocket.headers.get('origin')
    if not origin:
        return True
    if origin in settings.cors_origins:
        return True
    return urlsplit(origin).netloc == websocket.headers.get('host')


class BaseWebSocketService:
    """
    Channels of websocket connections. `send_message` publishes through pub/sub (Redis in production), so a
    message sent from any API worker or the taskiq worker reaches clients connected to every API worker.
    Each send has a timeout; a slow or dead client is dropped instead of stalling the others.
    Authenticated connections are re-checked on a timer and when their token expires.
    """

    # Services with registered routes; `start_websocket_fanout` subscribes them in the API process.
    registry: ClassVar[list[BaseWebSocketService]] = []

    def __init__(self, channels: list[ChannelConfig], name: str | None = None):
        self.name = name or type(self).__name__
        self.channels = channels
        self.connections: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        self.channel_map = {channel.name: channel for channel in channels}

    @property
    def topic(self) -> str:
        return f'ws:{self.name}'

    # ACCESS

    async def get_authentication(self, websocket: WebSocket, *, refresh: bool = False) -> Authentication | None:
        """The handshake credential, resolved once per connection (again with `refresh=True`)."""
        if refresh or _AUTH_STATE_KEY not in websocket.scope.setdefault('state', {}):
            websocket.scope['state'][_AUTH_STATE_KEY] = await authenticate_connection(websocket)
        return websocket.scope['state'][_AUTH_STATE_KEY]

    async def check_access(self, websocket: WebSocket, channel: str, recipient_id: str | None = None) -> bool:
        """
        Check if user has access to the channel.
        Override this method to implement custom access control; use `get_authentication` for the user.
        """
        channel_config = self.channel_map.get(channel)
        if not channel_config:
            return False

        return not channel_config.secure

    async def revalidate(self, websocket: WebSocket, channel: str, recipient_id: str | None) -> int | None:
        """Close code when the connection must end, else None."""
        had_authentication = websocket.scope.get('state', {}).get(_AUTH_STATE_KEY) is not None
        if had_authentication and not await self.get_authentication(websocket, refresh=True):
            return CLOSE_UNAUTHORIZED
        if not await self.check_access(websocket, channel, recipient_id):
            return CLOSE_FORBIDDEN
        return None

    async def process_message(self, websocket: WebSocket, message: WebSocketMessage) -> None:
        """
        Process incoming message from WebSocket connection.
        Override this method to handle incoming messages.
        """

    # CONNECTIONS

    def _get_channel_key(self, channel: str, recipient_id: str | None = None) -> str:
        if recipient_id:
            return f'{channel}/{recipient_id}'
        return channel

    def _get_connection_id(self, websocket: WebSocket) -> str:
        return str(id(websocket))

    def has_connection(self, channel: str, recipient_id: str | None = None) -> bool:
        """Whether this process holds a connection for the channel (other processes are not consulted)."""
        channel_key = self._get_channel_key(channel, recipient_id)
        return len(self.connections.get(channel_key, {})) > 0

    def _remove(self, channel_key: str, connection_id: str) -> None:
        connections = self.connections.get(channel_key)
        if connections is None:
            return
        connections.pop(connection_id, None)
        if not connections:
            del self.connections[channel_key]

    async def _handle_connection(self, websocket: WebSocket, channel: str, recipient_id: str | None = None):
        channel_config = self.channel_map.get(channel)
        if not channel_config:
            await websocket.close(code=CLOSE_POLICY, reason='Channel not found')
            return

        if channel_config.is_detail and not recipient_id:
            await websocket.close(code=CLOSE_POLICY, reason='Recipient ID required for detail channel')
            return

        if not is_allowed_origin(websocket):
            await websocket.close(code=CLOSE_POLICY, reason='Origin not allowed')
            return

        if not await self.check_access(websocket, channel, recipient_id):
            await websocket.close(code=CLOSE_POLICY, reason='Access denied')
            return

        await websocket.accept()

        channel_key = self._get_channel_key(channel, recipient_id)
        connection_id = self._get_connection_id(websocket)
        self.connections[channel_key][connection_id] = websocket

        # The watchdog closes the socket when access ends; the client's close reply then ends the receive loop.
        watchdog = asyncio.create_task(self._watch_access(websocket, channel, recipient_id))
        try:
            await self._receive_loop(websocket, channel_config, recipient_id)
        finally:
            self._remove(channel_key, connection_id)
            watchdog.cancel()

    async def _receive_loop(self, websocket: WebSocket, channel_config: ChannelConfig, recipient_id: str | None):
        try:
            while True:
                data = await websocket.receive_text()
                if len(data.encode()) > settings.websocket_max_message_bytes:
                    await websocket.close(code=CLOSE_TOO_BIG, reason='Message too big')
                    return
                try:
                    message_dict = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_json({'error': 'Invalid JSON'})
                    continue
                if not isinstance(message_dict, dict) or 'type' not in message_dict:
                    await websocket.send_json({'error': 'Invalid message format'})
                    continue
                message = WebSocketMessage(
                    channel=channel_config,
                    message_type=message_dict['type'],
                    data=message_dict.get('data'),
                    recipient_id=recipient_id,
                )
                await self.process_message(websocket, message)
        except WebSocketDisconnect:
            return

    async def _watch_access(self, websocket: WebSocket, channel: str, recipient_id: str | None) -> None:
        while True:
            delay = float(settings.websocket_auth_check_interval_seconds)
            authentication = websocket.scope.get('state', {}).get(_AUTH_STATE_KEY)
            if authentication and authentication.expires_at:
                delay = min(delay, max(0.0, (authentication.expires_at - utcnow()).total_seconds()))
            await asyncio.sleep(delay)
            if code := await self.revalidate(websocket, channel, recipient_id):
                with contextlib.suppress(Exception):
                    await websocket.close(code=code)
                return

    # SENDING

    def register_routes(self, router: APIRouter) -> None:
        """
        Register WebSocket routes in the router and subscribe the service to fan-out.
        Routes should work with both trailing slash and without it.
        """
        if self not in BaseWebSocketService.registry:
            BaseWebSocketService.registry.append(self)

        for channel_config in self.channels:
            channel_name = channel_config.name

            if channel_config.is_detail:
                path_with_slash = f'/{channel_name}/{{recipient_id}}/'
                path_without_slash = f'/{channel_name}/{{recipient_id}}'

                def create_detail_handler(ch_name: str):
                    async def websocket_endpoint(websocket: WebSocket, recipient_id: str):
                        await self._handle_connection(websocket, ch_name, recipient_id)

                    return websocket_endpoint

                handler = create_detail_handler(channel_name)
                router.websocket(path_with_slash)(handler)
                router.websocket(path_without_slash)(handler)
            else:
                path_with_slash = f'/{channel_name}/'
                path_without_slash = f'/{channel_name}'

                def create_handler(ch_name: str):
                    async def websocket_endpoint(websocket: WebSocket):
                        await self._handle_connection(websocket, ch_name)

                    return websocket_endpoint

                handler = create_handler(channel_name)
                router.websocket(path_with_slash)(handler)
                router.websocket(path_without_slash)(handler)

    async def send_message(
        self,
        channel: str,
        message_type: str,
        data: Any,
        recipients: list[str] | None = None,
    ) -> None:
        """
        Send a message to the channel's connections in every process.

        Args:
            channel: Channel name
            message_type: Type of message (e.g., "device.updated")
            data: Message data; anything `jsonable_encoder` accepts
            recipients: Recipient IDs. None sends to all connections of a non-detail channel;
                       an empty list does nothing.
        """
        if recipients is not None and len(recipients) == 0:
            return
        text = encode_message(message_type, data)
        envelope = json.dumps({'channel': channel, 'recipients': recipients, 'text': text})
        try:
            await get_pubsub().publish(self.topic, envelope)
        except Exception as e:
            # Without the broker only this process's clients can be reached.
            logger.warning('WebSocket fan-out unavailable ({}); delivering locally', e)
            await self.deliver_local(channel, recipients, text)

    async def handle_fanout(self, envelope: str) -> None:
        payload = json.loads(envelope)
        await self.deliver_local(payload['channel'], payload['recipients'], payload['text'])

    async def deliver_local(self, channel: str, recipients: list[str] | None, text: str) -> None:
        keys = (
            [self._get_channel_key(channel)]
            if recipients is None
            else [self._get_channel_key(channel, recipient_id) for recipient_id in recipients]
        )
        targets = [
            (key, connection_id, websocket)
            for key in keys
            for connection_id, websocket in list(self.connections.get(key, {}).items())
        ]
        if not targets:
            return
        results = await asyncio.gather(*(self._send(websocket, text) for _, _, websocket in targets))
        dropped = [
            (key, connection_id, websocket) for ok, (key, connection_id, websocket) in zip(results, targets) if not ok
        ]
        for key, connection_id, _ in dropped:
            self._remove(key, connection_id)
        if dropped:
            await asyncio.gather(*(self._close_quietly(websocket) for _, _, websocket in dropped))

    @staticmethod
    async def _send(websocket: WebSocket, text: str) -> bool:
        try:
            await asyncio.wait_for(websocket.send_text(text), timeout=settings.websocket_send_timeout_seconds)
            return True
        except Exception:
            return False

    @staticmethod
    async def _close_quietly(websocket: WebSocket) -> None:
        with contextlib.suppress(Exception):
            await asyncio.wait_for(websocket.close(code=CLOSE_TRY_AGAIN), timeout=1.0)


async def start_websocket_fanout() -> None:
    pubsub = get_pubsub()
    for service in BaseWebSocketService.registry:
        pubsub.subscribe(service.topic, service.handle_fanout)
    await pubsub.start()


async def stop_websocket_fanout() -> None:
    await get_pubsub().stop()
