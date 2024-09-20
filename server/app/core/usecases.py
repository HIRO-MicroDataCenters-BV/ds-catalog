from pydantic import AnyUrl

from .context import Context
from .entities import Dataset, DatasetImport, DatasetInput, NewDataset
from .repository import ICatalogItemRepository, catalog_item_repo
from .repository.queries import DatasetsFilterByIdQuery, IQuery

REPO = catalog_item_repo


async def get_datasets_list(
    query: IQuery, context: Context, repo: ICatalogItemRepository = REPO
) -> list[Dataset]:
    return await repo.list(query)


async def get_dataset(
    id: str, context: Context, repo: ICatalogItemRepository = REPO
) -> Dataset:
    return await repo.get(DatasetsFilterByIdQuery(id))


async def create_dataset(
    data: DatasetInput, context: Context, repo: ICatalogItemRepository = REPO
) -> Dataset:
    dataset = NewDataset(
        **data.model_dump(),
        is_local=True,
        is_shared=False,
        creator=context["user"],
    )
    return await repo.create(dataset)


async def update_dataset(
    id: str, data: DatasetInput, context: Context, repo: ICatalogItemRepository = REPO
) -> Dataset:
    dataset = await repo.get(DatasetsFilterByIdQuery(id))
    dataset = dataset.model_validate(
        {
            **dataset.model_dump(),
            **data.model_dump(exclude_unset=True, exclude_defaults=True),
        }
    )
    return await repo.update(dataset)


async def delete_dataset(
    id: str, context: Context, repo: ICatalogItemRepository = REPO
) -> None:
    dataset = await repo.get(DatasetsFilterByIdQuery(id))
    await repo.delete(dataset)


async def share_dataset(
    id: str,
    marketplace_url: AnyUrl,
    context: Context,
    repo: ICatalogItemRepository = REPO,
) -> Dataset:
    # TODO: Implement
    from .tests.factories import DatasetFactory

    return DatasetFactory.build()


async def import_dataset(
    data: DatasetImport, context: Context, repo: ICatalogItemRepository = REPO
) -> Dataset:
    # TODO: Implement
    from .tests.factories import DatasetFactory

    return DatasetFactory.build()
