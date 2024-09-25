from unittest.mock import AsyncMock, Mock

from fastapi import status
from fastapi.encoders import jsonable_encoder

from app.core.exceptions import DatasetAlredyExists
from app.core.tests.factories import DatasetFactory, DatasetImportFactory
from app.rest_api.depends.user import get_user
from app.rest_api.serializers.catalog import Dataset, DatasetImportForm
from app.rest_api.strings import DATASET_ALREDY_EXISTS

from ..datasets import DatasetsRoutes
from ..datasets_importing import DatasetsImportingRoutes
from .helpers import create_test_client


class TestDatasetsImportingRoutes:
    def test_import_dataset(self) -> None:
        entity_input = DatasetImportFactory.build()
        entity_output = DatasetFactory.build()
        form_input = DatasetImportForm.from_entity(entity_input)
        item_output = Dataset.from_entity(entity_output)

        usecases = Mock()
        usecases.import_data = AsyncMock(return_value=entity_output)

        catalog_routes = DatasetsRoutes(
            usecases=Mock(),
            local_catalog_title="Test catalog",
            local_catalog_description="Test catalog description",
        )
        importing_routes = DatasetsImportingRoutes(usecases=usecases)

        client = create_test_client(
            catalog_routes.router,
            importing_routes.router,
        )
        response = client.post(
            "/datasets/import/",
            json=jsonable_encoder(form_input.model_dump(by_alias=True)),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.text == item_output.model_dump_json(by_alias=True)
        assert "Location" in response.headers
        assert f"/datasets/{entity_output.identifier}/" in response.headers["Location"]
        usecases.import_data.assert_called_once_with(
            form_input.to_entity(), context={"user": get_user()}
        )

    def test_import_dataset_if_alredy_exists(self) -> None:
        entity_input = DatasetImportFactory.build()
        form_input = DatasetImportForm.from_entity(entity_input)

        usecases = Mock()
        usecases.import_data = AsyncMock(side_effect=DatasetAlredyExists)

        routes = DatasetsImportingRoutes(usecases=usecases)
        client = create_test_client(routes.router)

        response = client.post(
            "/datasets/import/",
            json=jsonable_encoder(form_input.model_dump(by_alias=True)),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == DATASET_ALREDY_EXISTS
