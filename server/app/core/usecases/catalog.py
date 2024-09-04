from ..entities.catalog import CatalogItem, CatalogItemData, CatalogItemInput
from ..queries import IQuery
from .mock_data import DUMMY_CATALOG_ITEM_DATA, DUMMY_CATALOG_ITEMS


async def get_catalog_items_list(query: IQuery | None = None) -> list[CatalogItem]:
    return DUMMY_CATALOG_ITEMS


async def get_catalog_item(catalog_item_id: str) -> CatalogItem:
    return DUMMY_CATALOG_ITEMS[0]


async def create_catalog_item(catalog_item_input: CatalogItemInput) -> CatalogItem:
    return DUMMY_CATALOG_ITEMS[0]


async def update_catalog_item(
    catalog_item_id: str,
    catalog_item_input: CatalogItemInput,
) -> CatalogItem:
    return DUMMY_CATALOG_ITEMS[0]


async def delete_catalog_item(catalog_item_id: str) -> None:
    ...


async def get_catalog_item_data(catalog_item_id: str) -> CatalogItemData:
    return DUMMY_CATALOG_ITEM_DATA


async def create_catalog_item_data(
    catalog_item_id: str,
    catalog_item_data: CatalogItemData,
) -> CatalogItemData:
    return DUMMY_CATALOG_ITEM_DATA


async def change_catalog_item_data(
    catalog_item_id: str,
    catalog_item_data: CatalogItemData,
) -> CatalogItemData:
    return DUMMY_CATALOG_ITEM_DATA


async def delete_catalog_item_data(catalog_item_id: str) -> None:
    ...
