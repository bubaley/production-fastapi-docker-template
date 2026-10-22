from uuid import UUID

from fastapi import WebSocket

from app.core.services.websocket_service import BaseWebSocketService, ChannelConfig, WebSocketMessage
from app.domains.organization.models import OrganizationUser


class _OrganizationWebSocketService(BaseWebSocketService):
    CHANNEL_NAME = 'organizations'

    def __init__(self):
        channels = [
            ChannelConfig(name=self.CHANNEL_NAME, is_detail=True),
        ]
        super().__init__(channels=channels, name='organizations')

    async def check_access(self, websocket: WebSocket, channel: str, recipient_id: str | None = None) -> bool:
        if channel != self.CHANNEL_NAME or not recipient_id:
            return False
        try:
            organization_id = UUID(recipient_id)
        except ValueError:
            return False
        authentication = await self.get_authentication(websocket)
        if not authentication:
            return False
        return await OrganizationUser.filter(organization_id=organization_id, user_id=authentication.user.id).exists()

    async def notify(self, organization_id: UUID | str, message_type: str, data: object) -> None:
        """Send to every member connected to the organization channel, in any process."""
        await self.send_message(self.CHANNEL_NAME, message_type, data, recipients=[str(organization_id)])

    async def process_message(self, websocket: WebSocket, message: WebSocketMessage):
        pass


OrganizationWebSocketService = _OrganizationWebSocketService()
