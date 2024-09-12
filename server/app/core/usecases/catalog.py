from pydantic import AnyUrl

from ..entities.catalog import Dataset, DatasetImport, DatasetInput
from ..entities.tests.factories import DatasetFactory, PersonFactory
from ..queries.catalog import DatasetsQuery

DUMMY_PERSON = PersonFactory.build()
DUMMY_DATASETS = [
    DatasetFactory.build(),
    DatasetFactory.build(),
]


async def get_datasets_list(query: DatasetsQuery | None = None) -> list[Dataset]:
    # TODO: Implement
    return DUMMY_DATASETS


async def get_dataset(id: str) -> Dataset:
    # TODO: Implement
    return DUMMY_DATASETS[0]


async def create_dataset(data: DatasetInput) -> Dataset:
    # TODO: Implement
    return DUMMY_DATASETS[0]


async def update_dataset(id: str, data: DatasetInput) -> Dataset:
    # TODO: Implement
    return DUMMY_DATASETS[0]


async def delete_dataset(id: str) -> None:
    # TODO: Implement
    ...


async def share_dataset(id: str, marketplace_url: AnyUrl) -> Dataset:
    # TODO: Implement
    return DUMMY_DATASETS[0]


async def import_dataset(data: DatasetImport) -> Dataset:
    # TODO: Implement
    return DUMMY_DATASETS[0]
