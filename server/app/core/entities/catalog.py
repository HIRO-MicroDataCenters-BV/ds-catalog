from typing import Any

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from .users import User


class Ontology(Enum):
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
    size: int
    mimetype: str
    digest: str
    source: Source


@dataclass
class DataProduct(DataProductBase):
    _links: dict[str, str]


@dataclass
class DataProductForm(DataProductBase):
    accessPointUrl: str


@dataclass
class CatalogItemBase:
    ontology: Ontology
    title: str
    summary: str
    data_products: list[DataProductForm]


@dataclass
class CatalogItem(CatalogItemBase):
    id: UUID
    is_local: bool
    is_shared: bool
    created: datetime
    creator: User
    _links: dict[str, str]


@dataclass
class CatalogItemForm(CatalogItemBase):
    ...


@dataclass
class CatalogItemImport(CatalogItemBase):
    id: UUID


@dataclass
class CatalogItemData:
    data: dict[str, Any]
