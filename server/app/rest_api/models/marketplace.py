from uuid import UUID

from app.core.entities import catalog as catalog_entities

from .base import BaseModel
from .catalog import CatalogItemForm


class CatalogItemShareForm(BaseModel):
    marketplace_id: UUID


class CatalogItemImportForm(CatalogItemForm):
    id: UUID

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "c6b59f81-e7b5-46d6-84b9-c0dee695c7ec",
                    "ontology": "DCAT-3",
                    "title": "Cancer 2024",
                    "summary": "Some description",
                    "dataProducts": [
                        {
                            "id": "dataproduct1",
                            "name": "cancer_data_2024",
                            "size": 1024,
                            "mimetype": "text/plain",
                            "digest": "1df50e8ad219e34f0b911e097b7b588e31f9b435",
                            "source": {
                                "node": {
                                    "protocol": "https",
                                    "host": "localhost",
                                    "port": 8000,
                                },
                                "connector": {"id": "connector1"},
                                "interface": {"id": "interface2"},
                            },
                            "accessPointUrl": "/connector1/interface2/dataproduct1/",
                        }
                    ],
                }
            ]
        }
    }

    def to_entity(self) -> catalog_entities.CatalogItemImport:
        return catalog_entities.CatalogItemImport(**self.model_dump())
