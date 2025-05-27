from typing import Any

import io
import json
import tarfile

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


def tar_factory(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        for name, content in files.items():
            info = tarfile.TarInfo(name=name)
            data = content.encode()
            info.size = len(data)
            tar.addfile(tarinfo=info, fileobj=io.BytesIO(data))
    buffer.seek(0)
    return buffer.read()
