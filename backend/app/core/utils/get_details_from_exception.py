from typing import Any

from fastapi.exceptions import ValidationException
from pydantic import ValidationError
from starlette.exceptions import HTTPException


def _get_validation_error_details(exc: ValidationError | ValidationException) -> dict[str, Any]:
    errors = []
    for error in exc.errors():
        loc = error.get('loc') or ()
        errors.append(
            {
                'location': '.'.join(str(part) for part in loc),
                'attribute': loc[-1] if loc else None,
                'message': error.get('msg'),
                'code': error.get('type'),
            }
        )
    return {'type': type(exc).__name__, 'errors': errors}


def _get_http_error_details(exc: HTTPException) -> dict[str, Any]:
    return {'type': type(exc).__name__, 'content': exc.detail}


def _get_unhandled_error_details(exc: Exception) -> dict[str, Any]:
    return {
        'type': type(exc).__name__,
        'content': str(exc) or type(exc).__name__,
    }


def get_details_from_exception(exc: Exception) -> dict[str, Any]:
    """Details for an error the caller chose to expose. Never pass unexpected exceptions: they include str(exc)."""
    if isinstance(exc, ValidationError | ValidationException):
        return _get_validation_error_details(exc)

    if isinstance(exc, HTTPException):
        return _get_http_error_details(exc)

    return _get_unhandled_error_details(exc)
