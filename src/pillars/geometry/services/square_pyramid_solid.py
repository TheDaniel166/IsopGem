"""Square pyramid solid math utilities and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty


@dataclass(frozen=True)
class SquarePyramidMetrics:
    """
    Square Pyramid Metrics class definition.
    
    """
    base_edge: float
    height: float
    slant_height: float
    base_apothem: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float
    lateral_edge: float


@dataclass(frozen=True)
class SquarePyramidSolidResult:
    """
    Square Pyramid Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: SquarePyramidMetrics


def _compute_metrics(base_edge: float, height: float) -> SquarePyramidMetrics:
    """
    Calculate metrics for a right square pyramid.
    
    THE SQUARE PYRAMID - THE ICONIC PYRAMID:
    =========================================
    
    DEFINITION:
    -----------
    The square pyramid is THE pyramid\u2014the archetypal form with square base
    and four congruent isosceles triangular faces meeting at an apex.
    
    This is the shape of the Egyptian pyramids (Giza, Saqqara, etc.), the
    most recognizable pyramid form in human culture.
    
    Components:
    - 1 square base (all sides = a, all angles = 90\u00b0)
    - 4 congruent isosceles triangular lateral faces
    - 1 apex vertex
    - 5 vertices (4 base corners + 1 apex)
    - 8 edges (4 base + 4 lateral)
    - 5 faces (1 square + 4 triangles)
    
    ESSENTIAL FORMULAS:
    -------------------
    
    Base Area:
        A_base = a\u00b2
    
    Volume:
        V = (1/3) \u00d7 a\u00b2 \u00d7 h
    
    Slant Height (perpendicular from apex to base edge midpoint):
        s = \u221a(h\u00b2 + (a/2)\u00b2)
        
        Pythagorean theorem: vertical leg h, horizontal leg a/2 (half edge)
    
    Lateral Surface Area:
        A_lateral = 4 \u00d7 (\u00bd \u00d7 a \u00d7 s) = 2 \u00d7 a \u00d7 s
        
        Four congruent triangles, each with base a and height s
    
    Total Surface Area:
        A_total = a\u00b2 + 2as
    
    Lateral Edge (base corner to apex):
        L = \u221a(h\u00b2 + d\u00b2/4)  where d = a\u221a2 is base diagonal
        L = \u221a(h\u00b2 + a\u00b2/2)
        
        Space diagonal from corner to apex
    
    Special angles:
    - Base diagonal: d = a\u221a2 (45-45-90 triangle)
    - Apothem: r = a/2 (half edge, perpendicular to face)
    
    AHA MOMENT #1: FOUR-FOLD SYMMETRY - THE CARDINAL DIRECTIONS
    ============================================================
    The square pyramid has perfect 4-fold rotational symmetry:\n    - 4 identical triangular faces (North, South, East, West)\n    - 4 identical base edges\n    - 4 identical lateral edges\n    - 4 identical slant heights\n    \n    Rotation by 90\u00b0 about vertical axis leaves pyramid unchanged!\n    \n    This creates CARDINAL DIRECTIONALITY:\n    - Four directions of space (NSEW)\n    - Four faces aligned with compass bearings\n    - Four corners at intermediate directions (NE, SE, SW, NW)\n    \n    Symmetry group: C\u2084v (cyclic 4 + 4 vertical reflections = order 8)\n    \n    Why square and not triangle/pentagon/hexagon?\n    \n    1. Architectural stability:\n       - Square base is easy to level and measure\n       - 90\u00b0 angles align with natural coordinate axes\n       - Four sides balance weight distribution\n    \n    2. Symbolic resonance:\n       - Four elements (earth, water, air, fire)\n       - Four seasons (spring, summer, autumn, winter)\n       - Four directions (NSEW)\n       - Four ages/phases of life\n    \n    3. Construction efficiency:\n       - Right angles are easy to construct (carpenter's square)\n       - Square cuts from rectangular blocks\n       - Fewer distinct measurements than pentagon/hexagon\n    \n    The square pyramid is the PERFECT BALANCE between:\n    - Simplicity (fewer sides than pentagon+)\n    - Stability (more than triangle, which lacks symmetry about center)\n    - Symbolism (four = manifest world, elements, directions)\n    \n    AHA MOMENT #2: THE EGYPTIAN PROPORTIONS - SEKED AND PHI\n    ========================================================\n    Ancient Egyptians didn't use angle measures\u2014they used SEKED!\n    \n    Seked (sḳd): The horizontal distance traveled for 1 cubit vertical rise\n        seked = (a/2) / h  [in Egyptian units: palms per cubit]\n        \n    Modern equivalent: seked = cot(\u03b8)  where \u03b8 = face angle from horizontal\n    \n    Great Pyramid of Giza:\n    - Base edge: a \u2248 230.4 m (originally 440 royal cubits)\n    - Height: h \u2248 146.6 m (280 royal cubits)\n    - Ratio: h/a \u2248 0.636\n    \n    Or equivalently:\n    - Slant height / half-base = s / (a/2) \u2248 1.618 \u2248 \u03c6 (GOLDEN RATIO!)\n    \n    Was this intentional or coincidental? Debate continues!\n    \n    Golden ratio in pyramid:\n        If s = \u03c6 \u00d7 (a/2), then:\n        \u221a(h\u00b2 + (a/2)\u00b2) = \u03c6 \u00d7 (a/2)\n        h\u00b2 + (a/2)\u00b2 = \u03c6\u00b2 \u00d7 (a/2)\u00b2\n        h\u00b2 = (a/2)\u00b2 \u00d7 (\u03c6\u00b2 - 1)\n        h = (a/2) \u00d7 \u221a(\u03c6\u00b2 - 1) \u2248 0.6367 \u00d7 a\n    \n    This matches Giza to within 0.5%!\n    \n    Other special ratios:\n    - \u03c0 pyramid: slope such that perimeter = 2\u03c0 \u00d7 height\n      4a = 2\u03c0h \u21d2 h = 2a/\u03c0 \u2248 0.6366a (also close to Giza!)\n    \n    - Angle 51.84\u00b0: The \"perfect pyramid\" angle (close to Giza's 51.84\u00b0)\n    \n    The square pyramid allows for HARMONIC PROPORTIONS that blend\n    geometry, astronomy, and sacred mathematics!\n    \n    AHA MOMENT #3: SQUARE PYRAMID AS \"COLLAPSED CUBE\"\n    ==================================================\n    The square pyramid can be seen as a CUBE squeezed to a point!\n    \n    Imagine:\n    1. Start with cube: 8 vertices, 12 edges, 6 square faces\n    2. Identify top 4 vertices as ONE point (collapse top face to apex)\n    3. Result: 5 vertices, 8 edges, 5 faces \u2014 square pyramid!\n    \n    Vertices:\n        Cube: 8 = 4 (bottom) + 4 (top)\n        Pyramid: 5 = 4 (base) + 1 (apex, collapsed from 4)\n    \n    Edges:\n        Cube: 12 = 4 (bottom) + 4 (top) + 4 (vertical)\n        Pyramid: 8 = 4 (base) + 4 (lateral, collapsed from 8)\n    \n    Faces:\n        Cube: 6 = 1 (bottom) + 1 (top) + 4 (sides)\n        Pyramid: 5 = 1 (base) + 4 (triangular, collapsed from 5)\n    \n    Euler characteristic preserved:\n        V - E + F = 8 - 12 + 6 = 2  (cube)\n        V - E + F = 5 - 8 + 5 = 2  (pyramid) \u2713\n    \n    This \"collapse\" operation is a CONTINUOUS DEFORMATION:\n    - Start: Cube (h = a, top square at z = +a/2)\n    - Midpoint: Intermediate frustum (h = a/2, top square shrinking)\n    - End: Pyramid (h = any, top square \u2192 point)\n    \n    Volume during collapse:\n        V(h, top_edge) = (h/3) \u00d7 (a\u00b2 + a\u00d7t + t\u00b2)  (frustum formula)\n        When t = a (cube): V = (h/3) \u00d7 3a\u00b2 = h \u00d7 a\u00b2 = a\u00b3 (cube)\n        When t = 0 (pyramid): V = (h/3) \u00d7 a\u00b2 (pyramid)\n    \n    The square pyramid is the LIMIT of shrinking the top of a prism!\n    \n    HERMETIC NOTE - THE GEOMETRY OF THE SACRED FOUR:\n    ================================================\n    The square pyramid represents ELEMENTAL CONVERGENCE:\n    \n    - **Square Base**: The four elements (earth-water-air-fire)\n    - **Four Faces**: The four paths of transmutation\n    - **Apex**: The Quintessence (5th element, aether)\n    - **Five Vertices**: The Pentad (human, five senses, five-pointed star)\n    \n    Symbolism:\n    - **Four = Manifest**: Material world (4 directions, 4 seasons, 4 elements)\n    - **Five = Human**: Spirit + matter (1 head + 4 limbs, pentagon)\n    - **Convergence**: Four elements reuniting in spirit (apex)\n    - **Ascent**: Material (square) rising to spiritual (point)\n    \n    In Egyptian Cosmology:\n    - **Pyramid = Primordial Mound**: Ben-ben, first land emerging from Nun\n    - **Four Faces = Four Sons of Horus**: Guardians of cardinal directions\n    - **Apex = Ra**: Sun god, apex of being, source of light\n    - **Alignment**: Faces aligned to true North (stellar navigation)\n    \n    In Alchemy:\n    - **Square**: The four elements in base matter\n    - **Triangle**: The three principles (salt, sulfur, mercury)\n    - **Point**: The Prima Materia (first matter, philosopher's stone)\n    - **Pyramid**: The Opus (Great Work), transmutation of lead to gold\n    \n    The square pyramid is THE ALCHEMICAL VESSEL:\n    - Base contains the four (multiplicity)\n    - Faces are the work (process)\n    - Apex is the one (unity)\n    \n    This is the geometry of SYNTHESIS\u2014taking the four corners of reality\n    and unifying them upward into transcendent singularity. The pyramid\n    IS the process: four becoming one, many becoming unity, earth reaching\n    toward heaven.\n    \n    The square pyramid is EMBODIED GNOSIS\u2014the shape of enlightenment made\n    stone, the path from quaternary matter to unitary spirit.\n    \"\"\"\n    half_edge = base_edge / 2.0\n    slant_height = math.hypot(height, half_edge)\n    base_area = base_edge ** 2\n    lateral_area = 2.0 * base_edge * slant_height\n    surface_area = base_area + lateral_area\n    volume = (base_area * height) / 3.0\n    half_diagonal = half_edge * math.sqrt(2.0)\n    lateral_edge = math.hypot(height, half_diagonal)
    return SquarePyramidMetrics(
        base_edge=base_edge,
        height=height,
        slant_height=slant_height,
        base_apothem=half_edge,
        base_area=base_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        lateral_edge=lateral_edge,
    )
    """

