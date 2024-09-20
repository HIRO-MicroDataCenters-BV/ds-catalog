from typing import TypedDict

from dataclasses import dataclass

from neomodel import AsyncNodeSet

from .interface import IQuery


class PaginatorQueryDTO(TypedDict):
    page: int
    page_size: int


class OrderQueryDTO(TypedDict):
    order_by: str


@dataclass
class PaginatorQuery(IQuery):
    page: int
    page_size: int

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        query.skip = self.page_size * (self.page - 1)
        query.limit = self.page_size
        return query


@dataclass
class OrderQuery(IQuery):
    order_by: str

    def apply(self, query: AsyncNodeSet) -> AsyncNodeSet:
        if self.order_by == "":
            return query
        return query.order_by(self.order_by)
