from collections.abc import Mapping
from http import HTTPStatus
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from loguru import logger
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.core.schemas import ErrorCode, ErrorData, ResultData
from app.core.utils.get_details_from_exception import get_details_from_exception

STATUS_ERROR_CODES: dict[int, ErrorCode] = {
    400: ErrorCode.VALIDATION_ERROR,
    401: ErrorCode.UNAUTHORIZED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    409: ErrorCode.CONFLICT,
    422: ErrorCode.VALIDATION_ERROR,
    429: ErrorCode.RATE_LIMITED,
}

ERROR_CODE_STATUSES: dict[ErrorCode, int] = {
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.UNHANDLED_ERROR: 500,
}


def error_code_for_status(status_code: int) -> ErrorCode:
    if status_code >= 500:
        return ErrorCode.UNHANDLED_ERROR
    return STATUS_ERROR_CODES.get(status_code, ErrorCode.APP_ERROR)


class AppException(Exception):
    def __init__(self, error_data: ErrorData, status_code: int | None = None, headers: Mapping[str, str] | None = None):
        super().__init__(error_data.message)
        self.error_data = error_data
        self.status_code = status_code or ERROR_CODE_STATUSES.get(error_data.code, 400)
        self.headers = headers

    @classmethod
    def from_attrs(
        cls,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> AppException:
        return cls(error_data=ErrorData(code=code, message=message, details=details or {}), headers=headers)

    @classmethod
    def from_exception(cls, code: ErrorCode, message: str, exception: Exception) -> AppException:
        return cls(error_data=ErrorData.from_exception(code=code, message=message, exception=exception))


def _error_response(status_code: int, error: ErrorData, headers: Mapping[str, str] | None = None) -> JSONResponse:
    content = ResultData(error=error).model_dump(mode='json')
    return JSONResponse(status_code=status_code, content=content, headers=headers)


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    app_exc = cast(AppException, exc)
    return _error_response(app_exc.status_code, app_exc.error_data, headers=app_exc.headers)


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    http_exc = cast(StarletteHTTPException, exc)
    status_code = http_exc.status_code
    message = http_exc.detail if isinstance(http_exc.detail, str) else HTTPStatus(status_code).phrase
    error = ErrorData(
        code=error_code_for_status(status_code), message=message, details=get_details_from_exception(http_exc)
    )
    return _error_response(status_code, error, headers=http_exc.headers)


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error = ErrorData.from_exception(code=ErrorCode.VALIDATION_ERROR, message='Validation error', exception=exc)
    return _error_response(422, error)


async def does_not_exist_handler(request: Request, exc: Exception) -> JSONResponse:
    return _error_response(404, ErrorData(code=ErrorCode.NOT_FOUND, message='Not found'))


async def integrity_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # The database message names constraints and values; keep it in logs only.
    logger.opt(exception=exc).warning('Integrity error on {} {}', request.method, request.url.path)
    return _error_response(409, ErrorData(code=ErrorCode.CONFLICT, message='Conflict with existing data'))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.opt(exception=exc).error('Unhandled error on {} {}', request.method, request.url.path)
    return _error_response(500, ErrorData(code=ErrorCode.UNHANDLED_ERROR, message='Internal server error'))


def register_exceptions_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(DoesNotExist, does_not_exist_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
