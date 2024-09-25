from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiohttp import ClientConnectorError, ClientResponseError
from pydantic import AnyUrl

from app.core.entities import Dataset
from app.core.exceptions import DatasetSharingError

from ..gateways import MarketplaceGateway, convert_keys_to_snake
from .factories import DatasetImportFactory


class TestMarketplaceGateway:
    dataset_import = DatasetImportFactory.build()
    marketplace_url = AnyUrl("https://marketplace.example.com")

    @pytest.mark.asyncio
    async def test_common(self):
        with patch("aiohttp.ClientSession.post") as mock_post:
            response_json = {
                "identifier": "1",
                "title": "Test dataset",
                "description": "Test description",
                "keyword": ["keyword1"],
                "license": "http://domain.com/license/",
                "isLocal": False,
                "isShared": False,
                "issued": "2024-01-01",
                "theme": ["theme1"],
                "creator": {
                    "id": "14eb400e-3ba3-4aed-a7b5-de030af3e411",
                    "name": "John Smith",
                },
                "distribution": [
                    {
                        "byteSize": 1024,
                        "mediaType": "text",
                        "checksum": {
                            "algorithm": "md5",
                            "checksumValue": "202cb962ac59075b964b07152d234b70",
                        },
                        "accessService": [{"endpointUrl": "http://domain.com/1"}],
                    }
                ],
            }

            mock_response = Mock()
            mock_response.raise_for_status = Mock(return_value=None)
            mock_response.json = AsyncMock(return_value=response_json)
            mock_post.return_value.__aenter__.return_value = mock_response

            gateway = MarketplaceGateway()
            result = await gateway.share_dataset(
                self.dataset_import, self.marketplace_url
            )

            assert result == Dataset.model_validate(
                convert_keys_to_snake(response_json)
            )
            mock_post.assert_called_once_with(
                str(self.marketplace_url),
                json=self.dataset_import.model_dump(),
            )

    @pytest.mark.asyncio
    async def test_connection_error(self):
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.side_effect = ClientConnectorError(Mock(), Mock())

            gateway = MarketplaceGateway()
            with pytest.raises(DatasetSharingError):
                await gateway.share_dataset(self.dataset_import, self.marketplace_url)

    @pytest.mark.asyncio
    async def test_response_error(self):
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status = Mock(
                side_effect=ClientResponseError(Mock(), Mock(), status=400)
            )
            mock_post.return_value.__aenter__.return_value = mock_response

            gateway = MarketplaceGateway()
            with pytest.raises(DatasetSharingError):
                await gateway.share_dataset(self.dataset_import, self.marketplace_url)
