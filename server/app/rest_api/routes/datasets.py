from typing import Annotated

from abc import ABC, abstractmethod

from classy_fastapi import Routable, delete, get, patch, post
from fastapi import Depends, HTTPException, Request, Response, status

from app.core import entities, usecases
from app.core.context import Context
from app.core.exceptions import DatasetDoesNotExist
from app.core.repository.queries import (
    CompositeQuery,
    DatasetsFilterDTO,
    DatasetsFilterQuery,
    IQuery,
    OrderQuery,
    OrderQueryDTO,
    PaginatorQuery,
    PaginatorQueryDTO,
)

from ..depends.catalog import datasets_filter
from ..depends.list import order_parameters, paginator_parameters
from ..depends.user import get_user
from ..serializers.catalog import Dataset, DatasetForm
from ..serializers.common import PaginatedResult
from ..strings import DATASET_NOT_FOUND
from ..tags import Tags


class IDatasetsUsecases(ABC):
    @abstractmethod
    async def list(
        self,
        query: IQuery,
        context: Context,
    ) -> list[entities.Dataset]:
        ...

    @abstractmethod
    async def get(
        self,
        id: str,
        context: Context,
    ) -> entities.Dataset:
        ...

    @abstractmethod
    async def create(
        self,
        data: entities.DatasetInput,
        context: Context,
    ) -> entities.Dataset:
        ...

    @abstractmethod
    async def update(
        self,
        id: str,
        data: entities.DatasetInput,
        context: Context,
    ) -> entities.Dataset:
        ...

    @abstractmethod
    async def delete(
        self,
        id: str,
        context: Context,
    ) -> None:
        ...


class DatasetsUsecases(IDatasetsUsecases):
    async def list(self, *args, **kwargs):
        return await usecases.get_datasets_list(*args, **kwargs)

    async def get(self, *args, **kwargs):
        return await usecases.get_dataset(*args, **kwargs)

    async def create(self, *args, **kwargs):
        return await usecases.create_dataset(*args, **kwargs)

    async def update(self, *args, **kwargs):
        return await usecases.update_dataset(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        return await usecases.delete_dataset(*args, **kwargs)


class DatasetsRoutes(Routable):
    _usecases: IDatasetsUsecases

    def __init__(self, usecases: IDatasetsUsecases) -> None:
        self._usecases = usecases
        super().__init__()

    @get(
        "/datasets/",
        operation_id="get_datasets",
        tags=[Tags.Datasets],
        response_model=PaginatedResult[Dataset],
    )
    async def get_datasets(
        self,
        paginator_parameters: Annotated[
            PaginatorQueryDTO, Depends(paginator_parameters)
        ],
        order_parameters: Annotated[OrderQueryDTO, Depends(order_parameters)],
        filters: Annotated[DatasetsFilterDTO, Depends(datasets_filter)],
        user: Annotated[entities.Person, Depends(get_user)],
    ) -> PaginatedResult[Dataset]:
        """Get the datasets list"""

        paginator_query = PaginatorQuery(**paginator_parameters)
        order_query = OrderQuery(**order_parameters)
        filters_query = DatasetsFilterQuery(**filters)

        query = CompositeQuery(
            paginator_query,
            order_query,
            filters_query,
        )

        output_entities = await self._usecases.list(query, context={"user": user})
        items = [Dataset.from_entity(entity) for entity in output_entities]

        return PaginatedResult(
            page=paginator_parameters["page"],
            size=paginator_parameters["page_size"],
            items=items,
        )

    @get(
        "/datasets/{id}/",
        operation_id="get_dataset",
        tags=[Tags.Datasets],
        response_model=Dataset,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "Dataset not found"},
        },
    )
    async def get_dataset(
        self,
        id: str,
        user: Annotated[entities.Person, Depends(get_user)],
    ) -> Dataset:
        """Get the dataset"""
        try:
            output_entity = await self._usecases.get(id, context={"user": user})
        except DatasetDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=DATASET_NOT_FOUND
            )
        return Dataset.from_entity(output_entity)

    @post(
        "/datasets/",
        operation_id="create_dataset",
        tags=[Tags.Datasets],
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
    async def create_dataset(
        self,
        item: DatasetForm,
        request: Request,
        response: Response,
        user: Annotated[entities.Person, Depends(get_user)],
    ) -> Dataset:
        """Create a dataset"""
        input_entity = item.to_entity()
        output_entity = await self._usecases.create(
            input_entity,
            context={"user": user},
        )
        output_item = Dataset.from_entity(output_entity)
        response.headers["Location"] = str(
            request.url_for("get_dataset", id=output_entity.identifier)
        )
        return output_item

    @patch(
        "/datasets/{id}/",
        operation_id="update_dataset",
        tags=[Tags.Datasets],
        response_model=Dataset,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "Dataset not found"},
        },
    )
    async def update_dataset(
        self,
        id: str,
        data: DatasetForm,
        user: Annotated[entities.Person, Depends(get_user)],
    ) -> Dataset:
        """Update the dataset"""
        input_entity = data.to_entity()
        try:
            output_entity = await self._usecases.update(
                id,
                input_entity,
                context={"user": user},
            )
        except DatasetDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=DATASET_NOT_FOUND
            )
        return Dataset.from_entity(output_entity)

    @delete(
        "/datasets/{id}/",
        operation_id="delete_dataset",
        tags=[Tags.Datasets],
        status_code=status.HTTP_204_NO_CONTENT,
        response_model=None,
        responses={
            status.HTTP_404_NOT_FOUND: {"description": "Dataset not found"},
        },
    )
    async def delete_dataset(
        self,
        id: str,
        user: Annotated[entities.Person, Depends(get_user)],
    ) -> None:
        """Delete the dataset"""
        try:
            await self._usecases.delete(id, context={"user": user})
        except DatasetDoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=DATASET_NOT_FOUND
            )


routes = DatasetsRoutes(usecases=DatasetsUsecases())
