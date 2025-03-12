from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import AnyUrl

from ..context import Context, CreateDatasetContext
from ..entities import Catalog, Dataset, DatasetImport, NewDataset
from ..exceptions import DatasetAlredyExists, DatasetDoesNotExist
from ..repository.queries import DatasetsFilterByIdQuery
from ..usecases import (
    create_dataset,
    delete_dataset,
    get_dataset,
    get_datasets_list,
    import_dataset,
    share_dataset,
    update_dataset,
)
from .factories import (
    DatasetFactory,
    DatasetImportFactory,
    DatasetInputFactory,
    PersonFactory,
)


@pytest.fixture
def context():
    return Context(user=PersonFactory.build())


class TestGetDatasetsList:
    @pytest.mark.asyncio
    async def test_common(self, context: Context) -> None:
        entities = [
            DatasetFactory.build(),
            DatasetFactory.build(),
        ]

        query = Mock()
        query.apply = AsyncMock()

        repo = Mock()
        repo.list = AsyncMock(return_value=entities)

        result = await get_datasets_list(query, context, repo)

        assert result == entities
        repo.list.assert_called_once_with(query)


class TestGetDataset:
    @pytest.mark.asyncio
    async def test_common(self, context: Context) -> None:
        id = "1"
        entity = DatasetFactory.build(identifier=id)

        repo = Mock()
        repo.get = AsyncMock(return_value=entity)

        result = await get_dataset(id, context, repo)

        assert result == entity
        repo.get.assert_called_once_with(DatasetsFilterByIdQuery(id))

    @pytest.mark.asyncio
    async def test_not_found(self, context: Context) -> None:
        repo = Mock()
        repo.get = AsyncMock(side_effect=DatasetDoesNotExist)

        with pytest.raises(DatasetDoesNotExist):
            await get_dataset("1", context, repo)


class TestCreateDataset:
    @pytest.mark.asyncio
    async def test_common(self) -> None:
        catalog_title = "Test catalog"
        catalog_description = "Test catalog description"

        context = CreateDatasetContext(
            user=PersonFactory.build(),
            catalog_title=catalog_title,
            catalog_description=catalog_description,
        )

        input = DatasetInputFactory.build()
        output = DatasetFactory.build()
        updated = NewDataset(
            **input.model_dump(),
            is_local=True,
            is_shared=False,
            creator=context["user"],
            catalog=Catalog(
                identifier=context["user"].id,
                title=catalog_title,
                description=catalog_description,
            ),
        )

        repo = Mock()
        repo.create = AsyncMock(return_value=output)

        result = await create_dataset(input, context, repo)

        assert result == output
        repo.create.assert_called_once_with(updated)


class TestUpdateDataset:
    @pytest.mark.asyncio
    async def test_common(self, context: Context) -> None:
        id = "1"
        input = DatasetInputFactory.build()
        exists = DatasetFactory.build()
        output = DatasetFactory.build()
        updated = exists.model_validate(
            {
                **exists.model_dump(),
                **input.model_dump(exclude_unset=True, exclude_defaults=True),
            }
        )

        repo = Mock()
        repo.get = AsyncMock(return_value=exists)
        repo.update = AsyncMock(return_value=output)

        result = await update_dataset(id, input, context, repo)

        assert result == output
        repo.get.assert_called_once_with(DatasetsFilterByIdQuery(id))
        repo.update.assert_called_once_with(updated)

    @pytest.mark.asyncio
    async def test_not_found(self, context: Context) -> None:
        input = DatasetInputFactory.build()

        repo = Mock()
        repo.get = AsyncMock(side_effect=DatasetDoesNotExist)

        with pytest.raises(DatasetDoesNotExist):
            await update_dataset("1", input, context, repo)


class TestDeleteDataset:
    @pytest.mark.asyncio
    async def test_common(self, context: Context) -> None:
        id = "1"
        exists = DatasetFactory.build()

        repo = Mock()
        repo.get = AsyncMock(return_value=exists)
        repo.delete = AsyncMock()

        await delete_dataset(id, context, repo)

        repo.get.assert_called_once_with(DatasetsFilterByIdQuery(id))
        repo.delete.assert_called_once_with(exists)

    @pytest.mark.asyncio
    async def test_not_found(self, context: Context) -> None:
        repo = Mock()
        repo.get = AsyncMock(side_effect=DatasetDoesNotExist)

        with pytest.raises(DatasetDoesNotExist):
            await delete_dataset("1", context, repo)


class TestShareDataset:
    @pytest.mark.asyncio
    async def test_common(self, context: Context) -> None:
        id = "1"
        marketplace_url = AnyUrl("http://example.com/1/")

        exists = DatasetFactory.build(is_shared=False)
        updated = DatasetFactory.build()
        imported = DatasetFactory.build()

        repo = Mock()
        repo.get = AsyncMock(return_value=exists)
        repo.update = AsyncMock(return_value=updated)

        gateway = Mock()
        gateway.share_dataset = AsyncMock(return_value=imported)

        result = await share_dataset(id, marketplace_url, context, repo, gateway)

        assert result == imported
        gateway.share_dataset.assert_called_once_with(
            DatasetImport(**exists.model_dump()),
            marketplace_url,
        )
        repo.update.assert_called_once_with(
            Dataset(
                **exists.model_dump(exclude=set(["is_shared"])),
                is_shared=True,
            )
        )


class TestImportDataset:
    @pytest.mark.asyncio
    async def test_common(self, context: Context) -> None:
        data = DatasetImportFactory.build()
        created = DatasetFactory.build()

        repo = Mock()
        repo.exists = AsyncMock(return_value=False)
        repo.create = AsyncMock(return_value=created)

        result = await import_dataset(data, context, repo)

        assert result == created
        repo.exists.assert_called_once_with(DatasetsFilterByIdQuery(data.identifier))
        repo.create.assert_called_once_with(
            Dataset(
                **data.model_dump(exclude=set(["catalog"])),
                is_local=False,
                is_shared=False,
                issued=date.today(),
                creator=context["user"],
                catalog=Catalog(
                    **data.catalog.model_dump(),
                    identifier=context["user"].id,
                ),
            )
        )

    @pytest.mark.asyncio
    async def test_if_exists(self, context: Context) -> None:
        data = DatasetImportFactory.build()

        repo = Mock()
        repo.exists = AsyncMock(return_value=True)

        with pytest.raises(DatasetAlredyExists):
            await import_dataset(data, context, repo)
