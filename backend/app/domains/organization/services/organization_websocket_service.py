from uuid import UUID

from fastapi import WebSocket

from app.core.auth import resolve_connection_user
from app.core.services.websocket_service import BaseWebSocketService, ChannelConfig, WebSocketMessage
from app.domains.organization.models import OrganizationUser


class _OrganizationWebSocketService(BaseWebSocketService):
    CHANNEL_NAME = 'organizations'

    def __init__(self):
        channels = [
            ChannelConfig(name=self.CHANNEL_NAME, is_detail=True),
        ]
        super().__init__(channels=channels)

    async def check_access(self, websocket: WebSocket, channel: str, recipient_id: str | None = None) -> bool:
        if channel != self.CHANNEL_NAME or not recipient_id:
            return False
        try:
            organization_id = UUID(recipient_id)
        except ValueError:
            return False
        user = await resolve_connection_user(websocket)
        if not user:
            return False
        return await OrganizationUser.filter(organization_id=organization_id, user_id=user.id).exists()

    async def process_message(self, websocket: WebSocket, message: WebSocketMessage):
        pass


OrganizationWebSocketService = _OrganizationWebSocketService()
