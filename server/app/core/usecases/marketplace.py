from ..entities.catalog import CatalogItem, CatalogItemImport
from .mock_data import create_dummy_catalog_item


async def share_catalog_item(
    catalog_item: CatalogItem,
    marketplace_id: str,
) -> CatalogItem:
    return catalog_item


async def import_catalog_item(catalog_item: CatalogItemImport) -> CatalogItem:
    return create_dummy_catalog_item(**catalog_item.__dict__)
