"""Fixed Stars calculation service using Swiss Ephemeris."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import swisseph as swe


@dataclass(slots=True)
class FixedStarPosition:
    """Position data for a fixed star."""
    name: str
    constellation: str
    longitude: float
    latitude: float
    distance: float
    magnitude: float
    nature: str  # Traditional planetary nature


# Curated list of astrologically significant fixed stars
# Format: (Star name for swe, Display Name, Constellation, Nature)
NOTABLE_STARS = [
    ("Aldebaran", "Aldebaran", "α Tauri", "Mars"),
    ("Regulus", "Regulus", "α Leonis", "Mars/Jupiter"),
    ("Antares", "Antares", "α Scorpii", "Mars/Jupiter"),
    ("Fomalhaut", "Fomalhaut", "α Piscis Australis", "Venus/Mercury"),
    ("Algol", "Algol", "β Persei", "Saturn/Jupiter"),
    ("Spica", "Spica", "α Virginis", "Venus/Mars"),
    ("Sirius", "Sirius", "α Canis Majoris", "Jupiter/Mars"),
    ("Vega", "Vega", "α Lyrae", "Venus/Mercury"),
    ("Capella", "Capella", "α Aurigae", "Mars/Mercury"),
    ("Rigel", "Rigel", "β Orionis", "Jupiter/Saturn"),
    ("Betelgeuse", "Betelgeuse", "α Orionis", "Mars/Mercury"),
    ("Procyon", "Procyon", "α Canis Minoris", "Mercury/Mars"),
    ("Pollux", "Pollux", "β Geminorum", "Mars"),
    ("Castor", "Castor", "α Geminorum", "Mercury"),
    ("Deneb", "Deneb", "α Cygni", "Venus/Mercury"),
    ("Altair", "Altair", "α Aquilae", "Mars/Jupiter"),
    ("Arcturus", "Arcturus", "α Bootis", "Mars/Jupiter"),
    ("Canopus", "Canopus", "α Carinae", "Saturn/Jupiter"),
    ("Achernar", "Achernar", "α Eridani", "Jupiter"),
    ("Hamal", "Hamal", "α Arietis", "Mars/Saturn"),
    ("Vindemiatrix", "Vindemiatrix", "ε Virginis", "Saturn/Mercury"),
    ("Alcyone", "Alcyone", "η Tauri", "Moon/Mars"),  # Pleiades
    ("Scheat", "Scheat", "β Pegasi", "Mars/Mercury"),
    ("Markab", "Markab", "α Pegasi", "Mars/Mercury"),
]


class FixedStarsService:
    """Service for calculating fixed star positions."""

    def __init__(self, ephemeris_path: Optional[str] = None):
        """Initialize with optional custom ephemeris path."""
        self._ephemeris_path = ephemeris_path
        self._configured = False

    def _ensure_configured(self) -> None:
        """Set up Swiss Ephemeris path if not already done."""
        if self._configured:
            return

        if self._ephemeris_path:
            swe.set_ephe_path(self._ephemeris_path)
        else:
            # Try to find OpenAstro2's ephemeris directory
            try:
                import openastro2
                pkg_path = Path(openastro2.__file__).parent
                ephe_path = pkg_path / "swiss_ephemeris"
                if ephe_path.exists():
                    swe.set_ephe_path(str(ephe_path))
            except ImportError:
                pass  # Use default path

        self._configured = True

    def get_star_positions(self, julian_day: float) -> List[FixedStarPosition]:
        """
        Calculate positions for notable fixed stars at a given Julian Day.

        Args:
            julian_day: Julian Day number (UT)

        Returns:
            List of FixedStarPosition objects
        """
        self._ensure_configured()
        positions = []

        for star_name, display_name, constellation, nature in NOTABLE_STARS:
            try:
                # swe.fixstar_ut returns ((lon, lat, dist, speed_lon, speed_lat, speed_dist), name, retflag)
                result, star_info, retflag = swe.fixstar_ut(star_name, julian_day)
                
                longitude = result[0]
                latitude = result[1]
                distance = result[2]
                
                # Extract magnitude from star_info if available
                magnitude = self._extract_magnitude(star_info)

                positions.append(FixedStarPosition(
                    name=display_name,
                    constellation=constellation,
                    longitude=longitude,
                    latitude=latitude,
                    distance=distance,
                    magnitude=magnitude,
                    nature=nature,
                ))
            except Exception:
                # Star not found or calculation error - skip
                continue

        # Sort by longitude
        positions.sort(key=lambda p: p.longitude)
        return positions

    def _extract_magnitude(self, star_info: str) -> float:
        """Extract visual magnitude from star info string."""
        # The star_info string contains magnitude data
        # Format varies, but magnitude is typically after a comma
        try:
            parts = star_info.split(",")
            if len(parts) >= 2:
                # Magnitude is usually in the second field
                mag_str = parts[1].strip()
                return float(mag_str)
        except (ValueError, IndexError):
            pass
        return 0.0

    def find_aspects(
        self,
        planet_longitudes: List[Tuple[str, float]],
        star_positions: List[FixedStarPosition],
        orb: float = 1.0,
    ) -> List[Tuple[str, FixedStarPosition, str, float]]:
        """
        Find fixed stars aspects to planets within given orb.
        Supports Conjunction (0), Opposition (180), Trine (120), Square (90), Sextile (60).

        Args:
            planet_longitudes: List of (planet_name, longitude) tuples
            star_positions: List of FixedStarPosition objects
            orb: Maximum orb in degrees

        Returns:
            List of (planet_name, star_position, aspect_name, orb_degrees) tuples
        """
        aspects_map = {
            0: "Conjunction",
            60: "Sextile",
            90: "Square",
            120: "Trine",
            180: "Opposition"
        }
        
        found_aspects = []

        for planet_name, planet_lon in planet_longitudes:
            for star in star_positions:
                diff = abs(planet_lon - star.longitude) % 360
                if diff > 180:
                    diff = 360 - diff
                
                # Check each aspect
                for angle, name in aspects_map.items():
                    orb_dist = abs(diff - angle)
                    if orb_dist <= orb:
                        found_aspects.append((planet_name, star, name, round(orb_dist, 2)))

        return found_aspects
