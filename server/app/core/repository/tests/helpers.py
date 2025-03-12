from typing import Any, Iterable

import pytest
from neomodel import clear_neo4j_database, db

from app.core.entities import Dataset
from app.database import initialize_graph_db_connection
from app.settings import get_settings

from ..repositories import catalog_item_repo

mark_async_db_test = pytest.mark.asyncio(loop_scope="session")


def connect_db() -> None:
    """
    Example of use.

    The connection is created for the session.
    Before each test, the database is cleared.
    The database is cleared after all tests are completed.

    @pytest.fixture(autouse=True, scope="session")
    def db_connection():
        connect_db()
        yield
        clean_db()

    @pytest.fixture(autouse=True)
    def clean_db_before_each_test():
        clean_db()

    @mark_async_db_test  # Necessary for correct connection to the database
    async def test_foo():
        ...

    """
    settings = get_settings()
    initialize_graph_db_connection(
        protocol=settings.test_database.protocol,
        host=settings.test_database.host,
        port=settings.test_database.port,
        name=settings.test_database.name,
        username=settings.test_database.username,
        password=settings.test_database.password,
    )


def clean_db() -> None:
    clear_neo4j_database(db)


async def create_dataset_nodes(entities: list[Dataset]) -> None:
    for entity in entities:
        await catalog_item_repo.create(entity)


def compare_sets_by_field(
    nodeset1: Iterable[Any],
    nodeset2: Iterable[Any],
    field_name: str,
) -> bool:
    set1 = set([getattr(i, field_name) for i in nodeset1])
    set2 = set([getattr(i, field_name) for i in nodeset2])
    return set1 == set2
