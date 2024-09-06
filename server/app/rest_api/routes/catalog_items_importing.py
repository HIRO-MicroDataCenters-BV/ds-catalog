from abc import ABC, abstractmethod

from classy_fastapi import Routable, post
from fastapi import Request, Response, status

from app.core.entities import catalog as catalog_entities
from app.core.usecases import marketplace as marketplace_usecases

from ..models.catalog import CatalogItem
from ..models.marketplace import CatalogItemImportForm
from ..tags import Tags


class ICatalogItemsImportingUsecases(ABC):
    @abstractmethod
    async def import_data(
        self, catalog_item: catalog_entities.CatalogItemImport
    ) -> catalog_entities.CatalogItem:
        ...


class CatalogItemsImportingUsecases(ICatalogItemsImportingUsecases):
    async def import_data(self, *args, **kwargs):
        return await marketplace_usecases.import_catalog_item(*args, **kwargs)


class CatalogItemsImportingRoutes(Routable):
    _usecases: ICatalogItemsImportingUsecases

    def __init__(self, usecases: ICatalogItemsImportingUsecases) -> None:
        self._usecases = usecases
        super().__init__()

    @post(
        "/catalog-items/import/",
        operation_id="import_catalog_item",
        summary="Import a catalog item",
        tags=[Tags.CatalogItemsImporting],
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
    async def import_catalog_item(
        self,
        data: CatalogItemImportForm,
        request: Request,
        response: Response,
    ) -> CatalogItem:
        """Import a catalog item from the local catalog"""
        input_entity = data.to_entity()
        output_entity = await self._usecases.import_data(input_entity)
        output_item = CatalogItem.from_entity(output_entity)
        response.headers["Location"] = str(
            request.url_for("get_catalog_item", id=output_entity.id)
        )
        return output_item


routes = CatalogItemsImportingRoutes(usecases=CatalogItemsImportingUsecases())
