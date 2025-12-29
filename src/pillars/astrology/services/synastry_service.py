"""
Synastry Service — The Muscle of Relationship Astrology.

Sovereign Service for calculating Synastry, Composite, and Davison charts.
This service owns all relationship chart calculation logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from ..models.chart_models import (
    AstrologyEvent, ChartRequest, ChartResult, GeoLocation,
    PlanetPosition, HousePosition
)
from .openastro_service import OpenAstroService


def calculate_midpoint(deg_a: float, deg_b: float) -> float:
    """
    Calculate the midpoint between two degrees on a circle.
    
    This is the core algorithm for Composite chart positions.
    Returns the shorter-arc midpoint between two zodiacal degrees.
    """
    a = deg_a % 360
    b = deg_b % 360
    
    mid1 = (a + b) / 2
    mid2 = mid1 + 180 if mid1 < 180 else mid1 - 180
    
    # If input degrees are more than 180 apart, use the opposite midpoint
    if abs(a - b) > 180:
        return mid2 % 360
    return mid1 % 360


@dataclass(slots=True)
class DavisonInfo:
    """Information about the Davison chart midpoint calculation."""
    midpoint_time: datetime
    midpoint_latitude: float
    midpoint_longitude: float


@dataclass(slots=True)
class CompositeResult:
    """Result of a Composite chart calculation."""
    planets: List[PlanetPosition]
    houses: List[HousePosition]
    julian_day: Optional[float] = None


@dataclass(slots=True)
class DavisonResult:
    """Result of a Davison chart calculation."""
    chart: ChartResult
    info: DavisonInfo


class SynastryService:
    """
    Sovereign Service for relationship chart calculations.
    
    The Three Modes:
    - Synastry: Bi-wheel comparison (no calculation, just two charts)
    - Composite: Midpoints of corresponding planetary positions
    - Davison: Chart cast for the time/space midpoint
    """
    
    def __init__(self, openastro_service: OpenAstroService):
        self._openastro = openastro_service
    
    def generate_chart(self, event: AstrologyEvent) -> ChartResult:
        """Generate a single radix chart."""
        req = ChartRequest(event, chart_type="Radix")
        return self._openastro.generate_chart(req)
    
    def calculate_composite(
        self,
        result_a: ChartResult,
        result_b: ChartResult
    ) -> CompositeResult:
        """
        Calculate a Composite chart from two existing chart results.
        
        The Composite is the midpoint of corresponding planetary positions.
        This creates a synthetic chart that does not correspond to any
        real moment in time, but represents the relationship's essence.
        """
        composite_planets: List[PlanetPosition] = []
        
        lookup_a = {p.name.lower(): p for p in result_a.planet_positions}
        lookup_b = {p.name.lower(): p for p in result_b.planet_positions}
        
        for name, pa in lookup_a.items():
            if name in lookup_b:
                mid_deg = calculate_midpoint(pa.degree, lookup_b[name].degree)
                composite_planets.append(PlanetPosition(
                    name=pa.name,
                    degree=mid_deg,
                    sign_index=int(mid_deg / 30) % 12
                ))
        
        # Midpoint houses
        composite_houses: List[HousePosition] = []
        house_a = {h.number: h for h in result_a.house_positions}
        house_b = {h.number: h for h in result_b.house_positions}
        
        for i in range(1, 13):
            if i in house_a and i in house_b:
                mid_deg = calculate_midpoint(house_a[i].degree, house_b[i].degree)
                composite_houses.append(HousePosition(number=i, degree=mid_deg))
        
        # Calculate approximate mean JD for fixed stars reference
        mean_jd = None
        if result_a.julian_day and result_b.julian_day:
            mean_jd = (result_a.julian_day + result_b.julian_day) / 2
        
        return CompositeResult(
            planets=composite_planets, 
            houses=composite_houses,
            julian_day=mean_jd
        )
    
    def calculate_davison(
        self,
        event_a: AstrologyEvent,
        event_b: AstrologyEvent
    ) -> DavisonResult:
        """
        Calculate a Davison Relationship Chart.
        
        The Davison chart is cast for the exact midpoint in both time
        and space between two people. Unlike the Composite, this is
        a real chart for a real moment and location.
        """
        # Time midpoint
        ts_a = event_a.timestamp
        if ts_a.tzinfo is None:
            ts_a = ts_a.replace(tzinfo=timezone.utc)
        
        ts_b = event_b.timestamp
        if ts_b.tzinfo is None:
            ts_b = ts_b.replace(tzinfo=timezone.utc)
        
        mid_timestamp = ts_a + (ts_b - ts_a) / 2
        
        # Location midpoint
        mid_lat = (event_a.location.latitude + event_b.location.latitude) / 2
        mid_lon = (event_a.location.longitude + event_b.location.longitude) / 2
        mid_loc = GeoLocation("Davison Midpoint", mid_lat, mid_lon)
        
        # Cast chart for midpoint time/space
        davison_event = AstrologyEvent(
            name="Davison Relationship Chart",
            timestamp=mid_timestamp,
            location=mid_loc
        )
        
        davison_chart = self.generate_chart(davison_event)
        
        info = DavisonInfo(
            midpoint_time=mid_timestamp,
            midpoint_latitude=mid_lat,
            midpoint_longitude=mid_lon
        )
        
        return DavisonResult(chart=davison_chart, info=info)
