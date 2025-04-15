import pytest
from rdflib import DCAT, DCTERMS, FOAF, RDF
from rdflib import Graph as RDFGraph
from rdflib import Literal, URIRef

from ..entities import CONTEXT, Catalog, CatalogFilters, Dataset, Graph, Person, User
from ..exceptions import NodeDoesNotExist
from ..namespace import DSPACE
from .factories import user_factory


class TestUser:
    def test_common(self):
        id = "1"
        name = "Smith"
        user = User(id=id, name=name)
        assert user["id"] == id
        assert user["name"] == name


class TestGraph:
    @pytest.fixture
    def graph_class(self):
        class CustomGraph(Graph):
            rdf_type = DCAT.Catalog
            label = "c"

        return CustomGraph

    def test_init_subclass_raises_exception(self):
        with pytest.raises(TypeError):

            class SubClass(Graph):
                ...

            _ = SubClass()

    def test_str(self, graph_class):
        graph = RDFGraph()

        catalog1 = URIRef("http://example.com/1")
        graph.add((catalog1, RDF.type, DCAT.Catalog))
        graph.add((catalog1, DCTERMS.title, Literal("Catalog 1")))

        catalog2 = URIRef("http://example.com/2")
        graph.add((catalog2, RDF.type, DCAT.Catalog))
        graph.add((catalog2, DCTERMS.title, Literal("Catalog 2")))

        instance = graph_class(graph)
        result = str(instance)

        instance2 = graph_class.from_json_ld(result)
        assert (catalog1, RDF.type, DCAT.Catalog) in instance2.graph
        assert (catalog1, DCTERMS.title, Literal("Catalog 1")) in instance2.graph

        assert (catalog2, RDF.type, DCAT.Catalog) in instance2.graph
        assert (catalog2, DCTERMS.title, Literal("Catalog 2")) in instance2.graph

    def test_add(self, graph_class):
        graph1 = RDFGraph()
        node1 = URIRef("http://example.com/1")
        graph1.add((node1, RDF.type, DCAT.Catalog))
        graph1.add((node1, DCTERMS.title, Literal("Catalog 1")))

        graph2 = RDFGraph()
        node2 = URIRef("http://example.com/2")
        graph2.add((node2, RDF.type, DCAT.Catalog))
        graph2.add((node2, DCTERMS.title, Literal("Catalog 2")))

        instance1 = graph_class(graph1)
        instance2 = graph_class(graph2)

        result = instance1 + instance2

        assert (node1, RDF.type, DCAT.Catalog) in result.graph
        assert (node1, DCTERMS.title, Literal("Catalog 1")) in result.graph

        assert (node2, RDF.type, DCAT.Catalog) in result.graph
        assert (node2, DCTERMS.title, Literal("Catalog 2")) in result.graph

    def test_eq(self, graph_class):
        class AnotherGraph(Graph):
            rdf_type = DCAT.DataService
            label = "ds"

        assert graph_class() == graph_class()
        assert graph_class.create_empty("1") == graph_class.create_empty("1")
        assert graph_class.create_empty("1") != graph_class.create_empty("2")
        assert graph_class() != AnotherGraph()

    def test_create_empty(self, graph_class):
        id = "http://example.com/1"
        result = graph_class.create_empty(id)
        assert isinstance(result, Graph)
        assert (URIRef(id), RDF.type, DCAT.Catalog) in result.graph

    def test_from_json_ld(self, graph_class):
        json_ld = """
        {
            "@context": {
                "dcat": "http://www.w3.org/ns/dcat#",
                "dcterms": "http://purl.org/dc/terms/"
            },
            "@id": "http://example.com/1",
            "@type": "dcat:Catalog",
            "dcterms:title": "Test"
        }
        """
        result = graph_class.from_json_ld(json_ld)
        node = result.uri
        assert str(node) == "http://example.com/1"
        assert (node, RDF.type, DCAT.Catalog) in result.graph
        assert (node, DCTERMS.title, Literal("Test")) in result.graph

    def test_to_json_ld(self, snapshot, graph_class):
        graph = RDFGraph()
        node = URIRef("http://example.com/1")
        graph.add((node, RDF.type, DCAT.Catalog))
        graph.add((node, DCTERMS.title, Literal("Test")))

        instance = graph_class(graph)
        result = instance.to_json_ld()

        snapshot.assert_match(result, "snapshot")

    def test_uri(self, graph_class):
        id = "http://example.org/1"
        instance = graph_class.create_empty(id)
        assert instance.uri == URIRef(id)

    def test_uri_raises_exception(self, graph_class):
        graph = RDFGraph()
        instance = graph_class(graph)
        with pytest.raises(NodeDoesNotExist):
            instance.uri

    def test_get_attribute(self, graph_class):
        title = "Test Title"
        instance = graph_class.create_empty("http://example.org/1")
        instance.set_attribute(DCTERMS.title, title)
        assert str(instance.get_attribute(DCTERMS.title)) == title

    def test_get_default_attribute(self, graph_class):
        default = "123"
        graph = graph_class.create_empty("http://example.org/1")
        result = graph.get_attribute(DCTERMS.title, default)
        assert result == default

    def test_set_attribute(self, graph_class):
        title = "Test Title"
        instance = graph_class.create_empty("http://example.org/1")
        instance.set_attribute(DCTERMS.title, title)
        assert (instance.uri, DCTERMS.title, Literal(title)) in instance.graph


class TestPerson:
    def test_common(self):
        assert Person.rdf_type == FOAF.Person
        assert Person.label == "p"
        assert Person.context == {
            "foaf": str(FOAF),
            "dcterms": str(DCTERMS),
        }

    def test_from_user(self):
        user = user_factory()
        instance = Person.from_user(user)
        assert str(instance.uri) == user["id"]
        assert instance.get_attribute(RDF.type) == FOAF.Person
        assert instance.get_attribute(DCTERMS.identifier) == Literal(user["id"])
        assert instance.get_attribute(FOAF.name) == Literal(user["name"])


class TestCatalogFilters:
    def test_common(self):
        assert CatalogFilters.rdf_type == DSPACE.Filters
        assert CatalogFilters.label == "f"
        assert CatalogFilters.context == CONTEXT


class TestCatalog:
    def test_common(self):
        assert Catalog.rdf_type == DCAT.Catalog
        assert Catalog.label == "c"
        assert Catalog.context == CONTEXT

    def test_create(self):
        title = "Test title"
        description = "Test description"
        instance = Catalog.create(title, description)

        id = str(instance.uri)
        assert instance.get_attribute(RDF.type) == DCAT.Catalog
        assert instance.get_attribute(DCTERMS.identifier) == Literal(id)
        assert instance.get_attribute(DCTERMS.title) == Literal(title)
        assert instance.get_attribute(DCTERMS.description) == Literal(description)


class TestDataset:
    def test_common(self):
        assert Dataset.rdf_type == DCAT.Dataset
        assert Dataset.label == "d"
        assert Dataset.context == CONTEXT
