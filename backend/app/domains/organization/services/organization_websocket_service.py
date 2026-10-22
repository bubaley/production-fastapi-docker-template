from enum import Enum
from uuid import UUID

from fastapi import WebSocket

from app.core.auth import resolve_connection_user
from app.core.services.websocket_service import BaseWebSocketService, ChannelConfig, WebSocketMessage
from app.domains.organization.models import OrganizationUser


class OrganizationWebSocketEventType(str, Enum):
    CHAT_MESSAGE_UPDATE = 'chat.message.update'
    CHAT_UPDATE = 'chat.update'


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

    # @async_task
    # async def chat_update(self, chat: Chat):
    #     result = await ChatReadSchema.from_tortoise_orm(chat)
    #     await self.send_message(
    #         self.CHANNEL_NAME,
    #         message_type=OrganizationWebSocketEventType.CHAT_UPDATE,
    #         data=result.model_dump(mode='json'),
    #         recipients=[str(chat.organization_id)],
    #     )


OrganizationWebSocketService = _OrganizationWebSocketService()
