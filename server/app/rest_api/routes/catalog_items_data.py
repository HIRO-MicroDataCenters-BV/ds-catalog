from typing import Annotated

from abc import ABC, abstractmethod

from classy_fastapi import Routable, delete, get, post, put
from fastapi import HTTPException, Path, Request, Response, status

from app.core.entities import catalog as catalog_entities
from app.core.exceptions import CatalogItemDataDoesNotExist, CatalogItemDoesNotExist
from app.core.usecases import catalog as catalog_usecases

from ..models.catalog import CatalogItemData
from ..tags import Tags


class ICatalogItemsDataUsecases(ABC):
    @abstractmethod
    async def get(
        self,
        catalog_item_id: str,
    ) -> catalog_entities.CatalogItemData:
        ...

    @abstractmethod
    async def create(
        self, catalog_item_id: str, catalog_item_data: catalog_entities.CatalogItemData
    ) -> catalog_entities.CatalogItemData:
        ...

    @abstractmethod
    async def change(
        self,
        catalog_item_id: str,
        catalog_item_data: catalog_entities.CatalogItemData,
    ) -> catalog_entities.CatalogItemData:
        ...

    @abstractmethod
    async def delete(self, catalog_item_id: str) -> None:
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
        "/catalog-items/{id}/data/",
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
        id: Annotated[str, Path(description="Catalog Item ID")],
    ) -> CatalogItemData:
        """Returns the data for the catalog item"""
        try:
            catalog_item_data = await self._usecases.get(id)
        except CatalogItemDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog item not found")
        except CatalogItemDataDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog item data not found")
        return CatalogItemData(catalog_item_data)

    @post(
        "/catalog-items/{id}/data/",
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
            status.HTTP_404_NOT_FOUND: {"description": "Catalog item not found"},
        },
    )
    async def create_catalog_item_data(
        self,
        id: Annotated[str, Path(description="Catalog Item ID")],
        data: CatalogItemData,
        request: Request,
        response: Response,
    ) -> CatalogItemData:
        """Create the data for the catalog item"""
        try:
            catalog_item_data = await self._usecases.create(id, data)
        except CatalogItemDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog Item not found")
        result = CatalogItemData(catalog_item_data)
        response.headers["Location"] = str(
            request.url_for("get_catalog_item_data", id=id)
        )
        return result

    @put(
        "/catalog-items/{id}/data/",
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
        id: Annotated[str, Path(description="Catalog Item ID")],
        data: CatalogItemData,
    ) -> CatalogItemData:
        """Change the data for the catalog item"""
        try:
            catalog_item_data = await self._usecases.change(id, data)
        except CatalogItemDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog Item not found")
        except CatalogItemDataDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog Item Data not found")
        return CatalogItemData(catalog_item_data)

    @delete(
        "/catalog-items/{id}/data/",
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
        id: Annotated[str, Path(description="Catalog Item ID")],
    ) -> None:
        """Delete the data for the catalog item"""
        try:
            await self._usecases.delete(id)
        except CatalogItemDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog Item not found")
        except CatalogItemDataDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog Item Data not found")


routes = CatalogItemsDataRoutes(usecases=CatalogItemsDataUsecases())
