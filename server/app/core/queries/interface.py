from typing import Generic, TypeVar

from abc import ABC, abstractmethod

T = TypeVar("T")


class IQuery(Generic[T], ABC):
    """Interface for implementing repository queries"""

    @abstractmethod
    def apply(self, query: T) -> T:
        ...
