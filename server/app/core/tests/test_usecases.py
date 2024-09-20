from unittest.mock import AsyncMock, Mock

import pytest

from ..context import Context
from ..entities import NewDataset
from ..exceptions import DatasetDoesNotExist
from ..repository.queries import DatasetsFilterByIdQuery
from ..usecases import (
    create_dataset,
    delete_dataset,
    get_dataset,
    get_datasets_list,
    update_dataset,
)
from .factories import DatasetFactory, DatasetInputFactory, PersonFactory


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
    async def test_common(self, context: Context) -> None:
        input = DatasetInputFactory.build()
        output = DatasetFactory.build()

        updated = NewDataset(
            **input.model_dump(),
            is_local=True,
            is_shared=False,
            creator=context["user"],
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
    # TODO: implement
    ...


class TestImportDataset:
    # TODO: implement
    ...
