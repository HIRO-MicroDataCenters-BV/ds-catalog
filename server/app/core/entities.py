from datetime import date

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str


class Checksum(BaseModel):
    algorithm: str
    checksum_value: str


class DataService(BaseModel):
    endpoint_url: str


class Distribution(BaseModel):
    byte_size: int | None
    media_type: str
    checksum: Checksum
    access_service: list[DataService]


class DatasetInput(BaseModel):
    title: str
    theme: list[str]
    distribution: list[Distribution]


class NewDataset(DatasetInput):
    is_local: bool
    is_shared: bool
    creator: Person


class Dataset(NewDataset):
    identifier: str
    issued: date


class DatasetImport(DatasetInput):
    identifier: str
