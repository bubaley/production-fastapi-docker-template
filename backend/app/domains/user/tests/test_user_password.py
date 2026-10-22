import threading
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from app.core.settings import settings
from app.domains.auth.services.auth_service import AuthService
from app.domains.auth.services.password_service import PasswordService
from app.domains.user.models import User

# Hash produced by the pre-PASSWORD_PEPPER code: bcrypt(HMAC(f'{id}{SECRET_KEY}', password)).
LEGACY_USER_ID = UUID('5f0c6b8e-2f4e-4c1a-9d3b-8a7e6f5d4c3b')
LEGACY_SECRET_KEY = 'legacy-jose-compat-secret-key-' + 'x' * 40
LEGACY_PASSWORD = 'legacy-password'
LEGACY_HASH = '$2b$04$hVLSkcjlXj8X0ZnLdtk4BeUtqCFMQQ6A57v2/8J4dkToq9bNNacF2'


async def _create_legacy_user(monkeypatch) -> User:
    monkeypatch.setattr(settings, 'secret_key', LEGACY_SECRET_KEY)
    return await User.create(
        id=LEGACY_USER_ID, email='Legacy@Example.test', first_name='L', last_name='U', password=LEGACY_HASH
    )


@pytest.mark.asyncio
async def test_new_hash_does_not_depend_on_secret_key(db, user_factory, monkeypatch):
    user = await user_factory()
    stored = user.password
    monkeypatch.setattr(settings, 'secret_key', 'rotated-' + 'y' * 60)
    assert await user.verify_password_async('test-password')
    assert not await user.verify_password_async('wrong-password')
    assert (await User.get(id=user.id)).password == stored


@pytest.mark.asyncio
async def test_password_pepper_is_applied(db, monkeypatch):
    monkeypatch.setattr(settings, 'password_pepper', 'pepper-one')
    user = User(email='pepper@example.test', first_name='P', last_name='U')
    await user.set_password_async('secret')
    assert PasswordService.verify_password('secret', user.password, 'pepper-one')
    assert not PasswordService.verify_password('secret', user.password, '')
    monkeypatch.setattr(settings, 'password_pepper', 'pepper-two')
    assert not await user.verify_password_async('secret')


@pytest.mark.asyncio
async def test_legacy_hash_verifies_and_is_upgraded_on_login(api_client, monkeypatch):
    user = await _create_legacy_user(monkeypatch)
    response = await api_client.post('/api/v1/auth/login', json={'email': user.email, 'password': LEGACY_PASSWORD})
    assert response.status_code == 200
    upgraded = (await User.get(id=user.id)).password
    assert upgraded != LEGACY_HASH
    assert PasswordService.match_pepper(LEGACY_PASSWORD, upgraded, User._password_peppers(user.id)) == 0
    # Once upgraded, the hash no longer depends on SECRET_KEY.
    monkeypatch.setattr(settings, 'secret_key', 'rotated-' + 'y' * 60)
    response = await api_client.post('/api/v1/auth/login', json={'email': user.email, 'password': LEGACY_PASSWORD})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_legacy_hash_is_kept_when_password_is_wrong(api_client, monkeypatch):
    user = await _create_legacy_user(monkeypatch)
    response = await api_client.post('/api/v1/auth/login', json={'email': user.email, 'password': 'wrong'})
    assert response.status_code == 401
    assert (await User.get(id=user.id)).password == LEGACY_HASH


@pytest.mark.asyncio
async def test_unknown_email_runs_dummy_password_check(api_client, monkeypatch):
    dummy = AsyncMock()
    monkeypatch.setattr(PasswordService, 'verify_dummy_password', dummy)
    response = await api_client.post('/api/v1/auth/login', json={'email': 'nobody@example.test', 'password': 'x'})
    assert response.status_code == 401
    dummy.assert_awaited_once()
    assert dummy.await_args is not None
    assert len(dummy.await_args.args[1]) == len(User._password_peppers(LEGACY_USER_ID))


@pytest.mark.asyncio
async def test_bcrypt_runs_outside_event_loop_thread(db, monkeypatch):
    threads: list[int] = []
    original = PasswordService.hash_password

    def spy(password: str, pepper: str) -> str:
        threads.append(threading.get_ident())
        return original(password, pepper)

    monkeypatch.setattr(PasswordService, 'hash_password', spy)
    await User(email='t@example.test', first_name='T', last_name='U').set_password_async('secret')
    assert threads
    assert threads[0] != threading.get_ident()


@pytest.mark.asyncio
async def test_emails_are_normalized(api_client, user_factory):
    admin = await user_factory(is_superuser=True)
    headers = {'Authorization': f'Bearer {(await AuthService.start_session(admin)).access.token}'}
    response = await api_client.post(
        '/api/v1/users',
        headers=headers,
        json={'email': ' New.User@Example.TEST ', 'first_name': 'N', 'last_name': 'U', 'password': 'new-password'},
    )
    assert response.status_code == 201
    assert response.json()['email'] == 'new.user@example.test'
    login = await api_client.post(
        '/api/v1/auth/login', json={'email': 'NEW.USER@example.test', 'password': 'new-password'}
    )
    assert login.status_code == 200
    response = await api_client.patch(
        f'/api/v1/users/{response.json()["id"]}', headers=headers, json={'email': 'Renamed@Example.TEST'}
    )
    assert response.status_code == 200
    assert response.json()['email'] == 'renamed@example.test'
