"""
Services for calculating Progressions and Directions.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import copy

from ..models.chart_models import AstrologyEvent, ChartResult, PlanetPosition, ChartRequest
from ..repositories.ephemeris_provider import EphemerisProvider
from .openastro_service import OpenAstroService

class ProgressionsService:
    """
    Sovereign Service for calculating Secondary Progressions and Solar Arc Directions.
    """

    def __init__(self, openastro_service: OpenAstroService):
        self._ephemeris = EphemerisProvider.get_instance()
        self._openastro = openastro_service

    def calculate_secondary_progression(self, natal_req: ChartRequest, target_date: datetime) -> ChartResult:
        """
        Calculates Secondary Progressions (1 Day = 1 Year).
        
        Logic:
        1. Calculate Age (Target Date - Natal Date).
        2. Add Age (in days) to Natal Date -> Progressed Date.
        3. Cast chart for Progressed Date.
        """
        natal_dt = natal_req.primary_event.timestamp
        
        # Calculate precise age
        # Ideally: (Target - Natal).days / 365.242199... 
        # But Secondary is simpler: "Day for a Year". 
        # We need the number of solar years passed.
        
        # Naive implementation: 
        # Progression Date = Natal + (Target - Natal) mapped to 1 day/year.
        # Let's be precise:
        # 1 Tropical Year = 1 Mean Solar Day? 
        # Usually: 1 Day after birth corresponds to 1 Year after birth.
        # So: T_prog = T_natal + Age_in_Years * 1_Day
        
        age_delta = target_date - natal_dt
        # Convert total seconds to years (approx)
        age_years = age_delta.total_seconds() / (365.24219 * 24 * 3600)
        
        progressed_delta = timedelta(days=age_years)
        prog_time = natal_dt + progressed_delta
        
        # Create Progressed Event
        # Maintain Natal Location (usually)
        prog_event = AstrologyEvent(
            name=f"Secondary Progressed to {target_date.date()}",
            timestamp=prog_time,
            location=natal_req.primary_event.location,
            # Timezone logic: usually we keep natal timezone offset context 
            # OR we treat it as UTC for calculation then display. 
            # OpenAstro handles it if we pass correct time.
        )
        
        # Generate Chart using standard engine
        prog_req = ChartRequest(
            primary_event=prog_event,
            chart_type="Progressed", # Or Radix if we just want positions
            settings=natal_req.settings
        )
        
        result = self._openastro.generate_chart(prog_req)
        result.chart_type = "Secondary Progression"
        return result

    def calculate_solar_arc(self, natal_req: ChartRequest, target_date: datetime) -> ChartResult:
        """
        Calculates Solar Arc Directions.
        
        Logic:
        1. Calculate Secondary Progressed Sun for target date.
        2. Calculate Arc = (Progressed Sun - Natal Sun).
        3. Add Arc to ALL natal planet positions.
        """
        # 1. Get Natal Chart (for base positions)
        natal_chart = self._openastro.generate_chart(natal_req)
        
        # 2. Get Progressed Chart (to find Sun's arc)
        prog_result = self.calculate_secondary_progression(natal_req, target_date)
        
        # Find Sun positions
        natal_sun = next((p.degree for p in natal_chart.planet_positions if p.name.lower() == 'sun'), None)
        prog_sun = next((p.degree for p in prog_result.planet_positions if p.name.lower() == 'sun'), None)
        
        if natal_sun is None or prog_sun is None:
            raise ValueError("Could not find Sun in charts")
            
        # Calculate Arc
        arc = prog_sun - natal_sun
        if arc < 0: arc += 360
        
        # 3. Apply Arc to all natal points
        directed_positions: List[PlanetPosition] = []
        for p in natal_chart.planet_positions:
            # New lon = old lon + arc
            new_deg = (p.degree + arc) % 360
            directed_positions.append(PlanetPosition(
                name=p.name,
                degree=new_deg,
                sign_index=int(new_deg // 30),
                speed=p.speed,
                declination=p.declination # Declination usually doesn't change in simple Solar Arc? 
                                        # Strict Solar Arc is Longitude only usually.
            ))
            
        # 4. Construct Result
        # Note: House cusps also receive the arc in some systems, or MC is moved and ASC derived.
        # For Phase 2, we simply arc the houses too.
        directed_houses = []
        for h in natal_chart.house_positions:
            new_deg = (h.degree + arc) % 360
            directed_houses.append(copy.replace(h, degree=new_deg))
            
        return ChartResult(
            chart_type="Solar Arc Direction",
            planet_positions=directed_positions,
            house_positions=directed_houses,
            aspect_summary={}, # Needs recalculation if desired
            svg_document=None, # Standard SVG won't generate this synthetic chart easily
            raw_payload={"solar_arc": arc}
        )
