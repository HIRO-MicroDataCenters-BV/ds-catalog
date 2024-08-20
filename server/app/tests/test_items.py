from typing import cast

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from .. import items


class TestStorage:
    def test_has(self) -> None:
        item = items.Item(id=1, name="test")
        storage = items.Storage({item.id: item})
        assert storage.has(item.id)
        assert not storage.has(999)

    def test_set(self) -> None:
        item = items.Item(id=1, name="test")
        storage = items.Storage({item.id: item})

        item_updated = items.Item(id=item.id, name="item_updated")
        new_item = items.Item(id=999, name="test3")

        storage.set(item_updated.id, item_updated)
        storage.set(new_item.id, new_item)

        assert storage.get(item.id) == item_updated
        assert storage.get(new_item.id) == new_item

    def test_get(self) -> None:
        item = items.Item(id=1, name="test")
        storage = items.Storage({item.id: item})
        assert storage.get(item.id) == item

    def test_all(self) -> None:
        item1 = items.Item(id=1, name="test1")
        item2 = items.Item(id=1, name="test2")

        storage = items.Storage(
            {
                item1.id: item1,
                item2.id: item2,
            }
        )

        assert set([item.id for item in storage.all()]) == set([item1.id, item2.id])

    def test_delete(self) -> None:
        item = items.Item(id=1, name="test")
        storage = items.Storage({item.id: item})
        storage.delete(item.id)
        assert not storage.has(item.id)

    def test_clear(self) -> None:
        item1 = items.Item(id=1, name="test1")
        item2 = items.Item(id=1, name="test2")

        storage = items.Storage(
            {
                item1.id: item1,
                item2.id: item2,
            }
        )

        storage.clear()

        assert len(storage.all()) == 0


class TestItemRoutes:
    @pytest.fixture
    def storage(self) -> items.Storage:
        return items.Storage(
            {
                1: items.Item(id=1, name="test1"),
                2: items.Item(id=2, name="test2"),
            }
        )

    @pytest.fixture
    def client(self, storage: items.Storage) -> TestClient:
        routes = items.ItemRoutes(storage)
        app = FastAPI()
        app.include_router(routes.router)
        return TestClient(app)

    def test_read_items(self, client: TestClient, storage: items.Storage) -> None:
        response = client.get("/item/")
        assert response.status_code == status.HTTP_200_OK
        expected_items = [item.model_dump() for item in storage.all()]
        assert response.json() == expected_items

    def test_create_item(self, client: TestClient, storage: items.Storage) -> None:
        item_data = {"id": 3, "name": "test3"}
        response = client.post("/item/", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == item_data
        item_in_storage = storage.get(cast(int, item_data["id"]))
        assert item_in_storage is not None
        assert item_in_storage.model_dump() == item_data

    def test_create_item_if_exists(
        self, client: TestClient, storage: items.Storage
    ) -> None:
        exists_item_data = storage.all()[0].model_dump()
        response = client.post("/item/", json=exists_item_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Item already exists"}

    def test_read_item(self, client: TestClient, storage: items.Storage) -> None:
        item = storage.all()[0]
        response = client.get(f"/item/{item.id}/")
        assert response.status_code == 200
        assert response.json() == item.model_dump()

    def test_read_item_if_does_not_exist(self, client: TestClient) -> None:
        response = client.get("/item/999/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found"}

    def test_update_item(self, client: TestClient, storage: items.Storage) -> None:
        item = storage.all()[0]
        updated_item = {"id": item.id, "name": "new test1"}
        response = client.put(f"/item/{item.id}/", json=updated_item)
        assert response.status_code == 200
        assert response.json() == updated_item
        item_in_storage = storage.get(item.id)
        assert item_in_storage is not None
        assert item_in_storage.model_dump() == updated_item

    def test_update_item_if_does_not_exist(self, client: TestClient) -> None:
        item_data = {"id": 999, "name": "test999"}
        response = client.put("/item/999/", json=item_data)
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found"}

    def test_delete_item(self, client: TestClient, storage: items.Storage) -> None:
        item = storage.all()[0]
        id = item.id
        response = client.delete(f"/item/{id}/")
        assert response.status_code == 204
        assert not storage.has(id)

    def test_delete_item_if_does_not_exist(self, client: TestClient) -> None:
        response = client.delete("/item/999/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found"}
