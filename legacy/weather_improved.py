import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuration
@dataclass
class Config:
    nws_api_base: str = "https://api.weather.gov"
    user_agent: str = "enhanced-weather-mcp/2.0"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    cache_ttl: int = 300  # 5 minutes
    max_forecast_periods: int = 5
    rate_limit_per_minute: int = 60


config = Config()

# Load environment variables
if env_timeout := os.getenv("WEATHER_TIMEOUT"):
    config.timeout = float(env_timeout)
if env_retries := os.getenv("WEATHER_MAX_RETRIES"):
    config.max_retries = int(env_retries)
if env_cache_ttl := os.getenv("WEATHER_CACHE_TTL"):
    config.cache_ttl = int(env_cache_ttl)

# Valid US state codes
VALID_STATES: set[str] = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
    "PR",
    "VI",
    "GU",
    "AS",
    "MP",
}


class AlertSeverity(Enum):
    EXTREME = "Extreme"
    SEVERE = "Severe"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


@dataclass
class WeatherAlert:
    event: str
    area: str
    severity: AlertSeverity
    description: str
    instructions: str
    expires: str | None = None

    def __str__(self) -> str:
        return f"""🚨 {self.event}
📍 Area: {self.area}
⚠️  Severity: {self.severity.value}
📝 Description: {self.description}
💡 Instructions: {self.instructions}
{f"⏰ Expires: {self.expires}" if self.expires else ""}"""


@dataclass
class ForecastPeriod:
    name: str
    temperature: int
    temperature_unit: str
    wind_speed: str
    wind_direction: str
    detailed_forecast: str
    is_daytime: bool

    def __str__(self) -> str:
        icon = "☀️" if self.is_daytime else "🌙"
        return f"""{icon} {self.name}:
🌡️  Temperature: {self.temperature}°{self.temperature_unit}
💨 Wind: {self.wind_speed} {self.wind_direction}
📋 Forecast: {self.detailed_forecast}"""


@dataclass
class CacheEntry:
    data: Any
    timestamp: float
    ttl: int

    @property
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class WeatherAPIError(Exception):
    """Base exception for weather API errors"""

    pass


class ValidationError(WeatherAPIError):
    """Raised when input validation fails"""

    pass


class RateLimitError(WeatherAPIError):
    """Raised when rate limit is exceeded"""

    pass


class APIUnavailableError(WeatherAPIError):
    """Raised when the weather API is unavailable"""

    pass


# Simple in-memory cache
_cache: dict[str, CacheEntry] = {}
_request_times: list[float] = []


def _clean_expired_cache():
    """Remove expired cache entries"""
    expired_keys = [k for k, v in _cache.items() if v.is_expired]
    for key in expired_keys:
        del _cache[key]


def _check_rate_limit():
    """Check if we're within rate limits"""
    now = time.time()
    # Remove requests older than 1 minute
    _request_times[:] = [t for t in _request_times if now - t < 60]

    if len(_request_times) >= config.rate_limit_per_minute:
        raise RateLimitError("Rate limit exceeded. Please try again later.")

    _request_times.append(now)


def validate_state_code(state: str) -> str:
    """Validate and normalize state code"""
    if not state:
        raise ValidationError("State code cannot be empty")

    state = state.upper().strip()
    if len(state) != 2:
        raise ValidationError("State code must be exactly 2 characters")

    if state not in VALID_STATES:
        raise ValidationError(
            f"Invalid state code: {state}. Must be a valid US state/territory code."
        )

    return state


def validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    """Validate latitude and longitude"""
    if not isinstance(latitude, int | float):
        raise ValidationError("Latitude must be a number")
    if not isinstance(longitude, int | float):
        raise ValidationError("Longitude must be a number")

    if not -90 <= latitude <= 90:
        raise ValidationError("Latitude must be between -90 and 90 degrees")
    if not -180 <= longitude <= 180:
        raise ValidationError("Longitude must be between -180 and 180 degrees")

    return float(latitude), float(longitude)


