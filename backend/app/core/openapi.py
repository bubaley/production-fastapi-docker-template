"""
OpenAPI conventions; `frontend/openapi.json` (`make openapi`) is generated from this schema.

- operationId: `<tag>_<route name>` (`organizations_list`, `auth_login`) — short and stable for generated clients
- every API operation documents the error envelope (`ErrorResponse`) for the common error statuses
- security schemes: session cookie, `Authorization: Token`, `Authorization: Bearer`; public auth routes have none
"""

import copy
import json
import re
from collections.abc import Callable, Collection
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

from app.core.schemas import ErrorResponse
from app.domains.auth.transport import ACCESS_COOKIE

ERROR_STATUSES = (400, 401, 403, 404, 409, 422, 429, 500)

# Router-level `responses=`: FastAPI adds them to every operation of the router (and drops its default 422 schema).
ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    status: {'model': ErrorResponse, 'description': HTTPStatus(status).phrase} for status in ERROR_STATUSES
}

SECURITY_SCHEMES: dict[str, dict[str, Any]] = {
    'cookieAuth': {
        'type': 'apiKey',
        'in': 'cookie',
        'name': ACCESS_COOKIE,
        'description': (
            'HttpOnly session cookie set by `POST /api/v1/auth/login`. Unsafe methods also need a trusted '
            '`Origin` (or `Referer`).'
        ),
    },
    'tokenAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'API token for integrations: `Authorization: Token <value>`.',
    },
    'bearerAuth': {
        'type': 'http',
        'scheme': 'bearer',
        'bearerFormat': 'JWT',
        'description': 'Access JWT minted server-side (tests, scripts). Browsers use the cookie.',
    },
}
SECURITY_REQUIREMENT: list[dict[str, list[str]]] = [{name: []} for name in SECURITY_SCHEMES]

COMPONENT_REF = '#/components/schemas/'
OPERATION_ID_PATTERN = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)+$')


def _snake(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')


def generate_operation_id(route: APIRoute) -> str:
    """`<first tag>_<route name>`; ronin names CRUD routes `list`/`retrieve`/`create`/`update`/... and actions by method."""
    tag = route.tags[0] if route.tags else route.path_format.strip('/').split('/')[-1]
    tag = tag.value if hasattr(tag, 'value') else tag
    return f'{_snake(str(tag))}_{_snake(route.name)}'


def split_put_patch_routes(router: Any, generate_id: Callable[[APIRoute], str]) -> None:
    """
    TEMPORARY workaround for fastapi-ronin <= 1.0.1, which registers PUT and PATCH as one route: both operations
    get the same operationId and generated clients drop one. Splits such routes into `update` (PUT) and
    `partial_update` (PATCH, same body schema as PUT) in `router` and every router included into it. Delete this
    function once the fixed ronin is released (branch `fix/split-put-patch-operations`); it is a no-op then.
    """
    result: list[BaseRoute] = []
    changed = False
    for route in router.routes:
        result.append(route)
        # FastAPI includes routers lazily: the effective routes are rebuilt from the original router's routes.
        if (included := getattr(route, 'original_router', None)) is not None:
            split_put_patch_routes(included, generate_id)
            continue
        if not isinstance(route, APIRoute) or not route.methods or not {'PUT', 'PATCH'} <= route.methods:
            continue
        patch_route = copy.copy(route)
        route.methods = route.methods - {'PATCH'}
        patch_route.methods = {'PATCH'}
        patch_route.name = 'partial_update' if route.name == 'update' else f'{route.name}_partial'
        patch_route.unique_id = generate_id(patch_route)
        result.append(patch_route)
        changed = True
    if changed:
        router.routes[:] = result
        if mark_changed := getattr(router, '_mark_routes_changed', None):
            mark_changed()


def _add_security(schema: dict[str, Any], public_paths: Collection[str]) -> None:
    schema.setdefault('components', {})['securitySchemes'] = SECURITY_SCHEMES
    for path, path_item in schema.get('paths', {}).items():
        for operation in path_item.values():
            operation['security'] = [] if path.rstrip('/') in public_paths else SECURITY_REQUIREMENT


def _rewrite_refs(node: Any, renames: dict[str, str]) -> None:
    if isinstance(node, dict):
        ref = node.get('$ref')
        if isinstance(ref, str) and ref.startswith(COMPONENT_REF):
            node['$ref'] = COMPONENT_REF + renames.get(ref.removeprefix(COMPONENT_REF), ref.removeprefix(COMPONENT_REF))
        for value in node.values():
            _rewrite_refs(value, renames)
    elif isinstance(node, list):
        for value in node:
            _rewrite_refs(value, renames)


def _rename_generic_components(schema: dict[str, Any]) -> None:
    """
    Pydantic names parametrized generics `PageResponse_UserReadSchema_LightPageNumberPagination_`; use the model
    title instead (`UserReadSchemaPage`, see `PageResponse.model_parametrized_name`) for readable client types.
    """
    components: dict[str, Any] = schema.get('components', {}).get('schemas', {})
    renames = {
        key: value['title']
        for key, value in components.items()
        if key.endswith('_') and str(value.get('title', '')).isidentifier() and value['title'] not in components
    }
    if len(set(renames.values())) != len(renames):
        return
    schema['components']['schemas'] = {renames.get(key, key): value for key, value in components.items()}
    _rewrite_refs(schema, renames)


def install_openapi(app: FastAPI, public_paths: Collection[str]) -> None:
    """Post-process the generated schema: readable generic names, security schemes and requirements."""
    build = app.openapi

    def openapi() -> dict[str, Any]:
        if app.openapi_schema is None:
            schema = build()
            _rename_generic_components(schema)
            _add_security(schema, public_paths)
        assert app.openapi_schema is not None
        return app.openapi_schema

    setattr(app, 'openapi', openapi)  # noqa: B010 - FastAPI's documented override point


def render_openapi(app: FastAPI) -> str:
    """The schema as committed in `frontend/openapi.json`: stable key order, trailing newline."""
    return json.dumps(app.openapi(), indent=2, ensure_ascii=False) + '\n'
