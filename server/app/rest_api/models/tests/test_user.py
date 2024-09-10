from app.core.entities.tests.factories import UserFactory as UserEntityFactory

from ..user import User
from .factories import UserFactory


class TestUser:
    def test_to_entity(self):
        user = UserFactory.build()
        entity = user.to_entity()

        assert user.id == entity.id
        assert user.full_name == entity.full_name

    def test_from_entity(self):
        entity = UserEntityFactory.build()
        user = User.from_entity(entity)

        assert user.id == entity.id
        assert user.full_name == entity.full_name
