"""Service for generating chart interpretations."""
from __future__ import annotations

import logging
from typing import List, Optional

from pillars.astrology.models.chart_models import ChartResult, PlanetPosition, HousePosition
from pillars.astrology.models.interpretation_models import InterpretationReport
from pillars.astrology.repositories.interpretation_repository import InterpretationRepository
from pillars.astrology.services.aspects_service import CalculatedAspect

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

    def interpret_chart(self, chart: ChartResult, chart_name: str = "Chart") -> InterpretationReport:
        """Generate a full interpretation report for the given chart."""
        report = InterpretationReport(chart_name=chart_name)

        # 1. Interpret Planets in Signs and Houses
        self._interpret_planets(chart.planet_positions, chart.house_positions, report)

        # 2. Interpret Aspects (if available in raw payload or re-calculated)
        # Note: ChartResult has aspect_summary but we might need CalculatedAspect objects.
        # Ideally, we should receive CalculatedAspects or derive them.
        # For now, we'll assume we can't easily get them from ChartResult.aspect_summary 
        # without parsing. In a real scenario, we might want to inject the AspectService 
        # here or pass the calculated aspects in.
        # TODO: Implement aspect interpretation once we have clean aspect objects.
        
        return report

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
