"""Input validation functions for the weather MCP server."""

from .config import VALID_STATES
from .exceptions import ValidationError


def validate_state_code(state: str) -> str:
    """Validate and normalize state code.

    Args:
        state: Two-letter state code

    Returns:
        Normalized state code in uppercase

    Raises:
        ValidationError: If state code is invalid
    """
    if not state:
        raise ValidationError("State code cannot be empty")

    state = state.upper().strip()
    if len(state) != 2:
        raise ValidationError("State code must be exactly 2 characters")

    if state not in VALID_STATES:
        raise ValidationError(
            f"Invalid state code: {state}. Must be a valid US state/territory code."
        )

    return state


def validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    """Validate latitude and longitude coordinates.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Tuple of validated coordinates

    Raises:
        ValidationError: If coordinates are invalid
    """
    if not isinstance(latitude, int | float):
        raise ValidationError("Latitude must be a number")
    if not isinstance(longitude, int | float):
        raise ValidationError("Longitude must be a number")

    if not -90 <= latitude <= 90:
        raise ValidationError("Latitude must be between -90 and 90 degrees")
    if not -180 <= longitude <= 180:
        raise ValidationError("Longitude must be between -180 and 180 degrees")

    return float(latitude), float(longitude)
