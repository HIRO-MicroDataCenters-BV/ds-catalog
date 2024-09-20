from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Database(BaseModel):
    protocol: str = "neo4j"
    host: str = "localhost"
    port: int = 7687
    name: str = "neo4j"
    username: str = "neo4j"
    password: str = "neo4j"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="DS__",
        case_sensitive=False,
        extra="ignore",
    )

    database: Database = Database()
    test_database: Database = Database()


def get_settings() -> Settings:
    settings = Settings()
    return settings
