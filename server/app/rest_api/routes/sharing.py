from typing import Annotated

from classy_fastapi import Routable, post
from fastapi import Depends, HTTPException, status

from app.core import entities, usecases
from app.core.exceptions import NodeDoesNotExist
from app.core.repository import Repositories

from ..depends import get_repositories, get_user
from ..strings import DATASET_NOT_FOUND
from ..tags import Tags


def get_usecases(
    repositories: Repositories = Depends(get_repositories),
) -> usecases.DatasetSharingUsecases:
    return usecases.DatasetSharingUsecases(repositories)


class DatasetSharingRoutes(Routable):
    @post(
        "/datasets/{id}/share/",
        operation_id="share_dataset",
        name="Share Dataset",
        tags=[Tags.Sharing],
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": DATASET_NOT_FOUND},
        },
    )
    async def share_dataset(
        self,
        id: str,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.DatasetSharingUsecases = Depends(get_usecases),
    ) -> None:
        """Share a dataset"""
        try:
            await usecases.share(id, context={"user": user})
        except NodeDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DATASET_NOT_FOUND,
            )

    @post(
        "/datasets/{id}/unshare/",
        operation_id="unshare_dataset",
        name="Unhare Dataset",
        tags=[Tags.Sharing],
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": DATASET_NOT_FOUND},
        },
    )
    async def unshare_dataset(
        self,
        id: str,
        user: Annotated[entities.User, Depends(get_user)],
        usecases: usecases.DatasetSharingUsecases = Depends(get_usecases),
    ) -> None:
        """Unshare a dataset"""
        try:
            await usecases.unshare(id, context={"user": user})
        except NodeDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DATASET_NOT_FOUND,
            )


routes = DatasetSharingRoutes()
