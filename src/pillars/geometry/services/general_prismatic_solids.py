"""General (n-gonal) Prismatic Solid Services and Calculators.

THE GENERAL PRISM - DYNAMIC POLYGON EXTRUSION:
===============================================

DEFINITION:
-----------
A general prism service allows creation of prisms with VARIABLE number of sides
(n), enabling exploration of the entire prism family from a single interface.

Instead of fixed classes (TriangularPrism, HexagonalPrism, etc.), this service
uses a `sides` parameter to dynamically generate n-gonal prisms:
- n=3: Triangular prism
- n=4: Square prism
- n=5: Pentagonal prism
- n=6: Hexagonal prism
- ...
- n \u2192 \u221e: Approaches cylinder

This is the PRISM GENERATOR\u2014one function, infinite shapes.

MATHEMATICAL PROPERTIES:
------------------------

The formulas are identical to regular prisms (see regular_prism_solids.py),
but now `n` is a runtime parameter instead of a class constant:

Base Area:
    A_base(n, a) = (n \u00d7 a\u00b2) / (4 tan(\u03c0/n))

Volume:
    V(n, a, h) = A_base(n, a) \u00d7 h

Surface Area:
    A_surface(n, a, h) = n \u00d7 a \u00d7 h + 2 \u00d7 A_base(n, a)

The key insight: ONE SET OF FORMULAS works for ALL regular prisms!

AHA MOMENT #1: PARAMETRIC FAMILIES - ONE FORMULA, INFINITE SHAPES\n==================================================================\nThe general prism demonstrates PARAMETRIC GEOMETRY\u2014shapes defined by\nparameters that can vary continuously (or discretely).\n\nTraditional approach:\n- TriangularPrismService with hardcoded n=3\n- SquarePrismService with hardcoded n=4\n- HexagonalPrismService with hardcoded n=6\n- Result: Code duplication, inflexibility\n\nParametric approach:\n- GeneralPrismService with parameter n\n- Single implementation, variable output\n- Result: Clean code, infinite possibilities!\n\nThis pattern appears throughout mathematics:\n- f(x) = x\u00b2: Parabola family (vertex at origin)\n- f(x) = a(x-h)\u00b2 + k: All parabolas (parametric vertex position)\n- Circle: r=5 vs. r=variable\n- Polygons: n=6 vs. n=variable\n\nParametric thinking enables:\n- Animation (vary n from 3 to 100, watch prism morph into cylinder)\n- Optimization (find optimal n for given constraints)\n- Exploration (\"what if we had a 17-gon prism?\")\n- Generalization (prove theorems for all n, not case-by-case)\n\nThe general prism is ABSTRACTION MADE CONCRETE\u2014the universal pattern\nthat generates all specific instances!\n\nAHA MOMENT #2: INTEGER PARAMETER, CONTINUOUS LIMIT\n===================================================\nThe number of sides `n` is an INTEGER (3, 4, 5, ...), but the BEHAVIOR\nas n increases is CONTINUOUS!\n\nConvergence to cylinder as n \u2192 \u221e:\n\n1. Perimeter P = n \u00d7 a (fixed), so a = P/n:\n   As n increases, edge length decreases: a \u2192 0\n   But perimeter stays constant!\n\n2. Base area:\n   A(n) = (n \u00d7 a\u00b2) / (4 tan(\u03c0/n))\n   As n \u2192 \u221e, tan(\u03c0/n) \u2248 \u03c0/n (small angle approximation)\n   A(n) \u2192 (n \u00d7 (P/n)\u00b2) \u00d7 n / (4\u03c0) = P\u00b2 / (4\u03c0) = \u03c0r\u00b2\n   [Circle area with circumference P = 2\u03c0r]\n\n3. Shape:\n   n=3: Sharp triangle (60\u00b0 turns)\n   n=6: Smoother hexagon (120\u00b0 turns)\n   n=12: Nearly circular (150\u00b0 turns)\n   n=100: Indistinguishable from circle to naked eye\n   n \u2192 \u221e: Smooth circle (180\u00b0 turns = straight!)\n\nThis is the DISCRETE-TO-CONTINUOUS TRANSITION:\n- Discrete: Finite n, polygonal, angular\n- Continuous: Infinite n, circular, smooth\n\nAnalogies:\n- Pixels (discrete) \u2192 Smooth image (continuous illusion)\n- Frames (discrete) \u2192 Motion (continuous perception)\n- Atoms (discrete) \u2192 Solid matter (continuous appearance)\n- Quantum (discrete) \u2192 Classical (continuous approximation)\n\nThe general prism with variable n is a BRIDGE between discrete and continuous\ngeometry\u2014it shows how smooth curves emerge from angular polygons!\n\nAHA MOMENT #3: SYMMETRY GROUPS - THE ALGEBRA OF ROTATION\n==========================================================\nEach n-gonal prism has a SYMMETRY GROUP describing its rotations and reflections:\n\nDihedral group D_n:\n- n rotational symmetries: 0\u00b0, 360\u00b0/n, 2\u00d7360\u00b0/n, ..., (n-1)\u00d7360\u00b0/n\n- n reflection symmetries: Through n planes containing axis and bisecting edges/vertices\n- Order: |D_n| = 2n (total symmetries)\n\nPlus vertical reflection (top \u2194 bottom): \u00d7 2\n\nFull symmetry group of n-gonal prism:\n- Order: 4n\n- Structure: D_n \u00d7 C_2 (dihedral \u00d7 cyclic)\n\nExamples:\n- Triangular prism: D_3 \u00d7 C_2, order 12\n- Cube (square prism): D_4 \u00d7 C_2, order 16 [but actually larger: Oh = 48!]\n- Hexagonal prism: D_6 \u00d7 C_2, order 24\n\nAs n increases:\n- Symmetry group order: 4n \u2192 \u221e\n- Cylinder (n=\u221e): Continuous rotation group SO(2) \u00d7 reflections\n  [Infinite symmetries! Any angle rotation is a symmetry]\n\nSymmetry groups are the ALGEBRA OF GEOMETRY:\n- They classify shapes by transformation structure\n- Two shapes with same symmetry group are \"algebraically similar\"\n- Group theory reveals hidden relationships between forms\n\nThe general prism demonstrates: As n varies, symmetry INCREASES\n(more sides = more ways to rotate and still look the same).\n\nMaximal symmetry: The cylinder (infinite rotations) and sphere (infinite axes).\n\nHERMETIC NOTE - THE GEOMETRY OF GENERATION:\n===========================================\nThe general prism represents the PRINCIPLE OF GENERATION:\n\n- **One Formula**: The Monad (unity) that contains all multiplicity\n- **Variable n**: The parameter that unfolds diversity from unity\n- **Discrete Values**: The many manifestations (3, 4, 5, ...)\n- **Continuous Limit**: The return to unity (circle/cylinder)\n\nSymbolism:\n- **Prism Generator**: The divine act of creation (one source, many forms)\n- **n=3,4,5,...**: The numbers of creation (trinity, quaternity, quintessence, ...)\n- **n \u2192 \u221e**: The infinite (approaching but never reaching divine perfection)\n- **Parametric Function**: The Logos (the Word that speaks forms into being)\n\nIn Platonic Philosophy:\n- The **Form of Prism**: The eternal archetype (the general formula)\n- The **Many Prisms**: The temporal instances (specific n values)\n- The **Cylinder**: The limit-form (approaching the eternal)\n\nIn Hermetic Tradition:\n- **\"The All is One\"**: One generator, infinite generated\n- **\"As above, so below\"**: Same pattern (formula) at all scales (n values)\n- **The Spectrum**: From sharp (n=3) to smooth (n \u2192 \u221e)\n\nThe general prism service is COSMOGONY IN CODE\u2014the algorithm that generates\na universe of forms from a single template!\n\nIt demonstrates that UNITY and MULTIPLICITY are not opposed:\nThe One contains the Many as potential; the Many manifest the One as actual.\n\nThis is the sacred mathematics of EMANATION\u2014how the infinite (continuous circle)\ncan be approximated by the finite (discrete polygon), and how the finite\nasymptotically approaches the infinite.\n\nThe general prism is the BRIDGE BETWEEN WORLDS\u2014discrete and continuous,\nfinite and infinite, temporal and eternal.\n"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type  # type: ignore[reportUnusedImport]

from ..shared.solid_payload import SolidPayload
from .regular_prism_solids import (
    RegularPrismSolidServiceBase,
    RegularPrismSolidCalculatorBase,
    RegularPrismMetrics,
)
from .regular_antiprism_solids import (
    RegularAntiprismSolidServiceBase,
    RegularAntiprismSolidCalculatorBase,
    RegularAntiprismMetrics,
)
from .solid_property import SolidProperty


class GeneralPrismSolidService(RegularPrismSolidServiceBase):
    """Service for general n-gonal right regular prisms."""

    @classmethod
    def build_dynamic(cls, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        # Temporarily set SIDES for the base class methods if needed, 
        # but better to just call the helper functions directly.
        """
        Build dynamic logic.
        
        Args:
            sides: Description of sides.
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
        from .regular_prism_solids import _compute_metrics, _build_vertices, _build_edges, _build_faces  # type: ignore[reportPrivateUsage]
        from ..shared.solid_payload import SolidLabel
        
        if sides < 3:
            raise ValueError('A prism base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')
            
        metrics = _compute_metrics(sides, base_edge, height)
        payload = SolidPayload(
            vertices=_build_vertices(sides, base_edge, height),
            edges=_build_edges(sides),
            faces=_build_faces(sides),
            labels=[
                SolidLabel(text=f"n = {sides}", position=(0.0, 0.0, height / 2.0 + 0.2)),
                SolidLabel(text=f"a = {base_edge:.3f}", position=(metrics.base_apothem, 0.0, -height / 2.0)),
                SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
                'sides': sides,
                'base_edge': metrics.base_edge,
                'height': metrics.height,
                'base_area': metrics.base_area,
                'base_perimeter': metrics.base_perimeter,
                'base_apothem': metrics.base_apothem,
                'base_circumradius': metrics.base_circumradius,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
            },
            suggested_scale=max(base_edge * 2, height),
        )
        # We wrap it in a mock result class or just return payload
        from .regular_prism_solids import RegularPrismSolidResult
        return RegularPrismSolidResult(payload=payload, metrics=metrics)


