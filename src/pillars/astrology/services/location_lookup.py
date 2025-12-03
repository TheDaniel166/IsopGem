"""Location lookup helpers for the astrology pillar."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import requests


class LocationLookupError(RuntimeError):
    """Raised when the geocoding API fails or returns no candidates."""


@dataclass(slots=True)
class LocationResult:
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    admin1: Optional[str] = None
    elevation: Optional[float] = None
    timezone_id: Optional[str] = None

    @property
    def label(self) -> str:
        parts: List[str] = [self.name]
        if self.admin1:
            parts.append(self.admin1)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


class LocationLookupService:
    """Queries the Open-Meteo geocoding API for city coordinates."""

    API_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self, session: Optional[requests.Session] = None):
        self._session = session or requests.Session()

    def search(self, query: str, count: int = 7, language: str = "en") -> List[LocationResult]:
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

    @staticmethod
    def _safe_float(value: Optional[float]) -> Optional[float]:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None
