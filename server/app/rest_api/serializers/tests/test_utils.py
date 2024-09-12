from dataclasses import dataclass

from ..base import BaseModel
from ..utils import entity_to_dict, model_to_dict


def test_entity_to_dict():
    @dataclass
    class Entry:
        id: int
        title: str

    entity = Entry(id=1, title="test title")
    result = entity_to_dict(entity)

    assert isinstance(result, dict)
    assert result["id"] == 1
    assert result["title"] == "test title"


def test_model_to_dict():
    class Model(BaseModel):
        id: int
        title: str

    model = Model(id=1, title="test title")
    result = model_to_dict(model)

    assert isinstance(result, dict)
    assert result["id"] == 1
    assert result["title"] == "test title"
