from typing import Annotated

from datetime import date

from fastapi import Query

from app.core.repository.queries import DatasetsFilterDTO


async def datasets_filter(
    search: Annotated[str, Query()] = "",
    keyword: Annotated[list[str] | None, Query()] = None,
    theme: Annotated[list[str] | None, Query()] = None,
    is_local: Annotated[bool | None, Query(alias="isLocal")] = None,
    is_shared: Annotated[bool | None, Query(alias="isShared")] = None,
    issued: Annotated[date | None, Query()] = None,
    issued_gte: Annotated[date | None, Query(alias="issued__gte")] = None,
    issued_lte: Annotated[date | None, Query(alias="issued__lte")] = None,
) -> DatasetsFilterDTO:
    return {
        "search": search,
        "keyword": keyword,
        "theme": theme,
        "is_local": is_local,
        "is_shared": is_shared,
        "issued": issued,
        "issued_gte": issued_gte,
        "issued_lte": issued_lte,
    }
