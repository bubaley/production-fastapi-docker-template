from enum import Enum

from fastapi import WebSocket

from app.core.services.websocket_service import BaseWebSocketService, ChannelConfig, WebSocketMessage


class OrganizationWebSocketEventType(str, Enum):
    CHAT_MESSAGE_UPDATE = 'chat.message.update'
    CHAT_UPDATE = 'chat.update'


class _OrganizationWebSocketService(BaseWebSocketService):
    CHANNEL_NAME = 'organizations'

    def __init__(self):
        channels = [
            ChannelConfig(name=self.CHANNEL_NAME, is_detail=True, secure=False),
        ]
        super().__init__(channels=channels)

    async def check_access(self, websocket: WebSocket, channel: str, recipient_id: str | None = None) -> bool:
        return True

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
