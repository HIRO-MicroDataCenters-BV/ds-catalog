from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from rdflib import DCTERMS

from app.core.entities import Dataset
from app.core.exceptions import NodeDoesNotExist
from app.core.tests.factories import user_factory
from app.rest_api.depends import get_user

from ..datasets import get_usecases, routes

usecases = Mock()

user = user_factory()

dataset = Dataset.create_empty("http://example.com/1")
dataset.set_attribute(DCTERMS.identifier, "1")
dataset.set_attribute(DCTERMS.title, "Test Dataset")


def override_get_user():
    return user


def override_get_usecases():
    return usecases


app = FastAPI()
app.include_router(routes.router)

app.dependency_overrides[get_user] = override_get_user
app.dependency_overrides[get_usecases] = override_get_usecases

client = TestClient(app)


class TestDatasetsRoutes:
    def test_save_dataset(self):
        usecases.save = AsyncMock(return_value=dataset)

        data = dataset.to_json_ld()
        response = client.post("/datasets/", content=data)

        assert response.status_code == status.HTTP_200_OK
        assert Dataset.from_json_ld(response.text) == dataset

        usecases.save.assert_called_once()
        assert usecases.save.call_args[0][0] == dataset
        assert usecases.save.call_args[1]["context"] == {"user": user}

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
