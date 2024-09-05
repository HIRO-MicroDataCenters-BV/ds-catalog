from ..entities.catalog import CatalogItem, CatalogItemImport
from .mock_data import DUMMY_CATALOG_ITEMS


async def share_catalog_item(
    catalog_item: CatalogItem,
    marketplace_id: str,
) -> CatalogItem:
    return catalog_item


async def import_catalog_item(catalog_item: CatalogItemImport) -> CatalogItem:
    return DUMMY_CATALOG_ITEMS[0]
