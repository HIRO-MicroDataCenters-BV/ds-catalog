from unittest.mock import AsyncMock, Mock

from fastapi import status
from fastapi.encoders import jsonable_encoder

from app.core.entities.tests.factories import DatasetFactory, DatasetImportFactory
from app.rest_api.serializers.catalog import Dataset, DatasetImportForm

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

        catalog_routes = DatasetsRoutes(usecases=Mock())
        sharing_routes = DatasetsImportingRoutes(usecases=usecases)

        client = create_test_client(
            catalog_routes.router,
            sharing_routes.router,
        )
        response = client.post(
            "/datasets/import/",
            json=jsonable_encoder(form_input.model_dump(by_alias=True)),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.text == item_output.model_dump_json(by_alias=True)
        assert "Location" in response.headers
        assert f"/datasets/{entity_output.identifier}/" in response.headers["Location"]
        usecases.import_data.assert_called_once_with(form_input.to_entity())
