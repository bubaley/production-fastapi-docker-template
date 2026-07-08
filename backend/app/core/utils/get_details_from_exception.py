from typing import Any, TypeVar

from fastapi import HTTPException
from fastapi.exceptions import ValidationException
from pydantic import ValidationError

T = TypeVar('T')


def _get_validation_error_details(exc: ValidationError | ValidationException) -> dict[str, Any]:
    return {
        'type': type(exc).__name__,
        'errors': [
            {
                'location': '.'.join(str(part) for part in error.get('loc', [])),
                'attribute': error.get('loc', [])[-1],
                'message': error.get('msg'),
                'code': error.get('type'),
            }
            for error in exc.errors()
        ],
    }


def _get_http_error_details(exc: HTTPException) -> dict[str, Any]:
    return {'type': type(exc).__name__, 'content': exc.detail}


def _get_unhandled_error_details(exc: Exception) -> dict[str, Any]:
    return {
        'type': type(exc).__name__,
        'content': str(exc) or type(exc).__name__,
    }


def get_details_from_exception(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, ValidationError | ValidationException):
        return _get_validation_error_details(exc)

    if isinstance(exc, HTTPException):
        return _get_http_error_details(exc)

    return _get_unhandled_error_details(exc)
