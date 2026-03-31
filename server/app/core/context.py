from typing import TypedDict

from .entities import User


class Context(TypedDict):
    user: User


class SaveDatasetContext(Context):
    oca_uri: str
    shacl_url: str | None
    ontology_url: str | None
    allowed_catalog_item_types: tuple[str, ...] | list[str]
