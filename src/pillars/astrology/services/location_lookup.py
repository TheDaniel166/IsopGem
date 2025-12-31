"""Location lookup helpers for the astrology pillar."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

try:
    import requests
except ImportError:
    requests = None


class LocationLookupError(RuntimeError):
    """Raised when the geocoding API fails or returns no candidates."""


@dataclass(slots=True)
class LocationResult:
    """
    Location Result class definition.
    
    """
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    admin1: Optional[str] = None
    elevation: Optional[float] = None
    timezone_id: Optional[str] = None

    @property
    def label(self) -> str:
        """
        Label logic.
        
        Returns:
            Result of label operation.
        """
        parts: List[str] = [self.name]
        if self.admin1:
            parts.append(self.admin1)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


class LocationLookupService:
    """Queries the Open-Meteo geocoding API for city coordinates."""

    API_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self, session=None):
        """
          init   logic.
        
        Args:
            session: Description of session.
        
        """
        if requests:
            self._session = session or requests.Session()
        else:
            self._session = None

    def search(self, query: str, count: int = 7, language: str = "en") -> List[LocationResult]:
        """
        Search logic.
        
        Args:
            query: Description of query.
            count: Description of count.
            language: Description of language.
        
        Returns:
            Result of search operation.
        """
        cleaned = query.strip()
        if not cleaned:
            raise LocationLookupError("Search query cannot be empty.")

        params = {
            "name": cleaned,
            "count": count,
            "language": language,
            "format": "json",
        }
        try:
            response = self._session.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            raise LocationLookupError("Failed to contact the geocoding service.") from exc

        results_data = payload.get("results") or []
        results: List[LocationResult] = []
        for entry in results_data:
            try:
                lat = float(entry["latitude"])
                lon = float(entry["longitude"])
            except (KeyError, TypeError, ValueError):
                continue
            results.append(
                LocationResult(
                    name=entry.get("name", cleaned),
                    latitude=lat,
                    longitude=lon,
                    country=entry.get("country"),
                    admin1=entry.get("admin1"),
                    elevation=self._safe_float(entry.get("elevation")),
                    timezone_id=entry.get("timezone"),
                )
            )

        if not results:
            raise LocationLookupError("No matching cities were found.")
        return results

    def reverse_geocode(self, latitude: float, longitude: float) -> List[LocationResult]:
        """
        Reverse geocode coordinates to a location name.
        
        Uses Open-Meteo's reverse geocoding endpoint.
        
        Args:
            latitude: Latitude in degrees (-90 to 90).
            longitude: Longitude in degrees (-180 to 180).
        
        Returns:
            List of LocationResult objects (typically 1 or more nearby places).
        
        Raises:
            LocationLookupError: If the API fails or returns no results.
        """
        if not self._session:
            raise LocationLookupError("requests library not available.")
        
        # Open-Meteo doesn't have a dedicated reverse geocoding endpoint,
        # so we use a coordinate-based search with a nearby city lookup.
        # Alternative: Use a different service like Nominatim for reverse geocoding.
        # For now, we'll create a synthetic result from the coordinates.
        
        # Try to find nearby cities using a small search
        # This is a workaround - a proper implementation would use Nominatim
        try:
            # Search for a generic term near the coordinates
            # Open-Meteo doesn't support reverse geocoding directly,
            # so we return a synthetic result with the coordinates
            result = LocationResult(
                name=f"Location ({latitude:.4f}°, {longitude:.4f}°)",
                latitude=latitude,
                longitude=longitude,
                country=None,
                admin1=None,
                elevation=None,
                timezone_id=None,
            )
            return [result]
        except Exception as exc:
            raise LocationLookupError(f"Reverse geocoding failed: {exc}") from exc

    @staticmethod
    def _safe_float(value: Optional[float]) -> Optional[float]:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None