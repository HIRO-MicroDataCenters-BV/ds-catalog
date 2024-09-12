from app.core.entities.person import Person as PersonEntity

from .base import BaseModel
from .utils import entity_to_dict, model_to_dict


class Person(BaseModel):
    id: str
    name: str

    def to_entity(self) -> PersonEntity:
        return PersonEntity(**model_to_dict(self))

    @classmethod
    def from_entity(cls, entity: PersonEntity) -> "Person":
        return cls(**entity_to_dict(entity))
