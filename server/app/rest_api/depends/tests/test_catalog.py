from datetime import datetime
from uuid import uuid4

import pytest

from app.core.entities.catalog import Ontology
from app.core.queries.catalog import CatalogItemsFiltersDTO

from ..catalog import catalog_items_filters


class TestCatalogItemsFilters:
    @pytest.mark.asyncio
    async def test_default_values(self):
        result = await catalog_items_filters()
        assert result == CatalogItemsFiltersDTO(
            search="",
            ontology=None,
            is_local=None,
            is_shared=None,
            creator_id=None,
            created=None,
            created_gte=None,
            created_lte=None,
            data_product_id="",
            data_product_size_gte=None,
            data_product_size_lte=None,
            data_product_mimetype="",
        )

    @pytest.mark.asyncio
    async def test_custom_values(self):
        now = datetime.now()
        creator_id = uuid4()
        result = await catalog_items_filters(
            search="test",
            ontology=Ontology.DCAT_3,
            is_local=True,
            is_shared=False,
            creator_id=creator_id,
            created=now,
            created_gte=now,
            created_lte=now,
            data_product_id="dp123",
            data_product_size_gte=100,
            data_product_size_lte=500,
            data_product_mimetype="application/json",
        )
        assert result == CatalogItemsFiltersDTO(
            search="test",
            ontology=Ontology.DCAT_3,
            is_local=True,
            is_shared=False,
            creator_id=creator_id,
            created=now,
            created_gte=now,
            created_lte=now,
            data_product_id="dp123",
            data_product_size_gte=100,
            data_product_size_lte=500,
            data_product_mimetype="application/json",
        )

    @pytest.mark.asyncio
    async def test_partial_values(self):
        creator_id = uuid4()
        result = await catalog_items_filters(
            creator_id=creator_id, data_product_id="dp123"
        )
        assert result == CatalogItemsFiltersDTO(
            search="",
            ontology=None,
            is_local=None,
            is_shared=None,
            creator_id=creator_id,
            created=None,
            created_gte=None,
            created_lte=None,
            data_product_id="dp123",
            data_product_size_gte=None,
            data_product_size_lte=None,
            data_product_mimetype="",
        )
