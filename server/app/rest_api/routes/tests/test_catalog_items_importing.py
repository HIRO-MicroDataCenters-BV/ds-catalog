from unittest.mock import AsyncMock, Mock

from fastapi import status
from fastapi.encoders import jsonable_encoder

from app.core.entities.tests.factories import (
    CatalogItemFactory,
    CatalogItemImportFactory,
)
from app.rest_api.models.catalog import CatalogItem, CatalogItemImportForm

from ..catalog_items import CatalogItemsRoutes
from ..catalog_items_importing import CatalogItemsImportingRoutes
from .helpers import create_test_client


class TestCatalogItemsImportingRoutes:
    def test_import_catalog_item(self) -> None:
        entity_input = CatalogItemImportFactory.build()
        entity_output = CatalogItemFactory.build()
        model_input = CatalogItemImportForm.from_entity(entity_input)
        model_output = CatalogItem.from_entity(entity_output)

        usecases = Mock()
        usecases.import_data = AsyncMock(return_value=entity_output)

        catalog_routes = CatalogItemsRoutes(usecases=Mock())
        sharing_routes = CatalogItemsImportingRoutes(usecases=usecases)

        client = create_test_client(
            catalog_routes.router,
            sharing_routes.router,
        )
        response = client.post(
            "/catalog-items/import/",
            json=jsonable_encoder(model_input.model_dump(by_alias=True)),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.text == model_output.model_dump_json(by_alias=True)
        assert "Location" in response.headers
        assert f"/catalog-items/{entity_output.id}/" in response.headers["Location"]
        usecases.import_data.assert_called_once_with(model_input.to_entity())
