import sys

import pytest

sys.path.append("/home/raghu/mcp-server-weather-py")

from src.exceptions import ValidationError
from src.validators import validate_coordinates, validate_state_code


class TestValidation:
    """Test input validation functions"""

    def test_validate_state_code_valid(self):
        assert validate_state_code("ca") == "CA"
        assert validate_state_code("NY") == "NY"
        assert validate_state_code(" TX ") == "TX"

    def test_validate_state_code_invalid(self):
        with pytest.raises(ValidationError, match="State code cannot be empty"):
            validate_state_code("")

        with pytest.raises(ValidationError, match="must be exactly 2 characters"):
            validate_state_code("CAL")

        with pytest.raises(ValidationError, match="Invalid state code"):
            validate_state_code("XX")

    def test_validate_coordinates_valid(self):
        lat, lon = validate_coordinates(37.7749, -122.4194)
        assert lat == 37.7749
        assert lon == -122.4194

        lat, lon = validate_coordinates(0, 0)
        assert lat == 0.0
        assert lon == 0.0

    def test_validate_coordinates_invalid(self):
        with pytest.raises(ValidationError, match="Latitude must be a number"):
            validate_coordinates("invalid", 0)

        with pytest.raises(ValidationError, match="Longitude must be a number"):
            validate_coordinates(0, "invalid")

        with pytest.raises(ValidationError, match="must be between -90 and 90"):
            validate_coordinates(91, 0)

        with pytest.raises(ValidationError, match="must be between -180 and 180"):
            validate_coordinates(0, 181)
