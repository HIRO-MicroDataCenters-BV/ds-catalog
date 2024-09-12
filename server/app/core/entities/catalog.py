from dataclasses import dataclass
from datetime import date

from .person import Person


@dataclass
class DataService:
    endpoint_url: str


@dataclass
class Distribution:
    bytesize: int | None
    mimetype: str
    checksum: str
    access_service: list[DataService]


@dataclass
class Dataset:
    identifier: str
    title: str
    is_local: bool
    is_shared: bool
    issued: date
    theme: list[str]
    creator: Person
    distribution: list[Distribution]


@dataclass
class DatasetInput:
    title: str
    theme: list[str]
    distribution: list[Distribution]


@dataclass
class DatasetImport:
    identifier: str
    title: str
    theme: list[str]
    distribution: list[Distribution]
