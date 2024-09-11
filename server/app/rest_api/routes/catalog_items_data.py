from abc import ABC, abstractmethod
from uuid import UUID

from classy_fastapi import Routable, delete, get, post, put
from fastapi import HTTPException, Request, Response, status

from app.core.entities import catalog as catalog_entities
from app.core.exceptions import CatalogItemDataDoesNotExist, CatalogItemDoesNotExist
from app.core.usecases import catalog as catalog_usecases

from ..serializers.catalog import CatalogItemData
from ..strings import CATALOG_ITEM_DATA_NOT_FOUND, CATALOG_ITEM_NOT_FOUND
from ..tags import Tags


class ICatalogItemsDataUsecases(ABC):
    @abstractmethod
    async def get(
        self,
        catalog_item_id: UUID,
    ) -> catalog_entities.CatalogItemData:
        ...

    @abstractmethod
    async def create(
        self, catalog_item_id: UUID, catalog_item_data: catalog_entities.CatalogItemData
    ) -> catalog_entities.CatalogItemData:
        ...

    @abstractmethod
    async def change(
        self,
        catalog_item_id: UUID,
        catalog_item_data: catalog_entities.CatalogItemData,
    ) -> catalog_entities.CatalogItemData:
        ...

    @abstractmethod
    async def delete(self, catalog_item_id: UUID) -> None:
        ...


class CatalogItemsDataUsecases(ICatalogItemsDataUsecases):
    async def get(self, *args, **kwargs):
        return await catalog_usecases.get_catalog_item_data(*args, **kwargs)

    async def create(self, *args, **kwargs):
        return await catalog_usecases.create_catalog_item_data(*args, **kwargs)

    async def change(self, *args, **kwargs):
        return await catalog_usecases.change_catalog_item_data(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        return await catalog_usecases.delete_catalog_item_data(*args, **kwargs)


class CatalogItemsDataRoutes(Routable):
    _usecases: CatalogItemsDataUsecases

    def __init__(self, usecases: CatalogItemsDataUsecases) -> None:
        self._usecases = usecases
        super().__init__()

    @get(
        "/catalog-items/{catalog_item_id}/data/",
        operation_id="get_catalog_item_data",
        summary="Get the data for the catalog item",
        tags=[Tags.CatalogItemsData],
        response_model=CatalogItemData,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "description": "Catalog Item or Catalog Item Data not found"
            },
        },
    )
    async def get_catalog_item_data(
        self,
        catalog_item_id: UUID,
    ) -> CatalogItemData:
        """Returns the data for the catalog item"""
        try:
            entity_output = await self._usecases.get(catalog_item_id)
        except CatalogItemDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CATALOG_ITEM_NOT_FOUND
            )
        except CatalogItemDataDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CATALOG_ITEM_DATA_NOT_FOUND,
            )
        return CatalogItemData.from_entity(entity_output)

    @post(
        "/catalog-items/{catalog_item_id}/data/",
        operation_id="create_catalog_item_data",
        summary="Create the data for the catalog item",
        tags=[Tags.CatalogItemsData],
        status_code=status.HTTP_201_CREATED,
        response_model=CatalogItemData,
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
            status.HTTP_404_NOT_FOUND: {"description": CATALOG_ITEM_NOT_FOUND},
        },
    )
    async def create_catalog_item_data(
        self,
        catalog_item_id: UUID,
        data: CatalogItemData,
        request: Request,
        response: Response,
    ) -> CatalogItemData:
        """Create the data for the catalog item"""
        entity_input = data.to_entity()
        try:
            entity_output = await self._usecases.create(catalog_item_id, entity_input)
        except CatalogItemDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CATALOG_ITEM_NOT_FOUND
            )
        item_data_output = CatalogItemData.from_entity(entity_output)
        response.headers["Location"] = str(
            request.url_for("get_catalog_item_data", catalog_item_id=catalog_item_id)
        )
        return item_data_output

    @put(
        "/catalog-items/{catalog_item_id}/data/",
        operation_id="change_catalog_item_data",
        summary="Change the data for the catalog item",
        tags=[Tags.CatalogItemsData],
        response_model=CatalogItemData,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "description": "Catalog Item or Catalog Item Data not found"
            },
        },
    )
    async def change_catalog_item_data(
        self,
        catalog_item_id: UUID,
        data: CatalogItemData,
    ) -> CatalogItemData:
        """Change the data for the catalog item"""
        input_entity = data.to_entity()
        try:
            output_entity = await self._usecases.change(catalog_item_id, input_entity)
        except CatalogItemDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CATALOG_ITEM_NOT_FOUND
            )
        except CatalogItemDataDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CATALOG_ITEM_DATA_NOT_FOUND,
            )
        return CatalogItemData.from_entity(output_entity)

    @delete(
        "/catalog-items/{catalog_item_id}/data/",
        operation_id="delete_catalog_item_data",
        summary="Delete the data for the catalog item",
        tags=[Tags.CatalogItemsData],
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "description": "Catalog Item or Catalog Item Data not found"
            },
        },
    )
    async def delete_catalog_item_data(
        self,
        catalog_item_id: UUID,
    ) -> None:
        """Delete the data for the catalog item"""
        try:
            await self._usecases.delete(catalog_item_id)
        except CatalogItemDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=CATALOG_ITEM_NOT_FOUND
            )
        except CatalogItemDataDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CATALOG_ITEM_DATA_NOT_FOUND,
            )


routes = CatalogItemsDataRoutes(usecases=CatalogItemsDataUsecases())
