from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Database(BaseModel):
    protocol: str = "bolt"
    host: str = "localhost"
    port: int = 7687
    name: str = "neo4j"
    username: str = "neo4j"
    password: str = "neo4j"


class Catalog(BaseModel):
    title: str = "Local Catalog"
    description: str = ""


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

    catalog: Catalog = Catalog()
    data_root_path: str = "/data/"
    oca_uri: str = "http://oca.example.org/123/"
    ontology_url: str = "https://www.w3.org/ns/dcat.ttl"
    shacl_url: str = (
        "https://semiceu.github.io/DCAT-AP/releases/3.0.0/shacl/dcat-ap-SHACL.ttl"
    )
    global_oca_bundles_base_url: str = (
        "https://oca-repository.marketplace.nextgen.hiro-develop.nl/oca-bundles"
    )
    connector_base_url: str = "https://ds-connector.{region}.nextgen.hiro-develop.nl"
    filters_file: str = str(Path(__file__).resolve().parent / "core" / "filters.json")
    allowed_values_config_path: str = str(
        Path(__file__).resolve().parent / "core" / "allowed_values.yaml"
    )


def get_settings() -> Settings:
    settings = Settings()
    return settings
