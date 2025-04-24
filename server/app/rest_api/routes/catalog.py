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
        user: Annotated[entities.User, Depends(get_user)],
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
          "@type": "Filters",
          "filters": [
            {
              ["@type": "<[namespace:]Class>",]
              "<[namespace:]attribute>": <nestedObject> | <value> | {
                "@value": <value>,
                ["@type": <type> | "@language": <language>]
              }
            }
          ]
        }
        ```

        ### Example:
        ```json
        {
          "@context": {
            "@vocab": "http://data-space.org/",
            "dcat": "http://www.w3.org/ns/dcat#",
            "med": "http://med.example.org/"
          },
          "@type": "Filters",
          "filters": [
            {
              "dcat:dataset": {
                "extraMetadata": {
                  "@type": "med:Diagnoses",
                  "med:hasDiagnosis": {
                    "med:code": "I10"
                  }
                }
              }
            }
          ]
        }
        ```

        ### More filter examples:
        - <b>Filter by dataset identifier</b>
        ```json
            {
                "@type": "dcat:Catalog",
                "dcat:dataset": {
                    "@type": "dcat:Dataset",
                    "dcterms:identifier": "123"
                }
            }
        ```

        - <b>Filtering without specifying classes:</b> The service will attempt to infer
        unspecified classes. If inferencing fails, an error will be returned.
        ```json
            {
                "dcat:dataset": {
                    "dcterms:identifier": "123"
                }
            }
        ```

        - <b>Filtering with language</b>
        ```json
            {
                "dcat:dataset": {
                    "dcterms:title": {
                        "@value": "example",
                        "@language": "en"
                    }
                }
            }
        ```

        - <b>Filtering with data type</b>
        ```json
            {
                "dcat:dataset": {
                    "extraMetadata": {
                        "@type": "med:Patient",
                        "med:height": {
                            "@value": "180",
                            "@type": "xsd:integer"
                        }
                    }
                }
            }
        ```

        - <b>Incomplete filter structure:</b> All datasets with diagnosis code I10
        will be found.
        ```json
            {
                "@type": "med:Diagnosis",
                "med:code": "I10"
            }
        ```
        ```json
            {
                "@type": "med:Diagnoses",
                "med:hasDiagnosis": {
                    "@type": "med:Diagnosis",
                    "med:code": "I10"
                }
            }
        ```

        - <b>Multiple conditions:</b> All datasets with identifier 123 <b>AND</b>
        diagnosis code I10 will be found.
        ```json
            {
                "dcat:dataset": {
                    "dcterms:identifier": "123",
                    "extraMetadata": {
                        "med:hasDiagnosis": {
                            "@type": "med:Diagnosis",
                            "med:code": "I10"
                        }
                    }
                }
            }
        ```

        - <b>Multiple conditions:</b> All datasets with patient height 180 <b>AND</b>
        diagnosis code I10 will be found.
        ```json
            {
                "dcat:dataset": {
                    "extraMetadata": [
                        {
                            "@type": "med:Patient",
                            "med:height": "180"
                        },
                        {
                            "@type": "med:Diagnoses",
                            "med:hasDiagnosis": {
                                "@type": "med:Diagnosis",
                                "med:code": "I10"
                            }
                        }
                    ]
                }
            }
        ```

        - <b>Multiple values:</b> All datasets will be found for which the patient's
        height is 190 <b>OR</b> 180.
        ```json
            {
                "dcat:dataset": {
                    "extraMetadata": [
                        {
                            "@type": "med:Patient",
                            "med:height": [
                                {
                                    "@value": "190",
                                    "@type": "xsd:integer"
                                },
                                {
                                    "@value": "180",
                                    "@type": "xsd:integer"
                                }
                            ]
                        }
                    ]
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
