from typing import Any

from datetime import datetime
from uuid import UUID

from pydantic import Field, RootModel

from app.core.entities import catalog as catalog_entities

from .base import BaseModel
from .user import User
from .utils import entity_to_dict, model_to_dict


class Node(BaseModel):
    protocol: str
    host: str
    port: int = Field(gt=0)

    def to_entity(self) -> catalog_entities.Node:
        return catalog_entities.Node(**model_to_dict(self))

    @classmethod
    def from_entity(cls, entity: catalog_entities.Node) -> "Node":
        return cls(**entity_to_dict(entity))


class Connector(BaseModel):
    id: str

    def to_entity(self) -> catalog_entities.Connector:
        return catalog_entities.Connector(**model_to_dict(self))

    @classmethod
    def from_entity(cls, entity: catalog_entities.Connector) -> "Connector":
        return cls(**entity_to_dict(entity))


class Interface(BaseModel):
    id: str

    def to_entity(self) -> catalog_entities.Interface:
        return catalog_entities.Interface(**model_to_dict(self))

    @classmethod
    def from_entity(cls, entity: catalog_entities.Interface) -> "Interface":
        return cls(**entity_to_dict(entity))


class Source(BaseModel):
    node: Node | None = None
    connector: Connector
    interface: Interface | None = None

    def to_entity(self) -> catalog_entities.Source:
        fields = model_to_dict(
            self, exclude_fields=set(["node", "connector", "interface"])
        )
        return catalog_entities.Source(
            **fields,
            node=self.node.to_entity() if self.node else None,
            connector=self.connector.to_entity(),
            interface=self.interface.to_entity() if self.interface else None,
        )

    @classmethod
    def from_entity(cls, entity: catalog_entities.Source) -> "Source":
        return cls(
            node=Node.from_entity(entity.node) if entity.node else None,
            connector=Connector.from_entity(entity.connector),
            interface=(
                Interface.from_entity(entity.interface) if entity.interface else None
            ),
        )


class DataProductBase(BaseModel):
    id: str
    name: str
    size: int | None = Field(gt=0)
    mimetype: str
    digest: str
    source: Source


class DataProduct(DataProductBase):
    links: dict[str, str] = Field(alias="_links")

    def to_entity(self) -> catalog_entities.DataProduct:
        fields = model_to_dict(self, exclude_fields=set(["source"]))
        return catalog_entities.DataProduct(
            **fields,
            source=self.source.to_entity(),
        )

    @classmethod
    def from_entity(cls, entity: catalog_entities.DataProduct) -> "DataProduct":
        fields = entity_to_dict(entity, exclude_fields=set(["source"]))
        return cls(
            **fields,
            source=Source.from_entity(entity.source),
        )


class DataProductForm(DataProductBase):
    access_point_url: str

    def to_entity(self) -> catalog_entities.DataProductInput:
        fields = model_to_dict(self, exclude_fields=set(["source"]))
        return catalog_entities.DataProductInput(
            **fields,
            source=self.source.to_entity(),
        )

    @classmethod
    def from_entity(
        cls, entity: catalog_entities.DataProductInput
    ) -> "DataProductForm":
        fields = entity_to_dict(entity, exclude_fields=set(["source"]))
        return cls(
            **fields,
            source=Source.from_entity(entity.source),
        )


class CatalogItemBase(BaseModel):
    ontology: catalog_entities.Ontology
    title: str
    summary: str


class CatalogItem(CatalogItemBase):
    id: UUID
    is_local: bool
    is_shared: bool
    created: datetime
    creator: User
    data_products: list[DataProduct]
    links: dict[str, str] = Field(alias="_links")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "c6b59f81-e7b5-46d6-84b9-c0dee695c7ec",
                    "ontology": "DCAT-3",
                    "title": "Cancer 2024",
                    "summary": "Some description",
                    "isLocal": True,
                    "isShared": False,
                    "created": "2023-08-27T14:00:00Z",
                    "creator": {
                        "id": "c6b59f81-e7b5-46d6-84b9-c0dee695c7ec",
                        "fullName": "John Smith",
                    },
                    "dataProducts": [
                        {
                            "id": "8D8AC610-566D-4EF0-9C22-186B2A5ED793",
                            "name": "cancer_data_2024",
                            "size": 1024,
                            "mimetype": "text/plain",
                            "digest": "1df50e8ad219e34f0b911e097b7b588e31f9b435",
                            "source": {
                                "node": {
                                    "protocol": "https",
                                    "host": "localhost",
                                    "port": 8000,
                                },
                                "connector": {"id": "connector1"},
                                "interface": {"id": "interface2"},
                            },
                            "_links": {
                                "accessPoint": "/connector1/interface2/8D8AC610-566D"
                                "-4EF0-9C22-186B2A5ED793/"
                            },
                        }
                    ],
                    "_links": {
                        "data": "/catalog-items/c6b59f81-e7b5-46d6-84b9-c0dee695c7ec"
                        "/data"
                    },
                }
            ]
        }
    }

    def to_entity(self) -> catalog_entities.CatalogItem:
        fields = model_to_dict(self, exclude_fields=set(["creator", "data_products"]))
        return catalog_entities.CatalogItem(
            **fields,
            creator=self.creator.to_entity(),
            data_products=[
                data_product.to_entity() for data_product in self.data_products
            ],
        )

    @classmethod
    def from_entity(cls, entity: catalog_entities.CatalogItem) -> "CatalogItem":
        fields = entity_to_dict(
            entity, exclude_fields=set(["creator", "data_products"])
        )
        data_products = [
            DataProduct.from_entity(data_product_entity)
            for data_product_entity in entity.data_products
        ]
        return cls(
            **fields,
            creator=User.from_entity(entity.creator),
            data_products=data_products,
        )


