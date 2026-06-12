import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect


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
    recipient_id: Optional[str] = None
    request_id: Optional[str] = None


class BaseWebSocketService:
    def __init__(self, channels: list[ChannelConfig]):
        self.channels = channels
        self.connections: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        self.channel_map = {channel.name: channel for channel in channels}

    async def check_access(self, websocket: WebSocket, channel: str, recipient_id: Optional[str] = None) -> bool:
        """
        Check if user has access to the channel.
        Override this method to implement custom access control.
        """
        channel_config = self.channel_map.get(channel)
        if not channel_config:
            return False

        if not channel_config.secure:
            return True

        return True

    async def _process_message(self, websocket: WebSocket, message: WebSocketMessage) -> None:
        """
        Process incoming message from WebSocket connection.
        Override this method to handle incoming messages.
        """
        error = None
        data = None
        try:
            data = await self.process_message(websocket, message)
        except Exception as e:
            error = str(e)
        await websocket.send_json(
            {
                'success': bool(not error),
                'type': 'message.response',
                'data': data,
                'request_id': message.request_id,
                'error': {'message': error} if error else None,
            }
        )

    async def process_message(self, websocket: WebSocket, message: WebSocketMessage) -> list | dict | None:
        """
        Process incoming message from WebSocket connection.
        Override this method to handle incoming messages.
        """

    def _get_channel_key(self, channel: str, recipient_id: Optional[str] = None) -> str:
        if recipient_id:
            return f'{channel}/{recipient_id}'
        return channel

    def _get_connection_id(self, websocket: WebSocket) -> str:
        return str(id(websocket))

    def has_connection(self, channel: str, recipient_id: Optional[str] = None) -> bool:
        """
        Check if there are active WebSocket connections for the given channel and recipient_id.

        Args:
            channel: Channel name
            recipient_id: Optional recipient ID for detail channels

        Returns:
            True if there is at least one active connection, False otherwise
        """
        channel_key = self._get_channel_key(channel, recipient_id)
        connections = self.connections.get(channel_key, {})
        return len(connections) > 0

    async def _handle_connection(self, websocket: WebSocket, channel: str, recipient_id: Optional[str] = None):
        channel_config = self.channel_map.get(channel)
        if not channel_config:
            await websocket.close(code=1008, reason='Channel not found')
            return

        if channel_config.is_detail and not recipient_id:
            await websocket.close(code=1008, reason='Recipient ID required for detail channel')
            return

        if not await self.check_access(websocket, channel, recipient_id):
            await websocket.close(code=1008, reason='Access denied')
            return

        await websocket.accept()

        channel_key = self._get_channel_key(channel, recipient_id)
        connection_id = self._get_connection_id(websocket)
        self.connections[channel_key][connection_id] = websocket

        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message_dict = json.loads(data)
                    if not isinstance(message_dict, dict) or 'type' not in message_dict:
                        await websocket.send_json({'error': 'Invalid message format'})
                        continue

                    message = WebSocketMessage(
                        channel=channel_config,
                        message_type=message_dict['type'],
                        data=message_dict.get('data'),
                        recipient_id=recipient_id,
                        request_id=message_dict.get('request_id'),
                    )
                    await self._process_message(websocket, message)
                except json.JSONDecodeError:
                    await websocket.send_json({'error': 'Invalid JSON'})
        except WebSocketDisconnect:
            pass
        finally:
            if connection_id in self.connections[channel_key]:
                del self.connections[channel_key][connection_id]
            if not self.connections[channel_key]:
                del self.connections[channel_key]

    def register_routes(self, router: APIRouter) -> None:
        """
        Register WebSocket routes in the router.
        Routes should work with both trailing slash and without it.
        """
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
        event_type: str,
        data: Any,
        recipients: Optional[list[str]] = None,
    ) -> None:
        """
        Send message to WebSocket connections.

        Args:
            channel: Channel name
            message_type: Type of message (e.g., "device.updated")
            data: Message data
            recipients: List of recipient IDs. If None, send to all connections in channel.
                       If empty list, do nothing.
        """
        if recipients is not None and len(recipients) == 0:
            return

        message = {'type': event_type, 'data': data}
        message_json = json.dumps(message)

        if recipients is None:
            channel_key = self._get_channel_key(channel)
            connections = self.connections.get(channel_key, {})
            disconnected = []

            for connection_id, ws in connections.items():
                try:
                    await ws.send_text(message_json)
                except Exception:
                    disconnected.append(connection_id)

            for connection_id in disconnected:
                if connection_id in connections:
                    del connections[connection_id]
        else:
            for recipient_id in recipients:
                channel_key = self._get_channel_key(channel, recipient_id)
                connections = self.connections.get(channel_key, {})
                disconnected = []

                for connection_id, ws in connections.items():
                    try:
                        await ws.send_text(message_json)
                    except Exception:
                        disconnected.append(connection_id)

                for connection_id in disconnected:
                    if connection_id in connections:
                        del connections[connection_id]
