"""
Services for Relationship Astrology (Synastry & Composite).
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional

from ..models.chart_models import ChartResult, PlanetPosition, HousePosition
from .aspects_service import AspectsService, CalculatedAspect

class SynastryService:
    """
    Sovereign Service for calculating interactions between two charts.
    """
    
    def __init__(self, aspects_service: AspectsService):
        self._aspects_service = aspects_service

    def calculate_synastry(
        self, 
        chart_a: ChartResult, 
        chart_b: ChartResult,
        orb_factor: float = 1.0
    ) -> List[CalculatedAspect]:
        """
        Calculate aspects between Chart A planets and Chart B planets.
        """
        # Map Planet -> Longitude
        pos_a = {p.name: p.degree for p in chart_a.planet_positions}
        pos_b = {p.name: p.degree for p in chart_b.planet_positions}
        
        cross_aspects = []
        
        # We need a modified aspect logic: check A(i) vs B(j)
        definitions = self._aspects_service.get_aspect_definitions(include_minor=False) # Configurable?
        
        for name_a, lon_a in pos_a.items():
            for name_b, lon_b in pos_b.items():
                for aspect_def in definitions:
                    orb = self._check_aspect(lon_a, lon_b, aspect_def.angle, aspect_def.default_orb * orb_factor)
                    if orb is not None:
                        # Applying check is tricky without time.
                        # For Synastry usually just "Orb" matters.
                        cross_aspects.append(CalculatedAspect(
                            planet_a=f"A: {name_a}",
                            planet_b=f"B: {name_b}",
                            aspect=aspect_def,
                            orb=orb,
                            is_applying=False # Unknown without temporal context of both keys
                        ))
        
        cross_aspects.sort(key=lambda x: x.orb)
        return cross_aspects

    def calculate_composite(self, chart_a: ChartResult, chart_b: ChartResult) -> ChartResult:
        """
        Calculate Composite Chart (Midpoints Strategy).
        Midpoint = (PosA + PosB) / 2.
        Shortest arc logic applies.
        """
        composite_planets = []
        
        # Match planets by name
        map_a = {p.name: p for p in chart_a.planet_positions}
        map_b = {p.name: p for p in chart_b.planet_positions}
        
        common_names = set(map_a.keys()) & set(map_b.keys())
        
        for name in common_names:
            p_a = map_a[name]
            p_b = map_b[name]
            
            mid = self._calculate_midpoint(p_a.degree, p_b.degree)
            
            composite_planets.append(PlanetPosition(
                name=name,
                degree=mid,
                sign_index=int(mid // 30)
            ))
            
        # Houses Midpoints (Requires both charts to have same system ideally)
        composite_houses = []
        if len(chart_a.house_positions) == len(chart_b.house_positions):
            for i in range(len(chart_a.house_positions)):
                h_a = chart_a.house_positions[i]
                h_b = chart_b.house_positions[i]
                
                mid = self._calculate_midpoint(h_a.degree, h_b.degree)
                composite_houses.append(HousePosition(number=h_a.number, degree=mid))
                
        return ChartResult(
            chart_type="Composite (Midpoint)",
            planet_positions=composite_planets,
            house_positions=composite_houses,
            aspect_summary={}, 
            svg_document=None
        )

    def _calculate_midpoint(self, a: float, b: float) -> float:
        """Calculate midpoint via shortest arc."""
        diff = abs(a - b)
        if diff > 180:
            # Crosses 0/360 boundary
            # e.g. 350 and 10. Mid is 0.
            # (350+10+360)/2 = 360 -> 0
            mid = (a + b + 360) / 2
        else:
            mid = (a + b) / 2
            
        return mid % 360
        
    def _check_aspect(self, lon_a: float, lon_b: float, target_angle: float, max_orb: float) -> Optional[float]:
        # Duplicate logic from AspectsService unfortunately unless we make it public utility.
        # Ideally AspectsService exposes a 'check_pair' method.
        # But for now, simple duplication for Sovereignty or use AspectsService instance.
        # Actually, let's use the instance method if possible, but the current AspectsService 
        # API is `calculate_aspects` which does N*N internal. 
        # I'll replicate the math here for speed/simplicity in this Phase.
        diff = abs(lon_a - lon_b)
        if diff > 180:
            diff = 360 - diff
        orb = abs(diff - target_angle)
        if orb <= max_orb:
            return round(orb, 2)
        return None
