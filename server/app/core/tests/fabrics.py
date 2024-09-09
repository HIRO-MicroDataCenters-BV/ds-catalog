from polyfactory.factories import DataclassFactory

from ..entities.catalog import (
    CatalogItem,
    CatalogItemInput,
    DataProduct,
    DataProductInput,
)
from ..entities.user import User


class UserFactory(DataclassFactory[User]):
    __model__ = User


class DataProductFactory(DataclassFactory[DataProduct]):
    __model__ = DataProduct


class DataProductInputFactory(DataclassFactory[DataProductInput]):
    __model__ = DataProductInput


class CatalogItemFactory(DataclassFactory[CatalogItem]):
    __model__ = CatalogItem


class CatalogItemInputFactory(DataclassFactory[CatalogItemInput]):
    __model__ = CatalogItemInput
