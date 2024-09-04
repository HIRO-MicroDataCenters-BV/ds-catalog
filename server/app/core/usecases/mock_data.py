import datetime
from uuid import uuid4

from ..entities.catalog import (
    CatalogItem,
    CatalogItemData,
    Connector,
    DataProduct,
    Interface,
    Ontology,
    Source,
)
from ..entities.users import User


def create_dummy_data_product():
    return DataProduct(
        id="dataproduct1",
        name="cancer_data_2024",
        size=1024,
        mimetype="text/plain",
        digest="1df50e8ad219e34f0b911e097b7b588e31f9b435",
        source=Source(
            node=None,
            connector=Connector(id="connector1"),
            interface=Interface(id="interface2"),
        ),
        _links={
            "accessPoint": "/connector1/interface2/dataproduct1/",
        },
    )


def create_dummy_catalog_item(**kwargs) -> CatalogItem:
    id = kwargs.pop("id", None)
    if id is None:
        id = uuid4()

    attributes = dict(
        id=id,
        ontology=Ontology.DCAT_3,
        title="Cancer 2024",
        summary="Some description",
        is_local=True,
        is_shared=False,
        created=datetime.datetime.now(),
        creator=User(
            id=uuid4(),
            full_name="John Smith",
        ),
        data_products=[
            create_dummy_data_product(),
        ],
        _links={"data": f"/catalog-items/{id}/data"},
    )
    attributes.update(kwargs)
    return CatalogItem(**attributes)


DUMMY_CATALOG_ITEMS = [
    create_dummy_catalog_item(title="Cancer 2022"),
    create_dummy_catalog_item(title="Cancer 2023"),
    create_dummy_catalog_item(title="Cancer 2024"),
]
DUMMY_CATALOG_ITEM_DATA = CatalogItemData(
    {
        "@context": {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dcterms": "http://purl.org/dc/terms/",
            "spdx": "http://spdx.org/rdf/terms#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "ex": "http://example.org/",
        },
        "ex:catalog": {
            "@type": "dcat:Catalog",
            "dcterms:identifier": "c6b59f81-e7b5-46d6-84b9-c0dee695c7ec",
            "dcterms:title": {
                "@value": "Cancer 2024",
                "@language": "en",
            },
            "dcat:version": "1.0.0",
            "dcat:dataset": {
                "@id": "ex:dataset-001",
            },
            "dcat:service": {
                "@id": "ex:data-service-001",
            },
        },
        "ex:dataset-001": {
            "@type": "dcat:Dataset",
            "dcterms:identifier": "dataproduct1",
            "dcterms:title": {
                "@value": "cancer_data_2024",
                "@language": "en",
            },
            "dcat:distribution": {
                "@id": "ex:distribution-001",
            },
        },
        "ex:distribution-001": {
            "@type": "dcat:Distribution",
            "spdx:checksum": {
                "@type": "spdx:Checksum",
                "spdx:algorithm": "spdx:checksumAlgorithm_sha256",
                "spdx:checksumValue": "3e23e8160039594a33894f6564e1b1348bb8e482aa04f8"
                "3e4d19b84",
            },
            "dcat:byteSize": {
                "@type": "xsd:nonNegativeInteger",
                "@value": "1024",
            },
            "dcat:mediaType": "text/plain",
            "dcat:accessService": {
                "@id": "ex:data-service-001",
            },
        },
        "ex:data-service-001": {
            "@type": "dcat:DataService",
            "dcat:endpointURL": {
                "@id": "/connector1/interface2/dataproduct1/",
            },
            "dcat:servesDataset": {
                "@id": "ex:dataset-001",
            },
        },
    }
)
