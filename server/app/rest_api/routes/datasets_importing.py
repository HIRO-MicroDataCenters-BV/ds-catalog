from typing import Annotated

from abc import ABC, abstractmethod

from classy_fastapi import Routable, post
from fastapi import Depends, HTTPException, Request, Response, status

from app.core import entities, exceptions, usecases
from app.core.context import Context

from ..depends.user import get_user
from ..serializers.catalog import Dataset, DatasetImportForm
from ..strings import DATASET_ALREDY_EXISTS
from ..tags import Tags


class IDatasetsImportingUsecases(ABC):
    @abstractmethod
    async def import_data(
        self, data: entities.DatasetImport, context: Context
    ) -> entities.Dataset:
        ...


class DatasetsImportingUsecases(IDatasetsImportingUsecases):
    async def import_data(self, *args, **kwargs):
        return await usecases.import_dataset(*args, **kwargs)


class DatasetsImportingRoutes(Routable):
    _usecases: IDatasetsImportingUsecases

    def __init__(self, usecases: IDatasetsImportingUsecases) -> None:
        self._usecases = usecases
        super().__init__()

    @post(
        "/datasets/import/",
        operation_id="import_dataset",
        tags=[Tags.Importing],
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
        },
    )
    async def import_dataset(
        self,
        data: DatasetImportForm,
        request: Request,
        response: Response,
        user: Annotated[entities.Person, Depends(get_user)],
    ) -> Dataset:
        """Import a dataset from the local catalog"""

        entity_input = data.to_entity()

        try:
            entity_output = await self._usecases.import_data(
                entity_input, context={"user": user}
            )
        except exceptions.DatasetAlredyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=DATASET_ALREDY_EXISTS
            )

        item_output = Dataset.from_entity(entity_output)
        response.headers["Location"] = str(
            request.url_for("get_dataset", id=entity_output.identifier)
        )
        return item_output


routes = DatasetsImportingRoutes(usecases=DatasetsImportingUsecases())
