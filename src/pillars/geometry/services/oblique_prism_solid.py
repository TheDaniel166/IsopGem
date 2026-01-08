"""Oblique regular prism solid services and calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload, Vec3, Edge, Face
from .solid_property import SolidProperty
from .solid_geometry import compute_surface_area, compute_volume
from .regular_prism_solids import _apothem as _regular_apothem
from .regular_prism_solids import _circumradius as _regular_circumradius
from .regular_prism_solids import _area as _regular_area


@dataclass(frozen=True)
class ObliquePrismMetrics:
    """
    Oblique Prism Metrics class definition.
    
    """
    sides: int
    base_edge: float
    height: float
    skew_x: float
    skew_y: float
    skew_magnitude: float
    base_area: float
    base_perimeter: float
    base_apothem: float
    base_circumradius: float
    lateral_edge_length: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class ObliquePrismSolidResult:
    """
    Oblique Prism Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: ObliquePrismMetrics


class ObliquePrismSolidService:
    """Generates payloads for right regular prisms skewed by a lateral offset."""

    SIDES: int = 6

    @classmethod
    def build(
        cls,
        base_edge: float = 2.0,
        height: float = 4.0,
        skew_x: float = 0.75,
        skew_y: float = 0.35,
    ) -> ObliquePrismSolidResult:
        """
        Build an oblique regular prism with lateral offset (skew).
        
        THE OBLIQUE PRISM - LEANING TOWER GEOMETRY:
        ===========================================
        
        DEFINITION:
        -----------
        An oblique prism is a prism whose lateral edges are NOT perpendicular
        to the base. The bases remain parallel and congruent, but the sides
        \"lean\" at an angle instead of rising vertically.
        
        Imagine a right prism (vertical sides), then shift the top base
        laterally by offset (skew_x, skew_y). The vertical height remains h,
        but the lateral edges are now slanted.\n        
        Components:\n        - 2 parallel congruent regular n-gon bases (bottom at z=-h/2, top at z=+h/2)\n        - Bottom base vertices: (x, y, -h/2)\n        - Top base vertices: (x + skew_x, y + skew_y, +h/2)\n        - n parallelogram lateral faces (no longer rectangles!)\n        - Lateral edges connect corresponding vertices with oblique slant\n        
        Key distinction from right prism:\n        - Right prism: Lateral edges perpendicular to base (\u22a5), lateral faces are rectangles\n        - Oblique prism: Lateral edges NOT perpendicular, lateral faces are parallelograms\n        
        ESSENTIAL FORMULAS:\n        -------------------\n        \n        Skew Magnitude (lateral offset in xy-plane):\n            s = \u221a(skew_x\u00b2 + skew_y\u00b2)\n            \n            This is how far the top is shifted from directly above bottom.\n        \n        Lateral Edge Length (slant distance):\n            L_edge = \u221a(h\u00b2 + s\u00b2) = \u221a(h\u00b2 + skew_x\u00b2 + skew_y\u00b2)\n            \n            3D Pythagorean theorem: vertical height h, horizontal offset s.\n        \n        Volume (CAVALIERI'S PRINCIPLE!):\n            V = A_base \u00d7 h\n            \n            CRITICAL INSIGHT: Volume depends ONLY on base area and vertical\n            height, NOT on the skew! Oblique and right prisms with same base\n            and height have IDENTICAL volumes!\n        \n        Lateral Surface Area:\n            A_lateral = (computed from actual faces)\n            \n            More complex than right prism because faces are parallelograms,\n            not rectangles. Each face has base edge 'a' and oblique edge L_edge.\n        \n        Total Surface Area:\n            A_total = A_lateral + 2 \u00d7 A_base\n        \n        AHA MOMENT #1: CAVALIERI'S PRINCIPLE - VOLUME IS INVARIANT!\n        ============================================================\n        The volume of an oblique prism equals that of a right prism with the\n        same base and height, REGARDLESS of the skew!\n        \n        Bonaventura Cavalieri (1635): If two solids have equal cross-sectional\n        areas at every height, they have equal volumes.\n        \n        Imagine a deck of cards:\n        - Stacked vertically (right prism): V = (card area) \u00d7 (stack height)\n        - Pushed into slant (oblique prism): V = (card area) \u00d7 (stack height)\n        - Volume UNCHANGED even though shape is skewed!\n        \n        Every horizontal slice at height z has the SAME area (the base polygon),\n        just shifted by (skew_x \u00d7 z/h, skew_y \u00d7 z/h). The area doesn't change!\n        \n        Mathematical proof:\n            V = \u222b\u222b\u222b dV = \u222b_{-h/2}^{h/2} A_base dz = A_base \u00d7 h\n        \n        The integral doesn't care about lateral position\u2014only vertical extent!\n        \n        This principle also explains:\n        - Cylinder volume = oblique cylinder volume (same base, height)\n        - Pyramid volume = oblique pyramid volume (same base, height)\n        - Spheroid volume = sphere volume (NO! different principle)\n        \n        Cavalieri's Principle is WHY we can compute volumes of complex shapes\n        by slicing them into infinitesimal layers and adding up areas!\n        \n        AHA MOMENT #2: PARALLELOGRAM FACES - SHEARED RECTANGLES\n        ========================================================\n        In a right prism, lateral faces are rectangles:\n        - Base edge: a (from base polygon)\n        - Height edge: h (perpendicular to base)\n        - Area of each face: a \u00d7 h\n        \n        In an oblique prism, lateral faces are parallelograms:\n        - Base edge: a (unchanged)\n        - Oblique edge: L = \u221a(h\u00b2 + (skew/n)\u00b2)  [varies by position!]\n        - Angle between edges: NOT 90\u00b0 (acute or obtuse)\n        \n        Each parallelogram is a SHEARED rectangle:\n        - Take a rectangle (a \u00d7 h)\n        - Push top edge sideways by some amount\n        - Area changes: A_parallelogram = base \u00d7 perpendicular_height\n          (perpendicular height < h for oblique prism)\n        \n        The faces are no longer congruent! Faces on the \"leading\" side of the\n        skew are stretched differently than faces on the \"trailing\" side.\n        \n        This is why oblique prisms are HARDER to manufacture:\n        - Right angles are easy (carpenter's square, machining)\n        - Oblique angles require precise angle measurement and jigs\n        \n        Yet oblique prisms are common in nature:\n        - Leaning crystals (monoclinic crystal system)\n        - Wind-bent plant stems\n        - Geological faults (sheared rock layers)\n        \n        AHA MOMENT #3: THE SPECTRUM FROM RIGHT TO OBLIQUE\n        ==================================================\n        Skew creates a continuous spectrum of prism forms:\n        \n        skew = 0:\n            Right prism (vertical sides, rectangular lateral faces)\n            Maximal symmetry: n-fold rotation + n mirror planes\n        \n        0 < skew < h:\n            Moderate oblique prism (tilted but stable)\n            Loses mirror symmetry, keeps only rotational symmetry\n        \n        skew = h:\n            45\u00b0 oblique prism (diagonal slant)\n            Lateral edges at 45\u00b0 angle to base\n        \n        skew > h:\n            Extreme oblique prism (\"overhang\")\n            Top base projects beyond bottom base footprint!\n        \n        skew \u2192 \u221e:\n            Degenerate case (infinite slant)\n        \n        Physical interpretation:\n        - Tower of Pisa: Small skew (3.97\u00b0 from vertical \u2248 7% skew)\n        - Playing cards pushed over: Medium skew\n        - Impossible architecture: Large skew (requires hidden support)\n        \n        The skew vector (skew_x, skew_y) has DIRECTION and magnitude:\n        - Direction: Which way the prism leans (compass bearing)\n        - Magnitude s = \u221a(skew_x\u00b2 + skew_y\u00b2): How much it leans\n        \n        The lateral edge length L = \u221a(h\u00b2 + s\u00b2) is always \u2265 h:\n        - Minimum (L = h): Right prism (s = 0)\n        - Maximum: No limit (as s increases, L increases)\n        \n        HERMETIC NOTE - THE GEOMETRY OF IMBALANCE:\n        ==========================================\n        The oblique prism represents DYNAMIC TENSION:\n        \n        - **Vertical Height h**: The intended path, the ideal axis\n        - **Lateral Skew s**: The deviation, the perturbation\n        - **Slant Edge L**: The actual path through space (hypotenuse)\n        - **Parallelogram Faces**: Sheared reality (distortion from ideal)\n        \n        Symbolism:\n        - **Leaning Tower**: Human ambition under gravitational pull\n        - **Playing Cards**: Order on the verge of collapse\n        - **Monoclinic Crystal**: Asymmetry creates unique properties\n        - **Shear Transform**: External force distorting structure\n        \n        In Esoteric Traditions:\n        - **Right Prism**: Perfect alignment (spirit \u22a5 matter)\n        - **Oblique Prism**: The fallen state (spirit at angle to matter)\n        - **Skew Vector**: The horizontal pull (worldly temptation)\n        - **Cavalieri's Invariant**: Inner volume (soul) unchanged despite outer skew!\n        \n        The oblique prism teaches: EXTERNAL FORM may be distorted, but\n        INTERNAL CONTENT (volume) remains constant if the foundation (base)\n        and height (vertical extent) are preserved.\n        \n        This is the geometry of RESILIENCE UNDER STRESS\u2014the structure that\n        leans but does not fall, the tower that reaches despite the wind.\n        
        Args:\n            base_edge: Description of base_edge.\n            height: Description of height.\n            skew_x: Description of skew_x.\n            skew_y: Description of skew_y.\n        \n        Returns:\n            Result of build operation.\n        \"\"\"\n        if cls.SIDES < 3:
            raise ValueError('A prism base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')

        base_area = _regular_area(cls.SIDES, base_edge)
        base_perimeter = cls.SIDES * base_edge
        base_apothem = _regular_apothem(cls.SIDES, base_edge)
        base_circumradius = _regular_circumradius(cls.SIDES, base_edge)
        skew_magnitude = math.hypot(skew_x, skew_y)
        lateral_edge = math.sqrt(height ** 2 + skew_magnitude ** 2)

        vertices = _build_vertices(cls.SIDES, base_edge, height, skew_x, skew_y)
        faces = _build_faces(cls.SIDES)
        edges = _build_edges(cls.SIDES)
        surface_area = compute_surface_area(vertices, faces)
        lateral_area = surface_area - 2.0 * base_area
        volume = compute_volume(vertices, faces)

        labels = [
            SolidLabel(text=f"a = {base_edge:.3f}", position=(base_apothem, 0.0, -height / 2.0)),
            SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            SolidLabel(text=f"skew = {skew_magnitude:.3f}", position=(skew_x / 2.0, skew_y / 2.0, height / 2.0)),
        ]

        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=labels,
            metadata={
                'sides': cls.SIDES,
                'base_edge': base_edge,
                'height': height,
                'skew_x': skew_x,
                'skew_y': skew_y,
                'skew_magnitude': skew_magnitude,
                'base_area': base_area,
                'base_perimeter': base_perimeter,
                'base_apothem': base_apothem,
                'base_circumradius': base_circumradius,
                'lateral_edge_length': lateral_edge,
                'lateral_area': lateral_area,
                'surface_area': surface_area,
                'volume': volume,
            },
            suggested_scale=max(base_edge, height, skew_magnitude),
        )

        metrics = ObliquePrismMetrics(
            sides=cls.SIDES,
            base_edge=base_edge,
            height=height,
            skew_x=skew_x,
            skew_y=skew_y,
            skew_magnitude=skew_magnitude,
            base_area=base_area,
            base_perimeter=base_perimeter,
            base_apothem=base_apothem,
            base_circumradius=base_circumradius,
            lateral_edge_length=lateral_edge,
            lateral_area=lateral_area,
            surface_area=surface_area,
            volume=volume,
        )
        return ObliquePrismSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, base_edge: float = 2.0, height: float = 4.0, skew_x: float = 0.75, skew_y: float = 0.35) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
            skew_x: Description of skew_x.
            skew_y: Description of skew_y.
        
        Returns:
            Result of payload operation.
        """
        return cls.build(base_edge=base_edge, height=height, skew_x=skew_x, skew_y=skew_y).payload


