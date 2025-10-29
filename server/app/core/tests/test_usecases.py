from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from freezegun import freeze_time
from rdflib import DCAT, DCTERMS, FOAF, RDF, Literal, URIRef

from ..context import Context, SaveDatasetContext
from ..entities import Catalog, Dataset, Metadata, Person
from ..exceptions import GraphValidationError, NodeDoesNotExist, QueryIsRequired
from ..namespace import DSPACE
from ..repository.queries import FilterDatasetByID, FilterPersonByID
from ..repository.query_builder import catalog_filter_to_query
from ..usecases import (
    CatalogUsecases,
    DatasetSharingUsecases,
    DatasetsUsecases,
    MMIOsUsecases,
)
from .factories import (
    catalog_filters_factory,
    namespace_factory,
    tar_factory,
    user_factory,
)


@pytest.fixture
def validator_instance():
    validator_instance = MagicMock()
    validator_instance.validate = Mock(return_value=None)
    return validator_instance


@pytest.fixture
def validator_class(validator_instance):
    ValidatorClass = MagicMock(return_value=validator_instance)
    return ValidatorClass


class TestCatalogUsecases:
    @pytest.fixture
    def repositories(self):
        return Mock()

    @pytest.mark.asyncio
    async def test_get_local_catalog(
        self, repositories, validator_class, validator_instance
    ):
        expected_result = Mock()
        namespaces = namespace_factory()

        repositories.get_namespaces = AsyncMock(return_value=namespaces)
        repositories.catalogs.get = AsyncMock(return_value=expected_result)

        usecase = CatalogUsecases(repositories)

        filters = catalog_filters_factory()
        context = Context(user=user_factory())
        result = await usecase.get_local_catalog(
            filters,
            context,
            validator_class=validator_class,
        )

        assert result == expected_result

        validator_class.assert_called_once_with()
        validator_instance.validate.assert_called_once_with(filters)

        repositories.get_namespaces.assert_called_once()
        repositories.catalogs.get.assert_called_once()

        [query] = repositories.catalogs.get.call_args[0]
        assert query == catalog_filter_to_query(filters, namespaces)

    @pytest.mark.asyncio
    async def test_get_local_catalog_if_graph_is_not_valid(
        self, repositories, validator_class, validator_instance
    ):
        error = GraphValidationError("test_code", "Test error", [])
        validator_instance.validate = Mock(side_effect=error)

        usecase = CatalogUsecases(repositories)

        filters = catalog_filters_factory()
        context = Context(user=user_factory())

        with pytest.raises(GraphValidationError):
            await usecase.get_local_catalog(
                filters,
                context,
                validator_class=validator_class,
            )

    @pytest.mark.asyncio
    async def test_get_public_catalog(
        self, repositories, validator_class, validator_instance
    ):
        expected_result = Mock()
        namespaces = namespace_factory()

        repositories.get_namespaces = AsyncMock(return_value=namespaces)
        repositories.catalogs.get = AsyncMock(return_value=expected_result)

        usecase = CatalogUsecases(repositories)

        filters = catalog_filters_factory()
        context = Context(user=user_factory())
        result = await usecase.get_public_catalog(
            filters,
            context,
            validator_class=validator_class,
        )

        assert result == expected_result

        validator_class.assert_called_once_with()
        validator_instance.validate.assert_called_once_with(filters)

        repositories.get_namespaces.assert_called_once()
        repositories.catalogs.get.assert_called_once()

        [query] = repositories.catalogs.get.call_args[0]

        expected_query = catalog_filter_to_query(filters, namespaces)
        assert expected_query is not None
        expected_query.add_where("d.dspace__isShared=true")

        assert query == expected_query

    @pytest.mark.asyncio
    async def test_get_public_catalog_if_graph_is_not_valid(
        self, repositories, validator_class, validator_instance
    ):
        error = GraphValidationError("test_code", "Test error", [])
        validator_instance.validate = Mock(side_effect=error)

        usecase = CatalogUsecases(repositories)

        filters = catalog_filters_factory()
        context = Context(user=user_factory())

        with pytest.raises(GraphValidationError):
            await usecase.get_public_catalog(
                filters,
                context,
                validator_class=validator_class,
            )

    @pytest.mark.asyncio
    async def test_get_public_catalog_if_no_query(
        self,
        repositories,
        validator_class,
    ):
        namespaces = namespace_factory()
        repositories.get_namespaces = AsyncMock(return_value=namespaces)

        usecase = CatalogUsecases(repositories)

        filters = catalog_filters_factory(filter_items=[])
        context = Context(user=user_factory())

        with pytest.raises(QueryIsRequired):
            await usecase.get_public_catalog(
                filters,
                context,
                validator_class=validator_class,
            )


