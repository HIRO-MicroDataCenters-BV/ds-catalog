from fastapi import Depends

from app.core.entities import Person
from app.core.repository import Repositories
from app.database import DatabaseDriver, get_db_driver


def get_user() -> Person:
    return Person(
        id="fd2a5fdf-366f-4a7a-b21c-d31d6eee6c76",
        name="John Smith",
    )


def get_repositories(
    db_driver: DatabaseDriver = Depends(get_db_driver),
) -> Repositories:
    return Repositories(db_driver)
