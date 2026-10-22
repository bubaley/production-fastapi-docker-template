from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core import health
from app.core.settings import settings
from app.main import app

client = TestClient(app)


def test_health_returns_version(monkeypatch):
    monkeypatch.setattr(settings, 'app_version', '1.2.3')
    monkeypatch.setattr(settings, 'git_sha', 'abc123')
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'version': '1.2.3', 'sha': 'abc123'}


def test_health_endpoints_are_not_in_openapi():
    paths = client.get('/openapi.json').json()['paths']
    assert '/health' not in paths
    assert '/ready' not in paths


@pytest.mark.parametrize(
    'database, redis, status_code',
    [(True, True, 200), (False, True, 503), (True, False, 503)],
)
def test_ready_reports_each_dependency(monkeypatch, database, redis, status_code):
    monkeypatch.setattr(health, '_check_database', AsyncMock(return_value=database))
    monkeypatch.setattr(health, 'ping_redis', AsyncMock(return_value=redis))
    response = client.get('/ready')
    assert response.status_code == status_code
    assert response.json() == {
        'status': 'ok' if status_code == 200 else 'error',
        'checks': {'database': 'ok' if database else 'error', 'redis': 'ok' if redis else 'error'},
    }


@pytest.mark.asyncio
async def test_ready_checks_the_real_database(api_client, monkeypatch):
    monkeypatch.setattr(health, 'ping_redis', AsyncMock(return_value=True))
    response = await api_client.get('/ready')
    assert response.status_code == 200
    assert response.json()['checks']['database'] == 'ok'


def test_request_id_is_generated_or_propagated():
    generated = client.get('/health').headers['X-Request-ID']
    assert len(generated) == 32
    assert client.get('/health', headers={'X-Request-ID': 'trace-1234abcd'}).headers['X-Request-ID'] == 'trace-1234abcd'
    # Unsafe values (header injection, oversized) are replaced.
    replaced = client.get('/health', headers={'X-Request-ID': 'bad id with spaces'}).headers['X-Request-ID']
    assert replaced != 'bad id with spaces'
    assert len(replaced) == 32
