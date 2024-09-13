from typing import Generator

from neo4j import Driver, GraphDatabase, Session

driver: Driver


def initialize_graph_connection(uri: str, auth_string: str) -> Driver:
    global driver
    username, password = auth_string.split("/")
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    return driver


def close_graph_connection() -> None:
    global driver
    driver.close()


def get_graph_session() -> Generator[Session, None, None]:
    global driver
    with driver.session() as session:
        yield session