def _build_vertices(sides: int, base_edge: float, height: float, skew_x: float, skew_y: float) -> List[Vec3]:
    radius = _regular_circumradius(sides, base_edge)
    half_height = height / 2.0
    bottom: List[Vec3] = []
    top: List[Vec3] = []
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        bottom.append((x, y, -half_height))
        top.append((x + skew_x, y + skew_y, half_height))
    return bottom + top


def _build_edges(sides: int) -> List[Edge]:
    edges: List[Edge] = []
    for i in range(sides):
        edges.append((i, (i + 1) % sides))
    offset = sides
    for i in range(sides):
        edges.append((offset + i, offset + ((i + 1) % sides)))
    for i in range(sides):
        edges.append((i, offset + i))
    return edges


def _build_faces(sides: int) -> List[Face]:
    faces: List[Face] = [tuple(range(sides))]
    offset = sides
    faces.append(tuple(offset + i for i in range(sides)))
    for i in range(sides):
        next_i = (i + 1) % sides
        faces.append((i, next_i, offset + next_i, offset + i))
    return faces


class ObliquePrismSolidCalculator:
    """Calculator for oblique regular prisms allowing bidirectional updates."""

    def __init__(self, base_edge: float = 2.0, height: float = 4.0, skew_x: float = 0.75, skew_y: float = 0.35):
        """
          init   logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
            skew_x: Description of skew_x.
            skew_y: Description of skew_y.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge if base_edge > 0 else 2.0
        self._height = height if height > 0 else 4.0
        self._skew_x = skew_x
        self._skew_y = skew_y
        self._result: Optional[ObliquePrismSolidResult] = None
        self._apply_dimensions(self._base_edge, self._height, self._skew_x, self._skew_y)

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('skew_x', 'Skew X Offset', 'units', 4, True),
        ('skew_y', 'Skew Y Offset', 'units', 4, True),
        ('skew_magnitude', 'Skew Magnitude', 'units', 4, False),
        ('lateral_edge_length', 'Oblique Edge Length', 'units', 4, False),
        ('base_area', 'Base Area', 'units²', 4, False),
        ('base_perimeter', 'Base Perimeter', 'units', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
    )

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
        if value is None:
            return False
        if key == 'base_edge' and value > 0:
            self._apply_dimensions(value, self._height, self._skew_x, self._skew_y)
            return True
        if key == 'height' and value > 0:
            self._apply_dimensions(self._base_edge, value, self._skew_x, self._skew_y)
            return True
        if key == 'skew_x':
            self._apply_dimensions(self._base_edge, self._height, value, self._skew_y)
            return True
        if key == 'skew_y':
            self._apply_dimensions(self._base_edge, self._height, self._skew_x, value)
            return True
        if key == 'volume' and value > 0:
            base_area = _regular_area(ObliquePrismSolidService.SIDES, self._base_edge)
            if base_area <= 0:
                return False
            new_height = value / base_area
            self._apply_dimensions(self._base_edge, new_height, self._skew_x, self._skew_y)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_edge = 2.0
        self._height = 4.0
        self._skew_x = 0.75
        self._skew_y = 0.35
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

    def metrics(self) -> Optional[ObliquePrismMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_edge: float, height: float, skew_x: float, skew_y: float):
        if base_edge <= 0 or height <= 0:
            return
        self._base_edge = base_edge
        self._height = height
        self._skew_x = skew_x
        self._skew_y = skew_y
        result = ObliquePrismSolidService.build(base_edge, height, skew_x, skew_y)
        self._result = result
        values = {
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'skew_x': result.metrics.skew_x,
            'skew_y': result.metrics.skew_y,
            'skew_magnitude': result.metrics.skew_magnitude,
            'lateral_edge_length': result.metrics.lateral_edge_length,
            'base_area': result.metrics.base_area,
            'base_perimeter': result.metrics.base_perimeter,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'ObliquePrismMetrics',
    'ObliquePrismSolidResult',
    'ObliquePrismSolidService',
    'ObliquePrismSolidCalculator',
]