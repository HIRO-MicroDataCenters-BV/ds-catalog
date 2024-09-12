from datetime import date

from pydantic import AnyUrl, Field

from app.core.entities import catalog as catalog_entities

from .base import BaseModel
from .person import Person
from .utils import entity_to_dict, model_to_dict


class DataService(BaseModel):
    endpoint_url: str

    def to_entity(self) -> catalog_entities.DataService:
        return catalog_entities.DataService(**model_to_dict(self))

    @classmethod
    def from_entity(cls, entity: catalog_entities.DataService) -> "DataService":
        return cls(**entity_to_dict(entity))


class Distribution(BaseModel):
    bytesize: int | None = Field(gt=0)
    mimetype: str
    checksum: str
    access_service: list[DataService]

    def to_entity(self) -> catalog_entities.Distribution:
        fields = model_to_dict(self, exclude_fields=set(["access_service"]))
        return catalog_entities.Distribution(
            **fields,
            access_service=[service.to_entity() for service in self.access_service],
        )

    @classmethod
    def from_entity(cls, entity: catalog_entities.Distribution) -> "Distribution":
        fields = entity_to_dict(entity, exclude_fields=set(["access_service"]))
        return cls(
            **fields,
            access_service=[DataService.from_entity(i) for i in entity.access_service],
        )


class Dataset(BaseModel):
    identifier: str
    title: str
    is_local: bool
    is_shared: bool
    issued: date
    theme: list[str]
    creator: Person
    distribution: list[Distribution]

    def to_entity(self) -> catalog_entities.Dataset:
        fields = model_to_dict(self, exclude_fields=set(["creator", "distribution"]))
        return catalog_entities.Dataset(
            **fields,
            creator=self.creator.to_entity(),
            distribution=[i.to_entity() for i in self.distribution],
        )

    @classmethod
    def from_entity(cls, entity: catalog_entities.Dataset) -> "Dataset":
        fields = entity_to_dict(entity, exclude_fields=set(["creator", "distribution"]))
        return cls(
            **fields,
            creator=Person.from_entity(entity.creator),
            distribution=[Distribution.from_entity(i) for i in entity.distribution],
        )


class DatasetForm(BaseModel):
    title: str
    theme: list[str]
    distribution: list[Distribution]

    def to_entity(self) -> catalog_entities.DatasetInput:
        fields = model_to_dict(self, exclude_fields=set(["distribution"]))
        return catalog_entities.DatasetInput(
            **fields,
            distribution=[i.to_entity() for i in self.distribution],
        )

    @classmethod
    def from_entity(cls, entity: catalog_entities.DatasetInput) -> "DatasetForm":
        fields = entity_to_dict(entity, exclude_fields=set(["distribution"]))
        return cls(
            **fields,
            distribution=[Distribution.from_entity(i) for i in entity.distribution],
        )


class DatasetShareForm(BaseModel):
    marketplace_url: AnyUrl


class DatasetImportForm(BaseModel):
    identifier: str
    title: str
    theme: list[str]
    distribution: list[Distribution]

    def to_entity(self) -> catalog_entities.DatasetImport:
        fields = model_to_dict(self, exclude_fields=set(["distribution"]))
        return catalog_entities.DatasetImport(
            **fields,
            distribution=[i.to_entity() for i in self.distribution],
        )

    @classmethod
    def from_entity(cls, entity: catalog_entities.DatasetImport) -> "DatasetImportForm":
        fields = entity_to_dict(entity, exclude_fields=set(["distribution"]))
        return cls(
            **fields,
            distribution=[Distribution.from_entity(i) for i in entity.distribution],
        )