def _build_vertices(base_edge: float, height: float) -> List[tuple[float, float, float]]:
    half = base_edge / 2.0
    base_z = -height / 2.0
    apex_z = height / 2.0
    return [
        (-half, -half, base_z),
        (half, -half, base_z),
        (half, half, base_z),
        (-half, half, base_z),
        (0.0, 0.0, apex_z),
    ]


_BASE_EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (0, 4),
    (1, 4),
    (2, 4),
    (3, 4),
]

_BASE_FACES = [
    (0, 1, 2, 3),
    (0, 1, 4),
    (1, 2, 4),
    (2, 3, 4),
    (3, 0, 4),
]


class SquarePyramidSolidService:
    """Generates payloads for right square pyramids."""

    @staticmethod
    def build(base_edge: float = 1.0, height: float = 1.0) -> SquarePyramidSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if base_edge <= 0 or height <= 0:
            raise ValueError("Base edge and height must be positive")
        metrics = _compute_metrics(base_edge, height)
        payload = SolidPayload(
            vertices=_build_vertices(base_edge, height),
            edges=list(_BASE_EDGES),
            faces=[tuple(face) for face in _BASE_FACES],
            labels=[
                SolidLabel(text=f"a = {base_edge:.3f}", position=(-base_edge / 2.0, 0.0, -height / 2.0)),
                SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
                'base_edge': metrics.base_edge,
                'height': metrics.height,
                'slant_height': metrics.slant_height,
                'base_apothem': metrics.base_apothem,
                'base_area': metrics.base_area,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'lateral_edge': metrics.lateral_edge,
            },
            suggested_scale=max(base_edge, height),
        )
        return SquarePyramidSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(base_edge: float = 1.0, height: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return SquarePyramidSolidService.build(base_edge, height).payload


class SquarePyramidSolidCalculator:
    """Calculator for right square pyramids with base edge and height inputs."""

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_height', 'Slant Height', 'units', 4, True),
        ('base_apothem', 'Base Apothem', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
        ('lateral_edge', 'Lateral Edge', 'units', 4, False),
    )

    def __init__(self, base_edge: float = 1.0, height: float = 1.0):
        """
          init   logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge if base_edge > 0 else 1.0
        self._height = height if height > 0 else 1.0
        self._result: Optional[SquarePyramidSolidResult] = None
        self._apply_dimensions(self._base_edge, self._height)

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

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
        if key == 'base_edge':
            self._apply_dimensions(value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_edge, value)
            return True
        if key == 'slant_height':
            half = self._base_edge / 2.0
            if value <= half:
                return False
            height = math.sqrt(value ** 2 - half ** 2)
            self._apply_dimensions(self._base_edge, height)
            return True
        if key == 'base_apothem':
            base_edge = value * 2.0
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'base_area':
            base_edge = math.sqrt(value)
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'volume':
            if self._base_edge > 0:
                height = (3.0 * value) / (self._base_edge ** 2)
                self._apply_dimensions(self._base_edge, height)
                return True
            if self._height > 0:
                base_edge = math.sqrt((3.0 * value) / self._height)
                self._apply_dimensions(base_edge, self._height)
                return True
            return False
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_edge = 1.0
        self._height = 1.0
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        """
        Payload logic.
        
        Returns:
            Result of payload operation.
        """
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        """
        Metadata logic.
        
        Returns:
            Result of metadata operation.
        """
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> Optional[SquarePyramidMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_edge: float, height: float):
        if base_edge <= 0 or height <= 0:
            return
        self._base_edge = base_edge
        self._height = height
        result = SquarePyramidSolidService.build(base_edge, height)
        self._result = result
        values = {
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'slant_height': result.metrics.slant_height,
            'base_apothem': result.metrics.base_apothem,
            'base_area': result.metrics.base_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'lateral_edge': result.metrics.lateral_edge,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'SquarePyramidMetrics',
    'SquarePyramidSolidResult',
    'SquarePyramidSolidService',
    'SquarePyramidSolidCalculator',
]