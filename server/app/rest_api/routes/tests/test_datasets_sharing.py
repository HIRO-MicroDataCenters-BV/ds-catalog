from unittest.mock import AsyncMock, Mock

from fastapi import status
from fastapi.encoders import jsonable_encoder
from pydantic_core import Url

from app.core.entities.tests.factories import DatasetFactory
from app.core.exceptions import DatasetDoesNotExist
from app.rest_api.serializers.catalog import Dataset, DatasetShareForm
from app.rest_api.strings import DATASET_NOT_FOUND

from ..datasets import DatasetsRoutes
from ..datasets_sharing import DatasetsSharingRoutes
from .helpers import create_test_client


class TestDatasetsSharingRoutes:
    def test_share_dataset(self) -> None:
        dataset_id = "1"
        marketplace_url = Url("https://example.com/import/")

        entity_output = DatasetFactory.build()
        form_input = DatasetShareForm(marketplace_url=marketplace_url)
        item_output = Dataset.from_entity(entity_output)

        usecases = Mock()
        usecases.share = AsyncMock(return_value=entity_output)

        catalog_routes = DatasetsRoutes(usecases=Mock())
        sharing_routes = DatasetsSharingRoutes(usecases=usecases)

        client = create_test_client(
            catalog_routes.router,
            sharing_routes.router,
        )
        response = client.post(
            f"/datasets/{dataset_id}/share/",
            json=jsonable_encoder(form_input.model_dump(by_alias=True)),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.text == item_output.model_dump_json(by_alias=True)
        assert "Location" in response.headers
        assert f"/datasets/{entity_output.identifier}/" in response.headers["Location"]
        usecases.share.assert_called_once_with(dataset_id, marketplace_url)

    def test_share_dataset_if_dataset_not_found(self) -> None:
        marketplace_url = Url("https://example.com/import/")

        form_input = DatasetShareForm(marketplace_url=marketplace_url)

        usecases = Mock()
        usecases.share = AsyncMock(side_effect=DatasetDoesNotExist)

        routes = DatasetsSharingRoutes(usecases=usecases)

        client = create_test_client(routes.router)
        response = client.post(
            "/datasets/1/share/",
            json=jsonable_encoder(form_input.model_dump(by_alias=True)),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == DATASET_NOT_FOUND
