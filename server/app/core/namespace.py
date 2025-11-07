from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class DSPACE(DefinedNamespace):
    _NS = Namespace("http://data-space.org/")

    # Classes
    Filters: URIRef

    # Properties
    isShared: URIRef
    isDeleted: URIRef
    extraMetadata: URIRef
    metadataFilename: URIRef
    operationValue: URIRef
    operation: URIRef
    filters: URIRef
    region: URIRef


class SPDX(DefinedNamespace):
    _NS = Namespace("http://spdx.org/rdf/terms#")

    # Classes
    Checksum: URIRef

    # Properties
    checksum: URIRef
    checksumValue: URIRef
    algorithm: URIRef

    # Algorithm values
    SHA256: URIRef


class DCATAP(DefinedNamespace):
    _NS = Namespace("http://data.europa.eu/r5r/")
    hasPolicy: URIRef
