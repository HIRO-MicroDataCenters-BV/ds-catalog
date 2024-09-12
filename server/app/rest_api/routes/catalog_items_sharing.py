from abc import ABC, abstractmethod
from uuid import UUID

from classy_fastapi import Routable, post
from fastapi import HTTPException, Request, Response, status

from app.core.entities import catalog as catalog_entities
from app.core.exceptions import CatalogItemDoesNotExist
from app.core.usecases import catalog as catalog_usecases

from ..serializers.catalog import CatalogItem, CatalogItemShareForm
from ..strings import CATALOG_ITEM_NOT_FOUND
from ..tags import Tags


class ICatalogItemsSharingUsecases(ABC):
    @abstractmethod
    async def share(
        self,
        catalog_item_id: UUID,
        marketplace_id: UUID,
    ) -> catalog_entities.CatalogItem:
        ...


class CatalogItemsSharingUsecases(ICatalogItemsSharingUsecases):
    async def share(self, *args, **kwargs):
        return await catalog_usecases.share_catalog_item(*args, **kwargs)


class CatalogItemsSharingRoutes(Routable):
    _usecases: ICatalogItemsSharingUsecases

    def __init__(self, usecases: ICatalogItemsSharingUsecases) -> None:
        self._usecases = usecases
        super().__init__()

    @post(
        "/catalog-items/{id}/share/",
        operation_id="share_catalog_item",
        summary="Share a catalog item",
        tags=[Tags.CatalogItemsSharing],
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
            status.HTTP_404_NOT_FOUND: {"description": "Catalog Item not found"},
        },
    )
    async def share_catalog_item(
        self,
        id: UUID,
        data: CatalogItemShareForm,
        request: Request,
        response: Response,
    ) -> CatalogItem:
        """Share a catalog item to the marketplace"""
        marketplace_id = data.marketplace_id
        try:
            entity_output = await self._usecases.share(id, marketplace_id)
        except CatalogItemDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=CATALOG_ITEM_NOT_FOUND,
            )
        item_output = CatalogItem.from_entity(entity_output)
        response.headers["Location"] = str(
            request.url_for("get_catalog_item", id=entity_output.id)
        )
        return item_output


routes = CatalogItemsSharingRoutes(usecases=CatalogItemsSharingUsecases())
