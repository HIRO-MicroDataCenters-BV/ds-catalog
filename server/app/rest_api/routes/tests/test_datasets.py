from unittest.mock import AsyncMock, Mock

from fastapi import status

from app.core.exceptions import DatasetDoesNotExist
from app.core.tests.factories import DatasetFactory, DatasetInputFactory
from app.rest_api.depends.user import get_user
from app.rest_api.serializers.catalog import Dataset, DatasetForm
from app.rest_api.serializers.common import PaginatedResult
from app.rest_api.strings import DATASET_NOT_FOUND

from ..datasets import DatasetsRoutes, IDatasetsUsecases
from .helpers import create_test_client


def dataset_routes_fabric(usecases: IDatasetsUsecases) -> DatasetsRoutes:
    return DatasetsRoutes(
        usecases=usecases,
        local_catalog_title="Test catalog",
        local_catalog_description="Test catalog description",
    )


class TestDatasetsRoutes:
    def test_get_datasets(self) -> None:
        page = 2
        page_size = 50

        entities_output = [
            DatasetFactory.build(),
            DatasetFactory.build(),
        ]
        items_output = [Dataset.from_entity(item) for item in entities_output]
        expected_result = PaginatedResult(page=page, size=page_size, items=items_output)

        usecases = Mock()
        usecases.list = AsyncMock(return_value=entities_output)

        routes = dataset_routes_fabric(usecases)

        client = create_test_client(routes.router)
        response = client.get(
            "/datasets/",
            params={
                "page": page,
                "pageSize": page_size,
                "orderBy": "title",
                "search": "search term",
                "is_local": "false",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.text == expected_result.model_dump_json(by_alias=True)
        usecases.list.assert_called_once()

    def test_get_dataset(self) -> None:
        entity_output = DatasetFactory.build()
        item_output = Dataset.from_entity(entity_output)

        usecases = Mock()
        usecases.get = AsyncMock(return_value=entity_output)

        routes = dataset_routes_fabric(usecases)

        client = create_test_client(routes.router)
        response = client.get(f"/datasets/{entity_output.identifier}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.text == item_output.model_dump_json(by_alias=True)
        usecases.get.assert_called_once_with(
            entity_output.identifier, context={"user": get_user()}
        )

    def test_get_dataset_if_it_not_found(self) -> None:
        usecases = Mock()
        usecases.get = AsyncMock(side_effect=DatasetDoesNotExist)

        routes = dataset_routes_fabric(usecases)

        client = create_test_client(routes.router)
        response = client.get("/datasets/1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == DATASET_NOT_FOUND

    def test_create_dataset(self) -> None:
        catalog_title = "Test catalog"
        catalog_description = "Test catalog description"

        entity_input = DatasetInputFactory.build()
        entity_output = DatasetFactory.build()
        item_input = DatasetForm.from_entity(entity_input)
        item_output = Dataset.from_entity(entity_output)

        usecases = Mock()
        usecases.create = AsyncMock(return_value=entity_output)

        routes = DatasetsRoutes(
            usecases=usecases,
            local_catalog_title=catalog_title,
            local_catalog_description=catalog_description,
        )

        client = create_test_client(routes.router)
        response = client.post(
            "/datasets/",
            json=item_input.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.text == item_output.model_dump_json(by_alias=True)
        assert "Location" in response.headers
        assert f"/datasets/{entity_output.identifier}" in response.headers["Location"]
        usecases.create.assert_called_once_with(
            item_input.to_entity(),
            context={
                "user": get_user(),
                "catalog_title": catalog_title,
                "catalog_description": catalog_description,
            },
        )

    def test_update_dataset(self) -> None:
        id = "1"
        entity_input = DatasetInputFactory.build()
        entity_output = DatasetFactory.build()
        item_input = DatasetForm.from_entity(entity_input)
        item_output = Dataset.from_entity(entity_output)

        usecases = Mock()
        usecases.update = AsyncMock(return_value=entity_output)

        routes = dataset_routes_fabric(usecases)

        client = create_test_client(routes.router)
        response = client.patch(
            f"/datasets/{id}/",
            json=item_input.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.text == item_output.model_dump_json(by_alias=True)
        usecases.update.assert_called_once_with(
            id, item_input.to_entity(), context={"user": get_user()}
        )

    def test_update_dataset_if_it_not_found(self) -> None:
        entity_input = DatasetInputFactory.build()
        item_input = DatasetForm.from_entity(entity_input)

        usecases = Mock()
        usecases.update = AsyncMock(side_effect=DatasetDoesNotExist)

        routes = dataset_routes_fabric(usecases)

        client = create_test_client(routes.router)
        response = client.patch(
            "/datasets/1/",
            json=item_input.model_dump(by_alias=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == DATASET_NOT_FOUND

    def test_delete_dataset(self) -> None:
        id = "1"

        usecases = Mock()
        usecases.delete = AsyncMock()

        routes = dataset_routes_fabric(usecases)

        client = create_test_client(routes.router)
        response = client.delete(f"/datasets/{id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        usecases.delete.assert_called_once_with(id, context={"user": get_user()})

    def test_delete_dataset_if_it_not_found(self) -> None:
        usecases = Mock()
        usecases.delete = AsyncMock(side_effect=DatasetDoesNotExist)

        routes = dataset_routes_fabric(usecases)

        client = create_test_client(routes.router)
        response = client.delete("/datasets/1/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == DATASET_NOT_FOUND
