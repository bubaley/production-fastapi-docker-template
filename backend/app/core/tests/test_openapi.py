import json
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
from fastapi import APIRouter, FastAPI
from fastapi_ronin.decorators import viewset
from typer.testing import CliRunner

from app.core.auth import PUBLIC_PATHS
from app.core.openapi import ERROR_STATUSES, OPERATION_ID_PATTERN, SECURITY_SCHEMES, generate_operation_id
from app.core.viewsets import BaseReadOnlyViewSet
from app.domains.organization.models import OrganizationUser
from app.domains.organization.schemas import OrganizationUserReadSchema
from app.domains.organization.views import OrganizationUserViewSet, OrganizationViewSet
from app.main import app

FRONTEND_SCHEMA = Path(__file__).resolve().parents[4] / 'frontend' / 'openapi.json'
HTTP_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}


@pytest.fixture(scope='module')
def schema() -> dict[str, Any]:
    app.openapi_schema = None
    with warnings.catch_warnings():
        warnings.simplefilter('error')  # e.g. FastAPI's "Duplicate Operation ID"
        return app.openapi()


def _operations(schema: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    return [
        (path, method, operation)
        for path, path_item in schema['paths'].items()
        for method, operation in path_item.items()
        if method in HTTP_METHODS
    ]


def test_operation_ids_are_unique_and_follow_the_convention(schema):
    operations = _operations(schema)
    assert operations
    ids = [operation.get('operationId') for _, _, operation in operations]
    assert [op_id for op_id, count in Counter(ids).items() if count > 1] == []
    for path, method, operation in operations:
        assert operation.get('tags'), f'{method.upper()} {path} has no tag'
        assert OPERATION_ID_PATTERN.match(operation['operationId']), operation['operationId']
        tag = operation['tags'][0].replace('-', '_')
        assert operation['operationId'].startswith(f'{tag}_')


def test_crud_and_auth_operation_ids(schema):
    ids = {(method, path): operation['operationId'] for path, method, operation in _operations(schema)}
    assert ids[('get', '/api/v1/organizations')] == 'organizations_list'
    assert ids[('get', '/api/v1/organizations/{item_id}')] == 'organizations_retrieve'
    assert ids[('put', '/api/v1/organizations/{item_id}')] == 'organizations_update'
    assert ids[('patch', '/api/v1/organizations/{item_id}')] == 'organizations_partial_update'
    assert ids[('delete', '/api/v1/organizations/{item_id}')] == 'organizations_destroy'
    assert ids[('post', '/api/v1/organization-users')] == 'organization_users_create'
    assert ids[('post', '/api/v1/auth/login')] == 'auth_login'
    assert ids[('post', '/api/v1/auth/logout-all')] == 'auth_logout_all'


def test_every_operation_documents_the_error_envelope(schema):
    for path, method, operation in _operations(schema):
        for status in ERROR_STATUSES:
            response = operation['responses'].get(str(status))
            assert response, f'{method.upper()} {path} lacks {status}'
            assert response['content']['application/json']['schema'] == {'$ref': '#/components/schemas/ErrorResponse'}
        assert any(code.startswith('2') for code in operation['responses'])
    assert 'HTTPValidationError' not in schema['components']['schemas']
    error = schema['components']['schemas']['ErrorResponse']
    assert set(error['required']) >= {'error', 'success'}


def test_security_schemes_and_public_operations(schema):
    assert schema['components']['securitySchemes'] == SECURITY_SCHEMES
    for path, _method, operation in _operations(schema):
        if path in PUBLIC_PATHS:
            assert operation['security'] == []
        else:
            assert {name for requirement in operation['security'] for name in requirement} == set(SECURITY_SCHEMES)


def test_generic_component_names_are_readable(schema):
    assert 'OrganizationReadSchemaPage' in schema['components']['schemas']
    assert not [name for name in schema['components']['schemas'] if name.endswith('_')]


def test_organization_header_is_declared_only_where_used():
    assert not OrganizationViewSet.uses_organization_header()
    assert not OrganizationUserViewSet.uses_organization_header()

    router = APIRouter(prefix='/scoped', tags=['scoped'])

    @viewset(router)
    class ScopedViewSet(BaseReadOnlyViewSet[OrganizationUser]):
        # Without the opt-out, a model with an `organization` FK takes it from the header on create.
        model = OrganizationUser
        read_schema = OrganizationUserReadSchema

    test_app = FastAPI(generate_unique_id_function=generate_operation_id)
    test_app.include_router(router)
    operation = test_app.openapi()['paths']['/scoped']['get']
    header = next(param for param in operation['parameters'] if param['in'] == 'header')
    assert header['name'] == 'Organization-Key'
    assert header['required'] is False


def test_manage_openapi_dumps_the_schema(tmp_path, schema):
    from manage import app as cli

    output = tmp_path / 'openapi.json'
    result = CliRunner().invoke(cli, ['openapi', '--output', str(output)])
    assert result.exit_code == 0, result.output
    assert json.loads(output.read_text()) == schema


@pytest.mark.skipif(not FRONTEND_SCHEMA.exists(), reason='frontend checkout not available')
def test_committed_frontend_schema_is_current(schema):
    committed = json.loads(FRONTEND_SCHEMA.read_text())
    committed['info'].pop('version', None)
    current = {**schema, 'info': {k: v for k, v in schema['info'].items() if k != 'version'}}
    assert committed == current, 'frontend/openapi.json is stale: run `make openapi`'
