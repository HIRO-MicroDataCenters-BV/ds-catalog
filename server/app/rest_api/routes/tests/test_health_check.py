from fastapi import FastAPI
from fastapi.testclient import TestClient

from .. import health_check

app = FastAPI()
app.include_router(health_check.routes.router)

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health-check/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
