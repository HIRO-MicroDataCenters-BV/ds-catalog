from typing import TypedDict

from dataclasses import dataclass, fields
from datetime import date

from neomodel import AsyncNodeSet

from .interface import IQuery


@dataclass
class DatasetsFilterByIdQuery(IQuery):
    id: str

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        return query.filter(identifier=self.id)


@dataclass
class DatasetsSearchQuery(IQuery):
    term: str

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        return query.filter(title__icontains=self.term)


@dataclass
class DatasetsThemeQuery(IQuery):
    theme: list[str]

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        return query.filter(theme__in=self.theme)


@dataclass
class DatasetsIsLocalQuery(IQuery):
    is_local: bool

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        return query.filter(is_local=self.is_local)


@dataclass
class DatasetsIsSharedQuery(IQuery):
    is_shared: bool

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        return query.filter(is_shared=self.is_shared)


@dataclass
class DatasetsIssuedQuery(IQuery):
    issued: date | None

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        return query.filter(issued=self.issued)


@dataclass
class DatasetsIssuedGteQuery(IQuery):
    issued: date | None

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        return query.filter(issued__gte=self.issued)


@dataclass
class DatasetsIssuedLteQuery(IQuery):
    issued: date | None

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        return query.filter(issued__lte=self.issued)


class DatasetsFilterDTO(TypedDict):
    search: str
    theme: list[str] | None
    is_local: bool | None
    is_shared: bool | None
    issued: date | None
    issued_gte: date | None
    issued_lte: date | None


@dataclass
class DatasetsFilterQuery(IQuery):
    search: str
    theme: list[str] | None
    is_local: bool | None
    is_shared: bool | None
    issued: date | None
    issued_gte: date | None
    issued_lte: date | None

    query_map = {
        "search": DatasetsSearchQuery,
        "theme": DatasetsThemeQuery,
        "is_local": DatasetsIsLocalQuery,
        "is_shared": DatasetsIsSharedQuery,
        "issued": DatasetsIssuedQuery,
        "issued_gte": DatasetsIssuedGteQuery,
        "issued_lte": DatasetsIssuedLteQuery,
    }

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                query_class = self.query_map.get(field.name)
                if query_class:
                    query = query_class(value).apply(query)
        return query
