import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.append("/home/raghu/mcp-server-weather-py")

from src.client import weather_client
from src.exceptions import WeatherAPIError
from src.tools import get_alerts, get_forecast, get_location_forecast, health_check


class TestMCPTools:
    """Test MCP tool functions"""

    @pytest.mark.asyncio
    async def test_get_alerts_success(self):
        mock_data = {
            "features": [
                {
                    "properties": {
                        "event": "Test Alert",
                        "areaDesc": "Test Area",
                        "severity": "Severe",
                        "description": "Test description",
                        "instruction": "Test instructions",
                    }
                }
            ]
        }

        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_data

            result = await get_alerts("CA")
            assert "Test Alert" in result
            assert "Test Area" in result

    @pytest.mark.asyncio
    async def test_get_forecast_success(self):
        points_data = {
            "properties": {
                "forecast": "http://test.com/forecast",
                "relativeLocation": {
                    "properties": {"city": "San Francisco", "state": "CA"}
                },
            }
        }

        forecast_data = {
            "properties": {
                "periods": [
                    {
                        "name": "Tonight",
                        "temperature": 65,
                        "temperatureUnit": "F",
                        "windSpeed": "10 mph",
                        "windDirection": "SW",
                        "detailedForecast": "Clear skies",
                        "isDaytime": False,
                    }
                ]
            }
        }

        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [points_data, forecast_data]

            result = await get_forecast(37.7749, -122.4194)
            assert "San Francisco" in result
            assert "Tonight" in result
            assert "65°F" in result

    @pytest.mark.asyncio
    async def test_get_location_forecast_empty_inputs(self):
        """Test get_location_forecast with empty inputs"""
        result = await get_location_forecast("", "CA")
        assert "Error: Both city and state must be provided" in result

        result = await get_location_forecast("Seattle", "")
        assert "Error: Both city and state must be provided" in result

    @pytest.mark.asyncio
    async def test_get_location_forecast_unexpected_error(self):
        """Test get_location_forecast with unexpected error"""
        # Create a mock that raises an exception during string operations
        with patch("src.tools.logger.error") as mock_logger:
            # Create a city object that raises an exception when .strip() is called
            class BadCity:
                def strip(self):
                    raise RuntimeError("Unexpected error during string processing")

                def __bool__(self):
                    return True  # Pass validation

            result = await get_location_forecast(BadCity(), "CA")
            assert "An unexpected error occurred." in result
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(weather_client, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None

            result = await health_check()
            assert "✅ Healthy" in result

    @pytest.mark.asyncio
    async def test_get_alerts_no_data(self):
        """Test get_alerts when no data is returned"""
        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {}

            result = await get_alerts("CA")
            assert "No alert data available" in result

    @pytest.mark.asyncio
    async def test_get_alerts_no_features(self):
        """Test get_alerts when no features are returned"""
        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"features": []}

            result = await get_alerts("CA")
            assert "No active alerts for CA" in result

    @pytest.mark.asyncio
    async def test_get_alerts_with_filter_no_matches(self):
        """Test get_alerts with severity filter that matches nothing"""
        mock_data = {
            "features": [
                {
                    "properties": {
                        "event": "Minor Alert",
                        "areaDesc": "Test Area",
                        "severity": "Minor",
                        "description": "Minor issue",
                        "instruction": "Be aware",
                    }
                }
            ]
        }

        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = mock_data

            result = await get_alerts("CA", "Extreme")
            assert "No active alerts found for CA with severity 'Extreme'" in result

    @pytest.mark.asyncio
    async def test_get_alerts_api_error(self):
        """Test get_alerts with API error"""
        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = WeatherAPIError("API Error")

            result = await get_alerts("CA")
            assert "Error: API Error" in result

    @pytest.mark.asyncio
    async def test_get_alerts_unexpected_error(self):
        """Test get_alerts with unexpected error"""
        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = Exception("Unexpected error")

            result = await get_alerts("CA")
            assert "An unexpected error occurred" in result

    @pytest.mark.asyncio
    async def test_get_forecast_no_points_data(self):
        """Test get_forecast when points data is unavailable"""
        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {}

            result = await get_forecast(37.7749, -122.4194)
            assert "Unable to get forecast data" in result

    @pytest.mark.asyncio
    async def test_get_forecast_no_forecast_url(self):
        """Test get_forecast when forecast URL is missing"""
        points_data = {"properties": {}}

        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = points_data

            result = await get_forecast(37.7749, -122.4194)
            assert "Forecast not available" in result

    @pytest.mark.asyncio
    async def test_get_forecast_no_forecast_data(self):
        """Test get_forecast when forecast data is unavailable"""
        points_data = {
            "properties": {
                "forecast": "http://test.com/forecast",
                "relativeLocation": {"properties": {"city": "Test", "state": "CA"}},
            }
        }

        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [points_data, {}]

            result = await get_forecast(37.7749, -122.4194)
            assert "Unable to get detailed forecast" in result

    @pytest.mark.asyncio
    async def test_get_forecast_no_periods(self):
        """Test get_forecast when no periods are available"""
        points_data = {
            "properties": {
                "forecast": "http://test.com/forecast",
                "relativeLocation": {"properties": {"city": "Test", "state": "CA"}},
            }
        }

        forecast_data = {"properties": {"periods": []}}

        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [points_data, forecast_data]

            result = await get_forecast(37.7749, -122.4194)
            assert "No forecast periods available" in result

    @pytest.mark.asyncio
    async def test_get_forecast_api_error(self):
        """Test get_forecast with API error"""
        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = WeatherAPIError("API Error")

            result = await get_forecast(37.7749, -122.4194)
            assert "Error: API Error" in result

    @pytest.mark.asyncio
    async def test_get_forecast_unexpected_error(self):
        """Test get_forecast with unexpected error"""
        with patch.object(
            weather_client, "make_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = Exception("Unexpected error")

            result = await get_forecast(37.7749, -122.4194)
            assert (
                "An unexpected error occurred while fetching the weather forecast"
                in result
            )

    @pytest.mark.asyncio
    async def test_health_check_warning_status(self):
        """Test health_check with warning status"""
        mock_response = Mock()
        mock_response.status_code = 503

        with patch.object(weather_client, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__aenter__.return_value = mock_client
            mock_get_client.return_value.__aexit__.return_value = None

            result = await health_check()
            assert "⚠️  Warning (HTTP 503)" in result

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health_check when check fails"""
        with patch.object(weather_client, "get_client") as mock_get_client:
            mock_get_client.side_effect = Exception("Connection failed")

            result = await health_check()
            assert "❌ Unhealthy: Connection failed" in result
