from typing import Annotated

from datetime import date

from fastapi import Query

from app.core.queries.catalog import DatasetsFilterDTO


async def datasets_filter(
    search: Annotated[str, Query()] = "",
    theme: Annotated[list[str] | None, Query()] = None,
    is_local: Annotated[bool | None, Query(alias="isLocal")] = None,
    is_shared: Annotated[bool | None, Query(alias="isShared")] = None,
    creator_id: Annotated[str, Query(alias="creator__id")] = "",
    issued: Annotated[date | None, Query()] = None,
    issued_gte: Annotated[date | None, Query(alias="issued__gte")] = None,
    issued_lte: Annotated[date | None, Query(alias="issued__lte")] = None,
    distribution_bytesize_gte: Annotated[
        int | None, Query(ge=0, alias="distribution__byteSize__gte")
    ] = None,
    distribution_bytesize_lte: Annotated[
        int | None, Query(ge=0, alias="distribution__byteSize__lte")
    ] = None,
    distribution_mimetype: Annotated[str, Query(alias="distribution__mimeType")] = "",
) -> DatasetsFilterDTO:
    return {
        "search": search,
        "theme": theme,
        "is_local": is_local,
        "is_shared": is_shared,
        "creator_id": creator_id,
        "issued": issued,
        "issued_gte": issued_gte,
        "issued_lte": issued_lte,
        "distribution_bytesize_gte": distribution_bytesize_gte,
        "distribution_bytesize_lte": distribution_bytesize_lte,
        "distribution_mimetype": distribution_mimetype,
    }
