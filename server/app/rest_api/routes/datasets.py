from typing import Annotated

from classy_fastapi import Routable, delete, get, post
from fastapi import Depends, HTTPException, Path, Query, status
from fastapi.exceptions import RequestValidationError

from app.core import entities, usecases
from app.core.exceptions import (
    ConnectorError,
    DistributionNotFound,
    ErrorParsingMMIO,
    GraphValidationError,
    InvalidDatasetError,
    NodeDoesNotExist,
)
from app.core.repository import Repositories
from app.settings import Settings, get_settings

from ..depends import get_repositories, get_user
from ..examples import dataset_example
from ..response import JSONLDResponse
from ..serializers import Dataset
from ..strings import DATASET_NOT_FOUND, FILE_NOT_FOUND
from ..tags import Tags


def get_usecases(
    repositories: Repositories = Depends(get_repositories),
) -> usecases.DatasetsUsecases:
    return usecases.DatasetsUsecases(repositories)


class DatasetsRoutes(Routable):
    @post(
        "/datasets/{filename}/",
        operation_id="save_dataset",
        name="Save Dataset",
        tags=[Tags.Datasets],
        response_class=JSONLDResponse,
        responses={
            200: {
                "description": "Successful Response",
                "content": {
                    "application/ld+json": {
                        "example": dataset_example,
                    },
                },
            }
        },
    )
    async def save_dataset(
        self,
        dataset: Dataset,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.DatasetsUsecases = Depends(get_usecases),
        settings: Settings = Depends(get_settings),
        filename: str = Path(
            ...,
            description="The name of the uploaded MMIO file.",
            examples=["mmio-sample.tar"],
        ),
        related_data_product: str = Query(
            None,
            description="Path to the related data product directory.",
            examples=["file:///data/disease_xyz/"],
        ),
    ) -> JSONLDResponse:
        """
        Create or update a dataset or application.

        This endpoint saves a new catalog item (or updates an existing one) using the
        metadata provided in the request body. The input
        must follow **DCAT-AP 3.0 JSON-LD**.

        ### Notes
        - Items are always stored as `dcat:Dataset`.
        - You can represent either:
            - A **dataset** (`dcterms:type = Dataset`)
            - An **application** (`dcterms:type = Software`)

        ### Example: Dataset
        ```json
        {
          "@context": {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dcterms": "http://purl.org/dc/terms/",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
          },
          "@id": "https://example.com/dataset/789",
          "@type": "dcat:Dataset",
          "dcterms:identifier": { "@type": "xsd:string", "@value": "abc-123-xyz" },
          "dcterms:title": { "@language": "en", "@value": "Sample Dataset" },
          "dcterms:description": { "@language": "en",
           "@value": "This dataset contains CSV data." },
          "dcterms:type": {
            "@id": "http://purl.org/dc/dcmitype/Dataset",
            "@type": "skos:Concept",
            "skos:prefLabel": { "@language": "en", "@value": "Dataset" }
          },
          "dcat:distribution": [
            {
              "@type": "dcat:Distribution",
              "dcat:accessURL": {
              "@id": "https://example.com/distribution/489/info" },
              "dcterms:format": {
                "@id": "https://www.iana.org/assignments/media-types/text/csv",
                "@type": "dcterms:MediaTypeOrExtent",
                "skos:prefLabel": { "@language": "en", "@value": "CSV" }
              }
            }
          ]
        }
        ```

        ### Example: Application (Software)
        ```json
        {
          "@context": {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dcterms": "http://purl.org/dc/terms/",
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
          },
          "@id": "https://example.com/dataset/5678",
          "@type": "dcat:Dataset",
          "dcterms:identifier": { "@type": "xsd:string", "@value": "5678" },
          "dcterms:title": { "@language": "en", "@value": "Image Application" },
          "dcterms:description": { "@language": "en",
           "@value": "A containerized app for satellite image analysis." },
          "dcterms:type": {
            "@id": "http://purl.org/dc/dcmitype/Software",
            "@type": "skos:Concept",
            "skos:prefLabel": { "@language": "en", "@value": "Software" }
          },
          "dcat:distribution": [
            {
              "@type": "dcat:Distribution",
              "dcat:accessURL": {
              "@id": "https://ghcr.io/my-org/image-analysis:1.0.0" },
              "dcterms:format": {
                "@id": "https://www.iana.org/assignments/media-types/
                application/vnd.docker.distribution.manifest.v2+json",
                "@type": "dcterms:MediaTypeOrExtent",
                "skos:prefLabel": { "@language": "en", "@value": "Docker Image v2" }
              }
            }
          ]
        }
        ```

        """

        input_entity = dataset.to_entity()

        try:
            output_entity, errors = await usecases.save(
                input_entity,
                filename,
                related_data_product=related_data_product,
                context={
                    "user": user,
                    "oca_uri": settings.oca_uri,
                    "shacl_url": settings.shacl_url,
                    "ontology_url": settings.ontology_url,
                    "allowed_values_config_path": settings.allowed_values_config_path,
                },
            )
        except ValueError as err:
            # Raised when accessURL is outside related_data_product
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(err),
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=FILE_NOT_FOUND,
            )

        except DistributionNotFound as err:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(err),
            )
        except InvalidDatasetError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(err),
            )
        except ConnectorError as err:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Connector service error: {err}",
            )

        except ErrorParsingMMIO as err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(err),
            )
        except GraphValidationError as err:
            raise RequestValidationError(
                errors=[
                    {
                        "code": err.code,
                        "message": err.message,
                        "details": err.details,
                    }
                ]
            )

        return JSONLDResponse(
            output_entity,
            headers={
                "X-MMIO-Errors": "; ".join(e.replace("\n", " ") for e in errors)
                if errors
                else ""
            },
            status_code=200,
        )

    @get(
        "/datasets/{id}/",
        operation_id="get_dataset",
        name="Get Dataset",
        tags=[Tags.Datasets],
        response_class=JSONLDResponse,
        responses={
            200: {
                "description": "Successful Response",
                "content": {
                    "application/ld+json": {
                        "example": dataset_example,
                    },
                },
            },
            status.HTTP_404_NOT_FOUND: {"description": DATASET_NOT_FOUND},
        },
    )
    async def get_dataset(
        self,
        id: str,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.DatasetsUsecases = Depends(get_usecases),
    ) -> JSONLDResponse:
        """Get a dataset"""
        try:
            entity = await usecases.get(id, context={"user": user})
        except NodeDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DATASET_NOT_FOUND,
            )
        return JSONLDResponse(entity)

    @delete(
        "/datasets/{id}/",
        operation_id="delete_dataset",
        name="Delete Dataset",
        tags=[Tags.Datasets],
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": DATASET_NOT_FOUND},
        },
    )
    async def delete_dataset(
        self,
        id: str,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.DatasetsUsecases = Depends(get_usecases),
    ) -> None:
        """Delete a dataset"""
        try:
            await usecases.delete(id, context={"user": user})
        except NodeDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DATASET_NOT_FOUND,
            )


routes = DatasetsRoutes()
