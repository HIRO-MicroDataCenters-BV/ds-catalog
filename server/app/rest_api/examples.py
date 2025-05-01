from typing import Any

context_example: dict[str, Any] = {
    "dspace": "http://data-space.org/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dcatap": "http://data.europa.eu/r5r/",
    "dcterms": "http://purl.org/dc/terms/",
    "spdx": "http://spdx.org/rdf/terms#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
}

base_dataset_body_example: dict[str, Any] = {
    "@id": "https://example.com/dataset/789",
    "@type": "dcat:Dataset",
    "dcterms:identifier": {"@type": "xsd:string", "@value": "abc-123-xyz"},
    "dcterms:title": [
        {
            "@language": "en",
            "@value": "Sample Dataset Title",
        },
        {
            "@language": "es",
            "@value": "Título del conjunto de " "datos de ejemplo",
        },
    ],
    "dcterms:description": [
        {
            "@language": "en",
            "@value": "This dataset contains " "sample data for testing purposes.",
        },
        {
            "@language": "es",
            "@value": "Este conjunto de datos contiene datos de ejemplo para "
            "fines de prueba.",
        },
    ],
    "dcat:keyword": [
        {"@type": "xsd:string", "@value": "sample"},
        {"@type": "xsd:string", "@value": "data"},
    ],
    "dcterms:license": {
        "@type": "xsd:string",
        "@value": "https://example.com/license/xyz",
    },
    "dcat:theme": [
        {
            "@id": "http://eurovoc.europa.eu/100142",
            "@type": "skos:Concept",
            "skos:prefLabel": {
                "@value": "Agriculture",
                "@language": "en",
            },
        },
        {
            "@id": "http://eurovoc.europa.eu/100141",
            "@type": "skos:Concept",
            "skos:prefLabel": {
                "@value": "Health",
                "@language": "en",
            },
        },
    ],
    "dcat:distribution": [
        {
            "@id": "https://example.com/distribution/489",
            "@type": "dcat:Distribution",
            "dcterms:description": {
                "@language": "en",
                "@value": "This is a sample " "distribution.",
            },
            "dcat:byteSize": {
                "@value": 1024,
                "@type": "xsd:decimal",
            },
            "dcat:mediaType": {
                "@id": "https://www.iana.org"
                "/assignments/media-types/application/json"
            },
            "dcat:format": {"@type": "xsd:string", "@value": "JSON"},
            "dcatap:availability": [{"@id": "http://data.europa.eu/r5r/AVAILABLE"}],
            "spdx:checksum": {
                "spdx:algorithm": {"@type": "xsd:string", "@value": "SHA-256"},
                "spdx:checksumValue": {
                    "@type": "xsd:string",
                    "@value": "3a7bd3e2360a3b5c1b2ef3b1a4e8f7a6",
                },
            },
            "dcat:accessURL": {
                "@id": "https://example.com/distribution/489/information"
            },
            "dcat:accessService": [
                {
                    "@id": "https://example.com/dataservice/456",
                    "@type": "dcat:DataService",
                    "dcterms:title": {
                        "@language": "en",
                        "@value": "Sample Data Service",
                    },
                    "dcat:endpointURL": {
                        "@id": "https://example.com/dataservice/456/download"
                    },
                }
            ],
        }
    ],
    "dcat:inSeries": {"@id": "https://example.com/series/541"},
    "dspace:extraMetadata": [],
}

