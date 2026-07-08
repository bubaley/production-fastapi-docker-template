from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse

from app.core.schemas import ErrorCode, ErrorData, ResultData

status_code_map = {
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.UNHANDLED_ERROR: 500,
}


class AppException(Exception):
    def __init__(self, error_data: ErrorData, status_code: int | None = None):
        super().__init__(error_data.message)
        self.error_data = error_data
        self.status_code = status_code or status_code_map.get(error_data.code, 400)

    @classmethod
    def from_attrs(cls, code: ErrorCode, message: str, details: dict[str, Any] | None = None) -> 'AppException':
        return cls(error_data=ErrorData(code=code, message=message, details=details or {}))

    @classmethod
    def from_exception(cls, code: ErrorCode, message: str, exception: Exception) -> 'AppException':
        return cls(error_data=ErrorData.from_exception(code=code, message=message, exception=exception))


class RollbackTransactionException(Exception):
    pass


def _format_http_exception_detail(detail: Any) -> str:
    if isinstance(detail, str):
        return detail

    return str(detail)


def _build_error_response(exc: Exception, *, status_code: int, code: ErrorCode, message: str) -> JSONResponse:
    error = ErrorData.from_exception(code=code, message=message, exception=exc)
    return JSONResponse(status_code=status_code, content=ResultData(error=error).model_dump(mode='json'))


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    http_exc = cast(HTTPException, exc)
    code = ErrorCode.VALIDATION_ERROR if http_exc.status_code < 500 else ErrorCode.UNHANDLED_ERROR

    return _build_error_response(
        http_exc, status_code=http_exc.status_code, code=code, message=_format_http_exception_detail(http_exc.detail)
    )


async def request_validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    validation_exc = cast(ValidationError, exc)

    return _build_error_response(
        validation_exc, status_code=422, code=ErrorCode.VALIDATION_ERROR, message='Validation error'
    )


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    app_exc = cast(AppException, exc)
    content = ResultData(error=app_exc.error_data).model_dump(mode='json')
    return JSONResponse(status_code=app_exc.status_code, content=content)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _build_error_response(exc, status_code=500, code=ErrorCode.UNHANDLED_ERROR, message='Internal server error')


def register_exceptions_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ValidationError, request_validation_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
