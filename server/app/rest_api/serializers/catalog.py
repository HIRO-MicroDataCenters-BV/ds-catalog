from datetime import date

from pydantic import AnyUrl, Field

from app.core import entities

from .base import BaseModel
from .person import Person


class Catalog(BaseModel):
    identifier: str
    title: str
    description: str

    def to_entity(self) -> entities.Catalog:
        return entities.Catalog(**self.model_dump())

    @classmethod
    def from_entity(cls, entity: entities.Catalog) -> "Catalog":
        return cls(**entity.model_dump())


class CatalogImportForm(BaseModel):
    title: str
    description: str

    def to_entity(self) -> entities.CatalogImport:
        return entities.CatalogImport(**self.model_dump())

    @classmethod
    def from_entity(cls, entity: entities.CatalogImport) -> "CatalogImportForm":
        return cls(**entity.model_dump())


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
    description: str
    keyword: list[str]
    license: str
    is_local: bool
    is_shared: bool
    issued: date
    theme: list[str]
    catalog: Catalog
    creator: Person
    distribution: list[Distribution]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "identifier": "9c208553-4685-473b-bdcc-466f724baae1",
                    "title": "Dataset 1",
                    "description": "Some description",
                    "keyword": ["keyword1", "keyword2"],
                    "license": "http://domain.com/license/",
                    "is_local": True,
                    "is_shared": False,
                    "issued": "2024-01-01",
                    "theme": ["theme1", "theme2"],
                    "catalog": {
                        "identifier": "9c208553-4685-473b-bdcc-466f724baae1",
                        "title": "Dataset 1",
                        "description": "Some description",
                    },
                    "creator": {
                        "id": "14eb400e-3ba3-4aed-a7b5-de030af3e411",
                        "name": "John Smith",
                    },
                    "distribution": [
                        {
                            "byteSize": 512,
                            "mediaType": "text",
                            "checksum": {
                                "algorithm": "md5",
                                "checksumValue": "202cb962ac59075b964b07152d234b70",
                            },
                            "accessService": [
                                {"endpointUrl": "http://domain.com/dataset1/"}
                            ],
                        }
                    ],
                }
            ]
        }
    }

    def to_entity(self) -> entities.Dataset:
        fields = self.model_dump(exclude=set(["catalog", "creator", "distribution"]))
        return entities.Dataset(
            **fields,
            catalog=self.catalog.to_entity(),
            creator=self.creator.to_entity(),
            distribution=[i.to_entity() for i in self.distribution],
        )

    @classmethod
    def from_entity(cls, entity: entities.Dataset) -> "Dataset":
        fields = entity.model_dump(exclude=set(["catalog", "creator", "distribution"]))
        return cls(
            **fields,
            catalog=Catalog.from_entity(entity.catalog),
            creator=Person.from_entity(entity.creator),
            distribution=[Distribution.from_entity(i) for i in entity.distribution],
        )


class DatasetForm(BaseModel):
    title: str
    description: str
    keyword: list[str]
    license: str
    theme: list[str]
    distribution: list[Distribution]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Dataset 1",
                    "description": "Some description",
                    "keyword": ["keyword1", "keyword2"],
                    "license": "http://domain.com/license/",
                    "theme": ["theme1", "theme2"],
                    "distribution": [
                        {
                            "byteSize": 512,
                            "mediaType": "text",
                            "checksum": {
                                "algorithm": "md5",
                                "checksumValue": "202cb962ac59075b964b07152d234b70",
                            },
                            "accessService": [
                                {"endpointUrl": "http://domain.com/dataset1/"}
                            ],
                        }
                    ],
                }
            ]
        }
    }

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
    description: str
    keyword: list[str]
    license: str
    theme: list[str]
    catalog: CatalogImportForm
    distribution: list[Distribution]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "identifier": "9c208553-4685-473b-bdcc-466f724baae1",
                    "title": "Dataset 1",
                    "description": "Some description",
                    "keyword": ["keyword1", "keyword2"],
                    "license": "http://domain.com/license/",
                    "theme": ["theme1", "theme2"],
                    "catalog": {
                        "title": "Dataset 1",
                        "description": "Some description",
                    },
                    "distribution": [
                        {
                            "byteSize": 512,
                            "mediaType": "text",
                            "checksum": {
                                "algorithm": "md5",
                                "checksumValue": "202cb962ac59075b964b07152d234b70",
                            },
                            "accessService": [
                                {"endpointUrl": "http://domain.com/dataset1/"}
                            ],
                        }
                    ],
                }
            ]
        }
    }

    def to_entity(self) -> entities.DatasetImport:
        fields = self.model_dump(exclude=set(["catalog", "distribution"]))
        return entities.DatasetImport(
            **fields,
            catalog=self.catalog.to_entity(),
            distribution=[i.to_entity() for i in self.distribution],
        )

    @classmethod
    def from_entity(cls, entity: entities.DatasetImport) -> "DatasetImportForm":
        fields = entity.model_dump(exclude=set(["catalog", "distribution"]))
        return cls(
            **fields,
            catalog=CatalogImportForm.from_entity(entity.catalog),
            distribution=[Distribution.from_entity(i) for i in entity.distribution],
        )
