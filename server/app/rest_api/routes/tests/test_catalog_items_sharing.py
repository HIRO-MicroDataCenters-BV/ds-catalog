from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from fastapi import status
from fastapi.encoders import jsonable_encoder

from app.core.entities.tests.factories import CatalogItemFactory
from app.core.exceptions import CatalogItemDoesNotExist
from app.rest_api.serializers.catalog import CatalogItem, CatalogItemShareForm
from app.rest_api.strings import CATALOG_ITEM_NOT_FOUND

from ..catalog_items import CatalogItemsRoutes
from ..catalog_items_sharing import CatalogItemsSharingRoutes
from .helpers import create_test_client


class TestCatalogItemsSharingRoutes:
    def test_share_catalog_item(self) -> None:
        catalog_item_id = uuid4()
        marketplace_id = uuid4()

        entity_output = CatalogItemFactory.build()
        form_input = CatalogItemShareForm(marketplace_id=marketplace_id)
        item_output = CatalogItem.from_entity(entity_output)

        usecases = Mock()
        usecases.share = AsyncMock(return_value=entity_output)

        catalog_routes = CatalogItemsRoutes(usecases=Mock())
        sharing_routes = CatalogItemsSharingRoutes(usecases=usecases)

        client = create_test_client(
            catalog_routes.router,
            sharing_routes.router,
        )
        response = client.post(
            f"/catalog-items/{catalog_item_id}/share/",
            json=jsonable_encoder(form_input.model_dump(by_alias=True)),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.text == item_output.model_dump_json(by_alias=True)
        assert "Location" in response.headers
        assert f"/catalog-items/{entity_output.id}/" in response.headers["Location"]
        usecases.share.assert_called_once_with(catalog_item_id, marketplace_id)

    def test_share_catalog_item_if_catalog_item_not_found(self) -> None:
        catalog_item_id = uuid4()
        marketplace_id = uuid4()

        form_input = CatalogItemShareForm(marketplace_id=marketplace_id)

        usecases = Mock()
        usecases.share = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsSharingRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.post(
            f"/catalog-items/{catalog_item_id}/share/",
            json=jsonable_encoder(form_input.model_dump(by_alias=True)),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND
