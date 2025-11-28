from unittest.mock import AsyncMock, Mock

import pytest
from rdflib import Graph as RDFGraph
from rdflib.namespace import DCTERMS

from app.core.entities import Catalog, Dataset, Person
from app.core.exceptions import ErrorSavingData, MultipleNodesFound, NodeDoesNotExist
from app.core.namespace import DSPACE

from ..queries import Query
from ..repositories import (
    CatalogsRepository,
    DatasetsRepository,
    FilesRepository,
    PersonsRepository,
    Repositories,
)


class TestPersonsRepository:
    @pytest.fixture
    def repository(self):
        db_driver = Mock()
        repository = PersonsRepository(db_driver)
        repository.neosemantics = Mock()
        return repository

    @pytest.mark.asyncio
    async def test_get(self, repository):
        mock_graph = Mock()
        mock_graph.subjects.return_value = [Mock()]

        repository.neosemantics.export = AsyncMock(return_value=mock_graph)

        query = Query()
        result = await repository.get(query)

        repository.neosemantics.export.assert_called_once_with(
            "MATCH (p:foaf__Person)-[r*0..]->(related)\n"
            'WHERE all(rel IN r WHERE type(rel) <> "rdf__type")\n'
            "RETURN p, r, related"
        )
        assert isinstance(result, Person)
        assert result.graph == mock_graph

    @pytest.mark.asyncio
    async def test_node_does_not_exist(self, repository):
        empty_graph = RDFGraph()
        repository.neosemantics.export = AsyncMock(return_value=empty_graph)
        query = Query()
        with pytest.raises(NodeDoesNotExist):
            await repository.get(query)

    @pytest.mark.asyncio
    async def test_multiple_nodes_found(self, repository):
        mock_graph = Mock()
        repository.neosemantics.export = AsyncMock(return_value=mock_graph)
        mock_graph.subjects.return_value = [Mock(), Mock()]
        query = Query()
        with pytest.raises(MultipleNodesFound):
            await repository.get(query)

    @pytest.mark.asyncio
    async def test_save_success(self, repository):
        repository.neosemantics.save = AsyncMock(return_value={"success": True})
        obj = Mock()
        await repository.save(obj)
        repository.neosemantics.save.assert_called_once_with(obj.graph)

    @pytest.mark.asyncio
    async def test_save_failure(self, repository):
        repository.neosemantics.save = AsyncMock(
            return_value={"success": False, "extra_info": "Error details"}
        )
        obj = Mock()
        with pytest.raises(ErrorSavingData):
            await repository.save(obj)


class TestCatalogsRepository:
    @pytest.fixture
    def repository(self):
        db_driver = Mock()
        repository = CatalogsRepository(db_driver)
        repository.neosemantics = Mock()
        return repository

    @pytest.mark.asyncio
    async def test_create(self, repository):
        repository.neosemantics.save = AsyncMock()

        title = "Test Catalog"
        description = "Test Description"
        result = await repository.create(title, description)

        repository.neosemantics.save.assert_called_once()
        assert isinstance(result, Catalog)
        assert str(result.get_attribute(DCTERMS.title)) == title
        assert str(result.get_attribute(DCTERMS.description)) == description

    @pytest.mark.asyncio
    async def test_get(self, repository):
        mock_graph = Mock()
        mock_graph.subjects.return_value = [Mock()]

        repository.neosemantics.export = AsyncMock(return_value=mock_graph)

        query = Query(
            optional_match=[
                "(d:dcat__Dataset)",
                "(m1:ns0__Diagnosis)",
            ],
            where=['m1.ns0__code="I10"'],
            with_clause="d",
        )
        result = await repository.get(query)

        repository.neosemantics.export.assert_called_once_with(
            "OPTIONAL MATCH (d:dcat__Dataset), (m1:ns0__Diagnosis)\n"
            'WHERE m1.ns0__code="I10"\n'
            "WITH d\n"
            "MATCH (c:dcat__Catalog)\n"
            "OPTIONAL MATCH (c)-[r0:dcat__dataset]->(d)-[r*0..]->(related)\n"
            'WHERE all(rel IN r WHERE type(rel) <> "rdf__type") '
            "AND d.dspace__isDeleted<>true\n"
            "RETURN c, r0, d, r, related"
        )
        assert isinstance(result, Catalog)
        assert result.graph == mock_graph

    @pytest.mark.asyncio
    async def test_node_does_not_exist(self, repository):
        empty_graph = RDFGraph()
        repository.neosemantics.export = AsyncMock(return_value=empty_graph)
        query = Query()
        with pytest.raises(NodeDoesNotExist):
            await repository.get(query)

    @pytest.mark.asyncio
    async def test_multiple_nodes_found(self, repository):
        mock_graph = Mock()
        repository.neosemantics.export = AsyncMock(return_value=mock_graph)
        mock_graph.subjects.return_value = [Mock(), Mock()]
        query = Query()
        with pytest.raises(MultipleNodesFound):
            await repository.get(query)

    @pytest.mark.asyncio
    async def test_save_success(self, repository):
        repository.neosemantics.save = AsyncMock(return_value={"success": True})
        obj = Mock()
        await repository.save(obj)
        repository.neosemantics.save.assert_called_once_with(obj.graph)

    @pytest.mark.asyncio
    async def test_save_failure(self, repository):
        repository.neosemantics.save = AsyncMock(
            return_value={"success": False, "extra_info": "Error details"}
        )
        obj = Mock()
        with pytest.raises(ErrorSavingData):
            await repository.save(obj)


