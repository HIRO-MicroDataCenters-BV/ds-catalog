from typing import Any

import pytest

from ..base import BaseModel


class DummyModel(BaseModel):
    some_field: str
    another_field: int


class TestBaseModel:
    @pytest.mark.asyncio
    async def test_to_camel_aliases(self):
        model_instance = DummyModel(some_field="test", another_field=123)

        assert model_instance.some_field == "test"
        assert model_instance.another_field == 123

        json_data = model_instance.model_dump(by_alias=True)
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
        model_instance = DummyModel(**data)

        assert model_instance.some_field == "test_value"
        assert model_instance.another_field == 42
