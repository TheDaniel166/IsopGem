"""Service for generating chart interpretations."""
from __future__ import annotations

import logging
from typing import List, Optional

from pillars.astrology.models.chart_models import ChartResult, PlanetPosition, HousePosition
from pillars.astrology.models.interpretation_models import InterpretationReport
from pillars.astrology.repositories.interpretation_repository import InterpretationRepository
from pillars.astrology.services.aspects_service import CalculatedAspect, AspectsService

logger = logging.getLogger(__name__)

class InterpretationService:
    """Orchestrates the generation of chart interpretation reports."""

    def __init__(self, repository: Optional[InterpretationRepository] = None):
        """
          init   logic.
        
        Args:
            repository: Description of repository.
        
        """
        self.repository = repository or InterpretationRepository()
        self.aspects_service = AspectsService()

    def interpret_chart(self, chart: ChartResult, chart_name: str = "Chart") -> InterpretationReport:
        """Generate a full interpretation report for the given chart."""
        report = InterpretationReport(chart_name=chart_name)

        # 1. Interpret Planets in Signs and Houses
        self._interpret_planets(chart.planet_positions, chart.house_positions, report)

        # 2. Interpret Aspects
        self._interpret_aspects(chart.planet_positions, report)
        
        # 3. Interpret Dominants (Elemental Balance)
        self._interpret_dominants(chart.planet_positions, report)

        return report

    def _interpret_aspects(self, planets: List[PlanetPosition], report: InterpretationReport) -> None:
        """Calculate and interpret planetary aspects."""
        # Convert list of PlanetPositions to dict for AspectsService
        planet_map = {p.name: p.degree for p in planets}
        
        # Calculate aspects (Tier 1: Major + Common Minor)
        aspects = self.aspects_service.calculate_aspects(planet_map, tier=1)
        for aspect in aspects:
            # We skip aspects involving the Nodes/Angles if we don't have text for them yet, 
            # but usually we want them.
            
            
            content = self.repository.get_aspect_text(aspect.planet_a, aspect.planet_b, aspect.aspect.name)
            
            if content:
                # Calculate weight: Tighter orb = Higher weight
                # Max orb is ~8-10. If orb is 0, weight is high (1.5). If max, weight is 0.5.
                # Simple linear scaling: 1.5 - (orb / max_orb)
                weight = 1.5 - (aspect.orb / aspect.aspect.default_orb)
                weight = max(0.5, weight) # Floor at 0.5
                
                applying_str = "Applying" if aspect.is_applying else "Separating"
                title = f"{aspect.planet_a} {aspect.aspect.symbol} {aspect.planet_b} ({applying_str}, Orb {aspect.orb}°)"
                
                report.add_segment(
                    title=title,
                    content=content,
                    tags=["Aspect", aspect.aspect.name, aspect.planet_a, aspect.planet_b],
                    weight=weight
                )

    def _interpret_dominants(self, planets: List[PlanetPosition], report: InterpretationReport) -> None:
        """Analyze elemental balance and dominants."""
        # Basic mapping (simplified for this iteration)
        # 0=Fire, 1=Earth, 2=Air, 3=Water
        ELEMENTS = ["Fire", "Earth", "Air", "Water"]
        MODALITIES = ["Cardinal", "Fixed", "Mutable"]
        
        # Sign index to element/modality
        # Fire: 0, 4, 8
        # Earth: 1, 5, 9
        # Air: 2, 6, 10
        # Water: 3, 7, 11
        
        element_counts = {e: 0 for e in ELEMENTS}
        modality_counts = {m: 0 for m in MODALITIES}
        
        # Weights for bodies (Sun/Moon=3, Personal=2, Outer=1)
        WEIGHTS = {
            "Sun": 3, "Moon": 3, "Ascendant": 3, "Midheaven": 2,
            "Mercury": 2, "Venus": 2, "Mars": 2,
            "Jupiter": 1, "Saturn": 1, "Uranus": 1, "Neptune": 1, "Pluto": 1
        }
        
        for p in planets:
            if p.sign_index is None:
                continue
                
            w = WEIGHTS.get(p.name, 1)
            
            # Element
            e_idx = p.sign_index % 4  
            # Note: The standard order is Fire(0), Earth(1), Air(2), Water(3)?
            # Zodiac: Aries(Fire), Taurus(Earth), Gemini(Air), Cancer(Water)..
            # Yes, index % 4 works specifically if 0=Fire.
            # Aries=0 (Fire), Taurus=1 (Earth), Gemini=2 (Air), Cancer=3 (Water). Matches.
            
            element_counts[ELEMENTS[e_idx]] += w
            
            # Modality
            # Cardinal: 0, 3, 6, 9
            # Fixed: 1, 4, 7, 10
            # Mutable: 2, 5, 8, 11
            m_idx = p.sign_index % 3
            modality_counts[MODALITIES[m_idx]] += w

        # Find Highs/Lows
        total_points = sum(element_counts.values())
        if total_points == 0:
            return

        # Simple logic: If element > 35% of chart -> High
        # If element < 10% -> Low
        
        for elem, score in element_counts.items():
            pct = score / total_points
            key = None
            if pct > 0.35:
                key = f"high_{elem.lower()}"
                title = f"Dominant Element: {elem}"
            elif pct < 0.10:
                key = f"low_{elem.lower()}"
                title = f"Deficient Element: {elem}"
            
            if key:
                content = self.repository.get_elementalist_text("elements", key)
                if content:
                    report.add_segment(title=title, content=content, tags=["Dominant", "Element", elem])

    def interpret_transits(self, transit_chart: ChartResult, natal_chart: ChartResult, aspects: List[CalculatedAspect]) -> InterpretationReport:
        """
        Interpret Transits vs Natal.
        """
        report = InterpretationReport(chart_name=f"Transits for {transit_chart.raw_payload.get('date', 'Unknown Date')}")
        
        # We assume 'aspects' list contains CalculatedAspect where planet_a is Transit and planet_b is Natal
        # Ideally, we should receive semantic objects or verify names.
        
        for aspect in aspects:
            # Check repository
            content = self.repository.get_transit_text(
                transiting_planet=aspect.planet_a, # e.g. "Transit Sun" or just "Sun"
                natal_planet=aspect.planet_b,
                aspect_name=aspect.aspect.name
            )
            
            if content:
                report.add_segment(
                    title=f"Transit {aspect.planet_a} {aspect.aspect.symbol} Natal {aspect.planet_b}",
                    content=content,
                    tags=["Transit", aspect.planet_a, aspect.planet_b]
                )

        if not report.segments:
            report.add_segment(
                title="Interpretation Unavailable",
                content=(
                    "Transit interpretation data is not available yet. "
                    "Add `src/pillars/astrology/data/interpretations/transits.json` to enable it."
                ),
                tags=["Notice", "MissingData", "Transits"],
            )

        return report

    def interpret_synastry(self, chart_a: ChartResult, chart_b: ChartResult, aspects: List[CalculatedAspect]) -> InterpretationReport:
        """
        Interpret Synastry (Relationship).
        """
        report = InterpretationReport(chart_name=f"Synastry: A vs B")
        
        # 'aspects' are cross-aspects
        for aspect in aspects:
            # Parse names if they are like "A: Sun" / "B: Moon"
            # Our SynastryService produces exact strings.
            # We strip prefixes if present.
            p_a = aspect.planet_a.split(": ")[-1] if ":" in aspect.planet_a else aspect.planet_a
            p_b = aspect.planet_b.split(": ")[-1] if ":" in aspect.planet_b else aspect.planet_b
            
            content = self.repository.get_synastry_text(p_a, p_b, aspect.aspect.name)
            
            if content:
                report.add_segment(
                    title=f"{p_a} {aspect.aspect.symbol} {p_b}",
                    content=content,
                    tags=["Synastry", p_a, p_b]
                )

        if not report.segments:
            report.add_segment(
                title="Interpretation Unavailable",
                content=(
                    "Synastry interpretation data is not available yet. "
                    "Add `src/pillars/astrology/data/interpretations/synastry.json` to enable it."
                ),
                tags=["Notice", "MissingData", "Synastry"],
            )

        return report

    def _interpret_planets(self, planets: List[PlanetPosition], houses: List[HousePosition], report: InterpretationReport) -> None:
        """Add interpretations for each planet."""
        SIGN_NAMES = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        
        # Only interpret these bodies
        SUPPORTED_BODIES = {
            "Sun", "Moon", "Mercury", "Venus", "Mars", 
            "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", 
            "Chiron", "North Node", "South Node"
        }

        for planet in planets:
            # Normalize name to Title Case (e.g. "sun" -> "Sun")
            # OpenAstro often returns lowercase or mixed case
            planet_name = planet.name.strip().title()
            
            # handle special cases if needed (e.g. "Mean Node" -> "North Node" mapping could go here if needed)
            if planet_name == "Mean Node":
                planet_name = "North Node"
                
            if planet_name not in SUPPORTED_BODIES:
                continue

            sign_name = "Unknown"
            if planet.sign_index is not None and 0 <= planet.sign_index < 12:
                sign_name = SIGN_NAMES[planet.sign_index]

            # Determine house placement using cusps
            house_num = self._resolve_house(planet.degree, houses)

            logger.debug(f"Interpreting {planet_name} in {sign_name} (House {house_num})")

            # 1. Try Combinatorial (Triad)
            content = self.repository.get_planet_sign_house_text(planet_name, sign_name, house_num)
            
            if content:
                logger.debug(f"Found Triad content for {planet_name}")
                report.add_segment(
                    title=f"{planet_name} in {sign_name} in House {house_num}",
                    content=content,
                    tags=[planet_name, sign_name, f"House {house_num}", "Triad"]
                )
            else:
                # 2. Fallback: Planet in Sign
                sign_content = self.repository.get_planet_sign_text(planet_name, sign_name)
                if sign_content:
                    logger.debug(f"Found Sign content for {planet_name}")
                    report.add_segment(
                        title=f"{planet_name} in {sign_name}",
                        content=sign_content,
                        tags=[planet_name, sign_name]
                    )
                else:
                    logger.warning(f"No Sign content for {planet_name} in {sign_name}")

                # 3. Fallback: Planet in House
                if house_num > 0:
                    house_content = self.repository.get_planet_house_text(planet_name, house_num)
                    if house_content:
                        logger.debug(f"Found House content for {planet_name}")
                        report.add_segment(
                            title=f"{planet_name} in House {house_num}",
                            content=house_content,
                            tags=[planet_name, f"House {house_num}"]
                        )
                    else:
                        logger.warning(f"No House content for {planet_name} in House {house_num}")

            # 4. Add Retrograde interpretation if applicable
            if planet.is_retrograde:
                retro_content = self.repository.get_retrograde_text(planet_name)
                if retro_content:
                    logger.debug(f"Found Retrograde content for {planet_name}")
                    report.add_segment(
                        title=f"{planet_name} Retrograde",
                        content=retro_content,
                        tags=[planet_name, "Retrograde"],
                        weight=1.2  # Slightly elevated importance
                    )

    def _resolve_house(self, planet_degree: float, houses: List[HousePosition]) -> int:
        """Determine which house a planet is in based on house cusps."""
        if not houses:
            return 0
            
        # Ensure houses are sorted by number (1-12)
        sorted_houses = sorted(houses, key=lambda h: h.number)
        
        # Simple algorithm: A planet is in House N if it is between Cusp N and Cusp N+1
        # Handling the wrap-around at 360/0 degrees.
        
        for i, house in enumerate(sorted_houses):
            cusp_start = house.degree
            # Get next house cusp (handle wrap for last house)
            next_house_idx = (i + 1) % len(sorted_houses)
            cusp_end = sorted_houses[next_house_idx].degree
            
            # Check if planet is in this sector
            if self._is_between(planet_degree, cusp_start, cusp_end):
                return house.number
                
        return 0

    @staticmethod
    def _is_between(target: float, start: float, end: float) -> bool:
        """Check if target degree is between start and end moving counter-clockwise."""
        # Normalize to 0-360 just in case
        t = target % 360
        s = start % 360
        e = end % 360
        
        if s < e:
            # Normal case: 10 to 40
            return s <= t < e
        else:
            # Wrap case: 350 to 20
            return s <= t or t < e
