from typing import Annotated

from datetime import datetime
from uuid import UUID

from fastapi import Query

from app.core.entities.catalog import Ontology
from app.core.queries.catalog import CatalogItemsFiltersDTO


async def catalog_items_filters(
    search: str = "",
    ontology: Ontology | None = None,
    is_local: Annotated[bool | None, Query(alias="isLocal")] = None,
    is_shared: Annotated[bool | None, Query(alias="isShared")] = None,
    creator_id: Annotated[UUID | None, Query(alias="creator__id")] = None,
    created: datetime | None = None,
    created_gte: Annotated[datetime | None, Query(alias="created__gte")] = None,
    created_lte: Annotated[datetime | None, Query(alias="created__lte")] = None,
    data_product_id: Annotated[str, Query(alias="dataProduct__id")] = "",
    data_product_size_gte: Annotated[
        int | None, Query(alias="dataProduct__size__gte")
    ] = None,
    data_product_size_lte: Annotated[
        int | None, Query(alias="dataProduct__size__lte")
    ] = None,
    data_product_mimetype: Annotated[str, Query(alias="dataProduct__mimetype")] = "",
) -> CatalogItemsFiltersDTO:
    return {
        "search": search,
        "ontology": ontology,
        "is_local": is_local,
        "is_shared": is_shared,
        "creator_id": creator_id,
        "created": created,
        "created_gte": created_gte,
        "created_lte": created_lte,
        "data_product_id": data_product_id,
        "data_product_size_gte": data_product_size_gte,
        "data_product_size_lte": data_product_size_lte,
        "data_product_mimetype": data_product_mimetype,
    }
