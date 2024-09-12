from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from fastapi import status

from app.core.entities.tests.factories import catalog_item_data_factory
from app.core.exceptions import CatalogItemDataDoesNotExist, CatalogItemDoesNotExist
from app.rest_api.serializers.catalog import CatalogItemData
from app.rest_api.strings import CATALOG_ITEM_DATA_NOT_FOUND, CATALOG_ITEM_NOT_FOUND

from ..catalog_items_data import CatalogItemsDataRoutes
from .helpers import create_test_client


class TestCatalogItemsDataRoutes:
    def test_get_catalog_item_data(self) -> None:
        catalog_item_id = uuid4()
        catalog_item_data = catalog_item_data_factory()
        item_data_output = CatalogItemData(catalog_item_data)

        usecases = Mock()
        usecases.get = AsyncMock(return_value=catalog_item_data)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.get(f"/catalog-items/{catalog_item_id}/data/")

        assert response.status_code == status.HTTP_200_OK
        assert response.text == item_data_output.model_dump_json(by_alias=True)
        usecases.get.assert_called_once_with(catalog_item_id)

    def test_get_catalog_item_data_if_catalog_item_not_found(self) -> None:
        catalog_item_id = uuid4()

        usecases = Mock()
        usecases.get = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.get(f"/catalog-items/{catalog_item_id}/data/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND

    def test_get_catalog_item_data_if_data_not_found(self) -> None:
        catalog_item_id = uuid4()

        usecases = Mock()
        usecases.get = AsyncMock(side_effect=CatalogItemDataDoesNotExist)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.get(f"/catalog-items/{catalog_item_id}/data/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_DATA_NOT_FOUND

    def test_create_catalog_item_data(self) -> None:
        catalog_item_id = uuid4()
        entity = catalog_item_data_factory()
        item_data = CatalogItemData.from_entity(entity)

        usecases = Mock()
        usecases.create = AsyncMock(return_value=entity)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.post(
            f"/catalog-items/{catalog_item_id}/data/",
            json=item_data.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.text == item_data.model_dump_json(by_alias=True)
        assert "Location" in response.headers
        assert f"/catalog-items/{catalog_item_id}/data/" in response.headers["Location"]
        usecases.create.assert_called_once_with(catalog_item_id, dict(entity))

    def test_create_catalog_item_data_if_catalog_item_not_found(self) -> None:
        catalog_item_id = uuid4()
        model = CatalogItemData.from_entity(catalog_item_data_factory())

        usecases = Mock()
        usecases.create = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.post(
            f"/catalog-items/{catalog_item_id}/data/",
            json=model.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND

    def test_change_catalog_item_data(self) -> None:
        catalog_item_id = uuid4()
        entity = catalog_item_data_factory()
        item_data = CatalogItemData.from_entity(entity)

        usecases = Mock()
        usecases.change = AsyncMock(return_value=entity)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.put(
            f"/catalog-items/{catalog_item_id}/data/",
            json=item_data.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.text == item_data.model_dump_json(by_alias=True)
        usecases.change.assert_called_once_with(catalog_item_id, dict(entity))

    def test_change_catalog_item_data_if_catalog_item_not_found(self) -> None:
        catalog_item_id = uuid4()
        item_data = CatalogItemData.from_entity(catalog_item_data_factory())

        usecases = Mock()
        usecases.change = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.put(
            f"/catalog-items/{catalog_item_id}/data/",
            json=item_data.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND

    def test_change_catalog_item_data_if_data_not_found(self) -> None:
        catalog_item_id = uuid4()
        item_data = CatalogItemData.from_entity(catalog_item_data_factory())

        usecases = Mock()
        usecases.change = AsyncMock(side_effect=CatalogItemDataDoesNotExist)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.put(
            f"/catalog-items/{catalog_item_id}/data/",
            json=item_data.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_DATA_NOT_FOUND

    def test_delete_catalog_item(self) -> None:
        catalog_item_id = uuid4()

        usecases = Mock()
        usecases.delete = AsyncMock()

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.delete(f"/catalog-items/{catalog_item_id}/data/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        usecases.delete.assert_called_once_with(catalog_item_id)

    def test_delete_catalog_item_if_catalog_item_not_found(self) -> None:
        catalog_item_id = uuid4()

        usecases = Mock()
        usecases.delete = AsyncMock(side_effect=CatalogItemDoesNotExist)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.delete(f"/catalog-items/{catalog_item_id}/data/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_NOT_FOUND

    def test_delete_catalog_item_if_data_not_found(self) -> None:
        catalog_item_id = uuid4()

        usecases = Mock()
        usecases.delete = AsyncMock(side_effect=CatalogItemDataDoesNotExist)

        routes = CatalogItemsDataRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.delete(f"/catalog-items/{catalog_item_id}/data/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == CATALOG_ITEM_DATA_NOT_FOUND
