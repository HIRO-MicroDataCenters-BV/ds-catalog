from polyfactory.factories.pydantic_factory import ModelFactory

from ..serializers import User


class UserFactory(ModelFactory[User]):
    __model__ = User
