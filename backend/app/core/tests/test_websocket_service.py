import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi import APIRouter, FastAPI, WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.services import websocket_service as websocket_module
from app.core.services.pubsub import InMemoryPubSub
from app.core.services.websocket_service import (
    CLOSE_TOO_BIG,
    CLOSE_TRY_AGAIN,
    CLOSE_UNAUTHORIZED,
    BaseWebSocketService,
    ChannelConfig,
    encode_message,
)
from app.core.settings import settings
from app.core.utils.date_utils import utcnow
from app.domains.auth.services.auth_service import Authentication, AuthMethod
from app.domains.user.models import User


class FakeWebSocket:
    def __init__(self, *, stall: bool = False, fail: bool = False):
        self.sent: list[str] = []
        self.closed_with: int | None = None
        self.scope: dict[str, Any] = {'type': 'websocket', 'headers': [], 'state': {}}
        self._stall = stall
        self._fail = fail

    async def send_text(self, text: str) -> None:
        if self._fail:
            raise RuntimeError('connection lost')
        if self._stall:
            await asyncio.Event().wait()
        self.sent.append(text)

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        self.closed_with = code


@pytest.fixture
def pubsub(monkeypatch) -> InMemoryPubSub:
    instance = InMemoryPubSub()
    monkeypatch.setattr(websocket_module, 'get_pubsub', lambda: instance)
    return instance


def _service(pubsub: InMemoryPubSub, *, is_detail: bool = False) -> BaseWebSocketService:
    service = BaseWebSocketService([ChannelConfig('feed', is_detail=is_detail, secure=False)], name=f'test-{uuid4()}')
    pubsub.subscribe(service.topic, service.handle_fanout)
    return service


def _connect(service: BaseWebSocketService, websocket: FakeWebSocket, key: str = 'feed') -> None:
    service.connections[key][str(id(websocket))] = websocket  # ty: ignore[invalid-assignment]


def test_messages_encode_uuid_and_datetime():
    item_id = UUID('5f0c6b8e-2f4e-4c1a-9d3b-8a7e6f5d4c3b')
    text = encode_message('item.updated', {'id': item_id, 'at': datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)})
    assert json.loads(text) == {
        'type': 'item.updated',
        'data': {'id': str(item_id), 'at': '2026-01-02T03:04:05+00:00'},
    }


@pytest.mark.asyncio
async def test_send_message_goes_through_pubsub(pubsub, monkeypatch):
    service = _service(pubsub)
    published: list[tuple[str, str]] = []
    original = pubsub.publish

    async def spy(topic: str, message: str) -> None:
        published.append((topic, message))
        await original(topic, message)

    monkeypatch.setattr(pubsub, 'publish', spy)
    client = FakeWebSocket()
    _connect(service, client)
    await service.send_message('feed', 'ping', {'n': 1})
    assert [topic for topic, _ in published] == [service.topic]
    assert [json.loads(text) for text in client.sent] == [{'type': 'ping', 'data': {'n': 1}}]


@pytest.mark.asyncio
async def test_detail_channel_reaches_only_recipients(pubsub):
    service = _service(pubsub, is_detail=True)
    first, second = FakeWebSocket(), FakeWebSocket()
    _connect(service, first, 'feed/a')
    _connect(service, second, 'feed/b')
    await service.send_message('feed', 'ping', None, recipients=['a'])
    await service.send_message('feed', 'ping', None, recipients=[])
    assert len(first.sent) == 1
    assert second.sent == []


@pytest.mark.asyncio
async def test_slow_or_dead_clients_are_dropped_without_stalling_others(pubsub, monkeypatch):
    monkeypatch.setattr(settings, 'websocket_send_timeout_seconds', 0.05)
    service = _service(pubsub)
    fast, slow, dead = FakeWebSocket(), FakeWebSocket(stall=True), FakeWebSocket(fail=True)
    for client in (fast, slow, dead):
        _connect(service, client)
    await asyncio.wait_for(service.send_message('feed', 'ping', {}), timeout=1)
    assert len(fast.sent) == 1
    assert slow.closed_with == CLOSE_TRY_AGAIN
    assert dead.closed_with == CLOSE_TRY_AGAIN
    assert list(service.connections['feed'].values()) == [fast]


