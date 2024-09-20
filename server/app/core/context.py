from typing import TypedDict

from .entities import Person


class Context(TypedDict):
    user: Person
