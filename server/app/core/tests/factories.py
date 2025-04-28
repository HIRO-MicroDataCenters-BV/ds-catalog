from typing import Any

import json

from ..entities import CONTEXT, CatalogFilters, User


def user_factory(id: str = "123", name: str = "Smith") -> User:
    return User(id=id, name=name)


def namespace_factory() -> dict[str, str]:
    return {
        **CONTEXT,
        "ns0": "http://med.example.org/",
    }


def catalog_filters_factory(
    filter_items: list[dict[str, Any]] | None = None,
    context: dict[str, str] | None = None,
) -> CatalogFilters:
    context = context if context is not None else CONTEXT
    filter_items = (
        filter_items
        if filter_items is not None
        else [{"dcat:dataset": {"dcterms:identifier": "123"}}]
    )
    json_ld = {
        "@context": context,
        "@type": "dspace:Filters",
        "dspace:filters": filter_items,
    }
    return CatalogFilters.from_json_ld(json.dumps(json_ld))
