from app.core.entities import Person as PersonEntity

from .base import BaseModel


class Person(BaseModel):
    id: str
    name: str

    def to_entity(self) -> PersonEntity:
        return PersonEntity(**self.model_dump())

    @classmethod
    def from_entity(cls, entity: PersonEntity) -> "Person":
        return cls(**entity.model_dump())
