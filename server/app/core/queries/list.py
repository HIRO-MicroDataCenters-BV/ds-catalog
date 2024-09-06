from typing import TypedDict, Unpack

from enum import Enum

from .interface import IQuery, QueryResult


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PaginatorQueryDTO(TypedDict):
    page: int
    page_size: int


class OrderQueryDTO(TypedDict):
    order_by: str
    order_direction: OrderDirection


class PaginatorQuery(IQuery):
    _page: int
    _page_size: int

    def __init__(self, **kwargs: Unpack[PaginatorQueryDTO]) -> None:
        self._page = kwargs["page"]
        self._page_size = kwargs["page_size"]

    def build(self) -> QueryResult:
        # TODO: Implement
        return QueryResult()


class OrderQuery(IQuery):
    _order_by: str
    _order_direction: OrderDirection

    def __init__(self, **kwargs: Unpack[OrderQueryDTO]) -> None:
        self._order_by = kwargs["order_by"]
        self._order_direction = kwargs["order_direction"]

    def build(self) -> QueryResult:
        # TODO: Implement
        return QueryResult()
