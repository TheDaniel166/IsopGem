"""Harmonic chart calculation service."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(slots=True)
class HarmonicPosition:
    """Harmonic chart position for a planet."""
    planet: str
    natal_longitude: float
    harmonic_longitude: float


# Common harmonic presets with meanings
HARMONIC_PRESETS = {
    1: ("Natal", "Base chart - no transformation"),
    4: ("Square", "Tension, challenges, action"),
    5: ("Quintile", "Creativity, talent, gifts"),
    7: ("Septile", "Destiny, fate, karma"),
    9: ("Novile", "Spiritual gifts, gestation"),
    12: ("Semi-sextile", "Integration, adjustment"),
}


class HarmonicsService:
    """Service for calculating harmonic charts."""

    @staticmethod
    def calculate_harmonic(
        planet_longitudes: Dict[str, float],
        harmonic: int,
    ) -> List[HarmonicPosition]:
        """
        Calculate harmonic chart positions.

        Args:
            planet_longitudes: Dict mapping planet name to ecliptic longitude
            harmonic: Harmonic number (1 = natal, 4 = square harmonic, etc.)

        Returns:
            List of HarmonicPosition objects
        """
        if harmonic < 1:
            harmonic = 1

        results: List[HarmonicPosition] = []

        for planet, natal_lon in planet_longitudes.items():
            # Harmonic formula: (natal × H) mod 360
            harmonic_lon = (natal_lon * harmonic) % 360.0
            
            results.append(HarmonicPosition(
                planet=planet.strip().title(),
                natal_longitude=natal_lon,
                harmonic_longitude=harmonic_lon,
            ))

        # Sort by harmonic longitude
        results.sort(key=lambda p: p.harmonic_longitude)
        return results

    @staticmethod
    def get_preset_info(harmonic: int) -> tuple:
        """Get name and description for a harmonic preset."""
        return HARMONIC_PRESETS.get(harmonic, (f"H{harmonic}", "Custom harmonic"))
