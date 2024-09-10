from ..common import PaginatedResult


def test_paginated_result():
    result = PaginatedResult[int](page=1, size=50, items=[1, 2, 3, 4, 5])
    assert result.page == 1
    assert result.size == 50
    assert result.items == [1, 2, 3, 4, 5]
