from typing import TypedDict

from .entities import User


class Context(TypedDict):
    user: User
