import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.domains.organization.services.organization_websocket_service import OrganizationWebSocketService
from app.domains.organization.tasks import notify_organization_members


@pytest.mark.asyncio
async def test_notify_task_reaches_connected_members(websocket_fanout):
    """The task runs on the in-memory broker and delivers through pub/sub, as the worker does via Redis."""
    organization_id = uuid4()
    member = AsyncMock()
    key = f'{OrganizationWebSocketService.CHANNEL_NAME}/{organization_id}'
    OrganizationWebSocketService.connections[key]['member'] = member
    try:
        task = await notify_organization_members.kiq(organization_id, 'organization.updated', {'id': organization_id})
        result = await task.wait_result(timeout=2)
        assert not result.is_err, result.error
    finally:
        OrganizationWebSocketService.connections.pop(key, None)
    member.send_text.assert_awaited_once()
    assert json.loads(member.send_text.await_args.args[0]) == {
        'type': 'organization.updated',
        'data': {'id': str(organization_id)},
    }
