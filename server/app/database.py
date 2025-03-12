from neomodel import config


def initialize_graph_db_connection(
    protocol: str,
    host: str,
    port: int,
    name: str,
    username: str,
    password: str,
) -> None:
    config.DATABASE_URL = f"{protocol}://{username}:{password}@{host}:{port}"
    config.DATABASE_NAME = name
    config.FORCE_TIMEZONE = True
