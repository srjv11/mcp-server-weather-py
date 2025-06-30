import sys
import time

sys.path.append("/home/raghu/mcp-server-weather-py")

from src.config import Config
from src.models import AlertSeverity, CacheEntry, ForecastPeriod, WeatherAlert


class TestDataModels:
    """Test data model classes"""

    def test_weather_alert_creation(self):
        alert = WeatherAlert(
            event="Tornado Warning",
            area="San Francisco County",
            severity=AlertSeverity.EXTREME,
            description="A tornado has been spotted",
            instructions="Take shelter immediately",
        )

        assert "🚨 Tornado Warning" in str(alert)
        assert "Extreme" in str(alert)
        assert "San Francisco County" in str(alert)

    def test_forecast_period_creation(self):
        period = ForecastPeriod(
            name="Tonight",
            temperature=65,
            temperature_unit="F",
            wind_speed="10 mph",
            wind_direction="SW",
            detailed_forecast="Clear skies",
            is_daytime=False,
        )

        assert "🌙 Tonight" in str(period)
        assert "65°F" in str(period)
        assert "Clear skies" in str(period)

    def test_config_class_defaults(self):
        """Test that Config class has proper defaults"""
        test_config = Config()
        assert test_config.timeout == 30.0
        assert test_config.max_retries == 3
        assert test_config.cache_ttl == 300

    def test_cache_entry_expiration(self):
        """Test CacheEntry expiration logic"""
        # Non-expired entry
        entry = CacheEntry({"test": "data"}, time.time(), 300)
        assert not entry.is_expired

        # Expired entry
        old_entry = CacheEntry({"test": "data"}, time.time() - 400, 300)
        assert old_entry.is_expired

    def test_alert_severity_parsing(self):
        """Test alert severity parsing"""
        from src.formatters import parse_alert_severity

        assert parse_alert_severity("Extreme").value == AlertSeverity.EXTREME.value
        assert parse_alert_severity("Invalid").value == AlertSeverity.UNKNOWN.value
