from rdflib import DCAT, DCTERMS, RDF, Literal, URIRef

from app.core import entities
from app.core.namespace import DSPACE

from ..serializers import CatalogFilters, Dataset, HealthCheck
from .factories import UserFactory


class TestHealthCheck:
    def test_common(self) -> None:
        health_check = HealthCheck(status="OK")
        assert health_check.status == "OK"

        health_check = HealthCheck(status="FAIL")
        assert health_check.status == "FAIL"


class TestUser:
    def test_to_entity(self) -> None:
        user = UserFactory.build()
        entity = user.to_entity()

        assert user.id == entity["id"]
        assert user.name == entity["name"]


class TestCatalogFilters:
    def test_to_entity(self):
        data = {
            "@context": {
                "dspace": "http://data-space.org/",
                "med": "http://med.example.org/",
            },
            "@type": "dspace:Filters",
            "dspace:filters": [{"med:code": "I10"}],
        }
        result = CatalogFilters(**data).to_entity()

        assert isinstance(result, entities.CatalogFilters)

        filters = list(result.graph.subjects(RDF.type, DSPACE.Filters))
        assert len(filters) == 1

        attributes = list(result.graph.objects(filters[0], DSPACE.filters))
        assert len(attributes) == 1

        assert (
            attributes[0],
            URIRef("http://med.example.org/code"),
            Literal("I10"),
        ) in result.graph


class TestDataset:
    def test_to_entity(self):
        data = {
            "@context": {
                "dcat": "http://www.w3.org/ns/dcat#",
                "dcterms": "http://purl.org/dc/terms/",
            },
            "@id": "http://example.com/1",
            "@type": "dcat:Dataset",
            "dcterms:title": "Test Dataset",
        }
        result = Dataset(**data).to_entity()

        assert isinstance(result, entities.Dataset)

        dataset = URIRef("http://example.com/1")
        assert (dataset, RDF.type, DCAT.Dataset) in result.graph
        assert (dataset, DCTERMS.title, Literal("Test Dataset")) in result.graph
