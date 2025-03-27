from typing import Any

from pydantic import BaseModel, Field

from app.core import entities
from app.core.repository.queries import Query

from .examples import catalog_filters_example, dataset_input_example


class HealthCheck(BaseModel):
    status: str = Field(examples=["OK"])


class Person(BaseModel):
    id: str
    name: str

    def to_entity(self) -> entities.Person:
        return entities.Person(id=self.id, name=self.name)


class CatalogFilters(BaseModel):
    context: dict[str, str]
    filters: list[dict[str, Any]]

    model_config = {
        "json_schema_extra": {
            "examples": [
                catalog_filters_example,
            ],
        }
    }

    def to_entity(self) -> Query:
        # TODO: Implement transformation to Query
        return Query()


class JsonLD(BaseModel):
    context: dict[str, Any] = Field(..., alias="@context")
    graph: dict[str, Any] = Field(..., alias="@graph")

    class Config:
        populate_by_name = True
        extra = "allow"


class Dataset(JsonLD):
    model_config = {
        "json_schema_extra": {
            "examples": [
                dataset_input_example,
            ],
        }
    }

    def to_entity(self) -> entities.Dataset:
        d = self.model_dump_json(by_alias=True)
        return entities.Dataset.from_json_ld(d)
