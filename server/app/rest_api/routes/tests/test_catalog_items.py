from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from fastapi import FastAPI, status
from fastapi.routing import APIRouter
from fastapi.testclient import TestClient

from app.core.exceptions import CatalogItemDoesNotExist
from app.core.tests.fabrics import CatalogItemFactory, CatalogItemInputFactory
from app.rest_api.models.catalog import CatalogItem, CatalogItemForm
from app.rest_api.models.common import PaginatedResult
from app.rest_api.strings import CATALOG_ITEM_NOT_FOUND

from ..catalog_items import CatalogItemsRoutes


def create_client(router: APIRouter) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestCatalogItemsRoutes:
    def test_get_catalog_items(self) -> None:
        catalog_items = [
            CatalogItemFactory.build(),
            CatalogItemFactory.build(),
        ]

        usecases = Mock()
        usecases.list = AsyncMock(return_value=catalog_items)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_client(routes.router)
        response = client.get("/catalog-items/")

        assert response.status_code == status.HTTP_200_OK

        items = [CatalogItem.from_entity(item) for item in catalog_items]
        expected = PaginatedResult(page=1, size=100, items=items)

        assert response.text == expected.model_dump_json(by_alias=True)
        usecases.list.assert_called_once()

    def test_get_catalog_item(self) -> None:
        catalog_item = CatalogItemFactory.build()

        usecases = Mock()
        usecases.get = AsyncMock(return_value=catalog_item)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_client(routes.router)
        response = client.get(f"/catalog-items/{catalog_item.id}/")

        assert response.status_code == status.HTTP_200_OK

        expected_item = CatalogItem.from_entity(catalog_item)
        assert response.text == expected_item.model_dump_json(by_alias=True)
        usecases.get.assert_called_once_with(str(catalog_item.id))

    def test_get_catalog_item_if_it_not_found(self) -> None:
        usecases = Mock()
        usecases.get = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_client(routes.router)
        response = client.get("/catalog-items/1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND

    def test_create_catalog_item(self) -> None:
        entity_input = CatalogItemInputFactory.build()
        entity_output = CatalogItemFactory.build()
        item_input = CatalogItemForm.from_entity(entity_input)
        item_output = CatalogItem.from_entity(entity_output)

        usecases = Mock()
        usecases.create = AsyncMock(return_value=entity_output)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_client(routes.router)
        response = client.post(
            "/catalog-items/",
            json=item_input.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.text == item_output.model_dump_json(by_alias=True)
        assert "Location" in response.headers
        assert f"/catalog-items/{entity_output.id}" in response.headers["Location"]
        usecases.create.assert_called_once_with(item_input.to_entity())

    def test_update_catalog_item(self) -> None:
        id = str(uuid4())
        entity_input = CatalogItemInputFactory.build()
        entity_output = CatalogItemFactory.build()
        item_input = CatalogItemForm.from_entity(entity_input)
        item_output = CatalogItem.from_entity(entity_output)

        usecases = Mock()
        usecases.update = AsyncMock(return_value=entity_output)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_client(routes.router)
        response = client.patch(
            f"/catalog-items/{id}/",
            json=item_input.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.text == item_output.model_dump_json(by_alias=True)
        usecases.update.assert_called_once_with(id, item_input.to_entity())

    def test_update_catalog_item_if_it_not_found(self) -> None:
        id = str(uuid4())
        entity_input = CatalogItemInputFactory.build()
        item_input = CatalogItemForm.from_entity(entity_input)

        usecases = Mock()
        usecases.update = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_client(routes.router)
        response = client.patch(
            f"/catalog-items/{id}/",
            json=item_input.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND

    def test_delete_catalog_item(self) -> None:
        id = str(uuid4())

        usecases = Mock()
        usecases.delete = AsyncMock()

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_client(routes.router)
        response = client.delete(f"/catalog-items/{id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        usecases.delete.assert_called_once_with(id)

    def test_delete_catalog_item_if_it_not_found(self) -> None:
        usecases = Mock()
        usecases.delete = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_client(routes.router)
        response = client.delete("/catalog-items/1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND
