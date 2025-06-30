"""MCP tool implementations for the weather server."""

import logging
import time

from mcp.server.fastmcp import FastMCP

from .client import cache, request_times, weather_client
from .config import config
from .exceptions import ValidationError, WeatherAPIError
from .formatters import format_alerts, format_forecast_periods
from .validators import validate_coordinates, validate_state_code

# Configure logging
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp: FastMCP = FastMCP("enhanced-weather")


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
        return f"\\n{'=' * 50}\\n".join(alert_strings)

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
        return f"{header}\\n{'=' * len(header)}\\n\\n" + f"\\n{'─' * 40}\\n".join(
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
Cache Entries: {len(cache)}
Rate Limit Usage: {len(request_times)}/{config.rate_limit_per_minute} per minute
API Base: {config.nws_api_base}"""

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return f"❌ Unhealthy: {str(e)}"
