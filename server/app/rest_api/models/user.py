from uuid import UUID

from app.core.entities.user import User as UserEntity

from .base import BaseModel
from .utils import entity_to_dict, model_to_dict


class User(BaseModel):
    id: UUID
    full_name: str

    def to_entity(self) -> UserEntity:
        return UserEntity(**model_to_dict(self))

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "User":
        return cls(**entity_to_dict(entity))
