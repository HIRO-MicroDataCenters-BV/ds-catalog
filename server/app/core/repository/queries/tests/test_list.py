from typing import Generator

import pytest

from app.core.repository.models import DatasetNode
from app.core.repository.tests.helpers import (
    clean_db,
    compare_sets_by_field,
    connect_db,
    create_dataset_nodes,
    mark_async_db_test,
)
from app.core.tests.factories import DatasetFactory

from ..list import OrderQuery, PaginatorQuery


@pytest.fixture(autouse=True, scope="session")
def db_connection() -> Generator[None, None, None]:
    connect_db()
    yield
    clean_db()


@pytest.fixture(autouse=True)
def clean_db_before_each_test() -> None:
    clean_db()


class TestPaginatorQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        entities = DatasetFactory.batch(10)
        await create_dataset_nodes(entities)

        query = PaginatorQuery(page=2, page_size=3)
        result = await query.apply(DatasetNode.nodes).order_by("title").all()

        expected = list(sorted(entities, key=lambda x: x.title))[3:6]
        assert compare_sets_by_field(result, expected, "identifier")


class TestOrderQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        entities = DatasetFactory.batch(3)
        await create_dataset_nodes(entities)

        query = OrderQuery(order_by="title")
        result = await query.apply(DatasetNode.nodes).all()
        expected = list(sorted(entities, key=lambda x: x.title))
        assert compare_sets_by_field(result, expected, "identifier")

        query = OrderQuery(order_by="-title")
        result = await query.apply(DatasetNode.nodes).all()
        expected = list(sorted(entities, key=lambda x: x.title))
        expected.reverse()
        assert compare_sets_by_field(result, expected, "identifier")
