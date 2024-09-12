from typing import Generic, TypeVar

from abc import ABC, abstractmethod

from sqlalchemy import Select

T = TypeVar("T")


class IQuery(Generic[T], ABC):
    """Interface for implementing repository queries"""

    @abstractmethod
    def apply(self, query: Select[tuple[T]]) -> Select[tuple[T]]:
        ...
