"""Shared geographic location model."""
from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
class GeoLocation:
    """Geographic location data.

    Attributes:
        name: Human readable label for the location (city, coordinates, etc.)
        latitude: Decimal degrees latitude (-90 to 90)
        longitude: Decimal degrees longitude (-180 to 180)
        elevation: Elevation above sea level in meters
    """

    name: str
    latitude: float
    longitude: float
    elevation: float = 0.0
    country_code: Optional[str] = None

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError("Latitude must be within -90 and 90 degrees.")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError("Longitude must be within -180 and 180 degrees.")
