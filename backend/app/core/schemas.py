from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar('T')


class ErrorCode(StrEnum):
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    UNHANDLED_ERROR = 'UNHANDLED_ERROR'


class ErrorData(BaseModel):
    code: ErrorCode
    message: str
    details: list[dict] = Field(default_factory=list)


class ResultData(BaseModel, Generic[T]):
    data: T | None = None
    error: ErrorData | None = None

    @computed_field
    @property
    def success(self) -> bool:
        return self.error is None