class WeatherClient:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    @asynccontextmanager
    async def get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(config.timeout),
                headers={
                    "User-Agent": config.user_agent,
                    "Accept": "application/geo+json",
                },
            )
        try:
            yield self._client
        finally:
            pass  # Keep client alive for reuse

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def make_request(
        self, url: str, cache_key: str | None = None
    ) -> dict[str, Any]:
        """Make a request to the NWS API with retries, caching, and error handling"""
        _check_rate_limit()

        # Check cache first
        if cache_key:
            _clean_expired_cache()
            cached = _cache.get(cache_key)
            if cached and not cached.is_expired:
                logger.info(f"Cache hit for {cache_key}")
                return cached.data

        last_exception: WeatherAPIError | None = None

        for attempt in range(config.max_retries):
            try:
                async with self.get_client() as client:
                    logger.info(f"Making request to {url} (attempt {attempt + 1})")
                    response = await client.get(url)

                    if response.status_code == 429:
                        raise RateLimitError("API rate limit exceeded")
                    elif response.status_code >= 500:
                        raise APIUnavailableError(
                            f"API server error: {response.status_code}"
                        )

                    response.raise_for_status()
                    data = response.json()

                    # Cache successful response
                    if cache_key:
                        _cache[cache_key] = CacheEntry(
                            data, time.time(), config.cache_ttl
                        )

                    logger.info(f"Successfully retrieved data from {url}")
                    return data

            except RateLimitError:
                # Rate limit errors should be raised immediately
                raise
            except httpx.TimeoutException as e:
                last_exception = APIUnavailableError(
                    f"Request timeout after {config.timeout}s"
                )
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise WeatherAPIError(
                        "Location not found or no data available"
                    ) from e
                last_exception = APIUnavailableError(
                    f"HTTP error {e.response.status_code}"
                )
                logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
            except Exception as e:
                last_exception = WeatherAPIError(f"Unexpected error: {str(e)}")
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")

            if attempt < config.max_retries - 1:
                delay = config.retry_delay * (2**attempt)  # Exponential backoff
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)

        raise last_exception or WeatherAPIError("All retry attempts failed")


# Global client instance
weather_client = WeatherClient()

# Initialize FastMCP server
mcp: FastMCP = FastMCP("enhanced-weather")


def parse_alert_severity(severity_str: str) -> AlertSeverity:
    """Parse alert severity from API response"""
    try:
        return AlertSeverity(severity_str)
    except ValueError:
        return AlertSeverity.UNKNOWN


def format_alerts(
    features: list[dict[str, Any]], severity_filter: str | None = None
) -> list[WeatherAlert]:
    """Format alert features into WeatherAlert objects"""
    alerts = []

    for feature in features:
        props = feature.get("properties", {})
        severity = parse_alert_severity(props.get("severity", "Unknown"))

        # Apply severity filter if specified
        if severity_filter:
            try:
                filter_severity = AlertSeverity(severity_filter)
                if severity != filter_severity:
                    continue
            except ValueError:
                pass  # Invalid filter, include all alerts

        alert = WeatherAlert(
            event=props.get("event", "Unknown Event"),
            area=props.get("areaDesc", "Unknown Area"),
            severity=severity,
            description=props.get("description", "No description available"),
            instructions=props.get("instruction", "No specific instructions provided"),
            expires=props.get("expires"),
        )
        alerts.append(alert)

    return alerts


def format_forecast_periods(periods: list[dict[str, Any]]) -> list[ForecastPeriod]:
    """Format forecast periods into ForecastPeriod objects"""
    forecast_periods = []

    for period in periods[: config.max_forecast_periods]:
        forecast_period = ForecastPeriod(
            name=period.get("name", "Unknown"),
            temperature=period.get("temperature", 0),
            temperature_unit=period.get("temperatureUnit", "F"),
            wind_speed=period.get("windSpeed", "Unknown"),
            wind_direction=period.get("windDirection", "Unknown"),
            detailed_forecast=period.get("detailedForecast", "No forecast available"),
            is_daytime=period.get("isDaytime", True),
        )
        forecast_periods.append(forecast_period)

    return forecast_periods


