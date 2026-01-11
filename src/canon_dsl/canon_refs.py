"""
Canon DSL — Canon Reference Utilities.

This module provides utilities for working with Canon article references.

Reference: Hermetic Geometry Canon v1.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class CanonRef:
    """
    A reference to a specific Canon article or section.
    
    Examples:
        CanonRef("I", "1")      -> "I.1" (Primacy of Form)
        CanonRef("V", "4.5")    -> "V.4.5" (Direction of Truth)
        CanonRef("XII", "8.1")  -> "XII.8.1" (Closure Invariance Test)
        CanonRef("C", "3")      -> "C.3" (Epsilon Law) [Appendix]
    """
    
    article: str
    section: str = ""
    
    def __str__(self) -> str:
        if self.section:
            return f"{self.article}.{self.section}"
        return self.article
    
    @classmethod
    def parse(cls, ref_str: str) -> CanonRef:
        """Parse a reference string like 'V.4.5' into a CanonRef."""
        parts = ref_str.split(".", 1)
        if len(parts) == 1:
            return cls(article=parts[0])
        return cls(article=parts[0], section=parts[1])


class Canon:
    """
    Constants and utilities for Canon article references.
    
    This class provides canonical identifiers for all articles
    to ensure consistency across the codebase.
    """
    
    # =========================================================================
    # ARTICLE I — ON AXIOMS
    # =========================================================================
    I_PRIMACY_OF_FORM: ClassVar[str] = "I.1"
    I_INVARIANCE_AS_REALITY: ClassVar[str] = "I.2"
    I_CENTER_AS_ANCHOR: ClassVar[str] = "I.3"
    I_CONTINUITY_AS_GROUND: ClassVar[str] = "I.4"
    I_DIMENSION_IS_EXTENSION: ClassVar[str] = "I.5"
    
    # =========================================================================
    # ARTICLE II — ON CANONICAL FORMS
    # =========================================================================
    II_FUNDAMENTAL_FORMS: ClassVar[str] = "II.1"
    II_BOUNDEDNESS_CONTAINMENT: ClassVar[str] = "II.2"
    II_COMPLETION_CLOSURE: ClassVar[str] = "II.3"
    II_DEGENERATE_FORMS: ClassVar[str] = "II.4"
    II_SYMMETRY_CLASSES: ClassVar[str] = "II.5"
    
    # =========================================================================
    # ARTICLE III — ON RELATIONSHIPS AND PROPORTION
    # =========================================================================
    III_PROPORTION_OVER_MAGNITUDE: ClassVar[str] = "III.1"
    III_DIMENSIONAL_ECHO: ClassVar[str] = "III.2"
    III_ROOT_PROGRESSION: ClassVar[str] = "III.3"
    III_TRANSCENDENTAL_CONSTANTS: ClassVar[str] = "III.4"
    
    # =========================================================================
    # ARTICLE IV — ON DIMENSIONAL LADDERS
    # =========================================================================
    IV_LADDER_PRINCIPLE: ClassVar[str] = "IV.1"
    IV_PROJECTION_SECTION: ClassVar[str] = "IV.2"
    IV_COLLAPSE_FORBIDDEN: ClassVar[str] = "IV.3"
    
    # =========================================================================
    # ARTICLE V — ON CONVENTIONS
    # =========================================================================
    V_UNITS_REPRESENTATION: ClassVar[str] = "V.1"
    V_MINIMAL_CANONICAL_FORM: ClassVar[str] = "V.2"
    V_APPROXIMATION_AS_RITUAL: ClassVar[str] = "V.3"
    V_CHIRALITY: ClassVar[str] = "V.4"
    V_CHIRALITY_DEFINITION: ClassVar[str] = "V.4.1"
    V_CHIRALITY_RELATIONAL_STATE: ClassVar[str] = "V.4.2"
    V_REFLECTION_NOT_NEUTRAL: ClassVar[str] = "V.4.3"
    V_CHIRALITY_AND_CENTER: ClassVar[str] = "V.4.4"
    V_DIRECTION_OF_TRUTH: ClassVar[str] = "V.4.5"
    V_CHIRALITY_DIMENSIONAL_STATUS: ClassVar[str] = "V.4.6"
    V_CHIRALITY_SYMBOLIC: ClassVar[str] = "V.4.7"
    
    # =========================================================================
    # ARTICLE VI — ON VOID AND REMAINDER
    # =========================================================================
    VI_VOID_IS_STRUCTURAL: ClassVar[str] = "VI.1"
    VI_MONOTONICITY_OF_REMOVAL: ClassVar[str] = "VI.2"
    VI_VOID_HAS_DIMENSIONALITY: ClassVar[str] = "VI.3"
    VI_VOID_RATIOS_CANONICAL: ClassVar[str] = "VI.4"
    
    # =========================================================================
    # ARTICLE VII — ON SYMBOL AND MEANING
    # =========================================================================
    VII_MEANING_FOLLOWS_STRUCTURE: ClassVar[str] = "VII.1"
    VII_ARCHETYPAL_STABILITY: ClassVar[str] = "VII.2"
    VII_NAMING_IS_BINDING: ClassVar[str] = "VII.3"
    
    # =========================================================================
    # ARTICLE VIII — ON FORBIDDEN MOVES
    # =========================================================================
    VIII_FORBIDDEN_MOVES: ClassVar[str] = "VIII"
    
    # =========================================================================
    # ARTICLE IX — ON CANONICAL TESTS
    # =========================================================================
    IX_PROPORTIONAL_RECOVERY: ClassVar[str] = "IX.1"
    IX_DIMENSIONAL_CONSISTENCY: ClassVar[str] = "IX.2"
    IX_VOID_MONOTONICITY: ClassVar[str] = "IX.3"
    IX_SCALING_INVARIANCE: ClassVar[str] = "IX.4"
    IX_LIMIT_BEHAVIOR: ClassVar[str] = "IX.5"
    IX_RECURSIVE_STABILITY: ClassVar[str] = "IX.6"
    IX_CURVATURE_INVARIANCE: ClassVar[str] = "IX.7"
    
    # =========================================================================
    # ARTICLE X — ON IMPLEMENTATION SUBORDINATION
    # =========================================================================
    X_CODE_IS_INSTRUMENT: ClassVar[str] = "X.1"
    X_AI_AS_MASON: ClassVar[str] = "X.2"
    X_CANON_EVOLVES: ClassVar[str] = "X.3"
    
    # =========================================================================
    # ARTICLE XI — CANONICAL DEFINITIONS
    # =========================================================================
    XI_DEFINITIONS: ClassVar[str] = "XI"
    
    # =========================================================================
    # ARTICLE XII — ON TIME, MOTION, AND TRAJECTORY
    # =========================================================================
    XII_MOTION_REVEALS: ClassVar[str] = "XII.1"
    XII_STATIC_VS_TRACED: ClassVar[str] = "XII.2"
    XII_TIME_AS_PARAMETER: ClassVar[str] = "XII.3"
    XII_CYCLIC_MOTION: ClassVar[str] = "XII.4"
    XII_INSTANTANEOUS_VS_PATH: ClassVar[str] = "XII.5"
    XII_TEMPORAL_SCOPE: ClassVar[str] = "XII.6"
    XII_TRACED_EXAMPLES: ClassVar[str] = "XII.7"
    XII_TRACED_TESTS: ClassVar[str] = "XII.8"
    XII_CLOSURE_INVARIANCE_TEST: ClassVar[str] = "XII.8.1"
    XII_PERIOD_RATIO_TEST: ClassVar[str] = "XII.8.2"
    XII_SYMMETRY_EMERGENCE_TEST: ClassVar[str] = "XII.8.3"
    XII_CYCLIC_VOID: ClassVar[str] = "XII.9"
    
    # =========================================================================
    # ARTICLE XIII — ON SELF-SIMILARITY AND RECURSIVE FORM
    # =========================================================================
    XIII_SELF_SIMILARITY: ClassVar[str] = "XIII.1"
    XIII_RECURSIVE_FORM: ClassVar[str] = "XIII.2"
    XIII_NON_INTEGER_DIMENSION: ClassVar[str] = "XIII.3"
    XIII_FRACTALS: ClassVar[str] = "XIII.4"
    XIII_VS_SYMBOLIC: ClassVar[str] = "XIII.5"
    XIII_TRUNCATION: ClassVar[str] = "XIII.6"
    XIII_DIMENSIONAL_LADDERS: ClassVar[str] = "XIII.7"
    
    # =========================================================================
    # ARTICLE XIV — ON CURVATURE AND INTRINSIC GEOMETRY
    # =========================================================================
    XIV_CURVATURE_DEFINITION: ClassVar[str] = "XIV.1"
    XIV_INTRINSIC_VS_EXTRINSIC: ClassVar[str] = "XIV.2"
    XIV_CANONICAL_CURVED_FORMS: ClassVar[str] = "XIV.3"
    XIV_GEODESICS: ClassVar[str] = "XIV.4"
    XIV_CURVATURE_DIMENSIONS: ClassVar[str] = "XIV.5"
    XIV_CURVATURE_TRACED: ClassVar[str] = "XIV.6"
    XIV_FORBIDDEN_CURVATURE: ClassVar[str] = "XIV.7"
    
    # =========================================================================
    # APPENDIX C — IMPLEMENTATION LAW
    # =========================================================================
    C_PURPOSE: ClassVar[str] = "C.1"
    C_APPROXIMATION: ClassVar[str] = "C.2"
    C_EPSILON_LAW: ClassVar[str] = "C.3"
    C_ABSOLUTE_VS_RELATIVE: ClassVar[str] = "C.4"
    C_ACCUMULATION_DRIFT: ClassVar[str] = "C.5"
    C_DISCRETE_REPRESENTATIONS: ClassVar[str] = "C.6"
    C_CANONICAL_SUPREMACY: ClassVar[str] = "C.7"


# Convenience: list of all orientation-sensitive form kinds
ORIENTATION_SENSITIVE_FORMS: set[str] = {
    "Spiral",
    "Helix",
    "OrbitTrace",
    "VenusRose",
    "Lissajous",
    "Epicycloid",
    "Cardioid",
}

# Convenience: list of all curved form kinds
CURVED_FORMS: set[str] = {
    "Circle",
    "Sphere",
    "Ellipse",
    "Ellipsoid",
    "Spiral",
    "Helix",
    "Cardioid",
    "Epicycloid",
    "Lissajous",
    "Torus",
}

# Convenience: list of all recursive form kinds
RECURSIVE_FORMS: set[str] = {
    "SierpinskiTriangle",
    "SierpinskiCarpet",
    "KochSnowflake",
    "MengerSponge",
    "FractalTree",
    "RecursiveForm",
}
