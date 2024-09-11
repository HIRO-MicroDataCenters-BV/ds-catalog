from typing import TypeAlias, TypedDict, Unpack

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select

from ..entities.catalog import Ontology
from ..models.catalog import CatalogItemModel
from .interface import IQuery

CatalogItemsQuery: TypeAlias = IQuery[CatalogItemModel]
CatalogItemsQueryResult: TypeAlias = Select[tuple[CatalogItemModel]]


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


class CatalogItemsFilterQuery(CatalogItemsQuery):
    def __init__(self, **kwargs: Unpack[CatalogItemsFiltersDTO]) -> None:
        # TODO: Implement
        ...

    def apply(self, query: CatalogItemsQueryResult) -> CatalogItemsQueryResult:
        # TODO: Implement
        return query
