from typing import Annotated

from fastapi import Query

from app.core.repository.queries import OrderQueryDTO, PaginatorQueryDTO


async def paginator_parameters(
    page: Annotated[int | None, Query(ge=1)] = None,
    page_size: Annotated[int | None, Query(alias="pageSize", ge=1, le=100)] = None,
) -> PaginatorQueryDTO:
    return {"page": page or 1, "page_size": page_size or 100}


async def order_parameters(
    order_by: Annotated[str, Query(alias="orderBy")] = "",
) -> OrderQueryDTO:
    return {"order_by": order_by}
