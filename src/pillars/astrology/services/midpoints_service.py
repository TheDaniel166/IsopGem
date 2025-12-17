"""Midpoints calculation service."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Set


@dataclass(slots=True)
class Midpoint:
    """Calculated midpoint between two planets."""
    planet_a: str
    planet_b: str
    longitude: float


# Planet sets for filtering
CLASSIC_7 = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}
MODERN_3 = {"Uranus", "Neptune", "Pluto"}
MODERN_10 = CLASSIC_7 | MODERN_3
EXTENDED = MODERN_10 | {"True Node", "North Node", "Chiron", "Asc", "MC"}


class MidpointsService:
    """Service for calculating planetary midpoints."""

    def calculate_midpoints(
        self,
        planet_longitudes: Dict[str, float],
        classic_only: bool = True,
    ) -> List[Midpoint]:
        """
        Calculate midpoints between all planet pairs.

        Args:
            planet_longitudes: Dict mapping planet name to ecliptic longitude
            classic_only: If True, only include Classic 7 planets

        Returns:
            List of Midpoint objects sorted by longitude
        """
        # Normalize planet names to title case
        norm_planets: Dict[str, float] = {}
        for name, lon in planet_longitudes.items():
            n = name.strip().title()
            norm_planets[n] = lon

        # Determine which planets to include
        allowed_set = CLASSIC_7 if classic_only else MODERN_10
        
        # Filter to only allowed planets that exist in chart
        available = {
            name: lon for name, lon in norm_planets.items()
            if name in allowed_set
        }

        midpoints: List[Midpoint] = []

        # Generate all unique pairs
        for (name_a, lon_a), (name_b, lon_b) in combinations(available.items(), 2):
            mid_lon = self._calculate_midpoint(lon_a, lon_b)
            midpoints.append(Midpoint(
                planet_a=name_a,
                planet_b=name_b,
                longitude=mid_lon,
            ))

        # Sort by longitude
        midpoints.sort(key=lambda m: m.longitude)
        return midpoints

    @staticmethod
    def _calculate_midpoint(lon_a: float, lon_b: float) -> float:
        """
        Calculate the midpoint between two longitudes.
        
        Uses the shorter arc to find the midpoint.
        """
        # Ensure values are in 0-360 range
        lon_a = lon_a % 360
        lon_b = lon_b % 360

        # Calculate the difference
        diff = abs(lon_a - lon_b)

        if diff <= 180:
            # Shorter arc is direct
            mid = (lon_a + lon_b) / 2
        else:
            # Shorter arc crosses 0°
            mid = (lon_a + lon_b) / 2 + 180

        return mid % 360
