from typing import Any, TypeAlias, TypedDict, Unpack

from datetime import datetime
from uuid import UUID

from ..entities.catalog import Ontology
from .interface import IQuery

CatalogItemsQuery: TypeAlias = Any


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


class CatalogItemsFilterQuery(IQuery[CatalogItemsQuery]):
    def __init__(self, **kwargs: Unpack[CatalogItemsFiltersDTO]) -> None:
        # TODO: Implement
        ...

    def apply(self, query: CatalogItemsQuery) -> CatalogItemsQuery:
        # TODO: Implement
        return query
