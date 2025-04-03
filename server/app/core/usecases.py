from abc import ABC, abstractmethod

from rdflib.namespace import DCAT

from .context import Context, CreateDatasetContext
from .entities import Catalog, CatalogFilters, Dataset
from .namespace import DSPACE
from .repository import Repositories
from .repository.queries import FilterDatasetByID, Query


class IUsecases(ABC):
    def __init__(self, repositories: Repositories) -> None:
        ...


class BaseUsecases(IUsecases):
    def __init__(self, repositories: Repositories) -> None:
        self.repositories = repositories


# --- Interfaces ---


class ICatalogUsecases(IUsecases):
    @abstractmethod
    async def get_local_catalog(
        self, filters: CatalogFilters, context: Context
    ) -> Catalog:
        ...


class IDatasetsUsecases(IUsecases):
    @abstractmethod
    async def save(self, data: Dataset, context: CreateDatasetContext) -> Dataset:
        ...

    @abstractmethod
    async def get(self, id: str, context: Context) -> Dataset:
        ...

    @abstractmethod
    async def delete(self, id: str, context: Context) -> None:
        ...


class IDatasetSharingUsecases(IUsecases):
    @abstractmethod
    async def share(self, id: str, context: Context) -> None:
        ...

    @abstractmethod
    async def unshare(self, id: str, context: Context) -> None:
        ...


# --- Implementations ---


class CatalogUsecases(BaseUsecases, ICatalogUsecases):
    async def get_local_catalog(
        self, filters: CatalogFilters, context: Context
    ) -> Catalog:
        """Get the local catalog"""
        query = Query()  # TODO: Build the query based on the filters
        return await self.repositories.catalog.get(query)


class DatasetsUsecases(BaseUsecases, IDatasetsUsecases):
    async def save(self, dataset: Dataset, context: CreateDatasetContext) -> Dataset:
        """Create or update a dataset"""
        node = dataset.get_node_by_type(DCAT.Dataset)
        dataset.set_attribute(node, DSPACE.isShared, False)
        # TODO: Add attributes (creator, etc.) to the dataset
        await self.repositories.datasets.save(dataset)
        return dataset

    async def get(self, id: str, context: Context) -> Dataset:
        """Get a dataset by its ID"""
        query = FilterDatasetByID(id)
        return await self.repositories.datasets.get(query)

    async def delete(self, id: str, context: Context) -> None:
        """Delete a dataset by its ID"""
        query = FilterDatasetByID(id)
        await self.repositories.datasets.delete(query)


class DatasetSharingUsecases(BaseUsecases, IDatasetSharingUsecases):
    async def share(self, id: str, context: Context) -> None:
        """Share a dataset"""
        query = FilterDatasetByID(id)
        dataset = await self.repositories.datasets.get(query)
        node = dataset.get_node_by_type(DCAT.Dataset)
        dataset.set_attribute(node, DSPACE.isShared, True)
        await self.repositories.datasets.save(dataset)

    async def unshare(self, id: str, context: Context) -> None:
        """Unshare a dataset"""
        query = FilterDatasetByID(id)
        dataset = await self.repositories.datasets.get(query)
        node = dataset.get_node_by_type(DCAT.Dataset)
        dataset.set_attribute(node, DSPACE.isShared, False)
        await self.repositories.datasets.save(dataset)
