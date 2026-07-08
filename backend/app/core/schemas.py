from enum import StrEnum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

from app.core.utils.get_details_from_exception import get_details_from_exception

T = TypeVar('T')


class ErrorCode(StrEnum):
    APP_ERROR = 'APP_ERROR'
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    NOT_FOUND = 'NOT_FOUND'
    UNAUTHORIZED = 'UNAUTHORIZED'
    FORBIDDEN = 'FORBIDDEN'
    UNHANDLED_ERROR = 'UNHANDLED_ERROR'
    INTEGRATION_ERROR = 'INTEGRATION_ERROR'


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


class ResultData(BaseModel, Generic[T]):
    data: T | None = None
    error: ErrorData | None = None

    @computed_field
    @property
    def success(self) -> bool:
        return self.error is None
