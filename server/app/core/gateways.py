from typing import Any

from abc import ABC, abstractmethod

import aiohttp
from pydantic import AnyUrl
from pydantic.alias_generators import to_snake

from .entities import Dataset, DatasetImport
from .exceptions import DatasetSharingError


def convert_keys_to_snake(
    data: dict[str, Any] | list[Any] | Any
) -> dict[str, Any] | list[Any] | Any:
    if isinstance(data, dict):
        return {
            to_snake(k): convert_keys_to_snake(v) if isinstance(v, (dict, list)) else v
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [
            convert_keys_to_snake(item) if isinstance(item, (dict, list)) else item
            for item in data
        ]
    else:
        return data


class IMarketplaceGateway(ABC):
    @abstractmethod
    async def share_dataset(
        self,
        dataset_entity: DatasetImport,
        marketplace_url: AnyUrl,
    ) -> Dataset:
        ...


class MarketplaceGateway(IMarketplaceGateway):
    async def share_dataset(
        self,
        dataset_entity: DatasetImport,
        marketplace_url: AnyUrl,
    ) -> Dataset:
        url = str(marketplace_url)
        data = dataset_entity.model_dump()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    response.raise_for_status()
                    response_json = await response.json()
            except aiohttp.ClientError as err:
                raise DatasetSharingError(err)

        return Dataset.model_validate(convert_keys_to_snake(response_json))


marketplace_gateway = MarketplaceGateway()
