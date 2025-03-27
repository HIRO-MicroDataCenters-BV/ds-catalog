from typing import Self

from ..entities import Dataset


class Query:
    def __init__(
        self,
        match: list[str] | None = None,
        optional_match: list[str] | None = None,
        where: list[str] | None = None,
        with_clause: str | None = None,
        return_clause: list[str] | None = None,
        order_by: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ):
        self.match = match if match else []
        self.optional_match = optional_match if optional_match else []
        self.where = where if where else []
        self.with_clause = with_clause
        self.return_clause = return_clause if return_clause else []
        self.order_by = order_by
        self.skip = skip
        self.limit = limit

    def join(self, query: Self) -> Self:
        self.match += query.match
        self.optional_match += query.optional_match
        self.where += query.where
        self.with_clause = query.with_clause
        self.return_clause += query.return_clause
        self.order_by = query.order_by
        self.skip = query.skip
        self.limit = query.limit
        return self

    def add_match(self, statement: str) -> Self:
        self.match += statement
        return self

    def add_optional_match(self, statement: str) -> Self:
        self.optional_match += statement
        return self

    def add_where(self, statement: str) -> Self:
        self.where += statement
        return self

    def add_return(self, statement: str) -> Self:
        self.return_clause += statement
        return self

    def build(self) -> str:
        query_parts = []
        if self.match:
            query_parts.append("MATCH " + ", ".join(self.match))
        if self.optional_match:
            query_parts.append("OPTIONAL MATCH " + ", ".join(self.optional_match))
        if self.where:
            query_parts.append("WHERE " + " AND ".join(self.where))
        if self.with_clause:
            query_parts.append(f"WITH {self.with_clause}")
        if self.return_clause:
            query_parts.append("RETURN " + ", ".join(self.return_clause))
        if self.order_by:
            query_parts.append(f"ORDER BY {self.order_by}")
        if self.skip:
            query_parts.append(f"SKIP {self.skip}")
        if self.limit:
            query_parts.append(f"LIMIT {self.limit}")
        return "\n".join(query_parts)


class FilterDatasetByID(Query):
    def __init__(self, id: str):
        super().__init__(where=[f'{Dataset.label}.dcterms__identifier="{id}"'])
