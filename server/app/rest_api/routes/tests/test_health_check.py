from .. import health_check
from .helpers import create_test_client


def test_health_check() -> None:
    client = create_test_client(health_check.routes.router)
    response = client.get("/health-check/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
