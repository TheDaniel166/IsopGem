"""
Data models for Quadset Analysis.
Used to transport calculation results between the engine and the UI.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class QuadsetMember:
    """Represents a single number within the Quadset (e.g., Original, Conrune)."""
    name: str
    decimal: int
    ternary: str
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuadsetResult:
    """Complete result set of a Quadset Analysis."""
    # Core Members
    original: QuadsetMember
    conrune: QuadsetMember
    reversal: QuadsetMember
    conrune_reversal: QuadsetMember
    
    # Differentials & Septad
    upper_diff: QuadsetMember
    lower_diff: QuadsetMember
    transgram: QuadsetMember
    
    # Aggregates
    quadset_sum: int
    septad_total: int
    
    # Analysis
    pattern_summary: str
    
    @property
    def members(self) -> List[QuadsetMember]:
        """Return the four main members as a list."""
        return [self.original, self.conrune, self.reversal, self.conrune_reversal]
