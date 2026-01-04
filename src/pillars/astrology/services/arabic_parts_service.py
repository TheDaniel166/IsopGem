"""Arabic Parts (Lots) calculation service."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple  # type: ignore[reportUnusedImport]


@dataclass(slots=True)
class ArabicPart:
    """Calculated Arabic Part result."""
    name: str
    longitude: float
    formula: str
    category: str  # 'hermetic', 'esoteric', 'traditional'


@dataclass
class PartDefinition:
    """Definition of an Arabic Part with its formula."""
    name: str
    # Formula components: (add_body, subtract_body) relative to ASC
    # For day charts. Night charts reverse these.
    day_add: str
    day_sub: str
    # If True, reverse the formula for night charts
    reverse_at_night: bool
    category: str
    description: str = ""


# Comprehensive list of Arabic Parts
# Format: (name, day_add, day_sub, reverse_at_night, category, description)
PARTS_DEFINITIONS: List[PartDefinition] = [
    # Core Hermetic Lots
    PartDefinition("Fortune", "Moon", "Sun", True, "hermetic", "Material luck and ease"),
    PartDefinition("Spirit", "Sun", "Moon", True, "hermetic", "Higher purpose, soul's direction"),
    PartDefinition("Eros", "Venus", "Spirit", True, "hermetic", "Love and desire"),
    PartDefinition("Necessity", "Fortune", "Mercury", True, "hermetic", "Inevitable fate"),
    PartDefinition("Courage", "Fortune", "Mars", True, "hermetic", "Valor and boldness"),
    
    # Esoteric & Occult Parts
    PartDefinition("Occultism", "Neptune", "Uranus", True, "esoteric", "Hidden knowledge, mysticism"),
    PartDefinition("Fatality", "Saturn", "Sun", False, "esoteric", "Fate, karma"),
    PartDefinition("Nemesis", "Saturn", "Jupiter", True, "esoteric", "Justice, retribution"),
    PartDefinition("Catastrophe", "Uranus", "Saturn", False, "esoteric", "Sudden upheaval"),
    PartDefinition("Treachery", "Mars", "Sun", False, "esoteric", "Hidden enemies, danger"),
    PartDefinition("Foundation", "Fortune", "Spirit", False, "esoteric", "Life's foundation"),
    PartDefinition("Captivity", "Saturn", "Fortune", False, "esoteric", "Bondage, restriction"),
    PartDefinition("Sorcery", "Neptune", "Mercury", False, "esoteric", "Magic, illusion"),
    PartDefinition("Secrets", "Pluto", "Moon", False, "esoteric", "Hidden truths"),
    
    # Traditional Life Parts
    PartDefinition("Marriage (M)", "Venus", "Saturn", True, "traditional", "Partnership (male)"),
    PartDefinition("Marriage (F)", "Saturn", "Venus", True, "traditional", "Partnership (female)"),
    PartDefinition("Children", "Saturn", "Jupiter", True, "traditional", "Offspring"),
    PartDefinition("Father", "Saturn", "Sun", True, "traditional", "Paternal figure"),
    PartDefinition("Mother", "Moon", "Venus", True, "traditional", "Maternal figure"),
    PartDefinition("Siblings", "Jupiter", "Saturn", False, "traditional", "Brothers and sisters"),
    PartDefinition("Inheritance", "Moon", "Saturn", True, "traditional", "Legacy, inheritance"),
    PartDefinition("Commerce", "Mercury", "Sun", False, "traditional", "Trade, business"),
    PartDefinition("Passion", "Mars", "Venus", True, "traditional", "Desire, drive"),
    PartDefinition("Death", "Moon", "H8", True, "traditional", "Mortality"),
]


class ArabicPartsService:
    """Service for calculating Arabic Parts (Lots)."""

    def __init__(self):
        """
          init   logic.
        
        """
        self._parts = PARTS_DEFINITIONS

    def calculate_parts(
        self,
        planet_longitudes: Dict[str, float],
        house_cusps: Dict[int, float],
        is_day_chart: bool,
    ) -> List[ArabicPart]:
        """
        Calculate all Arabic Parts for a chart.

        Args:
            planet_longitudes: Dict mapping planet name to ecliptic longitude
            house_cusps: Dict mapping house number (1-12) to cusp longitude
            is_day_chart: True if Sun is above horizon (houses 7-12)

        Returns:
            List of calculated ArabicPart objects
        """
        asc = house_cusps.get(1, 0.0)
        results = []

        # Normalize planet names to title case for matching
        norm_planet_lons: Dict[str, float] = {}
        for name, lon in planet_longitudes.items():
            n = name.strip().title()
            # Handle special cases
            if n.lower() in ("true node", "north node"):
                norm_planet_lons["True Node"] = lon
                norm_planet_lons["North Node"] = lon
            elif n.lower() == "south node":
                norm_planet_lons["South Node"] = lon
            else:
                norm_planet_lons[n] = lon

        # Pre-calculate Fortune and Spirit since other parts reference them
        fortune_lon = self._calc_part_longitude(
            asc, 
            norm_planet_lons.get("Moon", 0),
            norm_planet_lons.get("Sun", 0),
            is_day_chart,
            True  # reverse_at_night
        )
        spirit_lon = self._calc_part_longitude(
            asc,
            norm_planet_lons.get("Sun", 0),
            norm_planet_lons.get("Moon", 0),
            is_day_chart,
            True
        )
        
        # Add Fortune, Spirit, and house cusps to lookup
        reference_points: Dict[str, float] = {
            **norm_planet_lons,
            "Fortune": fortune_lon,
            "Spirit": spirit_lon,
            "H8": house_cusps.get(8, 0.0),
            "MC": house_cusps.get(10, 0.0),
        }

        for part_def in self._parts:
            add_val = reference_points.get(part_def.day_add)
            sub_val = reference_points.get(part_def.day_sub)
            
            if add_val is None or sub_val is None:
                # Missing planet/point - skip this part
                continue

            lon = self._calc_part_longitude(
                asc, add_val, sub_val, is_day_chart, part_def.reverse_at_night
            )

            formula = f"ASC + {part_def.day_add} - {part_def.day_sub}"
            if part_def.reverse_at_night and not is_day_chart:
                formula = f"ASC + {part_def.day_sub} - {part_def.day_add}"

            results.append(ArabicPart(
                name=part_def.name,
                longitude=lon,
                formula=formula,
                category=part_def.category,
            ))

        # Sort by category then name
        category_order = {"hermetic": 0, "esoteric": 1, "traditional": 2}
        results.sort(key=lambda p: (category_order.get(p.category, 99), p.name))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownMemberType]
        return results

    def _calc_part_longitude(
        self,
        asc: float,
        add_body: float,
        sub_body: float,
        is_day: bool,
        reverse_at_night: bool,
    ) -> float:
        """Calculate Part longitude with day/night reversal."""
        if reverse_at_night and not is_day:
            # Night chart - reverse the formula
            add_body, sub_body = sub_body, add_body

        raw = asc + add_body - sub_body
        # Normalize to 0-360
        return raw % 360.0

    @staticmethod
    def is_day_chart(sun_longitude: float, asc_longitude: float) -> bool:
        """
        Determine if chart is diurnal (day) or nocturnal (night).
        Sun is above horizon if it's in houses 7-12 (roughly 180° ahead of ASC).
        """
        diff = (sun_longitude - asc_longitude) % 360
        # Sun is "above horizon" if it's between 180° behind ASC and ASC
        # i.e., diff is between 180 and 360 (or 0)
        return diff >= 180 or diff == 0