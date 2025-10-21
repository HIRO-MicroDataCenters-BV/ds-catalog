from typing import Any, Self, TypedDict, cast

import json
import uuid

import polars as pl
from pyld import jsonld
from rdflib import Graph as RDFGraph
from rdflib import Literal, URIRef
from rdflib.compare import to_isomorphic
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, SKOS, XSD, Namespace

from .exceptions import NodeDoesNotExist
from .namespace import DCATAP, DSPACE, SPDX

CONTEXT = {
    "dspace": str(DSPACE),
    "xsd": str(XSD),
    "dcat": str(DCAT),
    "dcatap": str(DCATAP),
    "dcterms": str(DCTERMS),
    "spdx": str(SPDX),
    "foaf": str(FOAF),
    "skos": str(SKOS),
}


class User(TypedDict):
    id: str
    name: str


class Graph:
    rdf_type: URIRef
    label: str
    context = CONTEXT

    def __init__(self, graph: RDFGraph | None = None) -> None:
        self.graph = RDFGraph() if graph is None else graph

        for prefix, uri in self.get_context().items():
            self.graph.bind(prefix, uri)

    def __str__(self) -> str:
        context = self.get_context()
        return self.graph.serialize(format="json-ld", indent=4, context=context)

    def __add__(self, other):
        """Merge two graphs into one"""
        if not isinstance(other, Graph):
            raise TypeError("Cannot add non-graph object")
        self.graph += other.graph
        return self

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Graph):
            return False
        return (
            to_isomorphic(self.graph) == to_isomorphic(other.graph)
            and self.get_rdf_type() == other.get_rdf_type()
            and self.get_label() == other.get_label()
            and self.get_context() == other.get_context()
        )

    def get_rdf_type(self) -> URIRef:
        if not hasattr(self, "rdf_type"):
            raise AttributeError("rdf_type is not defined")
        return self.rdf_type

    def get_label(self) -> str:
        if not hasattr(self, "label"):
            raise AttributeError("label is not defined")
        return self.label

    def get_context(self) -> dict[str, str]:
        if not hasattr(self, "context"):
            raise AttributeError("context is not defined")
        return self.context

    @classmethod
    def create_empty(cls, id: str) -> Self:
        instance = cls()
        node = URIRef(id)
        instance.graph.add((node, RDF.type, cls.rdf_type))
        return instance

    @classmethod
    def from_json_ld(cls, json_ld: str) -> Self:
        instance = cls()
        instance.graph.parse(data=json_ld, format="json-ld")
        return instance

    def to_json_ld(self) -> str:
        frame = {
            "@context": self.get_context(),
            "@type": self.graph.namespace_manager.qname(self.get_rdf_type()),
        }
        json_ld_str = self.graph.serialize(format="json-ld")
        json_ld = json.loads(json_ld_str)
        framed_json_ld = jsonld.frame(json_ld, frame)
        return json.dumps(framed_json_ld, indent=4)

    @property
    def uri(self) -> URIRef:
        node = next(self.graph.subjects(RDF.type, self.get_rdf_type()), None)
        if node is None:
            raise NodeDoesNotExist("Root node not found in the graph")
        return cast(URIRef, node)

    def get_attribute(self, attr: URIRef, default: Any = None) -> Any:
        return next(self.graph.objects(self.uri, attr), default)

    def set_attribute(
        self,
        attr: URIRef,
        value: URIRef | str | int | bool,
        datatype: URIRef | None = None,
        lang: str | None = None,
    ) -> None:
        obj: Any
        if isinstance(value, URIRef):
            obj = value
        else:
            if lang:
                obj = Literal(value, lang=lang)
            elif datatype:
                obj = Literal(value, datatype=datatype)
            else:
                obj = Literal(value)
        self.graph.add((self.uri, attr, obj))


class Person(Graph):
    rdf_type = FOAF.Person
    label = "p"
    context = {
        "foaf": str(FOAF),
        "dcterms": str(DCTERMS),
    }

    @classmethod
    def from_user(cls, user: User) -> Self:
        person = cls.create_empty(user["id"])
        person.set_attribute(DCTERMS.identifier, user["id"])
        person.set_attribute(FOAF.name, user["name"])
        return person


class CatalogFilters(Graph):
    rdf_type = DSPACE.Filters
    label = "f"


class Catalog(Graph):
    rdf_type = DCAT.Catalog
    label = "c"

    @classmethod
    def create(cls, title: str, description: str) -> Self:
        id = str(uuid.uuid4())
        catalog = cls.create_empty(id)
        catalog.set_attribute(DCTERMS.identifier, id)
        catalog.set_attribute(DCTERMS.title, title)
        catalog.set_attribute(DCTERMS.description, description)
        return catalog


