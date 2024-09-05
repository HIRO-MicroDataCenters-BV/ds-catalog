from abc import ABC, abstractmethod

from classy_fastapi import Routable, post
from fastapi import HTTPException, Request, Response, status

from app.core.entities import catalog as catalog_entities
from app.core.exceptions import CatalogItemDoesNotExist
from app.core.usecases import marketplace as marketplace_usecases

from ..models.catalog import CatalogItem
from ..models.marketplace import CatalogItemShareForm
from ..tags import Tags


class ICatalogItemsSharingUsecases(ABC):
    @abstractmethod
    async def share(
        self,
        catalog_item_id: str,
        marketplace_id: str,
    ) -> catalog_entities.CatalogItem:
        ...


class CatalogItemsSharingUsecases(ICatalogItemsSharingUsecases):
    async def share(self, *args, **kwargs):
        return await marketplace_usecases.share_catalog_item(*args, **kwargs)


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
        id: str,
        data: CatalogItemShareForm,
        request: Request,
        response: Response,
    ) -> CatalogItem:
        """Share a catalog item to the marketplace"""
        marketplace_id = str(data.marketplace_id)
        try:
            catalog_item_entity = await self._usecases.share(id, marketplace_id)
        except CatalogItemDoesNotExist:
            raise HTTPException(status_code=404, detail="Catalog item is not found")
        result = CatalogItem.from_entity(catalog_item_entity)
        response.headers["Location"] = str(
            request.url_for("get_catalog_item", id=catalog_item_entity.id)
        )
        return result


routes = CatalogItemsSharingRoutes(usecases=CatalogItemsSharingUsecases())
