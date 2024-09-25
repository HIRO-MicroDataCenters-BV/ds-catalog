from typing import TypedDict

from .entities import Person


class Context(TypedDict):
    user: Person


class CreateDatasetContext(Context):
    catalog_title: str
    catalog_description: str
