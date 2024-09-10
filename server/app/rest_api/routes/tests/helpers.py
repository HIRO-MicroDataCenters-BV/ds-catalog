from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.testclient import TestClient


def create_test_client(*args: APIRouter) -> TestClient:
    app = FastAPI()
    for router in args:
        app.include_router(router)
    return TestClient(app)
