from typing import Any, AsyncGenerator, Dict

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator

from app.rest_api.routes import catalog, datasets, health_check, mmio, sharing

from .database import Neo4jDatabase
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


class CustomFastAPI(FastAPI):
    def openapi(self) -> Dict[str, Any]:
        if self.openapi_schema:
            return self.openapi_schema
        openapi_schema = get_openapi(
            title="Data Space Catalog Service",
            version="0.2.0",
            description="The service provides a REST API for managing and "
            "sharing catalog items.",
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
    await db.connect()
    yield
    await db.close()


app = CustomFastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


app.include_router(health_check.routes.router)
app.include_router(catalog.routes.router)
app.include_router(mmio.routes.router)
app.include_router(datasets.routes.router)
app.include_router(sharing.routes.router)
