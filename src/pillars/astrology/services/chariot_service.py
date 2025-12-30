"""Chariot Service - The Merkabah Engine.

This service calculates the Chariot Midpoints System from a natal chart,
synthesizing planetary midpoints into Major Arcana correspondences,
grouping them into functional Trios, deriving Axles of Will, and
computing the ultimate Chariot Point.

It builds upon:
- MidpointsService: For raw midpoint calculation
- MaatSymbolsService: For degree symbol lookup (360 Egyptian symbols)
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.chariot_models import (
    AxlePosition,
    ChariotMidpoint,
    ChariotPosition,
    ChariotReport,
    FatefulDegreePosition,
)
from ..models.chart_models import ChartResult
from .maat_symbols_service import MaatSymbol, MaatSymbolsService
from .midpoints_service import MidpointsService

# Zodiac signs for degree-to-sign conversion
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


class ChariotService:
    """The Merkabah Engine - calculates the Chariot system from a natal chart.
    
    This service synthesizes:
    - 21 Midpoints mapped to Major Arcana cards
    - 7 Trios (functional groupings of 3 midpoints each)
    - 7 Axles (mean of each Trio's midpoints)
    - The Chariot Point (mean of all Axles)
    - Fateful Degree detection (27° Aries/Leo/Sagittarius)
    - Degree symbol lookup for all positions
    """
    
    # Fateful degrees (Galactic Center alignment)
    FATEFUL_DEGREES = {27, 147, 267}
    FATEFUL_ORB = 2.0  # Degrees
    
    def __init__(self):
        """Initialize the Chariot service with required dependencies."""
        self.midpoints_service = MidpointsService()
        self.maat_service = MaatSymbolsService()
        self._definitions: Optional[Dict] = None
        self._load_definitions()
    
    def _load_definitions(self) -> None:
        """Load midpoint and trio definitions from JSON."""
        data_path = Path(__file__).parent.parent / "data" / "chariot" / "chariot_definitions.json"
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                self._definitions = json.load(f)
        else:
            raise FileNotFoundError(f"Chariot definitions not found at {data_path}")
    
    def _degree_to_sign(self, longitude: float) -> Tuple[str, float]:
        """Convert absolute longitude to sign name and degree within sign.
        
        Args:
            longitude: Absolute degree (0-360)
            
        Returns:
            Tuple of (sign_name, degree_within_sign)
        """
        longitude = longitude % 360
        sign_index = int(longitude // 30)
        sign_degree = longitude % 30
        return ZODIAC_SIGNS[sign_index], sign_degree
    
    def _calculate_mean_longitude(self, longitudes: List[float]) -> float:
        """Calculate the mean of multiple longitudes, handling 360° wraparound.
        
        Uses circular mean (vector averaging) to correctly handle
        positions that span the 0°/360° boundary.
        
        Args:
            longitudes: List of absolute degrees (0-360)
            
        Returns:
            Mean longitude (0-360)
        """
        if not longitudes:
            return 0.0
        
        # Convert to radians and compute circular mean
        sin_sum = sum(math.sin(math.radians(lon)) for lon in longitudes)
        cos_sum = sum(math.cos(math.radians(lon)) for lon in longitudes)
        
        mean_radians = math.atan2(sin_sum, cos_sum)
        mean_degrees = math.degrees(mean_radians)
        
        # Normalize to 0-360
        return mean_degrees % 360
    
    def get_chariot_midpoints(
        self, 
        planet_positions: Dict[str, float]
    ) -> List[ChariotMidpoint]:
        """Calculate the 21 Chariot midpoints from planetary positions.
        
        Uses the existing MidpointsService for raw calculation,
        then enriches with Major Arcana correspondences.
        
        Args:
            planet_positions: Dict mapping planet name to ecliptic longitude
            
        Returns:
            List of 21 ChariotMidpoint objects with Tarot mapping
        """
        # Get raw midpoints from existing service
        raw_midpoints = self.midpoints_service.calculate_midpoints(
            planet_positions, 
            classic_only=False  # Need Uranus for some cards
        )
        
        # Create lookup by planet pair
        raw_lookup: Dict[frozenset, float] = {}
        for mp in raw_midpoints:
            key = frozenset({mp.planet_a, mp.planet_b})
            raw_lookup[key] = mp.longitude
        
        # Map to Chariot midpoints using definitions
        chariot_midpoints = []
        for defn in self._definitions.get("midpoints", []):
            pair_key = frozenset({defn["planet_a"], defn["planet_b"]})
            
            # Find the calculated longitude for this pair
            longitude = raw_lookup.get(pair_key)
            if longitude is None:
                # Try to calculate directly if planets available
                lon_a = planet_positions.get(defn["planet_a"])
                lon_b = planet_positions.get(defn["planet_b"])
                if lon_a is not None and lon_b is not None:
                    longitude = self.midpoints_service._calculate_midpoint(lon_a, lon_b)
                else:
                    continue  # Skip if planets not available
            
            sign, sign_degree = self._degree_to_sign(longitude)
            
            chariot_midpoints.append(ChariotMidpoint(
                id=defn["id"],
                name=defn["name"],
                planet_a=defn["planet_a"],
                planet_b=defn["planet_b"],
                longitude=longitude,
                sign=sign,
                sign_degree=sign_degree,
                trio_id=defn.get("trio"),
                keywords=defn.get("keywords", []),
                description=defn.get("description", ""),
            ))
        
        return chariot_midpoints
    
    def calculate_axles(
        self, 
        midpoints: List[ChariotMidpoint]
    ) -> List[AxlePosition]:
        """Calculate the 7 Axles from the Chariot midpoints.
        
        Each Axle is the mean average of its Trio's three midpoints.
        
        Args:
            midpoints: List of 21 ChariotMidpoint objects
            
        Returns:
            List of 7 AxlePosition objects
        """
        # Group midpoints by trio
        trio_groups: Dict[str, List[ChariotMidpoint]] = {}
        for mp in midpoints:
            if mp.trio_id:
                if mp.trio_id not in trio_groups:
                    trio_groups[mp.trio_id] = []
                trio_groups[mp.trio_id].append(mp)
        
        # Calculate each axle
        axles = []
        for trio_def in self._definitions.get("trios", []):
            trio_id = trio_def["id"]
            trio_midpoints = trio_groups.get(trio_id, [])
            
            if len(trio_midpoints) != 3:
                continue  # Skip incomplete trios
            
            # Calculate mean longitude
            longitudes = [mp.longitude for mp in trio_midpoints]
            mean_lon = self._calculate_mean_longitude(longitudes)
            sign, sign_degree = self._degree_to_sign(mean_lon)
            
            axles.append(AxlePosition(
                id=trio_id,
                name=trio_def["axle_name"],
                longitude=mean_lon,
                sign=sign,
                sign_degree=sign_degree,
                midpoints=trio_midpoints,
                description=trio_def.get("description", ""),
            ))
        
        return axles
    
    def calculate_chariot_point(
        self, 
        axles: List[AxlePosition]
    ) -> ChariotPosition:
        """Calculate the Chariot Point - the mean of all 7 Axles.
        
        This is the absolute center of gravity of the soul's will,
        the magnetic north of the Merkabah.
        
        Args:
            axles: List of 7 AxlePosition objects
            
        Returns:
            ChariotPosition representing the ultimate synthesis
        """
        longitudes = [ax.longitude for ax in axles]
        mean_lon = self._calculate_mean_longitude(longitudes)
        sign, sign_degree = self._degree_to_sign(mean_lon)
        
        return ChariotPosition(
            longitude=mean_lon,
            sign=sign,
            sign_degree=sign_degree,
            axles=axles,
        )
    
    def detect_fateful_positions(
        self,
        midpoints: List[ChariotMidpoint],
        axles: List[AxlePosition],
        chariot_point: ChariotPosition,
    ) -> List[FatefulDegreePosition]:
        """Detect any positions on the three Fateful Degrees.
        
        The Fateful Degrees (27° Aries, Leo, Sagittarius) indicate
        direct connection to the Galactic Center.
        
        Args:
            midpoints: All 21 ChariotMidpoint objects
            axles: All 7 AxlePosition objects
            chariot_point: The ChariotPosition
            
        Returns:
            List of FatefulDegreePosition objects for any matches
        """
        fateful_info = self._definitions.get("fateful_degrees", {})
        results = []
        
        # Check all positions against fateful degrees
        all_positions = [
            *[(mp, mp.longitude) for mp in midpoints],
            *[(ax, ax.longitude) for ax in axles],
        ]
        
        for position, longitude in all_positions:
            abs_degree = int(longitude) % 360
            
            for fateful_deg in self.FATEFUL_DEGREES:
                orb = min(
                    abs(longitude - fateful_deg),
                    360 - abs(longitude - fateful_deg)
                )
                
                if orb <= self.FATEFUL_ORB:
                    info = fateful_info.get(str(fateful_deg), {})
                    results.append(FatefulDegreePosition(
                        degree=fateful_deg,
                        name=info.get("name", f"Fateful Degree {fateful_deg}°"),
                        initiation=info.get("initiation", "Unknown"),
                        affected_point=position,
                        orb=orb,
                    ))
        
        return results
    
    def generate_chariot_report(self, chart: ChartResult) -> ChariotReport:
        """Generate a complete Chariot analysis from a natal chart.
        
        This is the main entry point that synthesizes everything:
        midpoints, axles, chariot point, degree symbols, and fateful degrees.
        
        Args:
            chart: A calculated ChartResult from the astrology service
            
        Returns:
            Complete ChariotReport with all analysis
        """
        # Extract planet positions
        planet_positions = {p.name: p.degree for p in chart.planet_positions}
        
        # Calculate the Chariot structure
        midpoints = self.get_chariot_midpoints(planet_positions)
        axles = self.calculate_axles(midpoints)
        chariot_point = self.calculate_chariot_point(axles)
        
        # Get degree symbols for all positions
        midpoint_symbols = {
            mp.id: self.maat_service.get_symbol(mp.longitude)
            for mp in midpoints
        }
        axle_symbols = {
            ax.id: self.maat_service.get_symbol(ax.longitude)
            for ax in axles
        }
        chariot_symbol = self.maat_service.get_symbol(chariot_point.longitude)
        
        # Detect fateful positions
        fateful_positions = self.detect_fateful_positions(
            midpoints, axles, chariot_point
        )
        
        return ChariotReport(
            midpoints=midpoints,
            axles=axles,
            chariot_point=chariot_point,
            midpoint_symbols=midpoint_symbols,
            axle_symbols=axle_symbols,
            chariot_symbol=chariot_symbol,
            fateful_positions=fateful_positions,
        )
    
    def generate_from_positions(
        self, 
        planet_positions: Dict[str, float]
    ) -> ChariotReport:
        """Generate a Chariot report directly from planet positions.
        
        Convenience method when you have raw positions instead of a ChartResult.
        
        Args:
            planet_positions: Dict mapping planet name to ecliptic longitude
            
        Returns:
            Complete ChariotReport
        """
        # Build a minimal ChartResult-like structure
        from ..models.chart_models import PlanetPosition
        
        class MinimalChart:
            def __init__(self, positions: Dict[str, float]):
                self.planet_positions = [
                    PlanetPosition(name=name, degree=degree)
                    for name, degree in positions.items()
                ]
        
        return self.generate_chariot_report(MinimalChart(planet_positions))