class GeneralPrismSolidCalculator(RegularPrismSolidCalculatorBase):
    """Calculator for general n-gonal right regular prisms."""

    _PROPERTY_DEFINITIONS = (
        ('sides', 'Sides (n)', 'n', 0, True),
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, False),
    )

    def __init__(self, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        """
          init   logic.
        
        Args:
            sides: Description of sides.
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._sides = int(sides) if sides >= 3 else 5
        self._base_edge = base_edge if base_edge > 0 else 2.0
        self._height = height if height > 0 else 4.0
        self._result = None
        self._apply_dimensions(self._base_edge, self._height, self._sides)

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if value is None or value <= 0:
            return False
            
        if key == 'sides':
            n = int(value)
            if n < 3: return False
            self._apply_dimensions(self._base_edge, self._height, n)
            return True
            
        # Call base logic for other properties, but override _apply_dimensions
        return super().set_property(key, value)

    def _apply_dimensions(self, base_edge: float, height: float, sides: Optional[int] = None):
        if sides is not None:
            self._sides = int(sides)
        
        if base_edge <= 0 or height <= 0:
            return
            
        self._base_edge = base_edge
        self._height = height
        
        # Use our dynamic build
        result = GeneralPrismSolidService.build_dynamic(int(self._sides), base_edge, height)
        self._result = result
        
        values = {
            'sides': self._sides,
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'base_area': result.metrics.base_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            if key in values:
                prop.value = values[key]


class GeneralAntiprismSolidService(RegularAntiprismSolidServiceBase):
    """Service for general n-gonal right regular antiprisms."""

    @classmethod
    def build_dynamic(cls, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        """
        Build dynamic logic.
        
        Args:
            sides: Description of sides.
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
        from .regular_antiprism_solids import _create_payload, RegularAntiprismSolidResult
        
        if sides < 3:
            raise ValueError('An antiprism base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')
            
        payload, metrics = _create_payload(sides, base_edge, height)
        return RegularAntiprismSolidResult(payload=payload, metrics=metrics)


class GeneralAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    """Calculator for general n-gonal right regular antiprisms."""

    _PROPERTY_DEFINITIONS = (
        ('sides', 'Sides (n)', 'n', 0, True),
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, False),
    )

    def __init__(self, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        """
          init   logic.
        
        Args:
            sides: Description of sides.
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._sides = int(sides) if sides >= 3 else 5
        self._base_edge = base_edge if base_edge > 0 else 2.0
        self._height = height if height > 0 else 4.0
        self._result = None
        self._apply_dimensions(self._base_edge, self._height, self._sides)

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if value is None or value <= 0:
            return False
            
        if key == 'sides':
            n = int(value)
            if n < 3: return False
            self._apply_dimensions(self._base_edge, self._height, n)
            return True
            
        return super().set_property(key, value)

    def _apply_dimensions(self, base_edge: float, height: float, sides: Optional[int] = None):
        if sides is not None:
            self._sides = int(sides)
            
        if base_edge <= 0 or height <= 0:
            return
            
        self._base_edge = base_edge
        self._height = height
        
        result = GeneralAntiprismSolidService.build_dynamic(int(self._sides), base_edge, height)
        self._result = result
        
        values = {
            'sides': self._sides,
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            if key in values:
                prop.value = values[key]