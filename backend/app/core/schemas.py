from enum import StrEnum
from typing import Any, TypeVar

from pydantic import BaseModel, Field, computed_field

from app.core.utils.get_details_from_exception import get_details_from_exception

T = TypeVar('T')


class ErrorCode(StrEnum):
    APP_ERROR = 'APP_ERROR'
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    NOT_FOUND = 'NOT_FOUND'
    UNAUTHORIZED = 'UNAUTHORIZED'
    FORBIDDEN = 'FORBIDDEN'
    CONFLICT = 'CONFLICT'
    RATE_LIMITED = 'RATE_LIMITED'
    UNHANDLED_ERROR = 'UNHANDLED_ERROR'


class ErrorData(BaseModel):
    code: ErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_exception(cls, code: ErrorCode, message: str, exception: Exception):
        return cls(
            code=code,
            message=message,
            details=get_details_from_exception(exception),
        )


class ResultData[T](BaseModel):
    data: T | None = None
    error: ErrorData | None = None

    @computed_field
    @property
    def success(self) -> bool:
        return self.error is None


class ErrorResponse(BaseModel):
    """The error envelope every non-2xx response uses (`ResultData` with an error); documented on every operation."""

    data: None = None
    error: ErrorData

    @computed_field
    @property
    def success(self) -> bool:
        return False
