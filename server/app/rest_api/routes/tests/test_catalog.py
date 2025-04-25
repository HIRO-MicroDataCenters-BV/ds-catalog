import json
from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from rdflib import DCTERMS

from app.core.entities import Catalog, CatalogFilters
from app.core.exceptions import ErrorConstructingQuery
from app.core.tests.factories import user_factory
from app.rest_api.depends import get_user

from ..catalog import get_usecases, routes

user = user_factory()

catalog = Catalog.create_empty("http://example.com/1")
catalog.set_attribute(DCTERMS.title, "Test Catalog")

usecases = Mock()
usecases.get_local_catalog = AsyncMock(return_value=catalog)


def override_get_user():
    return user


def override_get_usecases():
    return usecases


app = FastAPI()
app.include_router(routes.router)

app.dependency_overrides[get_user] = override_get_user
app.dependency_overrides[get_usecases] = override_get_usecases

client = TestClient(app)


class TestCatalogRoutes:
    def test_get_local_catalog(self):
        filters = {
            "@context": {
                "dspace": "http://data-space.org/",
                "med": "http://med.example.org/",
            },
            "@type": "dspace:Filters",
            "dspace:filters": [{"med:code": "I10"}],
        }
        response = client.post("/catalog/", json=filters)

        assert response.status_code == status.HTTP_200_OK
        assert Catalog.from_json_ld(response.text) == catalog

        usecases.get_local_catalog.assert_called_once()
        assert usecases.get_local_catalog.call_args[0][
            0
        ] == CatalogFilters.from_json_ld(json.dumps(filters))
        assert usecases.get_local_catalog.call_args[1]["context"] == {"user": user}

    def test_get_local_catalog_if_error_constructing_query(self):
        error_message = "Test error"
        error = ErrorConstructingQuery(error_message)
        usecases.get_local_catalog = AsyncMock(side_effect=error)

        response = client.post("/catalog/", json={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": error_message}