class Dataset(Graph):
    rdf_type = DCAT.Dataset
    label = "d"


class Distribution(Graph):
    """
    Represents a dcat:Distribution — describes how a Dataset is made available.
    Includes all DCAT-AP standard properties and connector-specific extensions.
    """
    rdf_type = DCAT.Distribution
    label = "dist"

    @classmethod
    def create_from_connector_metadata(cls, metadata: dict[str, any]) -> Self:
        """
        Build a dcat:Distribution node from connector-provided metadata.
        Automatically sets all relevant fields if they exist in the metadata.
        """
        dist = cls.create_empty(str(uuid.uuid4()))

        # --- DCAT core & DCAT-AP 3.0 standard properties ---
        if metadata.get("title"):
            dist.set_attribute(DCTERMS.title, metadata["title"])
        if metadata.get("description"):
            dist.set_attribute(DCTERMS.description, metadata["description"])
        if metadata.get("issued"):
            dist.set_attribute(DCTERMS.issued, metadata["issued"], datatype=XSD.dateTime)
        if metadata.get("modified"):
            dist.set_attribute(DCTERMS.modified, metadata["modified"], datatype=XSD.dateTime)
        if metadata.get("license"):
            dist.set_attribute(DCTERMS.license, metadata["license"])
        if metadata.get("rights"):
            dist.set_attribute(DCTERMS.rights, metadata["rights"])
        if metadata.get("access_rights"):
            dist.set_attribute(DCTERMS.accessRights, metadata["access_rights"])
        if metadata.get("access_url"):
            dist.set_attribute(DCAT.accessURL, metadata["access_url"])
        if metadata.get("download_url"):
            dist.set_attribute(DCAT.downloadURL, metadata["download_url"])
        if metadata.get("media_type"):
            dist.set_attribute(DCAT.mediaType, metadata["media_type"])
        if metadata.get("format"):
            dist.set_attribute(DCTERMS.format, metadata["format"])
        if metadata.get("package_format"):
            dist.set_attribute(DCAT.packageFormat, metadata["package_format"])
        if metadata.get("compress_format"):
            dist.set_attribute(DCAT.compressFormat, metadata["compress_format"])
        if metadata.get("byte_size") is not None:
            dist.set_attribute(DCAT.byteSize, str(metadata["byte_size"]), datatype=XSD.nonNegativeInteger)
        if metadata.get("conforms_to"):
            dist.set_attribute(DCTERMS.conformsTo, metadata["conforms_to"])

        # --- SPDX & custom extensions ---
        if metadata.get("checksum"):
            checksum_node = URIRef(f"{dist.uri}/checksum")
            dist.graph.add((dist.uri, SPDX.checksum, checksum_node))
            dist.graph.add((checksum_node, RDF.type, SPDX.Checksum))
            dist.graph.add((checksum_node, SPDX.checksumValue, Literal(metadata["checksum"], datatype=XSD.hexBinary)))

        if metadata.get("access_service"):
            dist.set_attribute(DCAT.accessService, metadata["access_service"])
        if metadata.get("has_policy"):
            dist.set_attribute(DCAT.hasPolicy, metadata["has_policy"])

        # --- Optional: connector region field (custom extension) ---
        if metadata.get("region"):
            dist.set_attribute(DSPACE.region, metadata["region"])

        return dist


class Metadata(Graph):
    """Domain-specific metadata (subgraph of a dataset)"""

    namespace = "dsmeta"

    @staticmethod
    def build_uri(schema_uri: str, id: str, row_index: int) -> URIRef:
        return Namespace(schema_uri.rstrip("/"))[f"/{id}/{row_index}"]

    @staticmethod
    def build_type(schema_uri: str) -> URIRef:
        return Namespace(schema_uri.rstrip("/"))["/Record"]

    @classmethod
    def create_bunch_from_df(
        cls, schema_uri: str, id: str, df: pl.DataFrame
    ) -> list[Self]:
        instances = []

        for i, row in enumerate(df.iter_rows(named=True)):
            ns = Namespace(schema_uri)

            node = cls.build_uri(schema_uri, id, i)
            rdf_type = cls.build_type(schema_uri)

            graph = RDFGraph()
            graph.bind("dsmeta", schema_uri)
            graph.add((node, RDF.type, rdf_type))

            instance = cls(graph)
            instance.rdf_type = rdf_type
            instance.label = f"m-{id}-{i}"
            instance.context = {**cls.context, instance.namespace: schema_uri}

            for key, value in row.items():
                if value is not None:
                    instance.set_attribute(ns[key], Literal(value))

            instances.append(instance)

        return instances
