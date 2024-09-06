from typing import Any

from abc import ABC, abstractmethod


class QueryResult:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # TODO: Implement
        ...

    def __add__(self, other: "QueryResult") -> "QueryResult":
        # TODO: Implement
        return QueryResult()


class IQuery(ABC):
    """Interface for implementing repository queries"""

    @abstractmethod
    def build(self) -> QueryResult:
        ...

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.build()})"