@mcp.tool()
async def get_alerts(state: str, severity_filter: str | None = None) -> str:
    """Get weather alerts for a US state with optional severity filtering.

    Args:
        state: Two-letter US state code (e.g. CA, NY, TX)
        severity_filter: Optional severity filter (Extreme, Severe, Moderate, Minor)

    Returns:
        Formatted string with active weather alerts

    Raises:
        ValidationError: If state code is invalid
        WeatherAPIError: If API request fails
    """
    try:
        state = validate_state_code(state)

        url = f"{config.nws_api_base}/alerts/active/area/{state}"
        cache_key = f"alerts_{state}_{severity_filter or 'all'}"

        data = await weather_client.make_request(url, cache_key)

        if not data or "features" not in data:
            return "No alert data available for this state."

        if not data["features"]:
            return f"No active alerts for {state}."

        alerts = format_alerts(data["features"], severity_filter)

        if not alerts:
            filter_msg = (
                f" with severity '{severity_filter}'" if severity_filter else ""
            )
            return f"No active alerts found for {state}{filter_msg}."

        alert_strings = [str(alert) for alert in alerts]
        return f"\n{'=' * 50}\n".join(alert_strings)

    except (ValidationError, WeatherAPIError) as e:
        logger.error(f"Error getting alerts for {state}: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error getting alerts for {state}: {e}")
        return "An unexpected error occurred while fetching weather alerts."


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get detailed weather forecast for a location.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)

    Returns:
        Formatted string with weather forecast

    Raises:
        ValidationError: If coordinates are invalid
        WeatherAPIError: If API request fails
    """
    try:
        latitude, longitude = validate_coordinates(latitude, longitude)

        # Get forecast grid endpoint
        points_url = f"{config.nws_api_base}/points/{latitude},{longitude}"
        cache_key = f"points_{latitude}_{longitude}"

        points_data = await weather_client.make_request(points_url, cache_key)

        if not points_data or "properties" not in points_data:
            return "Unable to get forecast data for this location."

        forecast_url = points_data["properties"].get("forecast")
        if not forecast_url:
            return "Forecast not available for this location."

        # Get detailed forecast
        forecast_cache_key = f"forecast_{latitude}_{longitude}"
        forecast_data = await weather_client.make_request(
            forecast_url, forecast_cache_key
        )

        if not forecast_data or "properties" not in forecast_data:
            return "Unable to get detailed forecast."

        periods = forecast_data["properties"].get("periods", [])
        if not periods:
            return "No forecast periods available."

        forecast_periods = format_forecast_periods(periods)
        forecast_strings = [str(period) for period in forecast_periods]

        location_info = points_data["properties"]
        city = (
            location_info.get("relativeLocation", {})
            .get("properties", {})
            .get("city", "Unknown")
        )
        state = (
            location_info.get("relativeLocation", {})
            .get("properties", {})
            .get("state", "Unknown")
        )

        header = f"🌤️  Weather Forecast for {city}, {state} ({latitude}, {longitude})"
        return f"{header}\n{'=' * len(header)}\n\n" + f"\n{'─' * 40}\n".join(
            forecast_strings
        )

    except (ValidationError, WeatherAPIError) as e:
        logger.error(f"Error getting forecast for {latitude}, {longitude}: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(
            f"Unexpected error getting forecast for {latitude}, {longitude}: {e}"
        )
        return "An unexpected error occurred while fetching the weather forecast."


@mcp.tool()
async def get_location_forecast(city: str, state: str) -> str:
    """Get weather forecast by city and state name (geocoding).

    Args:
        city: City name
        state: State name or two-letter code

    Returns:
        Formatted string with weather forecast
    """
    try:
        if not city or not state:
            raise ValidationError("Both city and state must be provided")

        # Simple geocoding using NWS API
        search_query = f"{city.strip()}, {state.strip()}"
        # This is a simplified implementation - in a real app you'd use a proper geocoding service
        return f"Geocoding not fully implemented. Please use get_forecast with coordinates for {search_query}."

    except ValidationError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in location forecast: {e}")
        return "An unexpected error occurred."


@mcp.tool()
async def health_check() -> str:
    """Check the health status of the weather service.

    Returns:
        Health status information
    """
    try:
        # Test API connectivity
        test_url = f"{config.nws_api_base}/alerts/active/area/CA"
        start_time = time.time()

        async with weather_client.get_client() as client:
            response = await client.get(test_url)
            response_time = time.time() - start_time

        status = (
            "✅ Healthy"
            if response.status_code == 200
            else f"⚠️  Warning (HTTP {response.status_code})"
        )

        return f"""🏥 Weather Service Health Check
Status: {status}
Response Time: {response_time:.2f}s
Cache Entries: {len(_cache)}
Rate Limit Usage: {len(_request_times)}/{config.rate_limit_per_minute} per minute
API Base: {config.nws_api_base}"""

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return f"❌ Unhealthy: {str(e)}"


async def cleanup():
    """Cleanup resources on shutdown"""
    await weather_client.close()
    logger.info("Weather service shutdown complete")


if __name__ == "__main__":
    import atexit

    # Register cleanup function
    def cleanup_wrapper() -> None:
        asyncio.run(cleanup())

    atexit.register(cleanup_wrapper)

    logger.info("Starting Enhanced Weather MCP Server")
    logger.info(f"Configuration: {config}")

    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        asyncio.run(cleanup())
