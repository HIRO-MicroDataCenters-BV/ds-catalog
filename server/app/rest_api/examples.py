from typing import Any

context_example: dict[str, Any] = {
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dcatap": "http://data.europa.eu/r5r/",
    "dcterms": "http://purl.org/dc/terms/",
    "spdx": "http://spdx.org/rdf/terms#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dspace": "http://data-space.org/",
}

dataset_example: dict[str, Any] = {
    "@context": context_example,
    "@graph": {
        "@id": "https://example.com/dataset/789",
        "@type": "dcat:Dataset",
        "dcterms:identifier": "abc-123-xyz",
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
                "@value": "Este conjunto de datos "
                "contiene datos de ejemplo para "
                "fines de prueba.",
            },
        ],
        "dcat:keyword": ["sample", "data"],
        "dcterms:license": "https://example.com/license/xyz",
        "dcat:theme": [
            {
                "@id": "http://eurovoc.europa.eu/100142",
                "@type": "skos:Concept",
                "skos:prefLabel": [
                    {
                        "@value": "Agriculture",
                        "@language": "en",
                    }
                ],
            },
            {
                "@id": "http://eurovoc.europa.eu/100141",
                "@type": "skos:Concept",
                "skos:prefLabel": [
                    {
                        "@value": "Health",
                        "@language": "en",
                    }
                ],
            },
        ],
        "dcat:distribution": [
            {
                "@id": "https://example.com/distribution/489",
                "@type": "dcat:Distribution",
                "dcterms:description": [
                    {
                        "@language": "en",
                        "@value": "This is a sample " "distribution.",
                    }
                ],
                "dcat:byteSize": {
                    "@value": 1024,
                    "@type": "xsd:decimal",
                },
                "dcat:mediaType": {
                    "@id": "https://www.iana.org"
                    "/assignments/media-types/application/json"
                },
                "dcat:format": "JSON",
                "dcatap:availability": [
                    {"@id": "http://data.europa.eu" "/r5r/AVAILABLE"}
                ],
                "spdx:checksum": {
                    "spdx:algorithm": "SHA-256",
                    "spdx:checksumValue": "3a7bd3e2360a" "3b5c1b2ef3b1a4e8f7a6",
                },
                "dcat:accessURL": {
                    "@id": "https://example.com" "/distribution/489/information"
                },
                "dcat:accessService": [
                    {
                        "@id": "https://example.com" "/dataservice/456",
                        "@type": "dcat:DataService",
                        "dcterms:title": [
                            {
                                "@language": "en",
                                "@value": "Sample Data Service",
                            }
                        ],
                        "dcat:endpointURL": {
                            "@id": "https://example.com" "/dataservice/456/download"
                        },
                    }
                ],
            }
        ],
        "dcat:inSeries": {"@id": "string"},
        "dspace:extraMetadata": [
            {
                "@id": "https://example.com/metadata/1",
                "@type": "med:Patient",
                "med:height": {
                    "@value": "180",
                    "@type": "xsd:integer",
                },
                "med:weight": {
                    "@value": "75",
                    "@type": "xsd:integer",
                },
                "med:sex": "M",
                "med:birthDate": "1990-05-20",
            },
            {
                "@id": "https://example.com/metadata/2",
                "@type": "med:Diagnoses",
                "med:hasDiagnosis": [
                    {
                        "@id": "https://example.com" "/diagnosis/1",
                        "@type": "med:Diagnosis",
                        "med:code": "I10",
                        "med:description": "Essential " "(primary) hypertension",
                    },
                    {
                        "@id": "https://example.com" "/diagnosis/2",
                        "@type": "med:Diagnosis",
                        "med:code": "E11",
                        "med:description": "Type 2 diabetes " "mellitus",
                    },
                ],
            },
        ],
        "dcterms:issued": "2025-03-13",
        "dcterms:publisher": {
            "@id": "https://example.com/person/123",
            "@type": "foaf:Agent",
            "foaf:name": "John Doe",
        },
        "dspace:isShared": True,
    },
}

