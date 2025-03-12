from neomodel import AsyncNodeSet

from .interface import IQuery


class CompositeQuery(IQuery):
    def __init__(self, *queries: IQuery) -> None:
        self._queries = queries

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        for q in self._queries:
            query = q.apply(query)
        return query
