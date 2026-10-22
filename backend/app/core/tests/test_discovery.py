import json
import sys
from pathlib import Path

import pytest

from app.core.database import MODELS
from app.core.discovery import (
    DomainDiscoveryError,
    discover_model_modules,
    discover_routers,
    domain_names,
)
from app.domains.auth.views import auth_router
from app.domains.organization.views import organization_users_router, organizations_router
from app.domains.user.views import user_tokens_router, users_router
from app.main import app

FRONTEND_SCHEMA = Path(__file__).resolve().parents[4] / 'frontend' / 'openapi.json'


@pytest.fixture
def fake_domains(tmp_path, monkeypatch):
    """A throwaway `fakedomains` package; `add(name, views=...)` creates one domain in it."""
    package = tmp_path / 'fakedomains'
    package.mkdir()
    (package / '__init__.py').write_text('')
    monkeypatch.syspath_prepend(str(tmp_path))

    def add(name: str, *, views: str | None = None, models: bool = False) -> None:
        domain = package / name
        domain.mkdir()
        (domain / '__init__.py').write_text('')
        if models:
            (domain / 'models.py').write_text('')
        if views is not None:
            (domain / 'views.py').write_text(views)

    yield package, add
    for module in [name for name in sys.modules if name.startswith('fakedomains')]:
        del sys.modules[module]


def test_kernel_domains_come_first_then_alphabetical(fake_domains):
    package, add = fake_domains
    for name in ('zeta', 'organization', 'alpha', 'auth', 'user'):
        add(name)
    (package / 'not_a_domain').mkdir()  # no __init__.py

    assert domain_names(package) == ['auth', 'user', 'organization', 'alpha', 'zeta']


def test_registered_models_are_every_domain_models_module():
    assert MODELS == discover_model_modules()
    assert MODELS[:3] == ['app.domains.auth.models', 'app.domains.user.models', 'app.domains.organization.models']
    for module in MODELS:
        name = module.split('.')[2]
        assert (Path(__file__).resolve().parents[2] / 'domains' / name / 'models.py').is_file()


def test_domain_routers_are_discovered_in_a_stable_order():
    assert discover_routers()[:5] == [
        auth_router,
        users_router,
        user_tokens_router,
        organizations_router,
        organization_users_router,
    ]
    app.openapi_schema = None
    paths = set(app.openapi()['paths'])
    assert {'/api/v1/auth/login', '/api/v1/users', '/api/v1/user-tokens', '/api/v1/organizations'} <= paths


def test_single_router_export_and_models_without_views(fake_domains):
    package, add = fake_domains
    add('notes', models=True, views="from fastapi import APIRouter\nrouter = APIRouter(prefix='/notes')\n")
    add('ledger', models=True)

    assert discover_model_modules('fakedomains', package) == ['fakedomains.ledger.models', 'fakedomains.notes.models']
    assert [router.prefix for router in discover_routers('fakedomains', package)] == ['/notes']


@pytest.mark.parametrize(
    ('views', 'message'),
    [
        ('raise RuntimeError("boom")', 'Cannot import fakedomains.broken.views: RuntimeError: boom'),
        ('import missing_dependency_xyz', "No module named 'missing_dependency_xyz'"),
        ('value = 1', 'exports neither `router` nor `routers`'),
        (
            'from fastapi import APIRouter\nrouter = APIRouter()\nrouters = (router,)',
            'exports both `router` and `routers`',
        ),
        ('routers = ("not a router",)', 'not an APIRouter'),
    ],
)
def test_broken_domain_fails_loudly(fake_domains, views, message):
    package, add = fake_domains
    add('broken', views=views)

    with pytest.raises(DomainDiscoveryError, match=message.replace('(', r'\(').replace(')', r'\)')):
        discover_routers('fakedomains', package)


@pytest.mark.skipif(not FRONTEND_SCHEMA.exists(), reason='frontend checkout not available')
def test_committed_schema_keeps_the_path_order():
    app.openapi_schema = None
    assert list(json.loads(FRONTEND_SCHEMA.read_text())['paths']) == list(app.openapi()['paths'])
