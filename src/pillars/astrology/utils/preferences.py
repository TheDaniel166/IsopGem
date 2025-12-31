"""Preferences storage for the astrology pillar."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

DATA_DIR = Path.cwd() / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PREFS_PATH = DATA_DIR / "astrology_prefs.json"


@dataclass(slots=True)
class DefaultLocation:
    """
    Default Location class definition.
    
    """
    name: str
    latitude: float
    longitude: float
    elevation: float
    timezone_offset: float
    timezone_id: Optional[str] = None


class AstrologyPreferences:
    """Simple JSON-backed preference store."""

    def __init__(self, path: Optional[Path] = None):
        """
          init   logic.
        
        Args:
            path: Description of path.
        
        """
        self._path = path or PREFS_PATH

    def load_default_location(self) -> Optional[DefaultLocation]:
        """
        Load default location logic.
        
        Returns:
            Result of load_default_location operation.
        """
        data = self._read()
        payload = data.get("default_location")
        if not payload:
            return None
        try:
            return DefaultLocation(**payload)
        except TypeError:
            return None

    def save_default_location(self, location: DefaultLocation) -> None:
        """
        Save default location logic.
        
        Args:
            location: Description of location.
        
        Returns:
            Result of save_default_location operation.
        """
        data = self._read()
        data["default_location"] = asdict(location)
        self._write(data)

    def load_favorites(self) -> list:
        """
        Load favorite locations from preferences.
        
        Returns:
            List of DefaultLocation objects.
        """
        data = self._read()
        favorites_data = data.get("favorites", [])
        favorites = []
        for item in favorites_data:
            try:
                favorites.append(DefaultLocation(**item))
            except TypeError:
                continue
        return favorites

    def add_favorite(self, location: DefaultLocation) -> None:
        """
        Add a location to favorites.
        
        Args:
            location: Location to add.
        """
        data = self._read()
        favorites = data.get("favorites", [])
        
        # Avoid duplicates (by coordinates)
        for fav in favorites:
            if fav.get("latitude") == location.latitude and fav.get("longitude") == location.longitude:
                return  # Already exists
        
        favorites.append(asdict(location))
        data["favorites"] = favorites
        self._write(data)

    def remove_favorite(self, location: DefaultLocation) -> None:
        """
        Remove a location from favorites.
        
        Args:
            location: Location to remove.
        """
        data = self._read()
        favorites = data.get("favorites", [])
        
        # Filter out the matching location
        data["favorites"] = [
            fav for fav in favorites
            if not (fav.get("latitude") == location.latitude and fav.get("longitude") == location.longitude)
        ]
        self._write(data)

    # ------------------------------------------------------------------
    def _read(self) -> Dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {}

    def _write(self, payload: Dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)