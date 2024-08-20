from fastapi import FastAPI
from fastapi.testclient import TestClient

from .. import example

app = FastAPI()
app.include_router(example.router)

client = TestClient(app)


def test_read_main() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"value": "Hello World"}
