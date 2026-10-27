import json
from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from rdflib import DCTERMS

from app.core.entities import Dataset
from app.core.exceptions import (
    ConfigurationError,
    ErrorParsingMMIO,
    GraphValidationError,
    NodeDoesNotExist,
)
from app.core.tests.factories import user_factory
from app.rest_api.depends import get_user
from app.rest_api.strings import FILE_NOT_FOUND
from app.settings import Settings, get_settings

from ..datasets import get_usecases, routes

usecases = Mock()

oca_uri = "http://oca.example.org/123/"
shacl_url = "http://example.org/shacl.ttl"
ontology_url = "http://example.org/dcat.ttl"
allowed_values_config_path = "/code/app/core/allowed_values.yaml"


user = user_factory()

dataset = Dataset.create_empty("http://example.com/1")
dataset.set_attribute(DCTERMS.identifier, "1")
dataset.set_attribute(DCTERMS.title, "Test Dataset")


def override_get_settings():
    return Settings(
        oca_uri=oca_uri,
        shacl_url=shacl_url,
        ontology_url=ontology_url,
        allowed_values_config_path=allowed_values_config_path,
    )


def override_get_user():
    return user


def override_get_usecases():
    return usecases


app = FastAPI()
app.include_router(routes.router)

app.dependency_overrides[get_user] = override_get_user
app.dependency_overrides[get_usecases] = override_get_usecases
app.dependency_overrides[get_settings] = override_get_settings

client = TestClient(app)


class TestDatasetsRoutes:
    def test_save_dataset(self):
        filename = "test.csv"
        related_data_product = "disease_xyz"
        usecases.save = AsyncMock(return_value=(dataset, []))

        data = dataset.to_json_ld()
        response = client.post(
            f"/datasets/{filename}/?related_data_product={related_data_product}",
            json=json.loads(data),
            headers={"Content-Type": "application/ld+json"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert Dataset.from_json_ld(response.text) == dataset

        usecases.save.assert_called_once()

        args = usecases.save.call_args[0]
        kwargs = usecases.save.call_args[1]

        assert len(args) == 2
        assert len(kwargs) == 2

        assert usecases.save.call_args[0][0] == dataset
        assert usecases.save.call_args[0][1] == filename
        assert (
            usecases.save.call_args[1]["related_data_product"] == related_data_product
        )
        assert usecases.save.call_args[1]["context"] == {
            "user": user,
            "oca_uri": oca_uri,
            "shacl_url": shacl_url,
            "ontology_url": ontology_url,
            "allowed_values_config_path": allowed_values_config_path,
        }

    def test_save_dataset_if_file_not_found(self):
        usecases.save = AsyncMock(side_effect=FileNotFoundError)

        data = dataset.to_json_ld()
        response = client.post(
            "/datasets/test.csv/?related_data_product=disease_xyz",
            json=json.loads(data),
            headers={"Content-Type": "application/ld+json"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": FILE_NOT_FOUND}

    def test_save_dataset_if_mmio_is_invalid(self):
        error_message = "test error"
        usecases.save = AsyncMock(side_effect=ErrorParsingMMIO(error_message))

        data = dataset.to_json_ld()
        response = client.post(
            "/datasets/test.csv/?related_data_product=disease_xyz",
            json=json.loads(data),
            headers={"Content-Type": "application/ld+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {"detail": error_message}

    def test_save_dataset_if_graph_is_invalid(self):
        error_code = "test_code"
        error_message = "Test error"
        details = [{"node": "some node"}]

        error = GraphValidationError(error_code, error_message, details)
        usecases.save = AsyncMock(side_effect=error)

        data = dataset.to_json_ld()
        response = client.post(
            "/datasets/test.csv/?related_data_product=disease_xyz",
            json=json.loads(data),
            headers={"Content-Type": "application/ld+json"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "code": error_code,
                    "message": error_message,
                    "details": details,
                }
            ]
        }

    def test_save_dataset_if_configuration_error(self):
        usecases.save = AsyncMock(
            side_effect=ConfigurationError("internal config details")
        )

        data = dataset.to_json_ld()
        response = client.post(
            "/datasets/test.csv/?related_data_product=disease_xyz",
            json=json.loads(data),
            headers={"Content-Type": "application/ld+json"},
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json() == {"detail": "Server configuration error."}

    def test_get_dataset(self):
        usecases.get = AsyncMock(return_value=dataset)
        response = client.get("/datasets/1/")
        assert response.status_code == status.HTTP_200_OK
        assert Dataset.from_json_ld(response.text) == dataset
        usecases.get.assert_called_once_with("1", context={"user": user})

    def test_get_dataset_if_does_not_exist(self):
        usecases.get = AsyncMock(side_effect=NodeDoesNotExist)
        response = client.get("/datasets/1/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        usecases.get.assert_called_once_with("1", context={"user": user})

    def test_delete_dataset(self):
        usecases.delete = AsyncMock()
        response = client.delete("/datasets/1/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        usecases.delete.assert_called_once_with("1", context={"user": user})

    def test_delete_dataset_if_does_not_exist(self):
        usecases.delete = AsyncMock(side_effect=NodeDoesNotExist)
        response = client.delete("/datasets/1/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        usecases.delete.assert_called_once_with("1", context={"user": user})
