"""Right regular prism solid services and calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Type

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty

Vec3 = Tuple[float, float, float]
Edge = Tuple[int, int]
Face = Sequence[int]


@dataclass(frozen=True)
class RegularPrismMetrics:
    """
    Regular Prism Metrics class definition.
    
    """
    sides: int
    base_edge: float
    height: float
    base_area: float
    base_perimeter: float
    base_apothem: float
    base_circumradius: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class RegularPrismSolidResult:
    """
    Regular Prism Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: RegularPrismMetrics


def _apothem(sides: int, edge: float) -> float:
    return edge / (2.0 * math.tan(math.pi / sides))


def _circumradius(sides: int, edge: float) -> float:
    return edge / (2.0 * math.sin(math.pi / sides))


def _area(sides: int, edge: float) -> float:
    return (sides * edge ** 2) / (4.0 * math.tan(math.pi / sides))


def _edge_from_area(sides: int, area: float) -> float:
    return math.sqrt((4.0 * math.tan(math.pi / sides) * area) / sides)


def _compute_metrics(sides: int, base_edge: float, height: float) -> RegularPrismMetrics:
    """
    Calculate metrics for a right regular n-gonal prism.
    
    THE REGULAR PRISM - EXTRUSION OF POLYGONS:
    ==========================================
    
    DEFINITION:
    -----------
    A regular prism is a prism whose bases are congruent regular polygons
    (all sides equal, all angles equal) and whose lateral faces are rectangles
    perpendicular to the bases.
    
    Components:
    - 2 regular n-gon bases (top & bottom, parallel and congruent)
    - n rectangular lateral faces (connecting corresponding edges)
    - 2n vertices (n on each base)
    - 3n edges (n on each base, n connecting them)
    - n+2 faces (2 bases + n sides)
    
    Examples:
    - n=3: Triangular prism (2 triangles + 3 rectangles = 5 faces)
    - n=4: Square prism / Rectangular cuboid (2 squares + 4 rectangles = 6 faces)
    - n=5: Pentagonal prism (2 pentagons + 5 rectangles = 7 faces)
    - n=6: Hexagonal prism (2 hexagons + 6 rectangles = 8 faces)
    
    ESSENTIAL FORMULAS:
    -------------------
    
    Base Area (regular n-gon with edge a):
        A_base = (n × a²) / (4 tan(π/n))
        
        Alternative: A_base = (1/2) × perimeter × apothem
                            = (1/2) × (na) × (a / [2 tan(π/n)])
    
    Apothem (center to midpoint of edge):
        r_apothem = a / (2 tan(π/n))
        
        The "inradius" of the base polygon.
    
    Circumradius (center to vertex):
        R = a / (2 sin(π/n))
        
        Vertices lie on a circle of radius R.
    
    Volume:
        V = A_base × h = [(n × a²) / (4 tan(π/n))] × h
        
        Universal prism formula: V = (base area) × (perpendicular height)
    
    Lateral Surface Area (n rectangular sides):
        A_lateral = Perimeter × h = (n × a) × h
        
        Unroll the lateral faces into one large rectangle:
        width = perimeter of base, height = h
    
    Total Surface Area:
        A_total = A_lateral + 2 × A_base
                = nah + 2 × [(n × a²) / (4 tan(π/n))]
    
    AHA MOMENT #1: PRISM AS EXTRUSION - THE DIMENSIONAL SWEEP
    ==========================================================
    A prism is created by "extruding" a 2D polygon into the 3rd dimension!
    
    Construction:
    1. Start with a regular n-gon base in the xy-plane at z=0
    2. Copy it to the parallel plane at z=h
    3. Connect corresponding vertices with straight edges
    4. Result: n rectangular "walls" connecting the two bases
    
    This is the same pattern as:
    - Line segment (1D) extruded → Rectangle (2D)
    - Rectangle (2D) extruded → Rectangular prism (3D)
    - Prism (3D) extruded into 4D → 4D prismoid!
    
    The prism is the 3D SHADOW of a 2D shape moving through time:
    - Each horizontal slice at height z is the same base polygon
    - The shape is CONSTANT along the extrusion axis
    - Volume = (area of cross-section) × (length of extrusion)
    
    Prisms are the simplest 3D solids after pyramids because:
    - Only two "special" faces (top/bottom) - the rest are generic rectangles
    - Translational symmetry along the height axis
    - Easy to manufacture (extrusion, molding, cutting)
    
    Physical examples:
    - Crystal growth along c-axis (quartz, calcite, beryl)
    - Architectural columns (Pentagon building, hexagonal towers)
    - Honeycomb cells (hexagonal prisms)
    - Pencils (hexagonal prisms for better grip)
    - Toblerone chocolate (triangular prism)
    
    AHA MOMENT #2: THE LIMIT AS n → ∞ IS A CYLINDER
    ================================================
    As the number of sides increases, the regular prism approaches a cylinder!
    
    Limit behavior:
    - n=3: Triangular prism (sharp, few faces)
    - n=4: Square prism (blocky)
    - n=6: Hexagonal prism (smoother)
    - n=12: Dodecagonal prism (nearly round)
    - n→∞: Circular prism = CYLINDER!
    
    Mathematical convergence:
    
    1. Circumradius R = a / (2 sin(π/n)):
       As n→∞, for fixed perimeter P=na (and thus a=P/n):
       R → P/(2π)  [circle radius from perimeter]
    
    2. Base area A = (n × a²) / (4 tan(π/n)):
       As n→∞, tan(π/n) ≈ π/n, so:
       A → (n × a²) × n / (4π) = (na)² / (4π) = P² / (4π) = πR²
       [circle area!]
    
    3. Lateral faces become infinitely thin rectangles → curved surface!
       n rectangles → continuous cylindrical surface
    
    This limiting process is how calculus approaches curved shapes:
    - Polygons approximate circles
    - Prisms approximate cylinders
    - Pyramids approximate cones
    - Polyhedra approximate spheres
    
    The cylinder is the "perfect prism" with infinite sides!
    
    AHA MOMENT #3: ELEGANT COMBINATORIAL FORMULAS
    ==============================================
    The prism structure follows beautiful combinatorial patterns:
    
    Vertices: V = 2n
    - n vertices on top base
    - n vertices on bottom base
    - Simple doubling!
    
    Edges: E = 3n
    - n edges on top base
    - n edges on bottom base
    - n vertical edges connecting them
    - Total: n + n + n = 3n
    
    Faces: F = n + 2
    - n rectangular lateral faces
    - 2 polygonal bases (top & bottom)
    
    Euler's Formula Verification:
        V - E + F = 2n - 3n + (n+2) = 2  ✓
    
    This always equals 2 for any convex polyhedron!
    
    Edge lengths:
    - Base edges: n edges of length a
    - Lateral edges: n edges of length h
    - Total edge length: L_total = na + nh = n(a+h)
    
    The prism is EFFICIENT:
    - Minimal faces for given base (only n+2 faces)
    - Each lateral face is a simple rectangle (easy to compute)
    - Symmetry: n-fold rotational symmetry about central axis
    
    The regular prism is an INFINITE FAMILY—one formula describes
    all triangular, square, pentagonal, hexagonal, ... prisms!
    
    HERMETIC NOTE - THE GEOMETRY OF ELEVATION:
    ==========================================
    The prism represents VERTICAL ASCENSION:
    
    - **Two Parallel Bases**: Heaven and Earth, Spirit and Matter
    - **Height Axis**: The vertical pillar connecting realms
    - **Rectangular Walls**: The structured path of ascent
    - **n-fold Symmetry**: The number of paths/stations/emanations
    
    Symbolism:
    - **Triangular (n=3)**: Trinity pillar, three-fold path
    - **Square (n=4)**: Four elements, four cardinal directions
    - **Pentagonal (n=5)**: Human (5 points), quintessence
    - **Hexagonal (n=6)**: Honeycomb, natural efficiency (bees)
    - **Octagonal (n=8)**: Buddhist eightfold path, regeneration
    
    In Sacred Architecture:
    - **Pillars of Solomon's Temple**: Bronze pillars Jachin & Boaz
    - **Cathedral Columns**: Vertical axis mundi connecting earth to heaven
    - **Obelisks**: Tapered square prisms (rays of sun god Ra)
    - **Minaret**: Cylindrical or prismatic towers (call to prayer rises)
    
    The prism is the AXIS of transformation—the ladder, the stairway, the
    pillar that bridges dimensions. The base is FORM, the height is BECOMING,
    and the top is ATTAINMENT.
    
    Each horizontal slice is identical—the path is CONSISTENT. Unlike the
    pyramid (which tapers to a point), the prism maintains its full nature
    from bottom to top. This is the geometry of PRESERVATION through ascent.
    """
    base_area = _area(sides, base_edge)
    base_perimeter = sides * base_edge
    base_apothem = _apothem(sides, base_edge)
    base_circumradius = _circumradius(sides, base_edge)
    lateral_area = base_perimeter * height
    surface_area = lateral_area + 2.0 * base_area
    volume = base_area * height
    return RegularPrismMetrics(
        sides=sides,
        base_edge=base_edge,
        height=height,
        base_area=base_area,
        base_perimeter=base_perimeter,
        base_apothem=base_apothem,
        base_circumradius=base_circumradius,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
    )


