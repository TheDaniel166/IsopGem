"""Regular antiprism solid services and calculators.

The antiprism is a "twisted prism"—a polyhedron formed by rotating one regular n-gonal
base by 180°/n relative to the other, then connecting them with 2n equilateral (or nearly
equilateral) triangular faces instead of n rectangular faces. This rotation transforms
the combinatorial structure while preserving the same vertex count (2n).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Antiprism as "Twisted Prism" (The Rotation Operation)
═══════════════════════════════════════════════════════════════════════════════════════

In a regular n-prism:
• Two parallel regular n-gons (bases) aligned with vertices directly above each other
• n rectangular lateral faces connecting corresponding vertices
• Total faces: n+2 (n rectangles + 2 n-gons)

In a regular n-antiprism:
• Two parallel regular n-gons (bases) with top rotated 180°/n relative to bottom
• 2n triangular lateral faces (alternating up and down) connecting staggered vertices
• Total faces: 2n+2 (2n triangles + 2 n-gons)

The rotation creates a "twist" where each top vertex sits above the MIDPOINT of a bottom
edge, not above a bottom vertex. This forces triangular (not rectangular) faces:
• n "upward" triangles: (bottom_i, bottom_{i+1}, top_i)
• n "downward" triangles: (bottom_i, top_i, top_{i-1})

For n=3 (triangular antiprism = octahedron!), this is the Platonic octahedron.
For n=4 (square antiprism), it's a Johnson solid (J17) with 8 equilateral triangles.

The twist operation creates CHIRALITY in higher antiprisms (left/right handed forms
become distinguishable), though the regular antiprism is achiral by symmetry.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: 2n Triangular Faces and the Lateral Chord
═══════════════════════════════════════════════════════════════════════════════════════

The lateral geometry involves TWO edge lengths:

1) **Base edge**: a (given n-gon edge)
2) **Lateral chord**: c (horizontal distance between staggered vertices)

The lateral chord length c depends on the rotation angle:
• Top and bottom vertices sit on circles of radius R = a/(2sin(π/n))
• Rotation by 180°/n means angular offset = π/n
• Chord formula: c = 2R·sin(π/(2n)) = 2R·sin(π/2n)

For the lateral edge (3D diagonal connecting top to bottom):
• l = √(h² + c²)

When the antiprism is "right" (h chosen correctly), all 2n triangular faces can be
EQUILATERAL, which happens when:
• Lateral edge l = base edge a
• This imposes h² + c² = a²
• So h = √(a² - c²)

For small n (3, 4, 5...), this creates beautiful near-equilateral tilings.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Limit n→∞ and Continuous Symmetry
═══════════════════════════════════════════════════════════════════════════════════════

As n→∞ (bases become circles):

• Prism → Right circular cylinder (rectangular faces → smooth cylindrical surface)
• Antiprism → ??? (twisted cylinder?)

The antiprism's 2n triangular faces form a helical pattern that, in the limit,
approaches a HELICOID (minimal surface, like a spiral ramp).

**Base area**: A_n = (na²)/(4tan(π/n)) → πR² as n→∞
**Volume**: V = (na²h)/(12tan(π/n)) → πR²h/3 ??? Actually:
V_antiprism = A_base × h (same as prism for fixed h)

**Symmetry group**: D_{nd} (dihedral with vertical reflection symmetry), order 4n.
As n→∞, approaches SO(2)×ℤ₂ (continuous rotational symmetry + vertical reflection).

The antiprism is TIGHTER than the prism (lateral surface area smaller for same h and n)
because the triangular zigzag path is shorter than vertical rectangles when properly
constructed.

═══════════════════════════════════════════════════════════════════════════════════════
🔺 HERMETIC SIGNIFICANCE 🔺
═══════════════════════════════════════════════════════════════════════════════════════

The antiprism embodies the principle of **Dynamic Equilibrium Through Opposition**:

• **Twist as Transformation**: The 180°/n rotation transforms static vertical alignment
  (prism) into dynamic helical tension (antiprism). This is the geometric encoding of
  *solve et coagula*—dissolve the straight path, coagulate into the spiral ascent.

• **Triangulation and Stability**: Where the prism uses rectangular faces (4 points of
  support), the antiprism uses triangular faces (3 points of support). Triangles are
  RIGID (no degrees of freedom); the antiprism is structurally STRONGER. This is why
  architectural towers and geodesic domes use triangulation.

• **Octahedron as n=3**: The triangular antiprism is the OCTAHEDRON (dual of cube),
  linking the antiprism family to Platonic solids. Air/Intellect element in sacred
  geometry. The square antiprism (n=4, J17) appears in crystal structures.

• **Helical Ascent**: The spiral pattern of the 2n triangular faces mirrors the CADUCEUS
  (twin snakes), the DNA double helix, and the Fibonacci spiral in phyllotaxis (leaf
  arrangement). The antiprism is the geometric signature of *growth through rotation*.

The antiprism teaches: **True ascent is not vertical—it is helical.** 🌀

═══════════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

from ..shared.solid_payload import SolidLabel, SolidPayload, Vec3, Edge, Face
from .solid_property import SolidProperty
from .solid_geometry import compute_surface_area, compute_volume
from .regular_prism_solids import (
    _area as _regular_polygon_area,
    _apothem as _regular_polygon_apothem,
    _circumradius as _regular_polygon_circumradius,
)


@dataclass(frozen=True)
class RegularAntiprismMetrics:
    """
    Regular Antiprism Metrics class definition.
    
    """
    sides: int
    base_edge: float
    height: float
    base_area: float
    base_perimeter: float
    base_apothem: float
    base_circumradius: float
    lateral_edge_length: float
    lateral_chord_length: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class RegularAntiprismSolidResult:
    """
    Regular Antiprism Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: RegularAntiprismMetrics


