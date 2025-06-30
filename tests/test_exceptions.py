import sys

sys.path.append("/home/raghu/mcp-server-weather-py")

from src.exceptions import (
    APIUnavailableError,
    RateLimitError,
    ValidationError,
    WeatherAPIError,
)


class TestExceptions:
    """Test custom exception classes"""

    def test_validation_error(self):
        """Test ValidationError exception"""
        error = ValidationError("Test validation error")
        assert str(error) == "Test validation error"
        assert isinstance(error, WeatherAPIError)

    def test_weather_api_error(self):
        """Test WeatherAPIError exception"""
        error = WeatherAPIError("Test API error")
        assert str(error) == "Test API error"
        assert isinstance(error, Exception)

    def test_rate_limit_error(self):
        """Test RateLimitError exception"""
        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, WeatherAPIError)

    def test_api_unavailable_error(self):
        """Test APIUnavailableError exception"""
        error = APIUnavailableError("API unavailable")
        assert str(error) == "API unavailable"
        assert isinstance(error, WeatherAPIError)
