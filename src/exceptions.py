"""Custom exception classes for the weather MCP server."""


class WeatherAPIError(Exception):
    """Base exception for weather API errors."""

    pass


class ValidationError(WeatherAPIError):
    """Raised when input validation fails."""

    pass


class RateLimitError(WeatherAPIError):
    """Raised when rate limit is exceeded."""

    pass


class APIUnavailableError(WeatherAPIError):
    """Raised when the weather API is unavailable."""

    pass
