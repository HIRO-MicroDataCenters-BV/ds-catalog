from datetime import datetime

import pytest

from app.core.repository.queries import DatasetsFilterDTO

from ..catalog import datasets_filter


class TestDatasetsFilter:
    @pytest.mark.asyncio
    async def test_default_values(self) -> None:
        result = await datasets_filter()
        assert result == DatasetsFilterDTO(
            search="",
            theme=None,
            is_local=None,
            is_shared=None,
            issued=None,
            issued_gte=None,
            issued_lte=None,
        )

    @pytest.mark.asyncio
    async def test_custom_values(self) -> None:
        now = datetime.now().date()
        result = await datasets_filter(
            search="test",
            theme=["theme1", "theme2"],
            is_local=True,
            is_shared=False,
            issued=now,
            issued_gte=now,
            issued_lte=now,
        )
        assert result == DatasetsFilterDTO(
            search="test",
            theme=["theme1", "theme2"],
            is_local=True,
            is_shared=False,
            issued=now,
            issued_gte=now,
            issued_lte=now,
        )
