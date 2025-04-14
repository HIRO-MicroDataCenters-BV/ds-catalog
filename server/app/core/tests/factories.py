from ..entities import User


def user_factory(id="123", name="Smith"):
    return User(id=id, name=name)