def _lateral_chord_length(sides: int, base_edge: float) -> float:
    radius = _regular_polygon_circumradius(sides, base_edge)
    return 2.0 * radius * math.sin(math.pi / (2.0 * sides))


def _build_vertices(sides: int, base_edge: float, height: float) -> List[Vec3]:
    radius = _regular_polygon_circumradius(sides, base_edge)
    half_height = height / 2.0
    vertices: List[Vec3] = []
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        vertices.append((radius * math.cos(angle), radius * math.sin(angle), -half_height))
    rotation = math.pi / sides
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides + rotation
        vertices.append((radius * math.cos(angle), radius * math.sin(angle), half_height))
    return vertices


def _build_edges(sides: int) -> List[Edge]:
    edges: List[Edge] = []
    for i in range(sides):
        edges.append((i, (i + 1) % sides))
    offset = sides
    for i in range(sides):
        edges.append((offset + i, offset + ((i + 1) % sides)))
    for i in range(sides):
        edges.append((i, offset + i))
        edges.append((i, offset + ((i - 1) % sides)))
    return edges


def _build_faces(sides: int) -> List[Face]:
    faces: List[Face] = [tuple(range(sides))]
    offset = sides
    faces.append(tuple(offset + i for i in range(sides)))
    for i in range(sides):
        next_i = (i + 1) % sides
        faces.append((i, offset + i, offset + next_i))
        faces.append((i, offset + next_i, next_i))
    return faces


