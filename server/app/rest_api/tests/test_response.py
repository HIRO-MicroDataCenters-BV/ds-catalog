import json

from rdflib import DCAT, DCTERMS, RDF
from rdflib import Graph as RDFGraph
from rdflib import Literal, URIRef

from app.core.entities import Graph

from ..response import JSONLDResponse


class TestJSONLDResponse:
    def test_common(self):
        class CustomGraph(Graph):
            rdf_type = DCAT.Dataset
            label = "d"

        json_ld = {
            "@context": {
                "dcat": "http://www.w3.org/ns/dcat#",
                "dcterms": "http://purl.org/dc/terms/",
            },
            "@id": "http://example.com/1",
            "@type": "dcat:Dataset",
            "dcterms:title": "Test Dataset",
        }
        graph = CustomGraph.from_json_ld(json.dumps(json_ld))
        response = JSONLDResponse(
            graph, status_code=200, headers={"test key": "test value"}
        )

        assert isinstance(response.body, bytes)
        assert response.status_code == 200
        assert response.headers.get("test key", None) == "test value"

        rdf_graph = RDFGraph()
        rdf_graph.parse(data=response.body, format="json-ld")

        dataset = URIRef("http://example.com/1")
        assert (dataset, RDF.type, DCAT.Dataset) in rdf_graph
        assert (dataset, DCTERMS.title, Literal("Test Dataset")) in rdf_graph
