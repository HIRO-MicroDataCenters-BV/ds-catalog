from typing import BinaryIO

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from rdflib import DCAT
from rdflib.namespace import DCTERMS

from app.core.exceptions import NodeDoesNotExist, QueryIsRequired

from .context import Context, SaveDatasetContext
from .entities import Catalog, CatalogFilters, Dataset, Metadata, Person, User
from .mmio import (
    JsonMMIOParser,
    MMIO,
    mmio_available_attrs,
    mmio_data_to_entities
)
from .namespace import DSPACE
from .repository import Repositories
from .repository.queries import FilterDatasetByID, FilterPersonByID
from .repository.query_builder import catalog_filter_to_query, uri_to_cypher
from .validators import (
    CatalogFiltersValidatorService,
    DatasetValidatorService,
    IDatasetValidatorService,
    IValidatorService,
)


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
    async def save(
        self,
        data: Dataset,
        filename: str,
        context: SaveDatasetContext,
        validator_class: type[IDatasetValidatorService],
    ) -> tuple[Dataset, list[str]]:
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


class IMMIOsUsecases(IUsecases):
    @abstractmethod
    async def create(self, file: BinaryIO, filename: str, context: Context) -> None:
        ...

    @abstractmethod
    async def get(self, filename: str, context: Context) -> str:
        ...

    @abstractmethod
    async def delete(self, filename: str, context: Context) -> None:
        ...


# --- Implementations ---


class CatalogUsecases(BaseUsecases, ICatalogUsecases):
    async def get_local_catalog(
        self,
        filters: CatalogFilters,
        context: Context,
        validator_class: type[IValidatorService] = CatalogFiltersValidatorService,
    ) -> Catalog:
        """Get the local catalog"""

        validator = validator_class()
        validator.validate(filters)

        namespaces = await self.repositories.get_namespaces()
        query = catalog_filter_to_query(filters, namespaces)
        return await self.repositories.catalogs.get(query)

    async def get_public_catalog(
        self,
        filters: CatalogFilters,
        context: Context,
        validator_class: type[IValidatorService] = CatalogFiltersValidatorService,
    ) -> Catalog:
        """Get the public catalog"""

        validator = validator_class()
        validator.validate(filters)

        namespaces = await self.repositories.get_namespaces()
        query = catalog_filter_to_query(filters, namespaces)
        if query is None:
            raise QueryIsRequired("Query is required for public catalog")

        is_shared_attr_name = uri_to_cypher(DSPACE.isShared, namespaces)
        query.add_where(f"{Dataset.label}.{is_shared_attr_name}=true")

        return await self.repositories.catalogs.get(query)


class DatasetsUsecases(BaseUsecases, IDatasetsUsecases):
    async def save(
        self,
        dataset: Dataset,
        filename: str,
        context: SaveDatasetContext,
        validator_class: type[IDatasetValidatorService] = DatasetValidatorService,
    ) -> tuple[Dataset, list[str]]:
        """Create or update a dataset"""

        # Validate the input dataset
        validator = validator_class(
            shacl_url=context["shacl_url"],
            ontology_url=context["ontology_url"],
        )
        validator.validate(dataset)

        # Get the local catalog
        catalog = await self.repositories.catalogs.get()

        # Get or create the person
        user = context["user"]
        person = await self._get_or_create_person(user)

        # Add metadata from the MMIO file
        metadata_items, errors = await self._build_mmio_metadata(
            filename, context["oca_uri"]
        )
        for metadata in metadata_items:
            dataset += metadata
            dataset.set_attribute(DSPACE.extraMetadata, metadata.uri)
        dataset.set_attribute(DSPACE.metadataFilename, filename)

        # Set the additional attributes for the dataset
        is_shared = dataset.get_attribute(DSPACE.isShared)
        if is_shared is None:
            dataset.set_attribute(DSPACE.isShared, False)
        dataset.set_attribute(DCTERMS.issued, datetime.now(UTC).isoformat())
        dataset.set_attribute(DSPACE.isDeleted, False)
        dataset.set_attribute(DCTERMS.publisher, person.uri)

        # Set the dataset as a child of the catalog
        catalog.set_attribute(DCAT.dataset, dataset.uri)

        # Save the graph (including the dataset, catalog, and person)
        catalog += dataset
        catalog += person
        await self.repositories.catalogs.save(catalog)

        # Return the dataset
        id = dataset.get_attribute(DCTERMS.identifier)
        final_dataset = await self.get(id, context)
        return final_dataset, errors

    async def get(self, id: str, context: Context) -> Dataset:
        """Get a dataset by its ID"""
        query = FilterDatasetByID(id)
        return await self.repositories.datasets.get(query)

    async def delete(self, id: str, context: Context) -> None:
        """Delete a dataset by its ID"""
        query = FilterDatasetByID(id)
        await self.repositories.datasets.delete(query)

    async def _build_mmio_metadata(
        self, filename: str, schema_uri: str
    ) -> tuple[list[Metadata], list[str]]:
        mmio_bytes = await self.repositories.files.read(filename)
        parser = JsonMMIOParser()
        mmio = MMIO(mmio_bytes, parser=parser, schema_uri=schema_uri)
        mmio = mmio.transform_to(schema_uri)
        data = mmio_available_attrs(mmio)
        metadata = mmio_data_to_entities(schema_uri, mmio.id, data)

        return metadata, getattr(parser, "errors", [])

    async def _get_or_create_person(self, user: User) -> Person:
        query = FilterPersonByID(user["id"])
        try:
            person = await self.repositories.persons.get(query)
        except NodeDoesNotExist:
            person = Person.from_user(user)
        return person


class DatasetSharingUsecases(BaseUsecases, IDatasetSharingUsecases):
    async def share(self, id: str, context: Context) -> None:
        """Share a dataset"""
        query = FilterDatasetByID(id)
        dataset = await self.repositories.datasets.get(query)
        dataset.set_attribute(DSPACE.isShared, True)
        await self.repositories.datasets.save(dataset)

    async def unshare(self, id: str, context: Context) -> None:
        """Unshare a dataset"""
        query = FilterDatasetByID(id)
        dataset = await self.repositories.datasets.get(query)
        dataset.set_attribute(DSPACE.isShared, False)
        await self.repositories.datasets.save(dataset)


class MMIOsUsecases(BaseUsecases, IMMIOsUsecases):
    async def create(self, file: BinaryIO, filename: str, context: Context) -> None:
        """Create a new MMIO file"""
        await self.repositories.files.create(file, filename)

    async def get(self, filename: str, context: Context) -> str:
        """Get a MMIO file"""
        return await self.repositories.files.get_file_path(filename)

    async def delete(self, filename: str, context: Context) -> None:
        """Delete a MMIO file"""
        await self.repositories.files.delete(filename)
