"""
Test environment variable coverage by importing with env vars set
"""

import os
import sys
from unittest.mock import patch


def test_environment_variable_coverage():
    """Test environment variable loading by importing with env vars set"""
    # Remove the module if already imported
    if "weather_improved" in sys.modules:
        del sys.modules["weather_improved"]

    # Set environment variables before import
    with patch.dict(
        os.environ,
        {
            "WEATHER_TIMEOUT": "45",
            "WEATHER_MAX_RETRIES": "5",
            "WEATHER_CACHE_TTL": "600",
        },
    ):
        # Import the module to trigger environment variable loading
        import weather_improved

        # Check that the environment variables were loaded
        assert weather_improved.config.timeout == 45.0
        assert weather_improved.config.max_retries == 5
        assert weather_improved.config.cache_ttl == 600


if __name__ == "__main__":
    test_environment_variable_coverage()
    print("Environment variable coverage test passed!")
