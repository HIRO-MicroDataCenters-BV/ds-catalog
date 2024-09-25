from typing import Generator

import pytest

from app.core.exceptions import DatasetDoesNotExist
from app.core.tests.factories import DatasetFactory

from ..models import (
    CatalogNode,
    ChecksumNode,
    DataServiceNode,
    DatasetNode,
    DistributionNode,
    PersonNode,
)
from ..queries.catalog import DatasetsFilterByIdQuery
from ..queries.list import OrderQuery
from ..repositories import catalog_item_repo
from .helpers import clean_db, compare_sets_by_field, connect_db, mark_async_db_test


@pytest.fixture(autouse=True, scope="session")
def db_connection() -> Generator[None, None, None]:
    connect_db()
    yield
    clean_db()


@pytest.fixture(autouse=True)
def clean_db_before_each_test() -> None:
    clean_db()


class TestCatalogItemRepository:
    @mark_async_db_test
    async def test_list(self) -> None:
        dataset_entities = DatasetFactory.batch(2)
        for dataset_entity in dataset_entities:
            await catalog_item_repo.create(dataset_entity)

        query = OrderQuery(order_by="title")
        result = await catalog_item_repo.list(query)

        assert compare_sets_by_field(result, dataset_entities, "identifier")

    @mark_async_db_test
    async def test_get(self) -> None:
        dataset_entity = DatasetFactory.build()
        dataset_entity = await catalog_item_repo.create(dataset_entity)

        query = DatasetsFilterByIdQuery(id=dataset_entity.identifier)
        result = await catalog_item_repo.get(query)

        assert result == dataset_entity

    @mark_async_db_test
    async def test_get_if_not_exist(self) -> None:
        with pytest.raises(DatasetDoesNotExist):
            query = DatasetsFilterByIdQuery(id="123")
            await catalog_item_repo.get(query)

    @mark_async_db_test
    async def test_exists(self) -> None:
        dataset_entity = DatasetFactory.build()

        query = DatasetsFilterByIdQuery(id=dataset_entity.identifier)
        result = await catalog_item_repo.exists(query)
        assert result is False

        await catalog_item_repo.create(dataset_entity)

        result = await catalog_item_repo.exists(query)
        assert result is True

    @mark_async_db_test
    async def test_create(self) -> None:
        dataset_entity = DatasetFactory.build()
        dataset_entity = await catalog_item_repo.create(dataset_entity)

        dataset_node = await catalog_item_repo._get_node(dataset_entity)

        assert dataset_node.title == dataset_entity.title
        assert dataset_node.description == dataset_entity.description
        assert dataset_node.keyword == dataset_entity.keyword
        assert dataset_node.license == dataset_entity.license
        assert dataset_node.theme == dataset_entity.theme
        assert dataset_node.is_local == dataset_entity.is_local
        assert dataset_node.is_shared == dataset_entity.is_shared

        creator_node = await dataset_node.creator.get()
        assert creator_node is not None
        assert creator_node.identifier == dataset_entity.creator.id
        assert creator_node.name == dataset_entity.creator.name

        catalog_node = await dataset_node.catalog.get_or_none()
        assert catalog_node is not None
        assert await catalog_node.creator.get() == creator_node
        assert await catalog_node.dataset.all() == [dataset_node]
        assert await catalog_node.service.all() == await dataset_node.services.all()

        distribution_nodes = await dataset_node.distribution.all()
        assert len(distribution_nodes) == len(dataset_entity.distribution) == 1
        distribution_node = distribution_nodes[0]
        distribution_entity = dataset_entity.distribution[0]
        assert distribution_node.byte_size == distribution_entity.byte_size
        assert distribution_node.media_type == distribution_entity.media_type

        checksum_node = await distribution_node.checksum.get()
        checksum_entity = distribution_entity.checksum
        assert checksum_node.algorithm == checksum_entity.algorithm
        assert checksum_node.checksum_value == checksum_entity.checksum_value

        service_nodes = await distribution_node.access_service.all()
        assert len(service_nodes) == len(distribution_entity.access_service) == 1
        service_node = service_nodes[0]
        service_entity = distribution_entity.access_service[0]
        assert service_node.endpoint_url == service_entity.endpoint_url

    @mark_async_db_test
    async def test_update(self) -> None:
        exists_entity = await catalog_item_repo.create(DatasetFactory.build())
        await catalog_item_repo._get_node(exists_entity)

        dataset_entity = DatasetFactory.build()
        dataset_entity.identifier = exists_entity.identifier

        updated_entity = await catalog_item_repo.update(dataset_entity)
        dataset_node = await catalog_item_repo._get_node(updated_entity)

        assert updated_entity.model_dump() == dataset_entity.model_dump()

        creator_node = await dataset_node.creator.get()
        assert creator_node is not None

        catalog_node = await dataset_node.catalog.get_or_none()
        assert catalog_node is not None
        assert await catalog_node.creator.get() == creator_node
        assert await catalog_node.dataset.all() == [dataset_node]
        assert await catalog_node.service.all() == await dataset_node.services.all()

    @mark_async_db_test
    async def test_delete_node(self) -> None:
        dataset_entity = DatasetFactory.build()
        dataset_entity = await catalog_item_repo.create(dataset_entity)

        dataset_node = await catalog_item_repo._get_node(dataset_entity)

        catalog_node = await dataset_node.catalog.get()
        creator_node = await dataset_node.creator.get()

        await catalog_item_repo.delete(dataset_entity)

        query = OrderQuery(order_by="")
        result = await catalog_item_repo.list(query)

        assert result == []

        assert await DatasetNode.nodes.all() == []
        assert await ChecksumNode.nodes.all() == []
        assert await DistributionNode.nodes.all() == []
        assert await DataServiceNode.nodes.all() == []

        assert await catalog_node.dataset.all() == []
        assert await catalog_node.service.all() == []

        assert await CatalogNode.nodes.first() == catalog_node
        assert await catalog_node.creator.get() == creator_node

        assert await PersonNode.nodes.first() == creator_node
