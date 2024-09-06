from .interface import IQuery, QueryResult


class CompositeQuery(IQuery):
    def __init__(self, *queries: IQuery) -> None:
        self._queries = queries

    def build(self) -> QueryResult:
        result = QueryResult()
        for query in self._queries:
            result += query.build()
        return result
