from typing import Generic, TypeVar

from pydantic import Field

from .base import BaseModel

T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    page: int = Field(gt=0, examples=[1])
    size: int = Field(gt=0, examples=[100])
    items: list[T]
