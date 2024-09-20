from abc import ABC, abstractmethod

from neomodel import AsyncNodeSet


class IQuery(ABC):
    """Interface for implementing repository queries"""

    @abstractmethod
    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        ...
