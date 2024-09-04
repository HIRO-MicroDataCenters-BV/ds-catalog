from ..entities.catalog import CatalogItem, CatalogItemData, CatalogItemForm
from ..queries import IQuery
from .mock_data import (
    DUMMY_CATALOG_ITEM_DATA,
    DUMMY_CATALOG_ITEMS,
    create_dummy_catalog_item,
)


async def get_catalog_items_list(query: IQuery | None = None) -> list[CatalogItem]:
    return DUMMY_CATALOG_ITEMS


async def get_catalog_item(query: IQuery | None = None) -> CatalogItem:
    return DUMMY_CATALOG_ITEMS[0]


async def create_catalog_item(catalog_item_form: CatalogItemForm) -> CatalogItem:
    return create_dummy_catalog_item(**catalog_item_form.__dict__)


async def update_catalog_item(catalog_item: CatalogItem) -> CatalogItem:
    return catalog_item


async def delete_catalog_item(catalog_item: CatalogItem) -> None:
    ...


async def get_catalog_item_data(catalog_item: CatalogItem) -> CatalogItemData:
    return DUMMY_CATALOG_ITEM_DATA


async def create_catalog_item_data(
    catalog_item: CatalogItem,
    catalog_item_data: CatalogItemData,
) -> CatalogItemData:
    return catalog_item_data


async def change_catalog_item_data(
    catalog_item: CatalogItem,
    catalog_item_data: CatalogItemData,
) -> CatalogItemData:
    return catalog_item_data


async def delete_catalog_item_data(catalog_item: CatalogItem) -> None:
    ...