dataset_input_example: dict[str, Any] = {
    "@context": context_example,
    "@graph": {
        "@id": "https://example.com/dataset/789",
        "@type": "dcat:Dataset",
        "dcterms:identifier": "abc-123-xyz",
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
                "@value": "Este conjunto de datos "
                "contiene datos de ejemplo para "
                "fines de prueba.",
            },
        ],
        "dcat:keyword": ["sample", "data"],
        "dcterms:license": "https://example.com/license/xyz",
        "dcat:theme": [
            {
                "@id": "http://eurovoc.europa.eu/100142",
                "@type": "skos:Concept",
                "skos:prefLabel": [
                    {
                        "@value": "Agriculture",
                        "@language": "en",
                    }
                ],
            },
            {
                "@id": "http://eurovoc.europa.eu/100141",
                "@type": "skos:Concept",
                "skos:prefLabel": [
                    {
                        "@value": "Health",
                        "@language": "en",
                    }
                ],
            },
        ],
        "dcat:distribution": [
            {
                "@id": "https://example.com/distribution/489",
                "@type": "dcat:Distribution",
                "dcterms:description": [
                    {
                        "@language": "en",
                        "@value": "This is a sample " "distribution.",
                    }
                ],
                "dcat:byteSize": {
                    "@value": 1024,
                    "@type": "xsd:decimal",
                },
                "dcat:mediaType": {
                    "@id": "https://www.iana.org"
                    "/assignments/media-types/application/json"
                },
                "dcat:format": "JSON",
                "dcatap:availability": [
                    {"@id": "http://data.europa.eu" "/r5r/AVAILABLE"}
                ],
                "spdx:checksum": {
                    "spdx:algorithm": "SHA-256",
                    "spdx:checksumValue": "3a7bd3e2360a" "3b5c1b2ef3b1a4e8f7a6",
                },
                "dcat:accessURL": {
                    "@id": "https://example.com" "/distribution/489/information"
                },
                "dcat:accessService": [
                    {
                        "@id": "https://example.com" "/dataservice/456",
                        "@type": "dcat:DataService",
                        "dcterms:title": [
                            {
                                "@language": "en",
                                "@value": "Sample Data Service",
                            }
                        ],
                        "dcat:endpointURL": {
                            "@id": "https://example.com" "/dataservice/456/download"
                        },
                    }
                ],
            }
        ],
        "dspace:extraMetadata": [
            {
                "@id": "https://example.com/metadata/1",
                "@type": "med:Patient",
                "med:height": {
                    "@value": "180",
                    "@type": "xsd:integer",
                },
                "med:weight": {
                    "@value": "75",
                    "@type": "xsd:integer",
                },
                "med:sex": "M",
                "med:birthDate": "1990-05-20",
            },
            {
                "@id": "https://example.com/metadata/2",
                "@type": "med:Diagnoses",
                "med:hasDiagnosis": [
                    {
                        "@id": "https://example.com" "/diagnosis/1",
                        "@type": "med:Diagnosis",
                        "med:code": "I10",
                        "med:description": "Essential " "(primary) hypertension",
                    },
                    {
                        "@id": "https://example.com" "/diagnosis/2",
                        "@type": "med:Diagnosis",
                        "med:code": "E11",
                        "med:description": "Type 2 diabetes " "mellitus",
                    },
                ],
            },
        ],
    },
}

catalog_example: dict[str, Any] = {
    "@context": context_example,
    "@graph": {
        "@id": "https://example.com/catalog/123",
        "@type": "dcat:Catalog",
        "dcterms:title": [{"@language": "en", "@value": "Sample Catalog"}],
        "dcterms:description": [
            {
                "@language": "en",
                "@value": "This is a sample catalog containing "
                "various datasets and services.",
            }
        ],
        "dcterms:publisher": {
            "@id": "https://example.com/person/123",
            "@type": "foaf:Agent",
            "foaf:name": "John Doe",
        },
        "dcat:dataset": [
            dataset_example["@graph"],
        ],
    },
}

catalog_filters_example: dict[str, Any] = {
    "context": {
        "dcat": "http://www.w3.org/ns/dcat#",
        "dspace": "http://data-space.org/",
        "med": "http://med.example.org/",
    },
    "filters": [
        {
            "dcat:dataset": {
                "dspace:extraMetadata": {
                    "type": "med:Diagnoses",
                    "med:hasDiagnosis": {"med:code__contains": "I10"},
                }
            }
        }
    ],
}
