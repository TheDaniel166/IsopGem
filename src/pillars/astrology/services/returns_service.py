"""
Services for calculating Planetary Returns (Solar/Lunar Return Charts).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import math
from typing import Optional, Tuple

from ..models.chart_models import AstrologyEvent, ChartRequest, GeoLocation, ensure_tzinfo
from shared.services.ephemeris_provider import EphemerisProvider

class ReturnsService:
    """
    Sovereign Service for calculating the exact moment a planet returns 
    to its natal longitude (e.g. Solar Return, Lunar Return).
    
    Uses EphemerisProvider for high-precision iterative solving.
    """

    def __init__(self):
        self._ephemeris = EphemerisProvider.get_instance()

    def calculate_return(
        self,
        natal_event: AstrologyEvent,
        target_year: int,
        body_name: str = "sun",
        return_count: int = 1
    ) -> AstrologyEvent:
        """
        Calculate the exact return time for a body.
        
        Args:
            natal_event: The birth/root event.
            target_year: The year to find the return in.
            body_name: 'sun', 'moon', etc.
            return_count: For fast movers like Moon, which return to calculate (1-13).
                          For Sun, this is ignored (always 1 per year).
        
        Returns:
            AstrologyEvent: The precise moment of the return.
        """
        # 1. Get exact Natal Longitude
        natal_dt = ensure_tzinfo(natal_event.timestamp, natal_event.timezone_offset)
        natal_lon = self._ephemeris.get_geocentric_ecliptic_position(
            body_name,
            natal_dt,
        )
        
        # 2. Estimate start time
        # For Solar Return: Same Day/Month, Target Year
        # For Lunar Return: Approximate cycle is 27.32 days.
        estimate_dt = self._estimate_start_time(natal_dt, target_year, body_name, return_count)
        
        # 3. Solve for exact time (Tbs = Time of Exactitude)
        exact_time = self._solve_exact_time(body_name, natal_lon, estimate_dt)
        
        return AstrologyEvent(
            name=f"{body_name.title()} Return {target_year}",
            timestamp=exact_time,
            location=natal_event.location, # Usually relocated, but defaults to natal for calculation base
            timezone_offset=natal_event.timezone_offset,
        )

    def _estimate_start_time(self, natal_dt: datetime, target_year: int, body_name: str, count: int) -> datetime:
        """Provide a rough starting point for the solver."""
        if body_name.lower() == "sun":
            # Solar Return is roughly same calendar day
            try:
                return natal_dt.replace(year=target_year)
            except ValueError:
                # Handle leap year Feb 29 -> Feb 28 or Mar 1
                return natal_dt.replace(year=target_year, day=28, month=2)
                
        elif body_name.lower() == "moon":
             # Lunar Return roughly every 27.32 days
             # We need to find the Nth return after start of target year?
             # Or simply close to the target date.
             # Typically user wants "Lunar Return for [Month]"
             # For Phase 2, we'll implement a simple "Start search from Jan 1" logic or relative to natal.
             # Let's assume target_year implies "First return of that year" if count=1?
             # Better: 'count' iterations from the natal date? 
             # Let's pivot: simplest is "Return closest to Date X".
             # For now, let's implement Solar Return logic primarily and simple Lunar logic.
             
             start_of_year = datetime(target_year, 1, 1, tzinfo=timezone.utc)
             # Rough estimate
             return start_of_year
             
        return natal_dt.replace(year=target_year)

    def _solve_exact_time(self, body_name: str, target_lon: float, start_estimate: datetime) -> datetime:
        """
        Newton-Raphson / Secant solver to find T where Pos(T) = Target.
        """
        t = start_estimate
        
        # Max iterations
        for _ in range(20):
            current_lon = self._ephemeris.get_geocentric_ecliptic_position(body_name, t)
            
            diff = self._shortest_distance(current_lon, target_lon)
            
            if abs(diff) < 0.0001: # Precision: ~0.36 seconds of arc
                return t
                
            # Calculate speed (deg/day) to estimate delta
            # We assume speed is roughly constant in short window
            # Sun ~1 deg/day, Moon ~13 deg/day
            extended = self._ephemeris.get_extended_data(body_name, t)
            speed = extended.get("geo_speed", 0) 
            # Or use helio_speed if geo not avail, but geo usually is calculated in extended
            
            if speed == 0:
                # Fallback estimate
                speed = 1.0 if body_name == 'sun' else 13.0
            
            # Delta T (days) = -Diff / Speed
            # If we are at 10deg, want 11deg (Diff = -1), Speed = 1
            # dt = -(-1)/1 = +1 day.
            
            # Note: _shortest_distance(curr, target) returns (curr - target)
            # e.g. 10 - 11 = -1. 
            # We want to reduce diff to 0. 
            # next_t = t - (diff / speed)
            
            days_delta = diff / speed
            t = t - timedelta(days=days_delta)
            
        return t

    def _shortest_distance(self, a: float, b: float) -> float:
        """Return shortest distance from a to b on circle."""
        d = a - b
        if d > 180: d -= 360
        if d < -180: d += 360
        return d
