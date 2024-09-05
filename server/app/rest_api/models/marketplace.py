from uuid import UUID

from .base import BaseModel


class CatalogItemShareForm(BaseModel):
    marketplace_id: UUID
