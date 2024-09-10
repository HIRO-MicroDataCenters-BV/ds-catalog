from uuid import UUID

from app.core.entities.tests.factories import (
    CatalogItemFactory,
    UserFactory,
    catalog_item_data_factory,
)

from ..entities.catalog import (
    CatalogItem,
    CatalogItemData,
    CatalogItemImport,
    CatalogItemInput,
)
from ..queries import IQuery

DUMMY_USER = UserFactory.build()
DUMMY_CATALOG_ITEMS = [
    CatalogItemFactory.build(),
    CatalogItemFactory.build(),
]
DUMMY_CATALOG_ITEM_DATA = catalog_item_data_factory()


async def get_catalog_items_list(query: IQuery | None = None) -> list[CatalogItem]:
    # TODO: Implement
    return DUMMY_CATALOG_ITEMS


async def get_catalog_item(catalog_item_id: UUID) -> CatalogItem:
    # TODO: Implement
    return DUMMY_CATALOG_ITEMS[0]


async def create_catalog_item(catalog_item_input: CatalogItemInput) -> CatalogItem:
    # TODO: Implement
    return DUMMY_CATALOG_ITEMS[0]


async def update_catalog_item(
    catalog_item_id: UUID,
    catalog_item_input: CatalogItemInput,
) -> CatalogItem:
    # TODO: Implement
    return DUMMY_CATALOG_ITEMS[0]


async def delete_catalog_item(catalog_item_id: UUID) -> None:
    # TODO: Implement
    ...


async def get_catalog_item_data(catalog_item_id: UUID) -> CatalogItemData:
    # TODO: Implement
    return DUMMY_CATALOG_ITEM_DATA


async def create_catalog_item_data(
    catalog_item_id: UUID,
    catalog_item_data: CatalogItemData,
) -> CatalogItemData:
    # TODO: Implement
    return DUMMY_CATALOG_ITEM_DATA


async def change_catalog_item_data(
    catalog_item_id: UUID,
    catalog_item_data: CatalogItemData,
) -> CatalogItemData:
    # TODO: Implement
    return DUMMY_CATALOG_ITEM_DATA


async def delete_catalog_item_data(catalog_item_id: UUID) -> None:
    # TODO: Implement
    ...


async def share_catalog_item(
    catalog_item_id: UUID,
    marketplace_id: UUID,
) -> CatalogItem:
    # TODO: Implement
    return DUMMY_CATALOG_ITEMS[0]


async def import_catalog_item(catalog_item: CatalogItemImport) -> CatalogItem:
    # TODO: Implement
    return DUMMY_CATALOG_ITEMS[0]
