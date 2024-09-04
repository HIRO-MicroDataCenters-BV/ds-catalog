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
from ..entities.user import User


def create_dummy_data_product(**kwargs) -> DataProduct:
    id = kwargs.pop("id", None)
    if id is None:
        id = str(uuid4())

    attributes = dict(
        id=id,
        name="cancer_data_2024",
        size=1024,
        mimetype="text/plain",
        digest="1df50e8ad219e34f0b911e097b7b588e31f9b435",
        source=Source(
            node=None,
            connector=Connector(id="connector1"),
            interface=Interface(id="interfaceA"),
        ),
        _links={
            "accessPoint": f"/connector1/interfaceA/{id}/",
        },
    )
    attributes.update(kwargs)
    return DataProduct(**attributes)


DUMMY_USER = User(
    id=uuid4(),
    full_name="John Smith",
)
DUMMY_CATALOG_ITEMS = [
    CatalogItem(
        id=uuid4(),
        ontology=Ontology.DCAT_3,
        title="Cancer 2024",
        summary="Description of Cancer 2024",
        is_local=True,
        is_shared=False,
        created=datetime.datetime(2024, 1, 1),
        creator=DUMMY_USER,
        data_products=[
            create_dummy_data_product(name="cancer_dataset_2024_1"),
            create_dummy_data_product(name="cancer_dataset_2024_2"),
        ],
        _links={"data": "/catalog-items/1/data"},
    ),
    CatalogItem(
        id=uuid4(),
        ontology=Ontology.DCAT_AP,
        title="Cancer 2023",
        summary="Description of Cancer 2023",
        is_local=True,
        is_shared=True,
        created=datetime.datetime(2023, 1, 1),
        creator=DUMMY_USER,
        data_products=[
            create_dummy_data_product(name="cancer_dataset_2023"),
        ],
        _links={"data": "/catalog-items/2/data"},
    ),
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
