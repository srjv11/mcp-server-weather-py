"""Enhanced Weather MCP Server Package."""

# Re-export main components for backward compatibility
from .client import _cache, _request_times, weather_client
from .config import config
from .exceptions import (
    APIUnavailableError,
    RateLimitError,
    ValidationError,
    WeatherAPIError,
)
from .formatters import format_alerts, format_forecast_periods
from .models import AlertSeverity, CacheEntry, ForecastPeriod, WeatherAlert
from .tools import get_alerts, get_forecast, get_location_forecast, health_check
from .validators import validate_coordinates, validate_state_code

__version__ = "2.0.0"

__all__ = [
    # Models
    "AlertSeverity",
    "WeatherAlert",
    "ForecastPeriod",
    "CacheEntry",
    # Exceptions
    "WeatherAPIError",
    "ValidationError",
    "RateLimitError",
    "APIUnavailableError",
    # Tools
    "get_alerts",
    "get_forecast",
    "get_location_forecast",
    "health_check",
    # Validators
    "validate_state_code",
    "validate_coordinates",
    # Formatters
    "format_alerts",
    "format_forecast_periods",
    # Client and config
    "weather_client",
    "_cache",
    "_request_times",
    "config",
]
