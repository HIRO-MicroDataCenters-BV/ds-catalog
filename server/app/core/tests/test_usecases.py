from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time
from rdflib import DCAT, DCTERMS, FOAF, RDF, Literal, URIRef

from ..context import Context
from ..entities import Catalog, CatalogFilters, Dataset, Person
from ..exceptions import NodeDoesNotExist
from ..namespace import DSPACE
from ..repository.queries import FilterDatasetByID, FilterPersonByID
from ..usecases import CatalogUsecases, DatasetSharingUsecases, DatasetsUsecases
from .factories import user_factory


class TestCatalogUsecases:
    @pytest.fixture
    def repositories(self):
        return Mock()

    @pytest.mark.asyncio
    async def test_get_local_catalog(self, repositories):
        expected_result = Mock()
        repositories.catalogs.get = AsyncMock(return_value=expected_result)

        usecase = CatalogUsecases(repositories)

        filters = CatalogFilters()
        context = Context(user=user_factory())
        result = await usecase.get_local_catalog(filters, context)

        assert result == expected_result
        repositories.catalogs.get.assert_called_once()


class TestDatasetsUsecases:
    @pytest.fixture
    def repositories(self):
        return Mock()

    @freeze_time("2017-05-21T09:23:00+00:00")
    @pytest.mark.asyncio
    async def test_save(self, repositories):
        id = "http://example.com/1"
        user = user_factory()
        person = Person.from_user(user)
        catalog = Catalog.create("Test title", "Test description")
        dataset = Dataset.create_empty(id)
        dataset.set_attribute(DCTERMS.identifier, id)

        repositories.catalogs.get = AsyncMock(return_value=catalog)
        repositories.persons.get = AsyncMock(return_value=person)
        repositories.catalogs.save = AsyncMock()
        repositories.datasets.get = AsyncMock(return_value=dataset)

        usecase = DatasetsUsecases(repositories)

        context = Context(user=user)
        result = await usecase.save(dataset, context)

        repositories.catalogs.get.assert_called_once_with()
        repositories.persons.get.assert_called_once()
        assert repositories.persons.get.call_args[0][0] == FilterPersonByID(user["id"])
        repositories.catalogs.save.assert_called_once_with(catalog)
        repositories.datasets.get.assert_called_once()
        assert repositories.datasets.get.call_args[0][0] == FilterDatasetByID(id)

        assert result.get_attribute(DSPACE.isDeleted) == Literal(False)
        assert result.get_attribute(DSPACE.isShared) == Literal(False)
        assert result.get_attribute(DCTERMS.issued) == Literal(
            "2017-05-21T09:23:00+00:00"
        )
        assert result.get_attribute(DCTERMS.publisher) == person.uri

        assert catalog.get_attribute(DCAT.dataset) == dataset.uri

        assert result == dataset

    @pytest.mark.asyncio
    async def test_save_with_new_publisher(self, repositories):
        id = "http://example.com/1"
        user = user_factory()
        catalog = Catalog.create("Test title", "Test description")
        dataset = Dataset.create_empty(id)
        dataset.set_attribute(DCTERMS.identifier, id)

        repositories.catalogs.get = AsyncMock(return_value=catalog)
        repositories.persons.get = AsyncMock(side_effect=NodeDoesNotExist)
        repositories.catalogs.save = AsyncMock()
        repositories.datasets.get = AsyncMock(return_value=dataset)

        usecase = DatasetsUsecases(repositories)

        context = Context(user=user)
        result = await usecase.save(dataset, context)

        assert result == dataset

        publisher = URIRef(user["id"])
        assert result.get_attribute(DCTERMS.publisher) == publisher
        assert (publisher, RDF.type, FOAF.Person) in catalog.graph

    @pytest.mark.asyncio
    async def test_save_if_it_is_shared_alredy(self, repositories):
        id = "http://example.com/1"
        user = user_factory()
        catalog = Catalog.create("Test title", "Test description")
        dataset = Dataset.create_empty(id)
        dataset.set_attribute(DCTERMS.identifier, id)
        dataset.set_attribute(DSPACE.isShared, True)

        repositories.catalogs.get = AsyncMock(return_value=catalog)
        repositories.persons.get = AsyncMock(side_effect=NodeDoesNotExist)
        repositories.catalogs.save = AsyncMock()
        repositories.datasets.get = AsyncMock(return_value=dataset)

        usecase = DatasetsUsecases(repositories)

        context = Context(user=user)
        result = await usecase.save(dataset, context)

        assert result == dataset
        assert result.get_attribute(DSPACE.isShared) == Literal(True)

    @pytest.mark.asyncio
    async def test_get(self, repositories):
        id = "test-id"
        dataset = Dataset.create_empty(id)

        repositories.datasets.get = AsyncMock(return_value=dataset)

        usecase = DatasetsUsecases(repositories)

        context = Context(user=user_factory())
        result = await usecase.get(id, context)

        repositories.datasets.get.assert_called_once()
        assert repositories.datasets.get.call_args[0][0] == FilterDatasetByID(id)
        assert result == dataset

    @pytest.mark.asyncio
    async def test_delete(self, repositories):
        id = "test-id"

        repositories.datasets.delete = AsyncMock()

        usecase = DatasetsUsecases(repositories)

        context = Context(user=user_factory())
        await usecase.delete(id, context)

        repositories.datasets.delete.assert_called_once()
        assert repositories.datasets.delete.call_args[0][0] == FilterDatasetByID(id)


class TestDatasetSharingUsecases:
    @pytest.fixture
    def repositories(self):
        return Mock()

    @pytest.mark.asyncio
    async def test_share(self, repositories):
        id = "test-id"
        dataset = Dataset.create_empty(id)

        repositories.datasets.get = AsyncMock(return_value=dataset)
        repositories.datasets.save = AsyncMock()

        usecase = DatasetSharingUsecases(repositories)

        context = Context(user=user_factory())
        await usecase.share(id, context)

        repositories.datasets.get.assert_called_once()
        assert repositories.datasets.get.call_args[0][0] == FilterDatasetByID(id)

        assert dataset.get_attribute(DSPACE.isShared) == Literal(True)

        repositories.datasets.save.assert_called_once_with(dataset)

    @pytest.mark.asyncio
    async def test_unshare(self, repositories):
        id = "test-id"
        dataset = Dataset.create_empty(id)

        repositories.datasets.get = AsyncMock(return_value=dataset)
        repositories.datasets.save = AsyncMock()

        usecase = DatasetSharingUsecases(repositories)

        context = Context(user=user_factory())
        await usecase.unshare(id, context)

        repositories.datasets.get.assert_called_once()
        assert repositories.datasets.get.call_args[0][0] == FilterDatasetByID(id)

        assert dataset.get_attribute(DSPACE.isShared) == Literal(False)

        repositories.datasets.save.assert_called_once_with(dataset)
