from typing import Annotated

from abc import ABC, abstractmethod

from classy_fastapi import Routable, post
from fastapi import Depends, HTTPException, Request, Response, status
from pydantic import AnyUrl

from app.core import entities, usecases
from app.core.context import Context
from app.core.exceptions import DatasetDoesNotExist, DatasetSharingError

from ..depends.user import get_user
from ..serializers.catalog import Dataset, DatasetShareForm
from ..strings import DATASET_NOT_FOUND
from ..tags import Tags


class IDatasetsSharingUsecases(ABC):
    @abstractmethod
    async def share(
        self,
        id: str,
        marketplace_url: AnyUrl,
        context: Context,
    ) -> entities.Dataset:
        ...


class DatasetsSharingUsecases(IDatasetsSharingUsecases):
    async def share(self, *args, **kwargs):
        return await usecases.share_dataset(*args, **kwargs)


class DatasetsSharingRoutes(Routable):
    _usecases: IDatasetsSharingUsecases

    def __init__(self, usecases: IDatasetsSharingUsecases) -> None:
        self._usecases = usecases
        super().__init__()

    @post(
        "/datasets/{id}/share/",
        operation_id="share_dataset",
        tags=[Tags.Sharing],
        status_code=status.HTTP_201_CREATED,
        response_model=Dataset,
        responses={
            status.HTTP_201_CREATED: {
                "description": "Successful Response",
                "headers": {
                    "Location": {
                        "description": "The URL of the newly created resource",
                        "schema": {
                            "type": "string",
                            "format": "uri",
                        },
                    },
                },
            },
            status.HTTP_404_NOT_FOUND: {"description": "Dataset not found"},
        },
    )
    async def share_dataset(
        self,
        id: str,
        data: DatasetShareForm,
        request: Request,
        response: Response,
        user: Annotated[entities.Person, Depends(get_user)],
    ) -> Dataset:
        """Share the dataset to the marketplace"""

        marketplace_url = data.marketplace_url

        try:
            entity_output = await self._usecases.share(
                id, marketplace_url, context={"user": user}
            )
        except DatasetDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=DATASET_NOT_FOUND,
            )
        except DatasetSharingError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
            )

        item_output = Dataset.from_entity(entity_output)
        response.headers["Location"] = str(
            request.url_for("get_dataset", id=entity_output.identifier)
        )
        return item_output


routes = DatasetsSharingRoutes(usecases=DatasetsSharingUsecases())
