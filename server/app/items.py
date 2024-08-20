# This file uses Classy-FastAPI to create a FastAPI
# instance with dependency-injection of an *instance* of some class.
# This is especially handy if you want to maintain some common resource reused between
# invocations of the routes, e.g. a database connection.
# For detailed explanation and more examples see:
# https://gitlab.com/companionlabs-opensource/classy-fastapi


from typing import Optional

from enum import Enum

from classy_fastapi import Routable, delete, get, post, put
from fastapi import HTTPException, status
from pydantic import BaseModel

TAGS: list[str | Enum] = ["items"]


class Item(BaseModel):
    id: int
    name: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "test name",
                }
            ]
        }
    }


class Storage:
    def __init__(self, initial: Optional[dict[int, Item]] = None) -> None:
        self.kvs: dict[int, Item] = initial if initial is not None else {}

    def has(self, key: int) -> bool:
        return key in self.kvs

    def set(self, key: int, value: Item) -> None:
        self.kvs[key] = value

    def get(self, key: int) -> Item | None:
        return self.kvs.get(key)

    def all(self) -> list[Item]:
        return list(self.kvs.values())

    def delete(self, key: int) -> None:
        self.kvs.pop(key)

    def clear(self) -> None:
        self.kvs = {}


class ItemRoutes(Routable):
    def __init__(self, storage: Storage) -> None:
        super().__init__()
        self.__storage = storage

    @get(
        "/item/",
        operation_id="items__read_all",
        summary="Read all items",
        response_model=list[Item],
        tags=TAGS,
    )
    async def read_items(self) -> list[Item]:
        """Read all items from the storage"""
        return self.__storage.all()

    @post(
        "/item/",
        operation_id="items__create",
        summary="Create an item",
        response_model=Item,
        status_code=status.HTTP_201_CREATED,
        tags=TAGS,
    )
    async def create_item(self, item: Item) -> Item:
        """Create a new item in the storage"""
        if self.__storage.has(item.id):
            raise HTTPException(status_code=400, detail="Item already exists")
        self.__storage.set(item.id, item)
        return item

    @get(
        "/item/{id}/",
        operation_id="items__read_item",
        summary="Read an item",
        response_model=Item,
        tags=TAGS,
    )
    async def read_item(self, id: int) -> Item | None:
        """Read item from the storage"""
        item = self.__storage.get(id)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    @put(
        "/item/{id}/",
        operation_id="items__update_item",
        summary="Update an item",
        response_model=Item,
        tags=TAGS,
    )
    async def update_item(self, id: int, item: Item) -> Item:
        """Update an item in the storage"""
        if not self.__storage.has(id):
            raise HTTPException(status_code=404, detail="Item not found")
        self.__storage.set(item.id, item)
        return item

    @delete(
        "/item/{id}/",
        operation_id="items__delete_item",
        summary="Delete an item",
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
        tags=TAGS,
    )
    async def delete_item(self, id: int) -> None:
        """Delete an item from the storage"""
        if not self.__storage.has(id):
            raise HTTPException(status_code=404, detail="Item not found")
        self.__storage.delete(id)
        return


storage = Storage()
routes = ItemRoutes(storage)