def _build_vertices(sides: int, base_edge: float, height: float) -> List[Vec3]:
    radius = _circumradius(sides, base_edge)
    half_height = height / 2.0
    vertices: List[Vec3] = []
    for layer_z in (-half_height, half_height):
        for i in range(sides):
            angle = (2.0 * math.pi * i) / sides
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), layer_z))
    return vertices


def _build_edges(sides: int) -> List[Edge]:
    edges: List[Edge] = []
    # bottom ring
    for i in range(sides):
        edges.append((i, (i + 1) % sides))
    # top ring
    offset = sides
    for i in range(sides):
        edges.append((offset + i, offset + ((i + 1) % sides)))
    # verticals
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


class RegularPrismSolidServiceBase:
    """Base service for right regular prisms."""

    SIDES: int = 3
    NAME: str = 'Regular Prism'

    @classmethod
    def build(cls, base_edge: float = 2.0, height: float = 4.0) -> RegularPrismSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if cls.SIDES < 3:
            raise ValueError('A prism base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')
        metrics = _compute_metrics(cls.SIDES, base_edge, height)
        payload = SolidPayload(
            vertices=_build_vertices(cls.SIDES, base_edge, height),
            edges=_build_edges(cls.SIDES),
            faces=_build_faces(cls.SIDES),
            labels=[
                SolidLabel(text=f"a = {base_edge:.3f}", position=(metrics.base_apothem, 0.0, -height / 2.0)),
                SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
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
            suggested_scale=max(base_edge, height),
        )
        return RegularPrismSolidResult(payload=payload, metrics=metrics)

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


class RegularPrismSolidCalculatorBase:
    """Base calculator for right regular prisms."""

    SIDES: int = 3
    SERVICE: Type[RegularPrismSolidServiceBase] = RegularPrismSolidServiceBase

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('base_apothem', 'Base Apothem', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('base_perimeter', 'Base Perimeter', 'units', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('base_circumradius', 'Base Circumradius', 'units', 4, False),
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
        self._result: Optional[RegularPrismSolidResult] = None
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
        if key == 'base_apothem':
            base_edge = 2.0 * value * math.tan(math.pi / self.SIDES)
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'base_area':
            base_edge = _edge_from_area(self.SIDES, value)
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'volume':
            base_area = _area(self.SIDES, self._base_edge)
            if base_area <= 0:
                return False
            height = value / base_area
            self._apply_dimensions(self._base_edge, height)
            return True
            
        if key == 'lateral_area':
            # L = P * h = (n * s) * h
            # If s is valid > 0, solve for h: h = L / (n*s)
            # If h is valid > 0 (and we want to assume s?), typically we assume s is fixed if h not explicitly targeted? 
            # Pattern: prioritize solving for height if s is set.
            perimeter = self.SIDES * self._base_edge
            if perimeter > 0:
                height = value / perimeter
                self._apply_dimensions(self._base_edge, height)
                return True
            # Fallback: if s is 0/invalid but h is set?
            # s = L / (n * h)
            if self._height > 0:
                base_edge = value / (self.SIDES * self._height)
                self._apply_dimensions(base_edge, self._height)
                return True
            
        if key == 'surface_area':
            # S = 2B + L = 2*_area(s) + (n*s)*h
            # Prioritize solving for h if s is set (linear)
            base_area = _area(self.SIDES, self._base_edge)
            if value <= 2 * base_area: return False
            lateral_area = value - 2 * base_area
            
            # Solve L for h
            perimeter = self.SIDES * self._base_edge
            if perimeter > 0:
                height = lateral_area / perimeter
                self._apply_dimensions(self._base_edge, height)
                return True
                
            # If s is unknown/0? Solve quadratic?
            # S = 2 * (n * s^2 / 4 tan) + n * s * h
            # A s^2 + B s - C = 0
            # A = n / (2 tan(pi/n))
            # B = n * h
            # C = SurfaceArea
            # Not implementing quadratic solving for s yet unless requested, keeping it simple (solve for h).
            
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

    def metrics(self) -> Optional[RegularPrismMetrics]:
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
            'base_apothem': result.metrics.base_apothem,
            'base_area': result.metrics.base_area,
            'base_perimeter': result.metrics.base_perimeter,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'base_circumradius': result.metrics.base_circumradius,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


class TriangularPrismSolidService(RegularPrismSolidServiceBase):
    """
    Triangular Prism Solid Service class definition.
    
    """
    SIDES = 3
    NAME = 'Triangular Prism'


class PentagonalPrismSolidService(RegularPrismSolidServiceBase):
    """
    Pentagonal Prism Solid Service class definition.
    
    """
    SIDES = 5
    NAME = 'Pentagonal Prism'


class HexagonalPrismSolidService(RegularPrismSolidServiceBase):
    """
    Hexagonal Prism Solid Service class definition.
    
    """
    SIDES = 6
    NAME = 'Hexagonal Prism'


class OctagonalPrismSolidService(RegularPrismSolidServiceBase):
    """
    Octagonal Prism Solid Service class definition.
    
    """
    SIDES = 8
    NAME = 'Octagonal Prism'


class TriangularPrismSolidCalculator(RegularPrismSolidCalculatorBase):
    """
    Triangular Prism Solid Calculator class definition.
    
    """
    SIDES = 3
    SERVICE = TriangularPrismSolidService


class PentagonalPrismSolidCalculator(RegularPrismSolidCalculatorBase):
    """
    Pentagonal Prism Solid Calculator class definition.
    
    """
    SIDES = 5
    SERVICE = PentagonalPrismSolidService


class HexagonalPrismSolidCalculator(RegularPrismSolidCalculatorBase):
    """
    Hexagonal Prism Solid Calculator class definition.
    
    """
    SIDES = 6
    SERVICE = HexagonalPrismSolidService


class OctagonalPrismSolidCalculator(RegularPrismSolidCalculatorBase):
    """
    Octagonal Prism Solid Calculator class definition.
    
    """
    SIDES = 8
    SERVICE = OctagonalPrismSolidService


class HeptagonalPrismSolidService(RegularPrismSolidServiceBase):
    """
    Heptagonal Prism Solid Service class definition.
    
    """
    SIDES = 7
    NAME = 'Heptagonal Prism'


class HeptagonalPrismSolidCalculator(RegularPrismSolidCalculatorBase):
    """
    Heptagonal Prism Solid Calculator class definition.
    
    """
    SIDES = 7
    SERVICE = HeptagonalPrismSolidService


__all__ = [
    'RegularPrismMetrics',
    'RegularPrismSolidResult',
    'RegularPrismSolidServiceBase',
    'RegularPrismSolidCalculatorBase',
    'TriangularPrismSolidService',
    'TriangularPrismSolidCalculator',
    'PentagonalPrismSolidService',
    'PentagonalPrismSolidCalculator',
    'HexagonalPrismSolidService',
    'HexagonalPrismSolidCalculator',
    'OctagonalPrismSolidService',
    'OctagonalPrismSolidCalculator',
    'HeptagonalPrismSolidService',
    'HeptagonalPrismSolidCalculator',
]