dataset_body_example: dict[str, Any] = {
    **base_dataset_body_example,
    "dspace:extraMetadata": [
        {
            "@id": "https://example.com/metadata/1",
            "@type": "http://med.example.org/Patient",
            "http://med.example.org/birthDate": {
                "@type": "xsd:string",
                "@value": "1990-05-20",
            },
            "http://med.example.org/height": {"@type": "xsd:long", "@value": "180"},
            "http://med.example.org/sex": {"@type": "xsd:string", "@value": "M"},
            "http://med.example.org/weight": {"@type": "xsd:long", "@value": "75"},
        },
        {
            "@id": "https://example.com/metadata/2",
            "@type": "http://med.example.org/Diagnoses",
            "http://med.example.org/hasDiagnosis": [
                {
                    "@id": "https://example.com" "/diagnosis/1",
                    "@type": "http://med.example.org/Diagnosis",
                    "http://med.example.org/code": {
                        "@type": "xsd:string",
                        "@value": "I10",
                    },
                    "http://med.example.org/description": {
                        "@type": "xsd:string",
                        "@value": "Essential (primary) hypertension",
                    },
                },
                {
                    "@id": "https://example.com" "/diagnosis/2",
                    "@type": "http://med.example.org/Diagnosis",
                    "http://med.example.org/code": {
                        "@type": "xsd:string",
                        "@value": "E11",
                    },
                    "http://med.example.org/description": {
                        "@type": "xsd:string",
                        "@value": "Type 2 diabetes mellitus",
                    },
                },
            ],
        },
    ],
    "dcterms:issued": {"@type": "xsd:string", "@value": "2025-03-13"},
    "dcterms:publisher": {
        "@id": "https://example.com/person/123",
        "@type": "foaf:Agent",
        "foaf:name": "John Doe",
    },
    "dspace:isShared": {"@type": "xsd:boolean", "@value": False},
    "dspace:isDeleted": {"@type": "xsd:boolean", "@value": False},
}

dataset_example: dict[str, Any] = {
    "@context": context_example,
    **dataset_body_example,
}

dataset_input_example: dict[str, Any] = {
    "@context": {
        **context_example,
        "med": "http://med.example.org/",
    },
    **base_dataset_body_example,
    "dspace:extraMetadata": [
        {
            "@id": "https://example.com/metadata/1",
            "@type": "med:Patient",
            "med:birthDate": {"@type": "xsd:string", "@value": "1990-05-20"},
            "med:height": {"@type": "xsd:long", "@value": "180"},
            "med:sex": {"@type": "xsd:string", "@value": "M"},
            "med:weight": {"@type": "xsd:long", "@value": "75"},
        },
        {
            "@id": "https://example.com/metadata/2",
            "@type": "med:Diagnoses",
            "med:hasDiagnosis": [
                {
                    "@id": "https://example.com" "/diagnosis/1",
                    "@type": "med:Diagnosis",
                    "med:code": {"@type": "xsd:string", "@value": "I10"},
                    "med:description": {
                        "@type": "xsd:string",
                        "@value": "Essential (primary) hypertension",
                    },
                },
                {
                    "@id": "https://example.com" "/diagnosis/2",
                    "@type": "med:Diagnosis",
                    "med:code": {"@type": "xsd:string", "@value": "E11"},
                    "med:description": {
                        "@type": "xsd:string",
                        "@value": "Type 2 diabetes mellitus",
                    },
                },
            ],
        },
    ],
}

catalog_example: dict[str, Any] = {
    "@context": context_example,
    "@id": "https://example.com/catalog/123",
    "@type": "dcat:Catalog",
    "dcterms:title": {"@language": "en", "@value": "Sample Catalog"},
    "dcterms:description": {
        "@language": "en",
        "@value": "This is a sample catalog containing "
        "various datasets and services.",
    },
    "dcterms:publisher": {
        "@id": "https://example.com/person/123",
        "@type": "foaf:Agent",
        "foaf:name": "John Doe",
    },
    "dcat:dataset": [
        dataset_body_example,
    ],
}

catalog_filters_example: dict[str, Any] = {
    "@context": {
        "@vocab": "http://data-space.org/",
        "dcat": "http://www.w3.org/ns/dcat#",
        "med": "http://med.example.org/",
    },
    "@type": "Filters",
    "filters": [
        {
            "dcat:dataset": {
                "extraMetadata": {
                    "@type": "med:Diagnoses",
                    "med:hasDiagnosis": {"@type": "med:Diagnosis", "med:code": "I10"},
                }
            }
        }
    ],
}
