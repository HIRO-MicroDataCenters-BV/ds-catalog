from abc import ABC, abstractmethod

from classy_fastapi import Routable, delete, get, patch, post
from fastapi import HTTPException, status

from app.core.entities import catalog as catalog_entities
from app.core.exceptions import CatalogItemDoesNotExist
from app.core.queries import IQuery
from app.core.queries.common import GetPaginated
from app.core.usecases import catalog as catalog_usecases

from ..models.catalog import CatalogItem, CatalogItemForm
from ..models.common import PaginatedResult
from ..tags import Tags


class ICatalogItemsUsecases(ABC):
    @abstractmethod
    async def list(
        self,
        query: IQuery | None = None,
    ) -> list[catalog_entities.CatalogItem]:
        ...

    @abstractmethod
    async def get(self, catalog_item_id: str) -> catalog_entities.CatalogItem:
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
        catalog_item_id: str,
        catalog_item_input: catalog_entities.CatalogItemInput,
    ) -> catalog_entities.CatalogItem:
        ...

    @abstractmethod
    async def delete(self, catalog_item_id: str) -> None:
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
        response_model=PaginatedResult[CatalogItem],
        tags=[Tags.CatalogItems],
    )
    async def get_catalog_items(
        self,
        page: int = 1,
        pageSize: int = 100,
    ) -> PaginatedResult[CatalogItem]:
        """
        Returns the list of catalog items with the ability to search, filter and
        paginate.

        """
        query = GetPaginated(page=page, size=pageSize)
        catalog_items = await self._usecases.list(query)
        items = [CatalogItem.from_entity(item) for item in catalog_items]
        return PaginatedResult(page=page, size=pageSize, items=items)

    @get(
        "/catalog-items/{id}/",
        operation_id="get_catalog_item",
        summary="Get the catalog item",
        response_model=CatalogItem,
        tags=[Tags.CatalogItems],
    )
    async def get_catalog_item(self, id: str) -> CatalogItem:
        """Get the catalog item"""
        try:
            catalog_item_entity = await self._usecases.get(id)
        except CatalogItemDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog item is not found")
        return CatalogItem.from_entity(catalog_item_entity)

    @post(
        "/catalog-items/",
        operation_id="create_catalog_item",
        summary="Create a catalog item",
        response_model=CatalogItem,
        status_code=status.HTTP_201_CREATED,
        tags=[Tags.CatalogItems],
    )
    async def create_catalog_item(
        self,
        body: CatalogItemForm,
    ) -> CatalogItem:
        """Create a catalog item"""
        input_entity = body.to_entity()
        catalog_item_entity = await self._usecases.create(input_entity)
        return CatalogItem.from_entity(catalog_item_entity)

    @patch(
        "/catalog-items/{id}/",
        operation_id="update_catalog_item",
        summary="Update the catalog item",
        response_model=CatalogItem,
        tags=[Tags.CatalogItems],
    )
    async def update_catalog_item(self, id: str, body: CatalogItemForm) -> CatalogItem:
        """Update the catalog item"""
        input_entity = body.to_entity()
        try:
            catalog_item_entity = await self._usecases.update(id, input_entity)
        except CatalogItemDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog item is not found")
        return CatalogItem.from_entity(catalog_item_entity)

    @delete(
        "/catalog-items/{id}/",
        operation_id="delete_catalog_item",
        summary="Delete the catalog item",
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
        tags=[Tags.CatalogItems],
    )
    async def delete_catalog_item(self, id: str) -> None:
        """Delete the catalog item"""
        try:
            await self._usecases.delete(id)
        except CatalogItemDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog item is not found")
        return


routes = CatalogItemsRoutes(usecases=CatalogItemsUsecases())
