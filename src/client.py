"""HTTP client and caching functionality for the weather MCP server."""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any

import httpx

from .config import config
from .exceptions import APIUnavailableError, RateLimitError, WeatherAPIError
from .models import CacheEntry

# Configure logging
logger = logging.getLogger(__name__)

# Simple in-memory cache and rate limiting
cache: dict[str, CacheEntry] = {}
request_times: list[float] = []


def _clean_expired_cache():
    """Remove expired cache entries."""
    expired_keys = [k for k, v in cache.items() if v.is_expired]
    for key in expired_keys:
        del cache[key]


def _check_rate_limit():
    """Check if we're within rate limits."""
    now = time.time()
    # Remove requests older than 1 minute
    request_times[:] = [t for t in request_times if now - t < 60]

    if len(request_times) >= config.rate_limit_per_minute:
        raise RateLimitError("Rate limit exceeded. Please try again later.")

    request_times.append(now)


class WeatherClient:
    """HTTP client for weather API requests with caching and retry logic."""

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    @asynccontextmanager
    async def get_client(self):
        """Get or create HTTP client with proper configuration."""
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
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def make_request(
        self, url: str, cache_key: str | None = None
    ) -> dict[str, Any]:
        """Make a request to the NWS API with retries, caching, and error handling.

        Args:
            url: The URL to request
            cache_key: Optional cache key for caching the response

        Returns:
            JSON response data

        Raises:
            RateLimitError: If rate limit is exceeded
            APIUnavailableError: If API is unavailable
            WeatherAPIError: For other API errors
        """
        _check_rate_limit()

        # Check cache first
        if cache_key:
            _clean_expired_cache()
            cached = cache.get(cache_key)
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
                        cache[cache_key] = CacheEntry(
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


async def cleanup():
    """Cleanup resources on shutdown."""
    await weather_client.close()
    logger.info("Weather client cleanup complete")
