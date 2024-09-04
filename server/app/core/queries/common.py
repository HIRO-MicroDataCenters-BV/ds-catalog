from .interface import IQuery


class GetPaginated(IQuery):
    _page: int
    _size: int

    def __init__(self, page: int, size: int) -> None:
        self._page = page
        self._size = size

    def build(self) -> dict[str, int]:
        return {"page": self._page, "size": self._size}
