from typing import Any, Self, TypedDict, cast

from rdflib import RDF
from rdflib import Graph as RDFGraph
from rdflib import Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, SKOS, XSD

from .exceptions import MultipleNodesFound, NodeDoesNotExist
from .namespace import DCATAP, DSPACE, SPDX


class Person(TypedDict):
    id: str
    name: str


class Graph:
    context = {
        "xsd": XSD,
        "dcat": DCAT,
        "dcatap": DCATAP,
        "dcterms": DCTERMS,
        "spdx": SPDX,
        "foaf": FOAF,
        "skos": SKOS,
        "dspace": DSPACE,
    }

    def __init__(self, graph: RDFGraph | None = None) -> None:
        self.graph = RDFGraph() if graph is None else graph

        for prefix, uri in self.context.items():
            self.graph.bind(prefix, uri)

    @classmethod
    def from_json_ld(cls, json_ld: str) -> Self:
        instance = cls()
        instance.graph.parse(data=json_ld, format="json-ld")
        return instance

    def to_json_ld(self) -> str:
        return self.graph.serialize(format="json-ld", indent=4)

    def find_nodes_by_type(
        self, rdf_type: URIRef, unique: bool = False
    ) -> list[URIRef]:
        """Find all resources of the given rdf:type"""
        return [
            cast(URIRef, s)
            for s in self.graph.subjects(RDF.type, rdf_type, unique=unique)
        ]

    def get_node_by_type(self, rdf_type: URIRef) -> URIRef:
        """Find the first resource of the given rdf:type"""
        nodes = self.find_nodes_by_type(rdf_type)
        if not nodes:
            raise NodeDoesNotExist("Node not found in the graph")
        elif len(nodes) > 1:
            raise MultipleNodesFound("Multiple nodes found in the graph")
        return nodes[0]

    def get_attribute(
        self, subject: URIRef, predicate: URIRef, multiple: bool = False
    ) -> Any | list[Any] | None:
        """
        Get the value of an attribute (predicate) for a specific node
        If multiple is True, return a list of values.

        """
        values = [o for o in self.graph.objects(subject, predicate)]
        if not values:
            return None
        return values if multiple else values[0]

    def set_attribute(
        self,
        subject: URIRef,
        predicate: URIRef,
        value: Any,
        datatype_uri: str | None = None,
        lang: str | None = None,
    ) -> None:
        """Set or change an attribute (predicate) for a specific node"""
        self.graph.remove((subject, predicate, None))
        if lang:
            obj = Literal(value, lang=lang)
        elif datatype_uri:
            obj = Literal(value, datatype=URIRef(datatype_uri))
        else:
            obj = Literal(value)
        self.graph.add((subject, predicate, obj))


class Catalog(Graph):
    label = "c"


class Dataset(Graph):
    label = "d"
