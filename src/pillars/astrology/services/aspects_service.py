"""Comprehensive aspects calculation service."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple


@dataclass(slots=True)
class AspectDefinition:
    """Definition of an astrological aspect."""
    name: str
    angle: float
    default_orb: float
    symbol: str
    is_major: bool


# Major Aspects
MAJOR_ASPECTS = [
    AspectDefinition("Conjunction", 0, 8.0, "☌", True),
    AspectDefinition("Sextile", 60, 4.0, "⚹", True),
    AspectDefinition("Square", 90, 6.0, "□", True),
    AspectDefinition("Trine", 120, 8.0, "△", True),
    AspectDefinition("Opposition", 180, 8.0, "☍", True),
]

# Minor Aspects
MINOR_ASPECTS = [
    AspectDefinition("Semi-sextile", 30, 2.0, "⚺", False),
    AspectDefinition("Semi-square", 45, 2.0, "∠", False),
    AspectDefinition("Quintile", 72, 2.0, "Q", False),
    AspectDefinition("Sesquiquadrate", 135, 2.0, "⚼", False),
    AspectDefinition("Quincunx", 150, 3.0, "⚻", False),
]

ALL_ASPECTS = MAJOR_ASPECTS + MINOR_ASPECTS


@dataclass(slots=True)
class CalculatedAspect:
    """A calculated aspect between two planets."""
    planet_a: str
    planet_b: str
    aspect: AspectDefinition
    orb: float  # Actual orb in degrees
    is_applying: bool  # True if planets are moving closer


class AspectsService:
    """Service for calculating planetary aspects."""

    def calculate_aspects(
        self,
        planet_longitudes: Dict[str, float],
        include_minor: bool = False,
        orb_factor: float = 1.0,
    ) -> List[CalculatedAspect]:
        """
        Calculate all aspects between planets.

        Args:
            planet_longitudes: Dict mapping planet name to ecliptic longitude
            include_minor: If True, include minor aspects
            orb_factor: Multiplier for default orbs (0.5 = tight, 1.5 = wide)

        Returns:
            List of CalculatedAspect objects sorted by orb (tightest first)
        """
        # Normalize planet names
        norm_planets: Dict[str, float] = {}
        for name, lon in planet_longitudes.items():
            n = name.strip().title()
            norm_planets[n] = lon % 360

        # Select aspect definitions
        aspects_to_check = MAJOR_ASPECTS if not include_minor else ALL_ASPECTS

        results: List[CalculatedAspect] = []

        # Check all planet pairs
        for (name_a, lon_a), (name_b, lon_b) in combinations(norm_planets.items(), 2):
            for aspect_def in aspects_to_check:
                orb = self._check_aspect(lon_a, lon_b, aspect_def.angle, aspect_def.default_orb * orb_factor)
                if orb is not None:
                    # Determine if applying (simplified - would need speeds for accuracy)
                    is_applying = self._is_applying(lon_a, lon_b, aspect_def.angle)
                    
                    results.append(CalculatedAspect(
                        planet_a=name_a,
                        planet_b=name_b,
                        aspect=aspect_def,
                        orb=orb,
                        is_applying=is_applying,
                    ))

        # Sort by orb (tightest first)
        results.sort(key=lambda a: a.orb)
        return results

    @staticmethod
    def _check_aspect(lon_a: float, lon_b: float, target_angle: float, max_orb: float) -> float | None:
        """Check if two longitudes form an aspect. Returns orb if within, else None."""
        diff = abs(lon_a - lon_b)
        if diff > 180:
            diff = 360 - diff
        
        orb = abs(diff - target_angle)
        if orb <= max_orb:
            return round(orb, 2)
        return None

    @staticmethod
    def _is_applying(lon_a: float, lon_b: float, target_angle: float) -> bool:
        """Simplified check for applying aspect (would need speeds for accuracy)."""
        diff = (lon_b - lon_a) % 360
        if diff > 180:
            diff = 360 - diff
        return diff <= target_angle

    @staticmethod
    def get_aspect_definitions(include_minor: bool = False) -> List[AspectDefinition]:
        """Get list of aspect definitions."""
        return ALL_ASPECTS if include_minor else MAJOR_ASPECTS
