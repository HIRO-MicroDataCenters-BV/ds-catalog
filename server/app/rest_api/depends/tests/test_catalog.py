from datetime import datetime

import pytest

from app.core.queries.catalog import DatasetsFilterDTO

from ..catalog import datasets_filter


class TestDatasetsFilter:
    @pytest.mark.asyncio
    async def test_default_values(self):
        result = await datasets_filter()
        assert result == DatasetsFilterDTO(
            search="",
            theme=None,
            is_local=None,
            is_shared=None,
            creator_id="",
            issued=None,
            issued_gte=None,
            issued_lte=None,
            distribution_bytesize_gte=None,
            distribution_bytesize_lte=None,
            distribution_mimetype="",
        )

    @pytest.mark.asyncio
    async def test_custom_values(self):
        now = datetime.now().date()
        result = await datasets_filter(
            search="test",
            theme=["theme1", "theme2"],
            is_local=True,
            is_shared=False,
            creator_id="kate123",
            issued=now,
            issued_gte=now,
            issued_lte=now,
            distribution_bytesize_gte=100,
            distribution_bytesize_lte=500,
            distribution_mimetype="application/json",
        )
        assert result == DatasetsFilterDTO(
            search="test",
            theme=["theme1", "theme2"],
            is_local=True,
            is_shared=False,
            creator_id="kate123",
            issued=now,
            issued_gte=now,
            issued_lte=now,
            distribution_bytesize_gte=100,
            distribution_bytesize_lte=500,
            distribution_mimetype="application/json",
        )
