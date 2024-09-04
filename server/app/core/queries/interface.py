from typing import Any

from abc import ABC, abstractmethod


class IQuery(ABC):
    """Interface for implementing repository queries"""

    @abstractmethod
    def build(self) -> dict[str, Any]:
        ...

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.build()})"
