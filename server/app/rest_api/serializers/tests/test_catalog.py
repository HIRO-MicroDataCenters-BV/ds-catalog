from app.core.entities.tests import factories as entities_factories

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
from .factories import (
    CatalogItemDataFactory,
    CatalogItemFactory,
    CatalogItemFormFactory,
    CatalogItemImportFormFactory,
    ConnectorFactory,
    DataProductFactory,
    DataProductFormFactory,
    InterfaceFactory,
    NodeFactory,
    SourceFactory,
)


class TestNode:
    def test_to_entity(self):
        node = NodeFactory.build()
        entity = node.to_entity()

        assert node.protocol == entity.protocol
        assert node.host == entity.host
        assert node.port == entity.port

    def test_from_entity(self):
        entity = entities_factories.NodeFactory.build()
        node = Node.from_entity(entity)

        assert node.protocol == entity.protocol
        assert node.host == entity.host
        assert node.port == entity.port


class TestConnector:
    def test_to_entity(self):
        connector = ConnectorFactory.build()
        entity = connector.to_entity()

        assert connector.id == entity.id

    def test_from_entity(self):
        entity = entities_factories.ConnectorFactory.build()
        connector = Connector.from_entity(entity)

        assert connector.id == entity.id


class TestInterface:
    def test_to_entity(self):
        interface = InterfaceFactory.build()
        entity = interface.to_entity()

        assert interface.id == entity.id

    def test_from_entity(self):
        entity = entities_factories.InterfaceFactory.build()
        interface = Interface.from_entity(entity)

        assert interface.id == entity.id


class TestSource:
    def test_to_entity(self):
        source = SourceFactory.build()
        entity = source.to_entity()

        assert source.node is not None
        assert entity.node == source.node.to_entity()
        assert entity.connector == source.connector.to_entity()
        assert source.interface is not None
        assert entity.interface == source.interface.to_entity()

    def test_from_entity(self):
        entity = entities_factories.SourceFactory.build()
        source = Source.from_entity(entity)

        assert entity.node is not None
        assert source.node == Node.from_entity(entity.node)
        assert source.connector == Connector.from_entity(entity.connector)
        assert entity.interface is not None
        assert source.interface == Interface.from_entity(entity.interface)


class TestDataProduct:
    def test_to_entity(self):
        data_product = DataProductFactory.build()
        entity = data_product.to_entity()

        assert entity.id == data_product.id
        assert entity.name == data_product.name
        assert entity.size == data_product.size
        assert entity.mimetype == data_product.mimetype
        assert entity.digest == data_product.digest
        assert entity.source == data_product.source.to_entity()

    def test_from_entity(self):
        entity = entities_factories.DataProductFactory.build()
        data_product = DataProduct.from_entity(entity)

        assert data_product.id == entity.id
        assert data_product.name == entity.name
        assert data_product.size == entity.size
        assert data_product.mimetype == entity.mimetype
        assert data_product.digest == entity.digest
        assert data_product.source == Source.from_entity(entity.source)


class TestDataProductForm:
    def test_to_entity(self):
        product_form = DataProductFormFactory.build()
        entity = product_form.to_entity()

        assert entity.id == product_form.id
        assert entity.name == product_form.name
        assert entity.size == product_form.size
        assert entity.mimetype == product_form.mimetype
        assert entity.digest == product_form.digest
        assert entity.source == product_form.source.to_entity()

    def test_from_entity(self):
        entity = entities_factories.DataProductInputFactory.build()
        data_product_form = DataProductForm.from_entity(entity)

        assert data_product_form.id == entity.id
        assert data_product_form.name == entity.name
        assert data_product_form.size == entity.size
        assert data_product_form.mimetype == entity.mimetype
        assert data_product_form.digest == entity.digest
        assert data_product_form.source == Source.from_entity(entity.source)


class TestCatalogItem:
    def test_to_entity(self):
        catalog_item = CatalogItemFactory.build()
        entity = catalog_item.to_entity()

        assert entity.id == catalog_item.id
        assert entity.ontology == catalog_item.ontology
        assert entity.title == catalog_item.title
        assert entity.summary == catalog_item.summary
        assert entity.is_local == catalog_item.is_local
        assert entity.is_shared == catalog_item.is_shared
        assert entity.created == catalog_item.created
        assert entity.creator == catalog_item.creator.to_entity()
        assert entity.data_products == [
            data_product.to_entity() for data_product in catalog_item.data_products
        ]
        assert entity.links == catalog_item.links

    def test_from_entity(self):
        entity = entities_factories.CatalogItemFactory.build()
        catalog_item = CatalogItem.from_entity(entity)

        assert catalog_item.id == entity.id
        assert catalog_item.ontology == entity.ontology
        assert catalog_item.title == entity.title
        assert catalog_item.summary == entity.summary
        assert catalog_item.is_local == entity.is_local
        assert catalog_item.is_shared == entity.is_shared
        assert catalog_item.created == entity.created
        assert catalog_item.creator == User.from_entity(entity.creator)
        assert catalog_item.data_products == [
            DataProduct.from_entity(data_product)
            for data_product in entity.data_products
        ]
        assert catalog_item.links == entity.links


class TestCatalogItemForm:
    def test_to_entity(self):
        catalog_item_form = CatalogItemFormFactory.build()
        entity = catalog_item_form.to_entity()

        assert entity.ontology == catalog_item_form.ontology
        assert entity.title == catalog_item_form.title
        assert entity.summary == catalog_item_form.summary
        assert entity.data_products == [
            data_product.to_entity() for data_product in catalog_item_form.data_products
        ]

    def test_from_entity(self):
        entity = entities_factories.CatalogItemInputFactory.build()
        catalog_item_form = CatalogItemForm.from_entity(entity)

        assert catalog_item_form.ontology == entity.ontology
        assert catalog_item_form.title == entity.title
        assert catalog_item_form.summary == entity.summary
        assert catalog_item_form.data_products == [
            DataProductForm.from_entity(data_product)
            for data_product in entity.data_products
        ]


class TestCatalogItemImportForm:
    def test_to_entity(self):
        catalog_item_import = CatalogItemImportFormFactory.build()
        entity = catalog_item_import.to_entity()

        assert entity.id == catalog_item_import.id
        assert entity.ontology == catalog_item_import.ontology
        assert entity.title == catalog_item_import.title
        assert entity.summary == catalog_item_import.summary
        assert entity.data_products == [
            data_product.to_entity()
            for data_product in catalog_item_import.data_products
        ]

    def test_from_entity(self):
        entity = entities_factories.CatalogItemImportFactory.build()
        catalog_item_import = CatalogItemImportForm.from_entity(entity)

        assert catalog_item_import.id == entity.id
        assert catalog_item_import.ontology == entity.ontology
        assert catalog_item_import.title == entity.title
        assert catalog_item_import.summary == entity.summary
        assert catalog_item_import.data_products == [
            DataProductForm.from_entity(data_product)
            for data_product in entity.data_products
        ]


class TestCatalogItemData:
    def test_to_entity(self):
        catalog_item_data = CatalogItemDataFactory.build()
        entity = catalog_item_data.to_entity()

        assert entity == catalog_item_data.model_dump()

    def test_from_entity(self):
        entity = entities_factories.catalog_item_data_factory()
        catalog_item_data = CatalogItemData.from_entity(entity)

        assert entity == catalog_item_data.model_dump()
