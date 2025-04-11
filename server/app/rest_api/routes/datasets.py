from typing import Annotated

from classy_fastapi import Routable, delete, get, post
from fastapi import Depends, HTTPException, status

from app.core import entities, usecases
from app.core.exceptions import NodeDoesNotExist
from app.core.repository import Repositories

from ..depends import get_repositories, get_user
from ..examples import dataset_example
from ..response import JSONLDResponse
from ..serializers import Dataset
from ..strings import DATASET_NOT_FOUND
from ..tags import Tags


def get_usecases(
    repositories: Repositories = Depends(get_repositories),
) -> usecases.DatasetsUsecases:
    return usecases.DatasetsUsecases(repositories)


class DatasetsRoutes(Routable):
    @post(
        "/datasets/",
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
        data: Dataset,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.DatasetsUsecases = Depends(get_usecases),
    ) -> JSONLDResponse:
        """Create or update a dataset"""
        input_entity = data.to_entity()
        output_entity = await usecases.save(input_entity, context={"user": user})
        return JSONLDResponse(output_entity)

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
