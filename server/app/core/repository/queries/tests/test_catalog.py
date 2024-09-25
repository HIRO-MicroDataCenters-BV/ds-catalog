from typing import Generator

from datetime import date

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

from ..catalog import (
    DatasetsFilterByIdQuery,
    DatasetsFilterDTO,
    DatasetsFilterQuery,
    DatasetsIsLocalQuery,
    DatasetsIsSharedQuery,
    DatasetsIssuedGteQuery,
    DatasetsIssuedLteQuery,
    DatasetsIssuedQuery,
    DatasetsKeywordQuery,
    DatasetsSearchQuery,
    DatasetsThemeQuery,
)


@pytest.fixture(autouse=True, scope="session")
def db_connection() -> Generator[None, None, None]:
    connect_db()
    yield
    clean_db()


@pytest.fixture(autouse=True)
def clean_db_before_each_test() -> None:
    clean_db()


class TestDatasetsFilterByIdQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        entities = DatasetFactory.batch(2)
        await create_dataset_nodes(entities)

        query = DatasetsFilterByIdQuery(entities[0].identifier)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entities[0]], "identifier")


class TestDatasetsSearchQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        term = "test term"

        entity1 = DatasetFactory.build(title=f"some text {term} some text")
        entity2 = DatasetFactory.build(description=f"another text with {term}")
        entity3 = DatasetFactory.build()

        await create_dataset_nodes([entity1, entity2, entity3])

        query = DatasetsSearchQuery(term)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1, entity2], "identifier")


class TestDatasetsKeywordQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        keyword1 = "keyword1"
        keyword2 = "keyword2"

        entity1 = DatasetFactory.build(keyword=[keyword1, keyword2])
        entity2 = DatasetFactory.build(keyword=[keyword1])
        entity3 = DatasetFactory.build(keyword=[keyword2, "some keyword"])
        entity4 = DatasetFactory.build()

        await create_dataset_nodes([entity1, entity2, entity3, entity4])

        query = DatasetsKeywordQuery([keyword1, keyword2])
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1, entity2, entity3], "identifier")


class TestDatasetsThemeQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        theme1 = "theme1"
        theme2 = "theme2"

        entity1 = DatasetFactory.build(theme=[theme1, theme2])
        entity2 = DatasetFactory.build(theme=[theme1])
        entity3 = DatasetFactory.build(theme=[theme2, "some theme"])
        entity4 = DatasetFactory.build()

        await create_dataset_nodes([entity1, entity2, entity3, entity4])

        query = DatasetsThemeQuery([theme1, theme2])
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1, entity2, entity3], "identifier")


class TestDatasetsIsLocalQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        entity1 = DatasetFactory.build(is_local=True)
        entity2 = DatasetFactory.build(is_local=False)

        await create_dataset_nodes([entity1, entity2])

        query = DatasetsIsLocalQuery(True)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1], "identifier")


class TestDatasetsIsSharedQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        entity1 = DatasetFactory.build(is_shared=True)
        entity2 = DatasetFactory.build(is_shared=False)

        await create_dataset_nodes([entity1, entity2])

        query = DatasetsIsSharedQuery(True)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1], "identifier")


class TestDatasetsIssuedQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        issued = date(2024, 5, 1)

        entity1 = DatasetFactory.build(issued=issued)
        entity2 = DatasetFactory.build()

        await create_dataset_nodes([entity1, entity2])

        query = DatasetsIssuedQuery(issued)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1], "identifier")


class TestDatasetsIssuedGteQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        issued = date(2024, 1, 1)

        entity1 = DatasetFactory.build(issued=issued)
        entity2 = DatasetFactory.build(issued=date(2025, 1, 1))
        entity3 = DatasetFactory.build(issued=date(2023, 1, 1))

        await create_dataset_nodes([entity1, entity2, entity3])

        query = DatasetsIssuedGteQuery(issued)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1, entity2], "identifier")


class TestDatasetsIssuedLteQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        issued = date(2024, 1, 1)

        entity1 = DatasetFactory.build(issued=issued)
        entity2 = DatasetFactory.build(issued=date(2025, 1, 1))
        entity3 = DatasetFactory.build(issued=date(2023, 1, 1))

        await create_dataset_nodes([entity1, entity2, entity3])

        query = DatasetsIssuedLteQuery(issued)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1, entity3], "identifier")


class TestDatasetsFilterQuery:
    @mark_async_db_test
    async def test_common(self) -> None:
        title = "term"
        theme = ["theme"]
        keyword = ["keyword"]
        is_local = True
        is_shared = False
        issued = date(2024, 1, 1)

        entity1 = DatasetFactory.build(
            title=title,
            keyword=keyword,
            theme=theme,
            is_local=is_local,
            is_shared=is_shared,
            issued=issued,
        )
        entity2 = DatasetFactory.build()

        await create_dataset_nodes([entity1, entity2])

        dto = DatasetsFilterDTO(
            search=title,
            keyword=keyword,
            theme=theme,
            is_local=is_local,
            is_shared=is_shared,
            issued=issued,
            issued_gte=None,
            issued_lte=None,
        )
        query = DatasetsFilterQuery(**dto)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1], "identifier")

    @mark_async_db_test
    async def test_date_range(self) -> None:
        entity1 = DatasetFactory.build(issued=date(2024, 1, 1))
        entity2 = DatasetFactory.build(issued=date(2000, 1, 1))

        await create_dataset_nodes([entity1, entity2])

        dto = DatasetsFilterDTO(
            search="",
            keyword=None,
            theme=None,
            is_local=None,
            is_shared=None,
            issued=None,
            issued_gte=date(2023, 1, 1),
            issued_lte=date(2025, 1, 1),
        )
        query = DatasetsFilterQuery(**dto)
        result = await query.apply(DatasetNode.nodes).all()

        assert compare_sets_by_field(result, [entity1], "identifier")
