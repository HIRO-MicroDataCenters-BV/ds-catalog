from typing import Annotated, Any

from abc import ABC, abstractmethod
from uuid import UUID

from classy_fastapi import Routable, delete, get, patch, post
from fastapi import Depends, HTTPException, Request, Response, status

from app.core.entities import catalog as catalog_entities
from app.core.exceptions import CatalogItemDoesNotExist
from app.core.queries.catalog import (
    CatalogItemsFilterQuery,
    CatalogItemsFiltersDTO,
    CatalogItemsQuery,
)
from app.core.queries.common import CompositeQuery
from app.core.queries.list import (
    OrderQuery,
    OrderQueryDTO,
    PaginatorQuery,
    PaginatorQueryDTO,
)
from app.core.usecases import catalog as catalog_usecases

from ..depends.catalog import catalog_items_filters
from ..depends.list import order_parameters, paginator_parameters
from ..serializers.catalog import CatalogItem, CatalogItemForm
from ..serializers.common import PaginatedResult
from ..strings import CATALOG_ITEM_NOT_FOUND
from ..tags import Tags


class ICatalogItemsUsecases(ABC):
    @abstractmethod
    async def list(
        self,
        query: CatalogItemsQuery,
    ) -> list[catalog_entities.CatalogItem]:
        ...

    @abstractmethod
    async def get(self, catalog_item_id: UUID) -> catalog_entities.CatalogItem:
        ...

    @abstractmethod
    async def create(
        self,
        catalog_item_input: catalog_entities.CatalogItemInput,
    ) -> catalog_entities.CatalogItem:
        ...

    @abstractmethod
    async def update(
        self,
        catalog_item_id: UUID,
        catalog_item_input: catalog_entities.CatalogItemInput,
    ) -> catalog_entities.CatalogItem:
        ...

    @abstractmethod
    async def delete(self, catalog_item_id: UUID) -> None:
        ...


class CatalogItemsUsecases(ICatalogItemsUsecases):
    async def list(self, *args, **kwargs):
        return await catalog_usecases.get_catalog_items_list(*args, **kwargs)

    async def get(self, *args, **kwargs):
        return await catalog_usecases.get_catalog_item(*args, **kwargs)

    async def create(self, *args, **kwargs):
        return await catalog_usecases.create_catalog_item(*args, **kwargs)

    async def update(self, *args, **kwargs):
        return await catalog_usecases.update_catalog_item(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        return await catalog_usecases.delete_catalog_item(*args, **kwargs)


class CatalogItemsRoutes(Routable):
    _usecases: ICatalogItemsUsecases

    def __init__(self, usecases: ICatalogItemsUsecases) -> None:
        self._usecases = usecases
        super().__init__()

    @get(
        "/catalog-items/",
        operation_id="get_catalog_items",
        summary="Get the list of catalog items",
        tags=[Tags.CatalogItems],
        response_model=PaginatedResult[CatalogItem],
    )
    async def get_catalog_items(
        self,
        paginator_parameters: Annotated[
            PaginatorQueryDTO, Depends(paginator_parameters)
        ],
        order_parameters: Annotated[OrderQueryDTO, Depends(order_parameters)],
        catalog_items_filters: Annotated[
            CatalogItemsFiltersDTO, Depends(catalog_items_filters)
        ],
    ) -> PaginatedResult[CatalogItem]:
        """
        Returns the list of catalog items with the ability to search, filter and
        paginate.

        """

        paginator_query: PaginatorQuery[Any] = PaginatorQuery(**paginator_parameters)
        order_query: OrderQuery[Any] = OrderQuery(**order_parameters)
        catalog_items_filters_query = CatalogItemsFilterQuery(**catalog_items_filters)

        query = CompositeQuery(
            paginator_query,
            order_query,
            catalog_items_filters_query,
        )

        output_entities = await self._usecases.list(query)
        items = [CatalogItem.from_entity(entity) for entity in output_entities]

        return PaginatedResult(
            page=paginator_parameters["page"],
            size=paginator_parameters["page_size"],
            items=items,
        )

    @get(
        "/catalog-items/{id}/",
        operation_id="get_catalog_item",
        summary="Get the catalog item",
        tags=[Tags.CatalogItems],
        response_model=CatalogItem,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "Catalog Item not found"},
        },
    )
    async def get_catalog_item(self, id: UUID) -> CatalogItem:
        """Get the catalog item"""
        try:
            output_entity = await self._usecases.get(id)
        except CatalogItemDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CATALOG_ITEM_NOT_FOUND
            )
        return CatalogItem.from_entity(output_entity)

    @post(
        "/catalog-items/",
        operation_id="create_catalog_item",
        summary="Create a catalog item",
        tags=[Tags.CatalogItems],
        status_code=status.HTTP_201_CREATED,
        response_model=CatalogItem,
        responses={
            status.HTTP_201_CREATED: {
                "description": "Successful Response",
                "headers": {
                    "Location": {
                        "description": "The URL of the newly created resource",
                        "schema": {
                            "type": "string",
                            "format": "uri",
                        },
                    },
                },
            },
        },
    )
    async def create_catalog_item(
        self,
        item: CatalogItemForm,
        request: Request,
        response: Response,
    ) -> CatalogItem:
        """Create a catalog item"""
        input_entity = item.to_entity()
        output_entity = await self._usecases.create(input_entity)
        output_item = CatalogItem.from_entity(output_entity)
        response.headers["Location"] = str(
            request.url_for("get_catalog_item", id=output_entity.id)
        )
        return output_item

    @patch(
        "/catalog-items/{id}/",
        operation_id="update_catalog_item",
        summary="Update the catalog item",
        tags=[Tags.CatalogItems],
        response_model=CatalogItem,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "Catalog Item not found"},
        },
    )
    async def update_catalog_item(self, id: UUID, item: CatalogItemForm) -> CatalogItem:
        """Update the catalog item"""
        input_entity = item.to_entity()
        try:
            output_entity = await self._usecases.update(id, input_entity)
        except CatalogItemDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CATALOG_ITEM_NOT_FOUND
            )
        return CatalogItem.from_entity(output_entity)

    @delete(
        "/catalog-items/{id}/",
        operation_id="delete_catalog_item",
        summary="Delete the catalog item",
        tags=[Tags.CatalogItems],
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "Catalog Item not found"},
        },
    )
    async def delete_catalog_item(self, id: UUID) -> None:
        """Delete the catalog item"""
        try:
            await self._usecases.delete(id)
        except CatalogItemDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CATALOG_ITEM_NOT_FOUND
            )


routes = CatalogItemsRoutes(usecases=CatalogItemsUsecases())
