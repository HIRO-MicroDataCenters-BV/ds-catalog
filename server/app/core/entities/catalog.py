from typing import Any

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from .user import User


class Ontology(str, Enum):
    DCAT_3 = "DCAT-3"
    DCAT_AP = "DCAT-AP"


@dataclass
class Node:
    protocol: str
    host: str
    port: int


@dataclass
class Interface:
    id: str


@dataclass
class Connector:
    id: str


@dataclass
class Source:
    connector: Connector
    node: Node | None = None
    interface: Interface | None = None


@dataclass
class DataProductBase:
    id: str
    name: str
    size: int | None
    mimetype: str
    digest: str
    source: Source


@dataclass
class DataProduct(DataProductBase):
    _links: dict[str, str]


@dataclass
class DataProductInput(DataProductBase):
    access_point_url: str


@dataclass
class CatalogItemBase:
    ontology: Ontology
    title: str
    summary: str


@dataclass
class CatalogItem(CatalogItemBase):
    id: UUID
    is_local: bool
    is_shared: bool
    created: datetime
    creator: User
    data_products: list[DataProduct]
    _links: dict[str, str]


@dataclass
class CatalogItemInput(CatalogItemBase):
    data_products: list[DataProductInput]


@dataclass
class CatalogItemImport(CatalogItemInput):
    id: UUID


@dataclass
class CatalogItemData:
    data: dict[str, Any]
