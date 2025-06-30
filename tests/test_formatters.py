import sys

sys.path.append("/home/raghu/mcp-server-weather-py")

from src.formatters import format_alerts, format_forecast_periods
from src.models import AlertSeverity


class TestFormatting:
    """Test data formatting functions"""

    def test_format_alerts(self):
        features = [
            {
                "properties": {
                    "event": "Test Alert",
                    "areaDesc": "Test Area",
                    "severity": "Severe",
                    "description": "Test description",
                    "instruction": "Test instructions",
                }
            }
        ]

        alerts = format_alerts(features)
        assert len(alerts) == 1
        assert alerts[0].event == "Test Alert"
        assert alerts[0].severity == AlertSeverity.SEVERE

    def test_format_alerts_with_filter(self):
        features = [
            {
                "properties": {
                    "event": "Severe Alert",
                    "areaDesc": "Area 1",
                    "severity": "Severe",
                    "description": "Severe weather",
                    "instruction": "Take action",
                }
            },
            {
                "properties": {
                    "event": "Minor Alert",
                    "areaDesc": "Area 2",
                    "severity": "Minor",
                    "description": "Minor weather",
                    "instruction": "Be aware",
                }
            },
        ]

        severe_alerts = format_alerts(features, "Severe")
        assert len(severe_alerts) == 1
        assert severe_alerts[0].event == "Severe Alert"

    def test_format_alerts_with_invalid_filter(self):
        features = [
            {
                "properties": {
                    "event": "Test Alert",
                    "areaDesc": "Test Area",
                    "severity": "Severe",
                    "description": "Test description",
                    "instruction": "Test instructions",
                }
            }
        ]

        # Invalid filter should include all alerts
        alerts = format_alerts(features, "InvalidSeverity")
        assert len(alerts) == 1
        assert alerts[0].event == "Test Alert"

    def test_format_forecast_periods(self):
        periods = [
            {
                "name": "Today",
                "temperature": 72,
                "temperatureUnit": "F",
                "windSpeed": "5 mph",
                "windDirection": "N",
                "detailedForecast": "Sunny skies",
                "isDaytime": True,
            }
        ]

        formatted = format_forecast_periods(periods)
        assert len(formatted) == 1
        assert formatted[0].name == "Today"
        assert formatted[0].temperature == 72
