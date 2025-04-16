from typing import Optional

from neo4j import AsyncDriver, AsyncGraphDatabase

DatabaseDriver = AsyncDriver


class DatabaseError(Exception):
    ...


class DatabaseNotInitializedError(DatabaseError):
    def __init__(self, message="Database is not initialized"):
        self.message = message
        super().__init__(self.message)


class DriverNotInitializedError(DatabaseError):
    def __init__(self, message="Database driver is not initialized"):
        self.message = message
        super().__init__(self.message)


class Neo4jDatabase:
    _instance: Optional["Neo4jDatabase"] = None

    uri: str
    name: str
    auth: tuple[str, str]

    driver: AsyncDriver | None = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        protocol: str,
        host: str,
        port: int,
        name: str,
        username: str,
        password: str,
    ):
        self.uri = f"{protocol}://{host}:{port}"
        self.name = name
        self.auth = (username, password)

    @classmethod
    def get_instance(cls) -> "Neo4jDatabase":
        if not cls._instance:
            raise DatabaseNotInitializedError()
        return cls._instance

    async def connect(self) -> AsyncDriver:
        self.driver = AsyncGraphDatabase.driver(self.uri, auth=self.auth)
        await self.driver.verify_connectivity()
        return self.driver

    async def close(self):
        if self.driver:
            await self.driver.close()


def get_db_driver() -> AsyncDriver:
    """Get the Neo4j driver"""
    driver = Neo4jDatabase.get_instance().driver
    if driver is None:
        raise DriverNotInitializedError()
    return driver
