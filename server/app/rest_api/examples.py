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
}

dataset_body_example: dict[str, Any] = {
    **base_dataset_body_example,
    "dspace:extraMetadata": {
        "@id": "http://oca.example.org/123/"
        "EI2z8E6zYvMF_yvquoUJedWi0rKpQsscPf7JlBgIDoOm/0/0",
        "@type": "http://oca.example.org/123/Record",
        "http://oca.example.org/123/age": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/alanine_aminotransferase": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/albumin": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/alcohol_intake": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/alkaline_phosphatase": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/aspartate_aminotransferase": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/asthma": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/atrial_fibrillation": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/bmi": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/c_reactive_protein": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/calcium": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/chronic_kidney_disease": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/chronic_obstructive_pulmonary_disease": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/creatinine": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/creatinine_in_urine": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/dbp": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/diabetes": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/dietary_habits": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/eGFR": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/education": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/ethnicity": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/ffmi": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/fmi": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/gamma_glutamyl_transferase": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/gender": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/glycated_haemoglobin": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/haemoglobin": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/hdl_cholesterol": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/height": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/hypercholesterolemia": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/hypertension": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/ldl_cholesterol": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/mean_corpuscular_haemoglobin": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/mean_corpuscular_haemoglobin_concentration": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/p_duration": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/patient_id": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/peripheral_artery_disease": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/physical_activity_IPAQ_score": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/platelet_count": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/potassium_in_urine": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/pp_interval": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/previous_myocardial_infarction": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/pulse_rate": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/qrs_duration": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/qt_interval": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/qtc_interval": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/r_axis": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/red_blood_cell_distribution_width": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/sbp": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/sex": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/sleep_duration": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/smoking_history": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/sodium_in_urine": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/stroke": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/t_axis": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/time_using_computer": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/time_watching_TV": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/total_bilirubin": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/townsend_deprivation_index": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/triglycerides": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/urate": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/urea": {"@type": "xsd:boolean", "@value": True},
        "http://oca.example.org/123/ventricular_rate": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/vitamin_d": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/waist_height_ratio": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/waist_hip_ratio": {
            "@type": "xsd:boolean",
            "@value": True,
        },
        "http://oca.example.org/123/white_blood_cell_count": {
            "@type": "xsd:boolean",
            "@value": True,
        },
    },
    "dcterms:issued": {"@type": "xsd:string", "@value": "2025-03-13"},
    "dcterms:publisher": {
        "@id": "https://example.com/person/123",
        "@type": "foaf:Agent",
        "foaf:name": "John Doe",
    },
    "dspace:isShared": {"@type": "xsd:boolean", "@value": False},
    "dspace:isDeleted": {"@type": "xsd:boolean", "@value": False},
    "dspace:metadataFilename": {"@type": "xsd:string", "@value": "mmio-sample.tar"},
}

dataset_example: dict[str, Any] = {
    "@context": context_example,
    **dataset_body_example,
}

dataset_input_example: dict[str, Any] = {
    "@context": context_example,
    **base_dataset_body_example,
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
        "med": "http://oca.example.org/123/",
    },
    "@type": "Filters",
    "filters": [
        {
            "dcat:dataset": {
                "extraMetadata": {
                    "@type": "med:Record",
                    "med:age": True,
                    "med:bmi": True,
                }
            }
        }
    ],
}
