from typing import TypeVar

from sqlalchemy import Select

from .interface import IQuery

T = TypeVar("T")


class CompositeQuery(IQuery[T]):
    def __init__(self, *queries: IQuery[T]) -> None:
        self._queries = queries

    def apply(self, query: Select[tuple[T]]) -> Select[tuple[T]]:
        for q in self._queries:
            query = q.apply(query)
        return query
