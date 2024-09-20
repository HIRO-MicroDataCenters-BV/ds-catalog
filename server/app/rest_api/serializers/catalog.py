from datetime import date

from pydantic import AnyUrl, Field

from app.core import entities

from .base import BaseModel
from .person import Person


class Checksum(BaseModel):
    algorithm: str
    checksum_value: str

    def to_entity(self) -> entities.Checksum:
        return entities.Checksum(**self.model_dump())

    @classmethod
    def from_entity(cls, entity: entities.Checksum) -> "Checksum":
        return cls(**entity.model_dump())


class DataService(BaseModel):
    endpoint_url: str

    def to_entity(self) -> entities.DataService:
        return entities.DataService(**self.model_dump())

    @classmethod
    def from_entity(cls, entity: entities.DataService) -> "DataService":
        return cls(**entity.model_dump())


class Distribution(BaseModel):
    byte_size: int | None = Field(gt=0)
    media_type: str
    checksum: Checksum
    access_service: list[DataService]

    def to_entity(self) -> entities.Distribution:
        fields = self.model_dump(exclude=set(["checksum", "access_service"]))
        return entities.Distribution(
            **fields,
            checksum=self.checksum.to_entity(),
            access_service=[service.to_entity() for service in self.access_service],
        )

    @classmethod
    def from_entity(cls, entity: entities.Distribution) -> "Distribution":
        fields = entity.model_dump(exclude=set(["checksum", "access_service"]))
        return cls(
            **fields,
            checksum=Checksum.from_entity(entity.checksum),
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

    def to_entity(self) -> entities.Dataset:
        fields = self.model_dump(exclude=set(["creator", "distribution"]))
        return entities.Dataset(
            **fields,
            creator=self.creator.to_entity(),
            distribution=[i.to_entity() for i in self.distribution],
        )

    @classmethod
    def from_entity(cls, entity: entities.Dataset) -> "Dataset":
        fields = entity.model_dump(exclude=set(["creator", "distribution"]))
        return cls(
            **fields,
            creator=Person.from_entity(entity.creator),
            distribution=[Distribution.from_entity(i) for i in entity.distribution],
        )


class DatasetForm(BaseModel):
    title: str
    theme: list[str]
    distribution: list[Distribution]

    def to_entity(self) -> entities.DatasetInput:
        fields = self.model_dump(exclude=set(["distribution"]))
        return entities.DatasetInput(
            **fields,
            distribution=[i.to_entity() for i in self.distribution],
        )

    @classmethod
    def from_entity(cls, entity: entities.DatasetInput) -> "DatasetForm":
        fields = entity.model_dump(exclude=set(["distribution"]))
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

    def to_entity(self) -> entities.DatasetImport:
        fields = self.model_dump(exclude=set(["distribution"]))
        return entities.DatasetImport(
            **fields,
            distribution=[i.to_entity() for i in self.distribution],
        )

    @classmethod
    def from_entity(cls, entity: entities.DatasetImport) -> "DatasetImportForm":
        fields = entity.model_dump(exclude=set(["distribution"]))
        return cls(
            **fields,
            distribution=[Distribution.from_entity(i) for i in entity.distribution],
        )
