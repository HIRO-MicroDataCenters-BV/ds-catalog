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

        The request accepts filters as a JSON object in the body.

        ### Format:
        Filters are structured as nested JSON objects. Each filter defines the path
        to the field with optional operators or language annotations.

        ```json
        {
          "context": {
            "<namespace>": "<namespaceURL>",
            ...
          }
          "filters": [
            {
              ["type": "<namespace:Class>",]
              "<namespace:attribute>[@<lang>][__operator]": <value> | <nestedObject>
            },
            ...
          ]
        }
        ```

        ### Supported operators:
        - `__gte`, `__lte` — range filtering
        - `__in` — list filtering
        - `__contains` — substring search

        ### Example:
        ```json
        {
          "context": {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dspace": "http://data-space.org/",
            "med": "http://med.example.org/"
          },
          "filters": [
            {
              "dcat:dataset": {
                "dspace:extraMetadata": {
                  "type": "med:Diagnoses",
                  "med:hasDiagnosis": {
                    "med:code__contains": "I10"
                  }
                }
              }
            }
          ]
        }
        ```

        ### More filter examples:
        - ```json
          { "dcat:dataset": { "dcterms:title": "example" } }
          ```
        - ```json
          { "dcat:dataset": { "dcterms:title@en": "example" } }
          ```
        - ```json
          { "dcat:dataset": { "dcterms:title": { "@language": "en" } } }
          ```
        - ```json
          { "dcat:dataset": { "dcterms:title": { "@value": "example" } } }
          ```
        - ```json
          { "dcat:dataset": { "dcat:distribution": { "dcat:format": "PDF" } } }
          ```
        - ```json
          { "dcat:dataset": { "dspace:extraMetadata": { "med:sex": "M" } } }
          ```
        - ```json
          { "dcat:dataset": { "dspace:extraMetadata": { "type": "med:Patient",
          "med:sex": "M" } } }
          ```
        - ```json
          { "dcat:dataset": { "dspace:extraMetadata": { "med:weight": 75 } } }
          ```
        - ```json
          { "dcat:dataset": { "dspace:extraMetadata": { "med:weight": {
          "@value": 75 } } } }
          ```
        - ```json
          { "dcat:dataset": { "dspace:extraMetadata": { "med:weight": {
          "@type": "xsd:integer" } } } }
          ```
        - ```json
          { "dcat:dataset": { "dcterms:datePublished__gte": "2021-01-01" } }
          ```
        - ```json
          { "dcat:dataset": { "dcterms:datePublished__lte": "2021-12-31" } }
          ```
        - ```json
          { "dcat:dataset": { "dspace:extraMetadata": { "med:weight__gte": 70 } } }
          ```
        - ```json
          { "dcat:dataset": { "dspace:extraMetadata": { "med:weight__lte": 70 } } }
          ```
        - ```json
          { "dcat:dataset": { "dcat:keyword__in": ["science", "health"] } }
          ```
        - ```json
          { "dcat:dataset": { "dcterms:title@en__contains": "example" } }
          ```

        """
        query = filters.to_entity()
        entity = await usecases.get_local_catalog(query, context={"user": user})
        return JSONLDResponse(entity)


routes = CatalogRoutes()