class TestDatasetsRepository:
    @pytest.fixture
    def repository(self):
        db_driver = Mock()
        repository = DatasetsRepository(db_driver)
        repository.neosemantics = Mock()
        return repository

    @pytest.mark.asyncio
    async def test_get(self, repository):
        mock_graph = Mock()
        mock_graph.subjects.return_value = [Mock()]

        repository.neosemantics.export = AsyncMock(return_value=mock_graph)

        query = Query()
        result = await repository.get(query)

        repository.neosemantics.export.assert_called_once_with(
            "MATCH (d:dcat__Dataset)-[r*0..]->(related)\n"
            'WHERE all(rel IN r WHERE type(rel) <> "rdf__type") '
            "AND d.dspace__isDeleted<>true\n"
            "RETURN d, r, related"
        )
        assert isinstance(result, Dataset)
        assert result.graph == mock_graph

    @pytest.mark.asyncio
    async def test_node_does_not_exist(self, repository):
        empty_graph = RDFGraph()
        repository.neosemantics.export = AsyncMock(return_value=empty_graph)
        query = Query()
        with pytest.raises(NodeDoesNotExist):
            await repository.get(query)

    @pytest.mark.asyncio
    async def test_multiple_nodes_found(self, repository):
        mock_graph = Mock()
        repository.neosemantics.export = AsyncMock(return_value=mock_graph)
        mock_graph.subjects.return_value = [Mock(), Mock()]
        query = Query()
        with pytest.raises(MultipleNodesFound):
            await repository.get(query)

    @pytest.mark.asyncio
    async def test_save_success(self, repository):
        repository.neosemantics.save = AsyncMock(return_value={"success": True})
        obj = Mock()
        await repository.save(obj)
        repository.neosemantics.save.assert_called_once_with(obj.graph)

    @pytest.mark.asyncio
    async def test_save_failure(self, repository):
        repository.neosemantics.save = AsyncMock(
            return_value={"success": False, "extra_info": "Error details"}
        )
        obj = Mock()
        with pytest.raises(ErrorSavingData):
            await repository.save(obj)

    @pytest.mark.asyncio
    async def test_delete(self, repository):
        mock_dataset = Mock()
        repository.get = AsyncMock(return_value=mock_dataset)
        repository.save = AsyncMock()

        query = Query()
        await repository.delete(query)

        repository.get.assert_called_once_with(query)
        repository.save.assert_called_once_with(mock_dataset)
        mock_dataset.set_attribute.assert_called_once_with(DSPACE.isDeleted, True)


class TestFilesRepository:
    @pytest.mark.asyncio
    async def test_get_file_path(self, tmp_path):
        repository = FilesRepository(upload_folder=str(tmp_path))
        result = repository._get_file_path("Test-File~!@#$%^&*()_+.txt")
        assert result == tmp_path / "test-file~!@#$%^&*()_+.txt"

    @pytest.mark.asyncio
    async def test_create_success(self, tmp_path):
        filename = "testfile.txt"
        file_path = tmp_path / filename

        file_content = b"Test content"
        file_mock = Mock()
        file_mock.read.return_value = file_content

        assert not file_path.exists()

        repository = FilesRepository(upload_folder=str(tmp_path))
        await repository.create(file_mock, filename)

        assert file_path.exists()
        with file_path.open("rb") as f:
            assert f.read() == file_content

    @pytest.mark.asyncio
    async def test_create_if_file_exists(self, tmp_path):
        filename = "testfile.txt"
        file_path = tmp_path / filename
        file_path.write_text("old content")

        file_mock = Mock()
        file_mock.read.return_value = b"new content"

        repository = FilesRepository(upload_folder=str(tmp_path))

        await repository.create(file_mock, filename)

        assert file_path.read_text() == "new content"

        # with pytest.raises(FileExistsError):
        #     await repository.create(file_mock, filename)

    @pytest.mark.asyncio
    async def test_get_file_path_success(self, tmp_path):
        filename = "testfile.txt"
        file_path = tmp_path / filename
        file_path.touch()

        repository = FilesRepository(upload_folder=str(tmp_path))
        result = await repository.get_file_path(filename)

        assert result == str(file_path)

    @pytest.mark.asyncio
    async def test_get_file_path_if_file_not_found(self, tmp_path):
        filename = "testfile.txt"
        repository = FilesRepository(upload_folder=str(tmp_path))

        with pytest.raises(FileNotFoundError):
            await repository.get_file_path(filename)

    @pytest.mark.asyncio
    async def test_delete_success(self, tmp_path):
        filename = "testfile.txt"
        file_path = tmp_path / filename
        file_path.touch()

        repository = FilesRepository(upload_folder=str(tmp_path))

        await repository.delete(filename)
        assert not file_path.exists()

    @pytest.mark.asyncio
    async def test_delete_if_file_not_found(self, tmp_path):
        filename = "testfile.txt"
        repository = FilesRepository(upload_folder=str(tmp_path))

        with pytest.raises(FileNotFoundError):
            await repository.delete(filename)

    @pytest.mark.asyncio
    async def test_read_success(self, tmp_path):
        filename = "testfile.txt"
        file_path = tmp_path / filename
        file_content = b"Test content"
        with file_path.open("wb") as f:
            f.write(file_content)

        repository = FilesRepository(upload_folder=str(tmp_path))
        result = await repository.read(filename)

        assert result == file_content


class TestRepositories:
    @pytest.fixture
    def repositories(self):
        db_driver = Mock()
        repositories = Repositories(db_driver)
        repositories.neosemantics = Mock()
        return repositories

    @pytest.mark.asyncio
    async def test_get_namespaces(self, repositories):
        namespaces = Mock()
        repositories.neosemantics.list_namespaces = AsyncMock(return_value=namespaces)
        result = await repositories.get_namespaces()
        assert result == namespaces
