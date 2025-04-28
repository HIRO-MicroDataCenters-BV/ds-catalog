import uuid
from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.tests.factories import user_factory
from app.rest_api.depends import get_user
from app.rest_api.strings import FILE_ALREADY_EXISTS, FILE_NOT_FOUND, FILE_NOT_SELECTED

from ..mmio import get_usecases, routes

file = b"MMIO data"
filename_ = "test.mmio"

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


class TestMMIOsRoutes:
    def test_create(self):
        captured = {}

        async def capture_args(fileobj, fname, *, context):
            fileobj.seek(0)
            captured["content"] = fileobj.read()
            captured["filename"] = fname
            captured["context"] = context

        usecases.create = AsyncMock(side_effect=capture_args)

        response = client.post(
            "/mmio/",
            files={"file": (filename_, file)},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.headers["Location"] == "/mmio/test.mmio"

        usecases.create.assert_called_once()

        assert captured["content"] == file
        assert captured["filename"] == filename_
        assert captured["context"] == {"user": user}

    def test_create_no_filename(self):
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename=""\r\n'
            f"Content-Type: application/octet-stream\r\n"
            f"\r\n"
            f"dummy content here\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        response = client.post(
            "/mmio/",
            content=body,
            headers=headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": FILE_NOT_SELECTED}

    def test_create_file_exists(self):
        usecases.create = AsyncMock(side_effect=FileExistsError)

        response = client.post(
            "/mmio/",
            files={"file": (filename_, file)},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {"detail": FILE_ALREADY_EXISTS}

    def test_get(self, tmp_path):
        file_path = tmp_path / filename_
        file_path.write_bytes(file)

        usecases.get = AsyncMock(return_value=str(file_path))

        response = client.get(f"/mmio/{filename_}")

        assert response.status_code == status.HTTP_200_OK
        assert response.content == file

        usecases.get.assert_called_once_with(filename_, context={"user": user})

    def test_get_file_not_found(self):
        usecases.get = AsyncMock(side_effect=FileNotFoundError)

        response = client.get("/mmio/test.mmio")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": FILE_NOT_FOUND}

    def test_delete(self):
        usecases.delete = AsyncMock()

        response = client.delete(f"/mmio/{filename_}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        usecases.delete.assert_called_once_with(filename_, context={"user": user})

    def test_delete_file_not_found(self):
        usecases.delete = AsyncMock(side_effect=FileNotFoundError)

        response = client.delete(f"/mmio/{filename_}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": FILE_NOT_FOUND}
