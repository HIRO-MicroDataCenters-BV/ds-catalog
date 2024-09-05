from typing import Any, Dict

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator

from .rest_api.routes import (
    catalog_items,
    catalog_items_data,
    catalog_items_importing,
    catalog_items_sharing,
    health_check,
)


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


app = CustomFastAPI()


Instrumentator().instrument(app).expose(app)


app.include_router(health_check.routes.router)
app.include_router(catalog_items.routes.router)
app.include_router(catalog_items_data.routes.router)
app.include_router(catalog_items_sharing.routes.router)
app.include_router(catalog_items_importing.routes.router)
