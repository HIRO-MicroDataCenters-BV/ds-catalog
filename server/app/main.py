from typing import Any, AsyncGenerator, Dict

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator

from app.rest_api.routes import catalog, datasets, filters, health_check, mmio, sharing

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
            version="0.2.2",
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication via ds-auth (optional, off by default) ---
# Enabled per deployment by setting DS__AUTH__ENABLED=true alongside the
# other DS__AUTH__* env vars. Matches zero-trust / defense-in-depth
# guidance — the service enforces its own policy regardless of what the
# edge (APISIX / ds-gateway) did.
if settings.auth.enabled:
    # Validate required config BEFORE importing the optional ds-auth
    # package so a misconfiguration surfaces as the config error, not a
    # package-missing error, and the test suite can exercise this path
    # without the auth extra installed.
    if not settings.auth.jwks_url:
        raise RuntimeError(
            "DS__AUTH__ENABLED=true requires DS__AUTH__JWKS_URL to be set"
        )

    try:
        from ds_auth import DataspaceAuthMiddleware
    except ImportError as e:
        raise RuntimeError(
            "DS__AUTH__ENABLED=true but ds-auth is not installed. "
            "Install with: poetry install --extras auth"
        ) from e

    from app.rest_api.auth_config import PERMISSION_MAP, PUBLIC_PATHS

    if not settings.auth.policy_engine_url:
        raise RuntimeError(
            "DS__AUTH__ENABLED=true requires DS__AUTH__POLICY_ENGINE_URL "
            "to be set (ds-catalog cannot resolve permissions itself — "
            "ds-policy-engine does)"
        )

    app.add_middleware(
        DataspaceAuthMiddleware,
        jwks_url=settings.auth.jwks_url,
        issuer=settings.auth.jwt_issuer,
        audience=settings.auth.jwt_audience,
        policy_engine_url=settings.auth.policy_engine_url,
        permission_map=PERMISSION_MAP,
        public_paths=list(PUBLIC_PATHS),
    )


Instrumentator().instrument(app).expose(app)


app.include_router(health_check.routes.router)
app.include_router(catalog.routes.router)
app.include_router(mmio.routes.router)
app.include_router(datasets.routes.router)
app.include_router(sharing.routes.router)
app.include_router(filters.routes.router)
