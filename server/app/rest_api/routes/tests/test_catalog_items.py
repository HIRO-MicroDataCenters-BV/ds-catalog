from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from fastapi import status

from app.core.entities.tests.factories import (
    CatalogItemFactory,
    CatalogItemInputFactory,
)
from app.core.exceptions import CatalogItemDoesNotExist
from app.core.queries.common import CompositeQuery
from app.core.queries.list import OrderDirection
from app.rest_api.serializers.catalog import CatalogItem, CatalogItemForm
from app.rest_api.serializers.common import PaginatedResult
from app.rest_api.strings import CATALOG_ITEM_NOT_FOUND

from ..catalog_items import CatalogItemsRoutes
from .helpers import create_test_client


class TestCatalogItemsRoutes:
    def test_get_catalog_items(self) -> None:
        page = 2
        page_size = 50

        entities_output = [
            CatalogItemFactory.build(),
            CatalogItemFactory.build(),
        ]
        items_output = [CatalogItem.from_entity(item) for item in entities_output]
        expected_result = PaginatedResult(page=page, size=page_size, items=items_output)

        usecases = Mock()
        usecases.list = AsyncMock(return_value=entities_output)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.get(
            "/catalog-items/",
            params={
                "page": page,
                "pageSize": page_size,
                "orderBy": "title",
                "orderDirection": OrderDirection.ASC.value,
                "search": "search term",
                "is_local": "false",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.text == expected_result.model_dump_json(by_alias=True)
        usecases.list.assert_called_once()

        call_args = usecases.list.call_args[0]
        call_kwargs = usecases.list.call_args[1]

        assert len(call_args) == 1
        assert call_kwargs == {}

        query = call_args[0]
        assert isinstance(query, CompositeQuery)

    def test_get_catalog_item(self) -> None:
        entity_output = CatalogItemFactory.build()
        item_output = CatalogItem.from_entity(entity_output)

        usecases = Mock()
        usecases.get = AsyncMock(return_value=entity_output)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.get(f"/catalog-items/{entity_output.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.text == item_output.model_dump_json(by_alias=True)
        usecases.get.assert_called_once_with(entity_output.id)

    def test_get_catalog_item_if_it_not_found(self) -> None:
        id = uuid4()

        usecases = Mock()
        usecases.get = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.get(f"/catalog-items/{id}/")

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

        client = create_test_client(routes.router)
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
        id = uuid4()
        entity_input = CatalogItemInputFactory.build()
        entity_output = CatalogItemFactory.build()
        item_input = CatalogItemForm.from_entity(entity_input)
        item_output = CatalogItem.from_entity(entity_output)

        usecases = Mock()
        usecases.update = AsyncMock(return_value=entity_output)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.patch(
            f"/catalog-items/{id}/",
            json=item_input.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.text == item_output.model_dump_json(by_alias=True)
        usecases.update.assert_called_once_with(id, item_input.to_entity())

    def test_update_catalog_item_if_it_not_found(self) -> None:
        id = uuid4()
        entity_input = CatalogItemInputFactory.build()
        item_input = CatalogItemForm.from_entity(entity_input)

        usecases = Mock()
        usecases.update = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.patch(
            f"/catalog-items/{id}/",
            json=item_input.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND

    def test_delete_catalog_item(self) -> None:
        id = uuid4()

        usecases = Mock()
        usecases.delete = AsyncMock()

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.delete(f"/catalog-items/{id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        usecases.delete.assert_called_once_with(id)

    def test_delete_catalog_item_if_it_not_found(self) -> None:
        id = uuid4()

        usecases = Mock()
        usecases.delete = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.delete(f"/catalog-items/{id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND
