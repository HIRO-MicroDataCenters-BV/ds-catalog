from pydantic import BaseModel

from ..serializers import HealthCheck
from .factories import PersonFactory


class Serializer(BaseModel):
    some_field: str
    another_field: int


class TestHealthCheck:
    def test_common(self) -> None:
        health_check = HealthCheck(status="OK")
        assert health_check.status == "OK"

        health_check = HealthCheck(status="FAIL")
        assert health_check.status == "FAIL"


class TestPerson:
    def test_to_entity(self) -> None:
        user = PersonFactory.build()
        entity = user.to_entity()

        assert user.id == entity["id"]
        assert user.name == entity["name"]
