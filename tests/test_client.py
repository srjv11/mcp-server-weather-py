import sys
import time
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

sys.path.append("/home/raghu/mcp-server-weather-py")

from src.client import WeatherClient, request_times
from src.exceptions import APIUnavailableError, RateLimitError, WeatherAPIError


class TestWeatherClient:
    """Test WeatherClient functionality"""

    @pytest.mark.asyncio
    async def test_client_creation(self):
        client = WeatherClient()
        async with client.get_client() as http_client:
            assert isinstance(http_client, httpx.AsyncClient)
        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_success(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()

        client = WeatherClient()

        with patch.object(client, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None

            result = await client.make_request("http://test.com")
            assert result == {"test": "data"}

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_with_cache(self):
        # Clear cache first to ensure test isolation
        from src.client import cache

        cache.clear()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cached": "data"}
        mock_response.raise_for_status = Mock()

        client = WeatherClient()

        with patch.object(client, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None

            # First request should hit API
            result1 = await client.make_request("http://test.com", "test_key")
            assert result1 == {"cached": "data"}

            # Second request should hit cache
            result2 = await client.make_request("http://test.com", "test_key")
            assert result2 == {"cached": "data"}

            # Should only call get once (first time)
            assert mock_client.get.call_count == 1

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self):
        client = WeatherClient()

        # Fill up rate limit
        request_times.clear()
        current_time = time.time()
        for _ in range(61):  # Exceed limit of 60
            request_times.append(current_time)

        with pytest.raises(RateLimitError):
            await client.make_request("http://test.com")

        request_times.clear()  # Clean up
        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_api_rate_limit(self):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status = Mock()

        client = WeatherClient()

        with patch.object(client, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None

            with pytest.raises(RateLimitError):
                await client.make_request("http://test.com")

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_server_error(self):
        client = WeatherClient()

        with patch.object(client, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None

            # Server errors get caught and retried, then raise the last exception
            with pytest.raises(WeatherAPIError, match="Unexpected error"):
                await client.make_request("http://test.com")

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_timeout(self):
        client = WeatherClient()

        with patch.object(client, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.TimeoutException("Timeout")
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None

            with pytest.raises(APIUnavailableError):
                await client.make_request("http://test.com")

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_404_error(self):
        client = WeatherClient()

        with patch.object(client, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 404
            mock_client.get.return_value = mock_response
            mock_client.get.side_effect = httpx.HTTPStatusError(
                "Not found", request=Mock(), response=mock_response
            )
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None

            with pytest.raises(WeatherAPIError, match="Location not found"):
                await client.make_request("http://test.com")

        await client.close()
