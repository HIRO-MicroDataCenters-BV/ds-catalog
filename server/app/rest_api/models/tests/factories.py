from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from ..catalog import (
    CatalogItem,
    CatalogItemData,
    CatalogItemForm,
    CatalogItemImportForm,
    Connector,
    DataProduct,
    DataProductForm,
    Interface,
    Node,
    Source,
)
from ..user import User


class UserFactory(ModelFactory[User]):
    __model__ = User


class NodeFactory(ModelFactory[Node]):
    __model__ = Node


class ConnectorFactory(ModelFactory[Connector]):
    __model__ = Connector


class InterfaceFactory(ModelFactory[Interface]):
    __model__ = Interface


class SourceFactory(ModelFactory[Source]):
    __model__ = Source

    node = NodeFactory
    connector = ConnectorFactory
    interface = InterfaceFactory


class DataProductFactory(ModelFactory[DataProduct]):
    __model__ = DataProduct

    source = SourceFactory


class DataProductFormFactory(ModelFactory[DataProductForm]):
    __model__ = DataProductForm

    source = SourceFactory


class CatalogItemFactory(ModelFactory[CatalogItem]):
    __model__ = CatalogItem

    data_products = Use(DataProductFactory.batch, size=2)


class CatalogItemFormFactory(ModelFactory[CatalogItemForm]):
    __model__ = CatalogItemForm

    data_products = Use(DataProductFormFactory.batch, size=2)


class CatalogItemImportFormFactory(ModelFactory[CatalogItemImportForm]):
    __model__ = CatalogItemImportForm

    data_products = Use(DataProductFormFactory.batch, size=2)


class CatalogItemDataFactory(ModelFactory[CatalogItemData]):
    __model__ = CatalogItemData
