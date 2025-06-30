"""Configuration management for the weather MCP server."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration settings for the weather MCP server."""

    nws_api_base: str = "https://api.weather.gov"
    user_agent: str = "enhanced-weather-mcp/2.0"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    cache_ttl: int = 300  # 5 minutes
    max_forecast_periods: int = 5
    rate_limit_per_minute: int = 60


# Global configuration instance
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
