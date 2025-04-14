from unittest.mock import AsyncMock, Mock

import pytest
from rdflib import Graph as RDFGraph
from rdflib.namespace import DCTERMS

from app.core.entities import Catalog, Dataset, Person
from app.core.exceptions import ErrorSavingData, MultipleNodesFound, NodeDoesNotExist
from app.core.namespace import DSPACE

from ..queries import Query
from ..repositories import CatalogsRepository, DatasetsRepository, PersonsRepository


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

        query = Query()
        result = await repository.get(query)

        repository.neosemantics.export.assert_called_once_with(
            "MATCH (c:dcat__Catalog)\n"
            "OPTIONAL MATCH (c)-[dataset_rel:dcat__dataset]->(d:dcat__Dataset)\n"
            "WHERE d.dspace__isDeleted<>true\n"
            "OPTIONAL MATCH (d)-[r*0..]->(related)\n"
            'WHERE all(rel IN r WHERE type(rel) <> "rdf__type")\n'
            "RETURN c, dataset_rel, d, r, related"
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
