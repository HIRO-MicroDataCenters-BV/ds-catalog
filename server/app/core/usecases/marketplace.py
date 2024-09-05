from ..entities.catalog import CatalogItem, CatalogItemImport
from .mock_data import DUMMY_CATALOG_ITEMS


async def share_catalog_item(
    catalog_item_id: str,
    marketplace_id: str,
) -> CatalogItem:
    return DUMMY_CATALOG_ITEMS[0]


async def import_catalog_item(catalog_item: CatalogItemImport) -> CatalogItem:
    return DUMMY_CATALOG_ITEMS[0]
