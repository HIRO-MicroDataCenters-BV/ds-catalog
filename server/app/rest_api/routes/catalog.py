from typing import Annotated

from classy_fastapi import Routable, post
from fastapi import Depends

from app.core import entities, usecases
from app.core.repository import Repositories

from ..depends import get_repositories, get_user
from ..examples import catalog_example
from ..response import JSONLDResponse
from ..serializers import CatalogFilters
from ..tags import Tags


def get_usecases(
    repositories: Repositories = Depends(get_repositories),
) -> usecases.CatalogUsecases:
    return usecases.CatalogUsecases(repositories)


class CatalogRoutes(Routable):
    @post(
        "/catalog/",
        operation_id="get_catalog",
        name="Get Local Catalog",
        tags=[Tags.Catalog],
        response_class=JSONLDResponse,
        responses={
            200: {
                "description": "Successful Response",
                "content": {
                    "application/ld+json": {
                        "example": catalog_example,
                    },
                },
            }
        },
    )
    async def get_catalog(
        self,
        filters: CatalogFilters,
        user: Annotated[entities.Person, Depends(get_user)],
        usecases: usecases.CatalogUsecases = Depends(get_usecases),
    ) -> JSONLDResponse:
        """
        Get the local catalog with dataset list.

        The request accepts filters as a JSON-LD object in the body.

        ### Format:
        Filters are structured as nested JSON-LD objects. Each filter defines the path
        to the field with optional operators or language annotations.

        ```json
        {
          "@context": {
            "@vocab": "http://data-space.org/",
            "<namespace>": "<namespaceURL>",
            ...
          }
          "@type": "Filters"
          "filters": [
            {
              ["@type": "<[namespace:]Class>",]
              "<[namespace:]attribute>[@<lang>]": <nestedObject> | <value> | {
                "operation": "<operator>",
                "operationValue": <value>
              }
            },
            ...
          ]
        }
        ```

        ### Supported operators:
        - `gte`, `lte` — range filtering
        - `in` — list filtering
        - `contains` — substring search

        ### Example:
        ```json
        {
          "@context": {
            "@vocab": "http://data-space.org/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "med": "http://med.example.org/"
          },
          "filters": [
            {
              "dcat:dataset": {
                "extraMetadata": {
                  "@type": "med:Diagnoses",
                  "med:hasDiagnosis": {
                    "med:code": {
                      "operation": "contains",
                      "operationValue": "I10"
                    }
                  }
                }
              }
            }
          ]
        }
        ```

        ### More filter examples:
        - ```json
            {
                "dcat:dataset": {
                    "dcterms:title": "example"
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "dcterms:title@en": "example"
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "dcterms:title": {
                        "@language": "en"
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "dcterms:title": {
                        "@value": "example"
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "dcat:distribution": {
                        "dcat:format": "PDF"
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "extraMetadata": {
                        "med:sex": "M"
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "extraMetadata": {
                        "@type": "med:Patient",
                        "med:sex": "M"
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "extraMetadata": {
                        "med:weight": 75
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "extraMetadata": {
                        "med:weight": {
                            "@value": 75
                        }
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "extraMetadata": {
                        "med:weight": {
                            "@type": "xsd:integer"
                        }
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "dcterms:datePublished": {
                        "operationValue": "2021-01-01",
                        "operation": "gte"
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "dcterms:datePublished": {
                        "operationValue": "2021-12-31",
                        "operation": "lte"
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "extraMetadata": {
                        "med:weight": {
                            "operationValue": 70,
                            "operation": "gte"
                        }
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "extraMetadata": {
                        "med:weight": {
                            "operationValue": 70,
                            "operation": "lte"
                        }
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "dcat:keyword": {
                        "operationValue": ["science", "health"],
                        "operation": "in"
                    }
                }
            }
          ```
        - ```json
            {
                "dcat:dataset": {
                    "dcterms:title@en": {
                        "operationValue": "example",
                        "operation": "contains"
                    }
                }
            }
          ```

        """
        filters_entity = filters.to_entity()
        entity = await usecases.get_local_catalog(
            filters_entity, context={"user": user}
        )
        return JSONLDResponse(entity)


routes = CatalogRoutes()
