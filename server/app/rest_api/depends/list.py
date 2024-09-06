from typing import Annotated

from fastapi import Query

from app.core.queries.list import OrderDirection, OrderQueryDTO, PaginatorQueryDTO


async def paginator_parameters(
    page: int | None = None,
    page_size: Annotated[int | None, Query(alias="pageSize")] = None,
) -> PaginatorQueryDTO:
    return {"page": page or 1, "page_size": page_size or 100}


async def order_parameters(
    order_by: Annotated[str, Query(alias="orderBy")] = "",
    order_direction: Annotated[
        OrderDirection | None, Query(alias="orderDirection")
    ] = None,
) -> OrderQueryDTO:
    return {
        "order_by": order_by,
        "order_direction": order_direction or OrderDirection.ASC,
    }