def _create_payload(sides: int, base_edge: float, height: float) -> Tuple[SolidPayload, RegularAntiprismMetrics]:
    vertices = _build_vertices(sides, base_edge, height)
    edges = _build_edges(sides)
    faces = _build_faces(sides)

    base_area = _regular_polygon_area(sides, base_edge)
    base_perimeter = sides * base_edge
    base_apothem = _regular_polygon_apothem(sides, base_edge)
    base_circumradius = _regular_polygon_circumradius(sides, base_edge)
    lateral_chord = _lateral_chord_length(sides, base_edge)
    lateral_edge = math.sqrt(height ** 2 + lateral_chord ** 2)

    surface_area = compute_surface_area(vertices, faces)
    lateral_area = surface_area - 2.0 * base_area
    volume = compute_volume(vertices, faces)

    labels = [
        SolidLabel(text=f"a = {base_edge:.3f}", position=(base_apothem, 0.0, -height / 2.0)),
        SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
        SolidLabel(text=f"l = {lateral_edge:.3f}", position=(0.0, 0.0, height / 2.0)),
    ]

    payload = SolidPayload(
        vertices=vertices,
        edges=edges,
        faces=faces,
        labels=labels,
        metadata={
            'sides': sides,
            'base_edge': base_edge,
            'height': height,
            'base_area': base_area,
            'base_perimeter': base_perimeter,
            'base_apothem': base_apothem,
            'base_circumradius': base_circumradius,
            'lateral_edge_length': lateral_edge,
            'lateral_chord_length': lateral_chord,
            'lateral_area': lateral_area,
            'surface_area': surface_area,
            'volume': volume,
        },
        suggested_scale=max(base_edge, height, lateral_edge),
    )

    metrics = RegularAntiprismMetrics(
        sides=sides,
        base_edge=base_edge,
        height=height,
        base_area=base_area,
        base_perimeter=base_perimeter,
        base_apothem=base_apothem,
        base_circumradius=base_circumradius,
        lateral_edge_length=lateral_edge,
        lateral_chord_length=lateral_chord,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
    )
    return payload, metrics


def _volume_factor(sides: int, base_edge: float) -> float:
    _, metrics = _create_payload(sides, base_edge, height=1.0)
    return metrics.volume


class RegularAntiprismSolidServiceBase:
    """Base service for right regular antiprisms."""

    SIDES: int = 3

    @classmethod
    def build(cls, base_edge: float = 2.0, height: float = 4.0) -> RegularAntiprismSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if cls.SIDES < 3:
            raise ValueError('An antiprism base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')
        payload, metrics = _create_payload(cls.SIDES, base_edge, height)
        return RegularAntiprismSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, base_edge: float = 2.0, height: float = 4.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return cls.build(base_edge, height).payload