class TestDatasetsUsecases:
    @pytest.fixture
    def repositories(self):
        return Mock()

    @pytest.fixture
    def mmio_tar(self):
        mmio_data = (Path(__file__).parent / "fixtures" / "mmio.json").read_text()
        bundle_data = (Path(__file__).parent / "fixtures" / "bundle.json").read_text()
        return tar_factory({"mmio.json": mmio_data, "test.bundles": bundle_data})

    @pytest.fixture
    def user(self):
        return user_factory()

    @pytest.fixture
    def context(self, user):
        return SaveDatasetContext(
            user=user,
            oca_uri="http://oca.example.org/123/",
            shacl_url="http://example.org/shacl.ttl",
            ontology_url="http://example.org/dcat.ttl",
            related_data_product="disease_xyz",
        )

    @freeze_time("2017-05-21T09:23:00+00:00")
    @pytest.mark.asyncio
    async def test_save(
        self,
        repositories,
        mmio_tar,
        context,
        validator_class,
        validator_instance,
    ):
        id = "http://example.com/1"
        user = context["user"]
        person = Person.from_user(user)
        catalog = Catalog.create("Test title", "Test description")
        dataset = Dataset.create_empty(id)
        dataset.set_attribute(DCTERMS.identifier, id)
        filename = "mmio.tar"
        mmio_id = "EI2z8E6zYvMF_yvquoUJedWi0rKpQsscPf7JlBgIDoOm"  # from fixture

        repositories.catalogs.get = AsyncMock(return_value=catalog)
        repositories.persons.get = AsyncMock(return_value=person)
        repositories.catalogs.save = AsyncMock()
        repositories.datasets.get = AsyncMock(return_value=dataset)
        repositories.files.read = AsyncMock(return_value=mmio_tar)

        usecase = DatasetsUsecases(repositories)

        result, errors = await usecase.save(
            dataset,
            filename,
            context,
            validator_class=validator_class,
        )

        assert result == dataset

        validator_class.assert_called_once_with(
            shacl_url=context["shacl_url"],
            ontology_url=context["ontology_url"],
        )
        validator_instance.validate.assert_called_once_with(dataset)

        repositories.catalogs.get.assert_called_once_with()
        repositories.persons.get.assert_called_once()
        assert repositories.persons.get.call_args[0][0] == FilterPersonByID(user["id"])
        repositories.catalogs.save.assert_called_once_with(catalog)
        repositories.datasets.get.assert_called_once()
        assert repositories.datasets.get.call_args[0][0] == FilterDatasetByID(id)
        repositories.files.read.assert_called_once_with(filename)

        assert result.get_attribute(DSPACE.isDeleted) == Literal(False)
        assert result.get_attribute(DSPACE.isShared) == Literal(False)
        assert result.get_attribute(DCTERMS.issued) == Literal(
            "2017-05-21T09:23:00+00:00"
        )
        assert result.get_attribute(DCTERMS.publisher) == person.uri

        assert result.get_attribute(DSPACE.metadataFilename) == Literal(filename)

        oca_uri = context["oca_uri"]
        metadata_uri = Metadata.build_uri(oca_uri, f"{mmio_id}/0", 0)
        assert result.get_attribute(DSPACE.extraMetadata) == metadata_uri

        assert (metadata_uri, RDF.type, Metadata.build_type(oca_uri)) in dataset.graph
        assert (metadata_uri, URIRef(f"{oca_uri}age"), Literal(True)) in dataset.graph
        assert (metadata_uri, URIRef(f"{oca_uri}bmi"), Literal(True)) in dataset.graph

        assert catalog.get_attribute(DCAT.dataset) == dataset.uri

    @pytest.mark.asyncio
    async def test_save_with_new_publisher(
        self, repositories, mmio_tar, context, validator_class
    ):
        id = "http://example.com/1"
        catalog = Catalog.create("Test title", "Test description")
        dataset = Dataset.create_empty(id)
        dataset.set_attribute(DCTERMS.identifier, id)

        repositories.catalogs.get = AsyncMock(return_value=catalog)
        repositories.persons.get = AsyncMock(side_effect=NodeDoesNotExist)
        repositories.catalogs.save = AsyncMock()
        repositories.datasets.get = AsyncMock(return_value=dataset)
        repositories.files.read = AsyncMock(return_value=mmio_tar)

        usecase = DatasetsUsecases(repositories)

        result, errors = await usecase.save(
            dataset,
            "mmio.tar",
            context,
            validator_class=validator_class,
        )

        assert result == dataset

        publisher = URIRef(context["user"]["id"])
        assert result.get_attribute(DCTERMS.publisher) == publisher
        assert (publisher, RDF.type, FOAF.Person) in catalog.graph

    @pytest.mark.asyncio
    async def test_save_if_it_is_shared_alredy(
        self, repositories, mmio_tar, context, validator_class
    ):
        id = "http://example.com/1"
        catalog = Catalog.create("Test title", "Test description")
        dataset = Dataset.create_empty(id)
        dataset.set_attribute(DCTERMS.identifier, id)
        dataset.set_attribute(DSPACE.isShared, True)

        repositories.catalogs.get = AsyncMock(return_value=catalog)
        repositories.persons.get = AsyncMock(side_effect=NodeDoesNotExist)
        repositories.catalogs.save = AsyncMock()
        repositories.datasets.get = AsyncMock(return_value=dataset)
        repositories.files.read = AsyncMock(return_value=mmio_tar)

        usecase = DatasetsUsecases(repositories)

        result, errors = await usecase.save(
            dataset,
            "mmio.tar",
            context,
            validator_class=validator_class,
        )

        assert result == dataset
        assert result.get_attribute(DSPACE.isShared) == Literal(True)

    @pytest.mark.asyncio
    async def test_save_if_graph_is_not_valid(
        self, repositories, context, validator_class, validator_instance
    ):
        error = GraphValidationError("test_code", "Test error", [])
        validator_instance.validate = Mock(side_effect=error)

        usecase = DatasetsUsecases(repositories)

        dataset = Dataset.create_empty("test-id")

        with pytest.raises(GraphValidationError):
            await usecase.save(
                dataset,
                "test.csv",
                context,
                validator_class=validator_class,
            )

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


class TestMMIOsUsecases:
    @pytest.fixture
    def repositories(self):
        return Mock()

    @pytest.mark.asyncio
    async def test_create(self, repositories):
        file = Mock()
        filename = "test_file.mmio"
        user = user_factory()

        repositories.files.create = AsyncMock()

        usecase = MMIOsUsecases(repositories)

        context = Context(user=user)
        await usecase.create(file, filename, context)

        repositories.files.create.assert_called_once_with(file, filename)

    @pytest.mark.asyncio
    async def test_get(self, repositories):
        filename = "test_file.mmio"
        file_path = "/file-path"

        repositories.files.get_file_path = AsyncMock(return_value=file_path)

        usecase = MMIOsUsecases(repositories)

        context = Context(user=user_factory())
        result = await usecase.get(filename, context)

        repositories.files.get_file_path.assert_called_once_with(filename)
        assert result == file_path

    @pytest.mark.asyncio
    async def test_delete(self, repositories):
        filename = "test_file.mmio"

        repositories.files.delete = AsyncMock()

        usecase = MMIOsUsecases(repositories)

        context = Context(user=user_factory())
        await usecase.delete(filename, context)

        repositories.files.delete.assert_called_once_with(filename)
