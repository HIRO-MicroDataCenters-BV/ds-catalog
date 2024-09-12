from typing import TypedDict, TypeVar, Unpack

from enum import Enum

from sqlalchemy import Select, asc, desc

from .interface import IQuery

T = TypeVar("T")


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PaginatorQueryDTO(TypedDict):
    page: int
    page_size: int


class OrderQueryDTO(TypedDict):
    order_by: str
    order_direction: OrderDirection


class PaginatorQuery(IQuery[T]):
    _page: int
    _page_size: int

    def __init__(self, **kwargs: Unpack[PaginatorQueryDTO]) -> None:
        self._page = kwargs["page"]
        self._page_size = kwargs["page_size"]

    def apply(self, query: Select[tuple[T]]) -> Select[tuple[T]]:
        return query.limit(self._page_size).offset(self._page * self._page_size)


class OrderQuery(IQuery[T]):
    _order_by: str
    _order_direction: OrderDirection

    def __init__(self, **kwargs: Unpack[OrderQueryDTO]) -> None:
        self._order_by = kwargs["order_by"]
        self._order_direction = kwargs["order_direction"]

    def apply(self, query: Select[tuple[T]]) -> Select[tuple[T]]:
        direction = {
            OrderDirection.DESC: desc,
            OrderDirection.ASC: asc,
        }
        direction_func = direction[self._order_direction]
        return query.order_by(direction_func(self._order_by))
