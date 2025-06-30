import os
import sys
from unittest.mock import patch

sys.path.append("/home/raghu/mcp-server-weather-py")


def test_environment_variable_coverage():
    """Test environment variable loading by importing with env vars set"""
    # Remove modules if already imported
    modules_to_remove = [
        "src.config",
        "src.client",
        "src.tools",
        "src.validators",
        "src.formatters",
        "src.models",
        "src.exceptions",
    ]
    for module in modules_to_remove:
        if module in sys.modules:
            del sys.modules[module]

    # Set environment variables before import
    with patch.dict(
        os.environ,
        {
            "WEATHER_TIMEOUT": "45",
            "WEATHER_MAX_RETRIES": "5",
            "WEATHER_CACHE_TTL": "600",
        },
    ):
        # Import the config module to trigger environment variable loading
        from src.config import config

        # Check that the environment variables were loaded
        assert config.timeout == 45.0
        assert config.max_retries == 5
        assert config.cache_ttl == 600


if __name__ == "__main__":
    test_environment_variable_coverage()
    print("Environment variable coverage test passed!")
