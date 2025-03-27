from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class DSPACE(DefinedNamespace):
    _NS = Namespace("http://data-space.org/")

    isShared: URIRef
    extraMetadata: URIRef


class SPDX(DefinedNamespace):
    _NS = Namespace("http://spdx.org/rdf/terms#")


class DCATAP(DefinedNamespace):
    _NS = Namespace("http://data.europa.eu/r5r/")
