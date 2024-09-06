from datetime import datetime

import factory  # type: ignore

from ..entities.catalog import (
    CatalogItem,
    CatalogItemInput,
    Connector,
    DataProduct,
    DataProductInput,
    Interface,
    Node,
    Ontology,
    Source,
)
from ..entities.user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Faker("uuid4")
    full_name = factory.Faker("name")


class NodeFactory(factory.Factory):
    class Meta:
        model = Node

    protocol = "https"
    host = "example.com"
    port = 8000


class ConnectorFactory(factory.Factory):
    class Meta:
        model = Connector

    id = "connector1"


class InterfaceFactory(factory.Factory):
    class Meta:
        model = Interface

    id = "interface1"


class SourceFactory(factory.Factory):
    class Meta:
        model = Source

    node = factory.SubFactory(NodeFactory)
    connector = factory.SubFactory(ConnectorFactory)
    interface = factory.SubFactory(InterfaceFactory)


class BaseDataProductFactory(factory.Factory):
    id = factory.Faker("uuid4")
    name = factory.Faker("word")
    size = factory.Maybe(
        factory.Faker("boolean", chance_of_getting_true=75),
        factory.Faker("random_int", min=1, max=1000),
        None,
    )
    mimetype = factory.Faker("mime_type")
    digest = factory.Faker("md5")
    source = factory.SubFactory(SourceFactory)


class DataProductFactory(BaseDataProductFactory):
    class Meta:
        model = DataProduct

    _links = factory.Dict({"accessPoint": factory.Faker("url")})


class DataProductInputFactory(BaseDataProductFactory):
    class Meta:
        model = DataProductInput

    access_point_url = factory.Faker("url")


class CatalogItemFactory(factory.Factory):
    class Meta:
        model = CatalogItem

    id = factory.Faker("uuid4")
    ontology = Ontology.DCAT_3
    title = factory.Faker("sentence")
    summary = factory.Faker("paragraph")
    is_local = True
    is_shared = False
    created = factory.LazyFunction(datetime.now)
    creator = factory.SubFactory(UserFactory)
    data_products = factory.List([factory.SubFactory(DataProductFactory)])
    _links = factory.Dict({"data": factory.Faker("url")})


class CatalogItemInputFactory(factory.Factory):
    class Meta:
        model = CatalogItemInput

    ontology = Ontology.DCAT_3
    title = factory.Faker("sentence")
    summary = factory.Faker("paragraph")
    data_products = factory.List([factory.SubFactory(DataProductInputFactory)])
