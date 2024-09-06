from typing import TypedDict, Unpack

from datetime import datetime
from uuid import UUID

from ..entities.catalog import Ontology
from .interface import IQuery, QueryResult


class CatalogItemsFiltersDTO(TypedDict):
    search: str
    ontology: Ontology | None
    is_local: bool | None
    is_shared: bool | None
    creator_id: UUID | None
    created: datetime | None
    created_gte: datetime | None
    created_lte: datetime | None
    data_product_id: str
    data_product_size_gte: int | None
    data_product_size_lte: int | None
    data_product_mimetype: str


class CatalogItemsFilterQuery(IQuery):
    def __init__(self, **kwargs: Unpack[CatalogItemsFiltersDTO]) -> None:
        # TODO: Implement
        ...

    def build(self) -> QueryResult:
        # TODO: Implement
        return QueryResult()
