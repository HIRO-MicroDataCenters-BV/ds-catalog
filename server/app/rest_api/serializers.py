from pydantic import BaseModel, ConfigDict, Field

from app.core import entities

from .examples import catalog_filters_example, dataset_input_example


class HealthCheck(BaseModel):
    status: str = Field(examples=["OK"])


class User(BaseModel):
    id: str
    name: str

    def to_entity(self) -> entities.User:
        return entities.User(id=self.id, name=self.name)


class JsonLD(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )


class CatalogFilters(JsonLD):
    # TODO: Validate the data

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                catalog_filters_example,
            ],
        },
    )

    def to_entity(self) -> entities.CatalogFilters:
        d = self.model_dump_json(by_alias=True)
        return entities.CatalogFilters.from_json_ld(d)


class Dataset(JsonLD):
    # TODO: Validate the data

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                dataset_input_example,
            ],
        },
    )

    def to_entity(self) -> entities.Dataset:
        d = self.model_dump_json(by_alias=True)
        return entities.Dataset.from_json_ld(d)
