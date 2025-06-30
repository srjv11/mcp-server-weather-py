"""Data models and enums for the weather MCP server."""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class AlertSeverity(Enum):
    """Severity levels for weather alerts."""

    EXTREME = "Extreme"
    SEVERE = "Severe"
    MODERATE = "Moderate"
    MINOR = "Minor"
    UNKNOWN = "Unknown"


@dataclass
class WeatherAlert:
    """Data model for weather alerts."""

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
    """Data model for forecast periods."""

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
    """Data model for cache entries."""

    data: Any
    timestamp: float
    ttl: int

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() - self.timestamp > self.ttl
