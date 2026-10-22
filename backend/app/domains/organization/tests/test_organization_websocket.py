import hashlib
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.services.websocket_service import BaseWebSocketService, ChannelConfig
from app.domains.auth.services.auth_service import AuthService
from app.domains.organization.models import Organization, OrganizationUser
from app.domains.organization.services.organization_websocket_service import OrganizationWebSocketService
from app.domains.user.models import UserToken
from app.main import app


@pytest.mark.asyncio
@pytest.mark.parametrize('credential', ['access', 'cookie', 'api', 'refresh', 'anonymous'])
async def test_organization_websocket_requires_member_and_access_credential(db, user_factory, credential):
    actor = await user_factory()
    organization = await Organization.create(name='Org', key='org')
    await OrganizationUser.create(organization=organization, user=actor)
    headers = []
    if credential == 'cookie':
        headers = [(b'cookie', f'access_token={AuthService.create_access_token(actor).token}'.encode())]
    elif credential == 'api':
        value = 'isolated-test-api-token'
        await UserToken.create(
            user=actor, name='WS', value_hash=hashlib.sha256(value.encode()).hexdigest(), value_preview='***token'
        )
        headers = [(b'authorization', f'Token {value}'.encode())]
    elif credential in {'access', 'refresh'}:
        create_token = AuthService.create_access_token if credential == 'access' else AuthService.create_refresh_token
        headers = [(b'authorization', f'Bearer {create_token(actor).token}'.encode())]
    websocket = WebSocket({'type': 'websocket', 'path': '/ws', 'headers': headers}, AsyncMock(), AsyncMock())
    allowed = credential in {'access', 'cookie', 'api'}
    assert await OrganizationWebSocketService.check_access(websocket, 'organizations', str(organization.id)) is allowed


@pytest.mark.asyncio
@pytest.mark.parametrize('admin', [False, True])
async def test_websocket_rejects_authenticated_nonmembers(db, user_factory, admin):
    actor = await user_factory(is_superuser=admin)
    organization = await Organization.create(name='Other', key='other')
    websocket = WebSocket(
        {
            'type': 'websocket',
            'path': '/ws',
            'headers': [(b'authorization', f'Bearer {AuthService.create_access_token(actor).token}'.encode())],
        },
        AsyncMock(),
        AsyncMock(),
    )
    assert not await OrganizationWebSocketService.check_access(websocket, 'organizations', str(organization.id))
    assert not await OrganizationWebSocketService.check_access(websocket, 'organizations', 'not-a-uuid')


def test_anonymous_websocket_handshake_is_denied():
    with (
        pytest.raises(WebSocketDisconnect) as error,
        TestClient(app).websocket_connect(f'/ws/organizations/{uuid4()}'),
    ):
        pytest.fail('Anonymous connection was accepted')
    assert error.value.code == 1008


@pytest.mark.asyncio
async def test_secure_base_channels_require_explicit_access_policy():
    service = BaseWebSocketService([ChannelConfig('private'), ChannelConfig('public', secure=False)])
    websocket = WebSocket({'type': 'websocket', 'path': '/ws', 'headers': []}, AsyncMock(), AsyncMock())
    assert not await service.check_access(websocket, 'private')
    assert await service.check_access(websocket, 'public')
    assert not await service.check_access(websocket, 'unknown')
