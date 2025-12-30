"""Chariot system models - The Merkabah of the Soul.

This module defines the data structures for the Chariot Midpoints System,
which maps 21 planetary midpoints to Major Arcana cards, groups them into
7 functional Trios, and calculates Axles and the Chariot Point.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from ..services.maat_symbols_service import MaatSymbol


@dataclass(slots=True)
class ChariotMidpoint:
    """A planetary midpoint mapped to its Major Arcana correspondence.
    
    Attributes:
        id: Unique identifier (e.g., "magus", "priestess")
        name: Major Arcana card name (e.g., "The Magus")
        planet_a: First planet in the midpoint pair
        planet_b: Second planet in the midpoint pair
        longitude: Calculated midpoint position (0-360)
        sign: Zodiac sign the midpoint falls in
        sign_degree: Degree within the sign (0-30)
        trio_id: Which Trio this midpoint belongs to (or None for The Chariot)
        keywords: Symbolic keywords for interpretation
        description: Brief esoteric description
    """
    id: str
    name: str
    planet_a: str
    planet_b: str
    longitude: float
    sign: str
    sign_degree: float
    trio_id: Optional[str]
    keywords: List[str] = field(default_factory=list)
    description: str = ""


@dataclass(slots=True)
class AxlePosition:
    """The mean average of a Trio's three midpoints.
    
    An Axle is the central, load-bearing principle of a Trio,
    representing the core theme that unifies its three components.
    
    Attributes:
        id: Trio identifier (e.g., "vitality", "navigation")
        name: Axle name (e.g., "Axle of Vitality")
        longitude: Mean of the three midpoint longitudes
        sign: Zodiac sign the axle falls in
        sign_degree: Degree within the sign (0-30)
        midpoints: The three ChariotMidpoint objects that compose this axle
        description: The functional meaning of this axle
    """
    id: str
    name: str
    longitude: float
    sign: str
    sign_degree: float
    midpoints: List[ChariotMidpoint]
    description: str = ""


@dataclass(slots=True)
class ChariotPosition:
    """The absolute center of gravity - mean of all 7 Axles.
    
    The Chariot Point represents the ultimate synthesis of all 21
    midpoints into a single point of directed will. It is the soul's
    "magnetic north" and the center of its Merkabah.
    
    Attributes:
        longitude: Mean of all 7 axle longitudes
        sign: Zodiac sign the chariot point falls in
        sign_degree: Degree within the sign (0-30)
        axles: The 7 AxlePosition objects that compose this point
    """
    longitude: float
    sign: str
    sign_degree: float
    axles: List[AxlePosition]


@dataclass
class FatefulDegreePosition:
    """A midpoint or axle that falls on a Fateful Degree.
    
    The three Fateful Degrees (27° Aries, Leo, Sagittarius) are
    points where a natal position is directly connected to the
    Galactic Center, indicating a cosmic destiny.
    
    Attributes:
        degree: The absolute degree (27, 147, or 267)
        name: Fateful degree name (e.g., "The Masterpiece Anointed")
        initiation: Type of initiation (Inception, Personalization, Alignment)
        affected_point: The ChariotMidpoint or AxlePosition at this degree
        orb: How close the point is to the exact degree
    """
    degree: int
    name: str
    initiation: str
    affected_point: ChariotMidpoint | AxlePosition
    orb: float


@dataclass
class ChariotReport:
    """Complete Chariot analysis for a natal chart.
    
    This is the full synthesis of the Chariot system, containing
    all 21 midpoints, 7 axles, the chariot point, and their
    corresponding degree symbols from the Sacred Landscape.
    
    Attributes:
        midpoints: All 21 calculated ChariotMidpoint objects
        axles: All 7 calculated AxlePosition objects
        chariot_point: The ChariotPosition synthesis
        midpoint_symbols: Dict mapping midpoint ID to its MaatSymbol
        axle_symbols: Dict mapping axle ID to its MaatSymbol
        chariot_symbol: The MaatSymbol for the chariot point
        fateful_positions: Any positions on Fateful Degrees
    """
    midpoints: List[ChariotMidpoint]
    axles: List[AxlePosition]
    chariot_point: ChariotPosition
    midpoint_symbols: Dict[str, "MaatSymbol"]
    axle_symbols: Dict[str, "MaatSymbol"]
    chariot_symbol: "MaatSymbol"
    fateful_positions: List[FatefulDegreePosition] = field(default_factory=list)

