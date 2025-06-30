import sys
import time
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

sys.path.append("/home/raghu/mcp-server-weather-py/src")

from modular.client import WeatherClient, _request_times, weather_client
from modular.config import Config
from modular.exceptions import (
    APIUnavailableError,
    RateLimitError,
    ValidationError,
    WeatherAPIError,
)
from modular.formatters import format_alerts, format_forecast_periods
from modular.models import AlertSeverity, ForecastPeriod, WeatherAlert
from modular.tools import get_alerts, get_forecast, get_location_forecast, health_check
from modular.validators import validate_coordinates, validate_state_code


class TestValidation:
    """Test input validation functions"""

    def test_validate_state_code_valid(self):
        assert validate_state_code("ca") == "CA"
        assert validate_state_code("NY") == "NY"
        assert validate_state_code(" TX ") == "TX"

    def test_validate_state_code_invalid(self):
        with pytest.raises(ValidationError, match="State code cannot be empty"):
            validate_state_code("")

        with pytest.raises(ValidationError, match="must be exactly 2 characters"):
            validate_state_code("CAL")

        with pytest.raises(ValidationError, match="Invalid state code"):
            validate_state_code("XX")

    def test_validate_coordinates_valid(self):
        lat, lon = validate_coordinates(37.7749, -122.4194)
        assert lat == 37.7749
        assert lon == -122.4194

        lat, lon = validate_coordinates(0, 0)
        assert lat == 0.0
        assert lon == 0.0

    def test_validate_coordinates_invalid(self):
        with pytest.raises(ValidationError, match="Latitude must be a number"):
            validate_coordinates("invalid", 0)

        with pytest.raises(ValidationError, match="Longitude must be a number"):
            validate_coordinates(0, "invalid")

        with pytest.raises(ValidationError, match="must be between -90 and 90"):
            validate_coordinates(91, 0)

        with pytest.raises(ValidationError, match="must be between -180 and 180"):
            validate_coordinates(0, 181)


class TestDataModels:
    """Test data model classes"""

    def test_weather_alert_creation(self):
        alert = WeatherAlert(
            event="Tornado Warning",
            area="San Francisco County",
            severity=AlertSeverity.EXTREME,
            description="A tornado has been spotted",
            instructions="Take shelter immediately",
        )

        assert "🚨 Tornado Warning" in str(alert)
        assert "Extreme" in str(alert)
        assert "San Francisco County" in str(alert)

    def test_forecast_period_creation(self):
        period = ForecastPeriod(
            name="Tonight",
            temperature=65,
            temperature_unit="F",
            wind_speed="10 mph",
            wind_direction="SW",
            detailed_forecast="Clear skies",
            is_daytime=False,
        )

        assert "🌙 Tonight" in str(period)
        assert "65°F" in str(period)
        assert "Clear skies" in str(period)


class TestFormatting:
    """Test data formatting functions"""

    def test_format_alerts(self):
        features = [
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

        alerts = format_alerts(features)
        assert len(alerts) == 1
        assert alerts[0].event == "Test Alert"
        assert alerts[0].severity == AlertSeverity.SEVERE

    def test_format_alerts_with_filter(self):
        features = [
            {
                "properties": {
                    "event": "Severe Alert",
                    "areaDesc": "Area 1",
                    "severity": "Severe",
                    "description": "Severe weather",
                    "instruction": "Take action",
                }
            },
            {
                "properties": {
                    "event": "Minor Alert",
                    "areaDesc": "Area 2",
                    "severity": "Minor",
                    "description": "Minor weather",
                    "instruction": "Be aware",
                }
            },
        ]

        severe_alerts = format_alerts(features, "Severe")
        assert len(severe_alerts) == 1
        assert severe_alerts[0].event == "Severe Alert"

    def test_format_alerts_with_invalid_filter(self):
        features = [
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

        # Invalid filter should include all alerts
        alerts = format_alerts(features, "InvalidSeverity")
        assert len(alerts) == 1
        assert alerts[0].event == "Test Alert"

    def test_format_forecast_periods(self):
        periods = [
            {
                "name": "Today",
                "temperature": 72,
                "temperatureUnit": "F",
                "windSpeed": "5 mph",
                "windDirection": "N",
                "detailedForecast": "Sunny skies",
                "isDaytime": True,
            }
        ]

        formatted = format_forecast_periods(periods)
        assert len(formatted) == 1
        assert formatted[0].name == "Today"
        assert formatted[0].temperature == 72


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
        _request_times.clear()
        current_time = time.time()
        for _ in range(61):  # Exceed limit of 60
            _request_times.append(current_time)

        with pytest.raises(RateLimitError):
            await client.make_request("http://test.com")

        _request_times.clear()  # Clean up
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
        with patch("modular.tools.logger.error") as mock_logger:
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

    def test_config_class_defaults(self):
        """Test that Config class has proper defaults"""
        test_config = Config()
        assert test_config.timeout == 30.0
        assert test_config.max_retries == 3
        assert test_config.cache_ttl == 300

    def test_cache_entry_expiration(self):
        """Test CacheEntry expiration logic"""
        from modular.models import CacheEntry

        # Non-expired entry
        entry = CacheEntry({"test": "data"}, time.time(), 300)
        assert not entry.is_expired

        # Expired entry
        old_entry = CacheEntry({"test": "data"}, time.time() - 400, 300)
        assert old_entry.is_expired

    def test_alert_severity_parsing(self):
        """Test alert severity parsing"""
        from modular.formatters import parse_alert_severity
        from modular.models import AlertSeverity as ModularAlertSeverity

        assert parse_alert_severity("Extreme") == ModularAlertSeverity.EXTREME
        assert parse_alert_severity("Invalid") == ModularAlertSeverity.UNKNOWN
