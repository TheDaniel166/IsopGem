"""Astrology domain models for OpenAstro2 integration."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


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


@dataclass(slots=True)
class AstrologyEvent:
    """Normalized event descriptor for chart calculations."""

    name: str
    timestamp: datetime
    location: GeoLocation
    timezone_offset: Optional[float] = None  # Hours offset from UTC
    metadata: Dict[str, Any] = field(default_factory=dict)

    def resolved_timezone_offset(self) -> float:
        """Return the timezone offset in hours, deriving it from tzinfo when missing."""
        if self.timezone_offset is not None:
            return self.timezone_offset
        if self.timestamp.tzinfo and self.timestamp.utcoffset() is not None:
            offset_seconds = self.timestamp.utcoffset().total_seconds()
            return offset_seconds / 3600.0
        return 0.0

    def to_openastro_kwargs(self) -> Dict[str, Any]:
        """Serialize the event into the kwargs OpenAstro2 expects."""
        localized = self.timestamp
        if localized.tzinfo is None:
            localized = localized.replace(tzinfo=timezone.utc)
        return {
            "name": self.name,
            "year": localized.year,
            "month": localized.month,
            "day": localized.day,
            "hour": localized.hour,
            "minute": localized.minute,
            "second": localized.second,
            "timezone": self.resolved_timezone_offset(),
            "location": self.location.name,
            "countrycode": self.location.country_code or "",
            "geolat": self.location.latitude,
            "geolon": self.location.longitude,
            "altitude": self.location.elevation,
        }


@dataclass(slots=True)
class ChartRequest:
    """User-facing request describing the chart that should be produced."""

    primary_event: AstrologyEvent
    chart_type: str = "Radix"
    reference_event: Optional[AstrologyEvent] = None
    include_svg: bool = True
    settings: Optional[Dict[str, Any]] = None


@dataclass(slots=True)
class PlanetPosition:
    """Planet position metadata for UI consumption."""

    name: str
    degree: float
    sign_index: Optional[int] = None
    speed: Optional[float] = None  # Degrees per day
    declination: Optional[float] = None  # Degrees (-90 to +90)


@dataclass(slots=True)
class HousePosition:
    """House cusp information."""

    number: int
    degree: float


@dataclass(slots=True)
class ChartResult:
    """Normalized result returned by the OpenAstro service wrapper."""

    chart_type: str
    planet_positions: List[PlanetPosition] = field(default_factory=list)
    house_positions: List[HousePosition] = field(default_factory=list)
    aspect_summary: Dict[str, Any] = field(default_factory=dict)
    svg_document: Optional[str] = None
    raw_payload: Dict[str, Any] = field(default_factory=dict)
    julian_day: Optional[float] = None

    def has_svg(self) -> bool:
        """Return True when the chart includes SVG output."""
        return bool(self.svg_document)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the result into primitives for persistence or transport."""
        return {
            "chart_type": self.chart_type,
            "planet_positions": [self._serialize_dataclass(pos) for pos in self.planet_positions],
            "house_positions": [self._serialize_dataclass(house) for house in self.house_positions],
            "aspect_summary": self.aspect_summary,
            "svg_document": self.svg_document,
            "raw_payload": self.raw_payload,
        }

    @staticmethod
    def _serialize_dataclass(instance: Any) -> Dict[str, Any]:
        if is_dataclass(instance):
            return asdict(instance)
        raise TypeError("ChartResult serialization received a non-dataclass instance")