class CatalogItemForm(CatalogItemBase):
    data_products: list[DataProductForm]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ontology": "DCAT-3",
                    "title": "Cancer 2024",
                    "summary": "Some description",
                    "dataProducts": [
                        {
                            "id": "dataproduct1",
                            "name": "cancer_data_2024",
                            "size": 1024,
                            "mimetype": "text/plain",
                            "digest": "1df50e8ad219e34f0b911e097b7b588e31f9b435",
                            "source": {
                                "node": {
                                    "protocol": "https",
                                    "host": "localhost",
                                    "port": 8000,
                                },
                                "connector": {"id": "connector1"},
                                "interface": {"id": "interface2"},
                            },
                            "accessPointUrl": "/connector1/interface2/dataproduct1/",
                        }
                    ],
                }
            ]
        }
    }

    def to_entity(self) -> catalog_entities.CatalogItemInput:
        fields = model_to_dict(self, exclude_fields=set(["data_products"]))
        return catalog_entities.CatalogItemInput(
            **fields,
            data_products=[
                data_product.to_entity() for data_product in self.data_products
            ],
        )

    @classmethod
    def from_entity(
        cls, entity: catalog_entities.CatalogItemInput
    ) -> "CatalogItemForm":
        fields = entity_to_dict(entity, exclude_fields=set(["data_products"]))
        return cls(
            **fields,
            data_products=[
                DataProductForm.from_entity(data_product_entity)
                for data_product_entity in entity.data_products
            ],
        )


class CatalogItemShareForm(BaseModel):
    marketplace_id: UUID


class CatalogItemImportForm(CatalogItemBase):
    id: UUID
    data_products: list[DataProductForm]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "c6b59f81-e7b5-46d6-84b9-c0dee695c7ec",
                    "ontology": "DCAT-3",
                    "title": "Cancer 2024",
                    "summary": "Some description",
                    "dataProducts": [
                        {
                            "id": "dataproduct1",
                            "name": "cancer_data_2024",
                            "size": 1024,
                            "mimetype": "text/plain",
                            "digest": "1df50e8ad219e34f0b911e097b7b588e31f9b435",
                            "source": {
                                "node": {
                                    "protocol": "https",
                                    "host": "localhost",
                                    "port": 8000,
                                },
                                "connector": {"id": "connector1"},
                                "interface": {"id": "interface2"},
                            },
                            "accessPointUrl": "/connector1/interface2/dataproduct1/",
                        }
                    ],
                }
            ]
        }
    }

    def to_entity(self) -> catalog_entities.CatalogItemImport:
        fields = model_to_dict(self, exclude_fields=set(["data_products"]))
        return catalog_entities.CatalogItemImport(
            **fields,
            data_products=[
                data_product.to_entity() for data_product in self.data_products
            ],
        )

    @classmethod
    def from_entity(
        cls, entity: catalog_entities.CatalogItemImport
    ) -> "CatalogItemImportForm":
        fields = entity_to_dict(entity, exclude_fields=set(["data_products"]))
        return cls(
            **fields,
            data_products=[
                DataProductForm.from_entity(data_product_entity)
                for data_product_entity in entity.data_products
            ],
        )


class CatalogItemData(RootModel[dict[str, Any]]):
    """Catalog Item Data in Json-ld format"""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "@context": {
                        "dcat": "http://www.w3.org/ns/dcat#",
                        "dcterms": "http://purl.org/dc/terms/",
                        "spdx": "http://spdx.org/rdf/terms#",
                        "xsd": "http://www.w3.org/2001/XMLSchema#",
                        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                        "ex": "http://example.org/",
                    },
                    "ex:catalog": {
                        "@type": "dcat:Catalog",
                        "dcterms:identifier": "c6b59f81-e7b5-46d6-84b9-c0dee695c7ec",
                        "dcterms:title": {"@value": "Cancer 2024", "@language": "en"},
                        "dcat:version": "1.0.0",
                        "dcat:dataset": {"@id": "ex:dataset-001"},
                        "dcat:service": {"@id": "ex:data-service-001"},
                    },
                    "ex:dataset-001": {
                        "@type": "dcat:Dataset",
                        "dcterms:identifier": "dataproduct1",
                        "dcterms:title": {
                            "@value": "cancer_data_2024",
                            "@language": "en",
                        },
                        "dcat:distribution": {"@id": "ex:distribution-001"},
                    },
                    "ex:distribution-001": {
                        "@type": "dcat:Distribution",
                        "spdx:checksum": {
                            "@type": "spdx:Checksum",
                            "spdx:algorithm": "spdx:checksumAlgorithm_sha256",
                            "spdx:checksumValue": "3e23e8160039594a33894f6564e1b1348b"
                            "b8e482aa04f83e4d19b84",
                        },
                        "dcat:byteSize": {
                            "@type": "xsd:nonNegativeInteger",
                            "@value": "1024",
                        },
                        "dcat:mediaType": "text/plain",
                        "dcat:accessService": {"@id": "ex:data-service-001"},
                    },
                    "ex:data-service-001": {
                        "@type": "dcat:DataService",
                        "dcat:endpointURL": {
                            "@id": "/connector1/interface2/dataproduct1/"
                        },
                        "dcat:servesDataset": {"@id": "ex:dataset-001"},
                    },
                }
            ]
        }
    }

    @classmethod
    def from_entity(cls, entity: catalog_entities.CatalogItemData) -> "CatalogItemData":
        return cls(entity)

    def to_entity(self) -> catalog_entities.CatalogItemData:
        return catalog_entities.CatalogItemData(self.model_dump())
