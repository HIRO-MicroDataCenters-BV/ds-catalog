from pydantic import Field

from .base import BaseModel


class HealthCheck(BaseModel):
    status: str = Field(examples=["OK"])
