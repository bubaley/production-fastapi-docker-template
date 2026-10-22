from typing import Any
from uuid import UUID

from app.core.broker import broker
from app.domains.organization.services.organization_websocket_service import OrganizationWebSocketService


@broker.task(task_name='organization.notify_members')
async def notify_organization_members(organization_id: UUID, message_type: str, data: dict[str, Any]) -> None:
    """Push a websocket event to the organization's members; runs in the taskiq worker, delivered via pub/sub."""
    await OrganizationWebSocketService.notify(organization_id, message_type, data)
