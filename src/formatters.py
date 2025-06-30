"""Data formatting functions for the weather MCP server."""

from typing import Any

from .config import config
from .models import AlertSeverity, ForecastPeriod, WeatherAlert


def parse_alert_severity(severity_str: str) -> AlertSeverity:
    """Parse alert severity from API response.

    Args:
        severity_str: Severity string from API

    Returns:
        AlertSeverity enum value
    """
    try:
        return AlertSeverity(severity_str)
    except ValueError:
        return AlertSeverity.UNKNOWN


def format_alerts(
    features: list[dict[str, Any]], severity_filter: str | None = None
) -> list[WeatherAlert]:
    """Format alert features into WeatherAlert objects.

    Args:
        features: List of alert features from API
        severity_filter: Optional severity filter

    Returns:
        List of formatted WeatherAlert objects
    """
    alerts: list[WeatherAlert] = []

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
    """Format forecast periods into ForecastPeriod objects.

    Args:
        periods: List of forecast periods from API

    Returns:
        List of formatted ForecastPeriod objects
    """
    forecast_periods: list[ForecastPeriod] = []

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