@pytest.mark.asyncio
async def test_falls_back_to_local_delivery_when_pubsub_is_down(pubsub, monkeypatch):
    service = _service(pubsub)

    async def broken(topic: str, message: str) -> None:
        raise ConnectionError('redis down')

    monkeypatch.setattr(pubsub, 'publish', broken)
    client = FakeWebSocket()
    _connect(service, client)
    await service.send_message('feed', 'ping', {})
    assert len(client.sent) == 1


@pytest.mark.asyncio
async def test_watchdog_closes_connection_when_token_expires(monkeypatch):
    service = BaseWebSocketService([ChannelConfig('feed')], name='watchdog')
    websocket = FakeWebSocket()
    websocket.scope['state']['ws_authentication'] = Authentication(
        user=User(id=uuid4()), method=AuthMethod.JWT, expires_at=utcnow() - timedelta(seconds=1)
    )

    async def expired(connection) -> None:
        return None

    monkeypatch.setattr(websocket_module, 'authenticate_connection', expired)
    await asyncio.wait_for(service._watch_access(websocket, 'feed', None), timeout=1)  # ty: ignore[invalid-argument-type]
    assert websocket.closed_with == CLOSE_UNAUTHORIZED


# Handshake-level behavior through a real ASGI websocket (no database involved).


class _ExpiringAccessService(BaseWebSocketService):
    """Grants access with a credential that expires shortly; revalidation finds it gone."""

    async def get_authentication(self, websocket: WebSocket, *, refresh: bool = False) -> Authentication | None:
        if refresh:
            return None
        authentication = Authentication(
            user=User(id=uuid4()), method=AuthMethod.JWT, expires_at=utcnow() + timedelta(milliseconds=200)
        )
        websocket.scope.setdefault('state', {})['ws_authentication'] = authentication
        return authentication

    async def check_access(self, websocket: WebSocket, channel: str, recipient_id: str | None = None) -> bool:
        return await self.get_authentication(websocket) is not None


def _client(service: BaseWebSocketService) -> TestClient:
    test_app = FastAPI()
    router = APIRouter(prefix='/ws')
    service.register_routes(router)
    test_app.include_router(router)
    BaseWebSocketService.registry.remove(service)
    return TestClient(test_app)


def test_handshake_rejects_foreign_origin():
    client = _client(BaseWebSocketService([ChannelConfig('public', secure=False)], name='origin'))
    with (
        pytest.raises(WebSocketDisconnect) as error,
        client.websocket_connect('/ws/public', headers={'origin': 'https://evil.example'}),
    ):
        pytest.fail('Foreign origin was accepted')
    assert error.value.code == 1008
    with client.websocket_connect('/ws/public', headers={'origin': settings.cors_origins[0]}):
        pass
    with client.websocket_connect('/ws/public', headers={'origin': 'http://testserver'}):
        pass


def test_oversized_message_closes_the_connection(monkeypatch):
    monkeypatch.setattr(settings, 'websocket_max_message_bytes', 16)
    client = _client(BaseWebSocketService([ChannelConfig('public', secure=False)], name='size'))
    with client.websocket_connect('/ws/public') as websocket:
        websocket.send_text(json.dumps({'type': 'x', 'data': 'y' * 64}))
        with pytest.raises(WebSocketDisconnect) as error:
            websocket.receive_text()
    assert error.value.code == CLOSE_TOO_BIG


def test_expired_credential_closes_with_4401():
    client = _client(_ExpiringAccessService([ChannelConfig('private')], name='expiring'))
    with client.websocket_connect('/ws/private') as websocket, pytest.raises(WebSocketDisconnect) as error:
        websocket.receive_text()
    assert error.value.code == CLOSE_UNAUTHORIZED
