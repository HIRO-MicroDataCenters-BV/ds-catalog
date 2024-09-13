from pydantic import AnyUrl, Field
from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_uri: AnyUrl = Url("neo4j://localhost:7687")
    neo4j_auth: str = Field(pattern=r"^(.+)/(.+)$", default="neo4j/")


def get_settings() -> Settings:
    settings = Settings()
    return settings
