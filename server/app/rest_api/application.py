from typing import Any, Dict

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator

from .database import close_graph_connection, initialize_graph_connection
from .routes import datasets, datasets_importing, datasets_sharing, health_check
from .settings import get_settings


class CustomFastAPI(FastAPI):
    def openapi(self) -> Dict[str, Any]:
        if self.openapi_schema:
            return self.openapi_schema
        openapi_schema = get_openapi(
            title="Data Space Catalog",
            version="0.1.1",
            description="The service provides a REST API for managing and "
            "sharing catalog data. Interacts with connector services to "
            "obtain information about data products.",
            contact={
                "name": "HIRO-MicroDataCenters",
                "email": "all-hiro@hiro-microdatacenters.nl",
            },
            license_info={
                "name": "MIT",
                "url": "https://github.com/HIRO-MicroDataCenters-BV"
                "/ds-catalog/blob/main/LICENSE",
            },
            routes=self.routes,
        )
        self.openapi_schema = openapi_schema
        return self.openapi_schema


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    initialize_graph_connection(str(settings.database_uri), settings.neo4j_auth)
    yield
    close_graph_connection()


app = CustomFastAPI(lifespan=lifespan)


Instrumentator().instrument(app).expose(app)


app.include_router(health_check.routes.router)
app.include_router(datasets.routes.router)
app.include_router(datasets_sharing.routes.router)
app.include_router(datasets_importing.routes.router)