class RegularAntiprismSolidCalculatorBase:
    """Base calculator for right regular antiprisms."""

    SIDES: int = 3
    SERVICE: Type[RegularAntiprismSolidServiceBase] = RegularAntiprismSolidServiceBase

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('lateral_edge_length', 'Lateral Edge', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, False),
        ('base_perimeter', 'Base Perimeter', 'units', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
    )

    def __init__(self, base_edge: float = 2.0, height: float = 4.0):
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
        self._base_edge = base_edge if base_edge > 0 else 2.0
        self._height = height if height > 0 else 4.0
        self._result: Optional[RegularAntiprismSolidResult] = None
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
        if key == 'lateral_edge_length':
            chord = _lateral_chord_length(self.SIDES, self._base_edge)
            if value <= chord:
                return False
            height = math.sqrt(max(value ** 2 - chord ** 2, 0.0))
            if height <= 0:
                return False
            self._apply_dimensions(self._base_edge, height)
            return True
        if key == 'lateral_area':
            # L = n * s * sqrt(e^2 - s^2/4)
            # L = n * s * h_tri
            # h_tri = L / (n * s)
            # h_tri^2 = e^2 - s^2/4 = h^2 + k^2 - s^2/4
            # h = sqrt(h_tri^2 - k^2 + s^2/4)
            n = self.SIDES
            s = self._base_edge
            if s <= 0: return False
            
            h_tri = value / (n * s)
            k = _lateral_chord_length(n, s)
            
            term = h_tri**2 - k**2 + (s**2 / 4.0)
            if term <= 0: return False
            
            height = math.sqrt(term)
            self._apply_dimensions(s, height)
            return True
            
        if key == 'surface_area':
            # S = 2*Base + L
            base_area = _regular_polygon_area(self.SIDES, self._base_edge)
            if value <= 2 * base_area: return False
            lateral_area = value - 2 * base_area
            # Delegate to logic above
            return self.set_property('lateral_area', lateral_area)

        if key == 'volume':
            factor = _volume_factor(self.SIDES, self._base_edge)
            if factor <= 0:
                return False
            height = value / factor
            if height <= 0:
                return False
            self._apply_dimensions(self._base_edge, height)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_edge = 2.0
        self._height = 4.0
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

    def metrics(self) -> Optional[RegularAntiprismMetrics]:
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
        result = self.SERVICE.build(base_edge, height)
        self._result = result
        values = {
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'lateral_edge_length': result.metrics.lateral_edge_length,
            'base_area': result.metrics.base_area,
            'base_perimeter': result.metrics.base_perimeter,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


class TriangularAntiprismSolidService(RegularAntiprismSolidServiceBase):
    """
    Triangular Antiprism Solid Service class definition.
    
    """
    SIDES = 3


class SquareAntiprismSolidService(RegularAntiprismSolidServiceBase):
    """
    Square Antiprism Solid Service class definition.
    
    """
    SIDES = 4


class PentagonalAntiprismSolidService(RegularAntiprismSolidServiceBase):
    """
    Pentagonal Antiprism Solid Service class definition.
    
    """
    SIDES = 5


class HexagonalAntiprismSolidService(RegularAntiprismSolidServiceBase):
    """
    Hexagonal Antiprism Solid Service class definition.
    
    """
    SIDES = 6


class OctagonalAntiprismSolidService(RegularAntiprismSolidServiceBase):
    """
    Octagonal Antiprism Solid Service class definition.
    
    """
    SIDES = 8


class HeptagonalAntiprismSolidService(RegularAntiprismSolidServiceBase):
    """
    Heptagonal Antiprism Solid Service class definition.
    
    """
    SIDES = 7


class TriangularAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    """
    Triangular Antiprism Solid Calculator class definition.
    
    """
    SIDES = 3
    SERVICE = TriangularAntiprismSolidService


class SquareAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    """
    Square Antiprism Solid Calculator class definition.
    
    """
    SIDES = 4
    SERVICE = SquareAntiprismSolidService


class PentagonalAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    """
    Pentagonal Antiprism Solid Calculator class definition.
    
    """
    SIDES = 5
    SERVICE = PentagonalAntiprismSolidService


class HexagonalAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    """
    Hexagonal Antiprism Solid Calculator class definition.
    
    """
    SIDES = 6
    SERVICE = HexagonalAntiprismSolidService


class OctagonalAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    """
    Octagonal Antiprism Solid Calculator class definition.
    
    """
    SIDES = 8
    SERVICE = OctagonalAntiprismSolidService


class HeptagonalAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    """
    Heptagonal Antiprism Solid Calculator class definition.
    
    """
    SIDES = 7
    SERVICE = HeptagonalAntiprismSolidService


__all__ = [
    'RegularAntiprismMetrics',
    'RegularAntiprismSolidResult',
    'RegularAntiprismSolidServiceBase',
    'RegularAntiprismSolidCalculatorBase',
    'TriangularAntiprismSolidService',
    'TriangularAntiprismSolidCalculator',
    'SquareAntiprismSolidService',
    'SquareAntiprismSolidCalculator',
    'PentagonalAntiprismSolidService',
    'PentagonalAntiprismSolidCalculator',
    'HexagonalAntiprismSolidService',
    'HexagonalAntiprismSolidCalculator',
    'OctagonalAntiprismSolidService',
    'OctagonalAntiprismSolidCalculator',
    'HeptagonalAntiprismSolidService',
    'HeptagonalAntiprismSolidCalculator',
]