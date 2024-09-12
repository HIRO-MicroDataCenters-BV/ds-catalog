from typing import Any, TypeAlias, TypedDict, Unpack

from datetime import date

from .interface import IQuery

DatasetsQuery: TypeAlias = Any


class DatasetsFilterDTO(TypedDict):
    search: str
    theme: list[str] | None
    is_local: bool | None
    is_shared: bool | None
    creator_id: str
    issued: date | None
    issued_gte: date | None
    issued_lte: date | None
    distribution_bytesize_gte: int | None
    distribution_bytesize_lte: int | None
    distribution_mimetype: str


class DatasetsFilterQuery(IQuery[DatasetsQuery]):
    def __init__(self, **kwargs: Unpack[DatasetsFilterDTO]) -> None:
        # TODO: Implement
        ...

    def apply(self, query: DatasetsQuery) -> DatasetsQuery:
        # TODO: Implement
        return query
