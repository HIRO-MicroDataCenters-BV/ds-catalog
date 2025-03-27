from polyfactory.factories.pydantic_factory import ModelFactory

from ..serializers import Person


class PersonFactory(ModelFactory[Person]):
    __model__ = Person
