import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, model_validator
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.core.exceptions import AppException, register_exceptions_handlers
from app.core.schemas import ErrorCode
from app.main import app


class _Payload(BaseModel):
    value: int = 0

    @model_validator(mode='after')
    def reject(self):
        raise ValueError('model-level error')


def _build_app() -> FastAPI:
    test_app = FastAPI()
    register_exceptions_handlers(test_app)

    @test_app.get('/http/{status_code}')
    async def http_error(status_code: int):
        raise HTTPException(status_code=status_code, detail='Custom detail', headers={'X-Test': 'yes'})

    @test_app.get('/http-structured')
    async def http_structured():
        raise HTTPException(status_code=400, detail={'field': 'invalid'})

    @test_app.get('/query')
    async def query(number: int):
        return number

    @test_app.get('/pydantic')
    async def pydantic_error():
        _Payload.model_validate({})

    @test_app.get('/does-not-exist')
    async def does_not_exist():
        raise DoesNotExist('Organization')

    @test_app.get('/integrity')
    async def integrity():
        raise IntegrityError('duplicate key value violates unique constraint "user_email_key"')

    @test_app.get('/app')
    async def app_error():
        raise AppException.from_attrs(ErrorCode.FORBIDDEN, 'No access')

    @test_app.get('/boom')
    async def boom():
        raise RuntimeError('database password is hunter2')

    return test_app


client = TestClient(_build_app(), raise_server_exceptions=False)


def _error(response) -> dict:
    body = response.json()
    assert set(body) == {'data', 'error', 'success'}
    assert body['success'] is False
    assert body['data'] is None
    return body['error']


@pytest.mark.parametrize(
    'status_code, code',
    [
        (400, ErrorCode.VALIDATION_ERROR),
        (401, ErrorCode.UNAUTHORIZED),
        (403, ErrorCode.FORBIDDEN),
        (404, ErrorCode.NOT_FOUND),
        (409, ErrorCode.CONFLICT),
        (418, ErrorCode.APP_ERROR),
        (503, ErrorCode.UNHANDLED_ERROR),
    ],
)
def test_http_exception_status_maps_to_error_code(status_code, code):
    response = client.get(f'/http/{status_code}')
    assert response.status_code == status_code
    assert response.headers['X-Test'] == 'yes'
    error = _error(response)
    assert error['code'] == code
    assert error['message'] == 'Custom detail'


def test_structured_http_detail_goes_to_details():
    error = _error(client.get('/http-structured'))
    assert error['message'] == 'Bad Request'
    assert error['details']['content'] == {'field': 'invalid'}


def test_request_validation_error():
    response = client.get('/query', params={'number': 'abc'})
    assert response.status_code == 422
    error = _error(response)
    assert error['code'] == ErrorCode.VALIDATION_ERROR
    assert error['details']['errors'][0]['location'] == 'query.number'
    assert error['details']['errors'][0]['attribute'] == 'number'


def test_pydantic_error_with_empty_location():
    response = client.get('/pydantic')
    assert response.status_code == 422
    error = _error(response)
    assert error['code'] == ErrorCode.VALIDATION_ERROR
    assert error['details']['errors'][0]['location'] == ''
    assert error['details']['errors'][0]['attribute'] is None


def test_tortoise_errors_are_mapped_without_database_text():
    response = client.get('/does-not-exist')
    assert response.status_code == 404
    assert _error(response)['code'] == ErrorCode.NOT_FOUND
    response = client.get('/integrity')
    assert response.status_code == 409
    error = _error(response)
    assert error['code'] == ErrorCode.CONFLICT
    assert 'user_email_key' not in response.text


def test_app_exception_keeps_its_code():
    response = client.get('/app')
    assert response.status_code == 403
    assert _error(response) == {'code': ErrorCode.FORBIDDEN, 'message': 'No access', 'details': {}}


def test_unhandled_error_hides_exception_text():
    response = client.get('/boom')
    assert response.status_code == 500
    assert _error(response) == {'code': ErrorCode.UNHANDLED_ERROR, 'message': 'Internal server error', 'details': {}}
    assert 'hunter2' not in response.text


@pytest.mark.parametrize(
    'method, path, status_code, code',
    [
        ('get', '/api/v1/auth/me', 401, ErrorCode.UNAUTHORIZED),
        ('get', '/does-not-exist', 404, ErrorCode.NOT_FOUND),
        ('delete', '/health', 405, ErrorCode.APP_ERROR),
        ('post', '/api/v1/auth/login', 422, ErrorCode.VALIDATION_ERROR),
    ],
)
def test_application_uses_the_envelope(method, path, status_code, code):
    response = getattr(TestClient(app), method)(path)
    assert response.status_code == status_code
    assert _error(response)['code'] == code
