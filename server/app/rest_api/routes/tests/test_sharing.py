from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.exceptions import NodeDoesNotExist
from app.core.tests.factories import user_factory
from app.rest_api.depends import get_user

from ..sharing import get_usecases, routes

usecases = Mock()
user = user_factory()


def override_get_user():
    return user


def override_get_usecases():
    return usecases


app = FastAPI()
app.include_router(routes.router)

app.dependency_overrides[get_user] = override_get_user
app.dependency_overrides[get_usecases] = override_get_usecases

client = TestClient(app)


class TestDatasetSharingRoutes:
    def test_share(self):
        usecases.share = AsyncMock()
        response = client.post("/datasets/1/share/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        usecases.share.assert_called_once_with("1", context={"user": user})

    def test_share_if_does_not_exist(self):
        usecases.share = AsyncMock(side_effect=NodeDoesNotExist)
        response = client.post("/datasets/1/share/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        usecases.share.assert_called_once_with("1", context={"user": user})

    def test_unshare(self):
        usecases.unshare = AsyncMock()
        response = client.post("/datasets/1/unshare/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        usecases.unshare.assert_called_once_with("1", context={"user": user})

    def test_unshare_if_does_not_exist(self):
        usecases.unshare = AsyncMock(side_effect=NodeDoesNotExist)
        response = client.post("/datasets/1/unshare/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        usecases.unshare.assert_called_once_with("1", context={"user": user})
