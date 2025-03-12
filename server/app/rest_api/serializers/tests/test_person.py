from app.core.tests.factories import PersonFactory as PersonEntityFactory

from ..person import Person
from .factories import PersonFactory


class TestPerson:
    def test_to_entity(self) -> None:
        user = PersonFactory.build()
        entity = user.to_entity()

        assert user.id == entity.id
        assert user.name == entity.name

    def test_from_entity(self) -> None:
        entity = PersonEntityFactory.build()
        user = Person.from_entity(entity)

        assert user.id == entity.id
        assert user.name == entity.name
