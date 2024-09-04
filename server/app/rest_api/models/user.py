from uuid import UUID

from .base import BaseModel


class User(BaseModel):
    id: UUID
    full_name: str
