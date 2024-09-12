from typing import Any

import pytest

from ..base import BaseModel


class Serializer(BaseModel):
    some_field: str
    another_field: int


class TestBaseModel:
    @pytest.mark.asyncio
    async def test_to_camel_aliases(self):
        serializer = Serializer(some_field="test", another_field=123)

        assert serializer.some_field == "test"
        assert serializer.another_field == 123

        json_data = serializer.model_dump(by_alias=True)
        assert json_data == {
            "someField": "test",
            "anotherField": 123,
        }

    @pytest.mark.asyncio
    async def test_from_attributes(self):
        data: dict[str, Any] = {
            "someField": "test_value",
            "anotherField": 42,
        }
        serializer = Serializer(**data)

        assert serializer.some_field == "test_value"
        assert serializer.another_field == 42
