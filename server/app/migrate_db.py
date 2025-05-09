from typing import Awaitable, Callable

import asyncio

from app.core.repository.repositories import Repositories

from .database import DatabaseDriver, Neo4jDatabase, get_db_driver
from .settings import get_settings

settings = get_settings()
db = Neo4jDatabase(
    protocol=settings.database.protocol,
    host=settings.database.host,
    port=settings.database.port,
    name=settings.database.name,
    username=settings.database.username,
    password=settings.database.password,
)


async def configure_db(db_driver: DatabaseDriver) -> None:
    await db_driver.execute_query(
        """
        CALL n10s.graphconfig.init({
            handleVocabUris: "SHORTEN",
            handleRDFTypes: "LABELS_AND_NODES",
            baseSchemaNamespace: "http://example.com/",
            keepLangTag: true,
            keepCustomDataTypes: true,
            handleMultival: "ARRAY",
            multivalPropList : [
                "http://www.w3.org/ns/dcat#theme", "http://purl.org/dc/terms/title"]
        });
    """
    )

    await db_driver.execute_query(
        "CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) "
        "REQUIRE r.uri IS UNIQUE;"
    )

    await db_driver.execute_query(
        'CALL n10s.nsprefixes.add("xsd", "http://www.w3.org/2001/XMLSchema#");'
    )
    await db_driver.execute_query(
        'CALL n10s.nsprefixes.add("dcat", "http://www.w3.org/ns/dcat#");'
    )
    await db_driver.execute_query(
        'CALL n10s.nsprefixes.add("dcatap", "http://data.europa.eu/r5r/");'
    )
    await db_driver.execute_query(
        'CALL n10s.nsprefixes.add("dcterms", "http://purl.org/dc/terms/");'
    )
    await db_driver.execute_query(
        'CALL n10s.nsprefixes.add("spdx", "http://spdx.org/rdf/terms#");'
    )
    await db_driver.execute_query(
        'CALL n10s.nsprefixes.add("foaf", "http://xmlns.com/foaf/0.1/");'
    )
    await db_driver.execute_query(
        'CALL n10s.nsprefixes.add("skos", "http://www.w3.org/2004/02/skos/core#");'
    )
    await db_driver.execute_query(
        'CALL n10s.nsprefixes.add("dspace", "http://data-space.org/");'
    )


async def upload_ontology(db_driver: DatabaseDriver) -> None:
    await db_driver.execute_query(
        f'CALL n10s.onto.import.fetch("{settings.ontology_url}", "Turtle");'
    )


async def init_catalog(db_driver: DatabaseDriver) -> None:
    repositories = Repositories(db_driver)
    await repositories.catalogs.create(
        title=settings.catalog.title,
        description=settings.catalog.description,
    )


async def run_migrations(
    migrations: list[Callable[[DatabaseDriver], Awaitable[None]]]
) -> None:
    """Run the migrations"""

    print("Starting migrations...")

    print("Connecting to the database...")
    await db.connect()

    db_driver = get_db_driver()

    print("Running migrations:")
    for migration in migrations:
        print(f"- {migration.__name__}", end="")
        await migration(db_driver)
        print(" [OK]")

    print("Closing the database connection...")
    await db.close()

    print("Migrations completed.")


if __name__ == "__main__":
    asyncio.run(
        run_migrations(
            migrations=[
                configure_db,
                upload_ontology,
                init_catalog,
            ]
        )
    )
