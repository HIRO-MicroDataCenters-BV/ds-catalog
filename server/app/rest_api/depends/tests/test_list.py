import pytest

from app.core.repository.queries import OrderQueryDTO, PaginatorQueryDTO

from ..list import order_parameters, paginator_parameters


class TestPaginatorParameters:
    @pytest.mark.asyncio
    async def test_default_values(self) -> None:
        result = await paginator_parameters()
        assert result == PaginatorQueryDTO(page=1, page_size=100)

    @pytest.mark.asyncio
    async def test_custom_values(self) -> None:
        result = await paginator_parameters(page=2, page_size=20)
        assert result == PaginatorQueryDTO(page=2, page_size=20)

    @pytest.mark.asyncio
    async def test_partial_values(self) -> None:
        result = await paginator_parameters(page=3)
        assert result == PaginatorQueryDTO(page=3, page_size=100)

        result = await paginator_parameters(page_size=50)
        assert result == PaginatorQueryDTO(page=1, page_size=50)


class TestOrderParameters:
    @pytest.mark.asyncio
    async def test_default_values(self) -> None:
        result = await order_parameters()
        assert result == OrderQueryDTO(order_by="")

    @pytest.mark.asyncio
    async def test_custom_values(self) -> None:
        result = await order_parameters(order_by="name")
        assert result == OrderQueryDTO(order_by="name")
