"""
Domain auto-discovery: every package in `app/domains/` with an `__init__.py` is a domain.

- models: `app/domains/<name>/models.py` → Tortoise `MODELS` (`app/core/database.py`)
- routers: `app/domains/<name>/views.py` exports `routers` (a tuple/list) or a single `router` → `/api/v1`

Order is deterministic: the template's kernel domains first (`KERNEL_DOMAINS`, keeps the OpenAPI path order
stable), then every other domain alphabetically. A domain module that fails to import stops the app with
`DomainDiscoveryError` naming the module, instead of silently dropping its routes.
"""

import importlib
from pathlib import Path
from types import ModuleType

from fastapi import APIRouter

DOMAINS_PACKAGE = 'app.domains'
DOMAINS_DIR = Path(__file__).resolve().parent.parent / 'domains'

KERNEL_DOMAINS = ('auth', 'user', 'organization')

# Model modules outside `app/domains/` (none yet: `app.core.models` only holds abstract bases).
KERNEL_MODEL_MODULES: tuple[str, ...] = ()


class DomainDiscoveryError(RuntimeError):
    pass


def domain_names(path: Path = DOMAINS_DIR) -> list[str]:
    names = {p.name for p in path.iterdir() if p.is_dir() and (p / '__init__.py').is_file()}
    kernel = [name for name in KERNEL_DOMAINS if name in names]
    return kernel + sorted(names - set(kernel))


def discover_model_modules(package: str = DOMAINS_PACKAGE, path: Path = DOMAINS_DIR) -> list[str]:
    """Dotted paths of every domain `models.py`; Tortoise imports them."""
    domains = [f'{package}.{name}.models' for name in domain_names(path) if (path / name / 'models.py').is_file()]
    return [*KERNEL_MODEL_MODULES, *domains]


def _import(module_name: str) -> ModuleType:
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        raise DomainDiscoveryError(f'Cannot import {module_name}: {type(e).__name__}: {e}') from e


def _routers_of(module: ModuleType) -> list[APIRouter]:
    many = getattr(module, 'routers', None)
    one = getattr(module, 'router', None)
    if many is not None and one is not None:
        raise DomainDiscoveryError(f'{module.__name__} exports both `router` and `routers`; keep one')
    if many is None and one is None:
        raise DomainDiscoveryError(f'{module.__name__} exports neither `router` nor `routers`')
    routers = list(many) if many is not None else [one]
    for router in routers:
        if not isinstance(router, APIRouter):
            raise DomainDiscoveryError(f'{module.__name__} exports {router!r}, not an APIRouter')
    return routers


def discover_routers(package: str = DOMAINS_PACKAGE, path: Path = DOMAINS_DIR) -> list[APIRouter]:
    """Routers of every domain `views.py`, in domain order and then in the order the module lists them."""
    routers: list[APIRouter] = []
    for name in domain_names(path):
        if (path / name / 'views.py').is_file():
            routers.extend(_routers_of(_import(f'{package}.{name}.views')))
    return routers
