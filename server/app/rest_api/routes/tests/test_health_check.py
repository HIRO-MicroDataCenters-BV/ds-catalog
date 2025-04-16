from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from ..health_check import routes

app = FastAPI()
app.include_router(routes.router)

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health-check/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "OK"}
