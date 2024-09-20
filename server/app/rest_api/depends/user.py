from app.core.entities import Person


def get_user() -> Person:
    return Person(
        id="fd2a5fdf-366f-4a7a-b21c-d31d6eee6c76",
        name="John Smith",
    )
