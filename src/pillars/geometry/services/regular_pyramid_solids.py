"""Right regular n-gonal pyramid solid services and calculators."""
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
class RegularPyramidMetrics:
    """
    Regular Pyramid Metrics class definition.
    
    """
    sides: int
    base_edge: float
    height: float
    slant_height: float
    base_apothem: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float
    base_perimeter: float
    base_circumradius: float
    lateral_edge: float


@dataclass(frozen=True)
class RegularPyramidSolidResult:
    """
    Regular Pyramid Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: RegularPyramidMetrics


def _apothem(sides: int, base_edge: float) -> float:
    return base_edge / (2.0 * math.tan(math.pi / sides))


def _circumradius(sides: int, base_edge: float) -> float:
    return base_edge / (2.0 * math.sin(math.pi / sides))


def _base_area(sides: int, base_edge: float) -> float:
    return (sides * base_edge ** 2) / (4.0 * math.tan(math.pi / sides))


def _edge_from_area(sides: int, area: float) -> float:
    return math.sqrt((4.0 * math.tan(math.pi / sides) * area) / sides)


def _edge_from_apothem(sides: int, apothem: float) -> float:
    return 2.0 * apothem * math.tan(math.pi / sides)


def _compute_metrics(sides: int, base_edge: float, height: float) -> RegularPyramidMetrics:
    """
    Calculate metrics for a right regular n-gonal pyramid.
    
    THE REGULAR PYRAMID - TAPERING FROM POLYGON TO POINT:
    ======================================================
    
    DEFINITION:
    -----------
    A regular pyramid is a pyramid whose base is a regular polygon (all
    sides equal, all angles equal) and whose apex is directly above the
    center of the base.
    
    Components:
    - 1 regular n-gon base (n sides, all edges equal length a)
    - n congruent isosceles triangular lateral faces
    - 1 apex vertex
    - n+1 vertices total (n base + 1 apex)
    - 2n edges (n base edges + n lateral edges from base to apex)
    - n+1 faces (1 base + n triangular sides)
    
    Examples:
    - n=3: Triangular pyramid (tetrahedron if equilateral triangular faces)
    - n=4: Square pyramid (Egyptian pyramid, most iconic)
    - n=5: Pentagonal pyramid
    - n=6: Hexagonal pyramid
    - n→∞: Approaches cone (circular base, infinite triangular faces → curved surface)
    
    ESSENTIAL FORMULAS:
    -------------------
    
    Base Area (regular n-gon with edge a):
        A_base = (n × a²) / (4 tan(π/n))
        
        Or: A_base = (1/2) × perimeter × apothem
    
    Volume:
        V = (1/3) × A_base × h
        
        Universal for ALL pyramids! See AHA MOMENT #1.
    
    Apothem (perpendicular from center to edge midpoint):
        r = a / (2 tan(π/n))
        
        This is the "inradius" of the base polygon.
    
    Slant Height (perpendicular from apex to base edge midpoint):
        s = √(h² + r²)
        
        Pythagorean theorem in the plane containing apex, center, and edge midpoint.
    
    Lateral Surface Area (all n triangular faces):
        A_lateral = (1/2) × perimeter × slant_height
                  = (1/2) × (n × a) × s
        
        Each triangle: base=a, height=s, area=(1/2)×a×s
        Sum: n × (1/2)×a×s = (1/2) × n×a × s
    
    Total Surface Area:
        A_total = A_base + A_lateral
    
    Circumradius (center to vertex):
        R = a / (2 sin(π/n))
    
    Lateral Edge (base vertex to apex):
        L = √(h² + R²)
        
        Pythagorean in plane containing apex, center, and base vertex.
    
    AHA MOMENT #1: THE UNIVERSAL V = ⅓Bh - ALL PYRAMIDS!
    =====================================================
    The volume formula V = (1/3) × base_area × height works for EVERY pyramid:
    - Triangular base, square base, hexagonal base, 100-gon base
    - Regular polygon, irregular polygon, any shape!
    
    Why universal?
    
    Method 1: Cavalieri's Principle
    - At height z above base, the cross-section is a similar polygon
    - Scaling factor: (1 - z/h)  [shrinks linearly from base (z=0) to apex (z=h)]
    - Area at height z: A(z) = A_base × (1 - z/h)²  [area scales as square of length]
    
    Volume by integration:
        V = ∫₀ʰ A(z) dz = ∫₀ʰ A_base × (1 - z/h)² dz
        
    Let u = 1 - z/h, then du = -dz/h:
        V = A_base × h × ∫₀¹ u² du = A_base × h × [u³/3]₀¹ = A_base × h / 3
    
    The "⅓" comes from ∫ u² du = u³/3 — the cubic integral!
    
    Method 2: Dissection (Ancient Egypt / Greece)
    - Any pyramid can be related to a prism with same base and height
    - Prism volume: V_prism = B × h
    - By clever cutting, 3 pyramids = 1 prism
    - Therefore: V_pyramid = (1/3) × B × h
    
    This works even for:
    - Oblique pyramids (apex not over center): Still V = (⅓)Bh!
    - Irregular base: As long as base is flat, V = (⅓)Bh!
    
    The "one-third" is the SIGNATURE of linear tapering from area to point.
    
    AHA MOMENT #2: THE LIMIT AS n → ∞ IS A CONE
    ============================================
    As the number of base sides increases, the pyramid approaches a cone!
    
    Convergence sequence:
    - n=3: Triangular pyramid (sharp, 3 triangular faces)
    - n=4: Square pyramid (Egyptian form)
    - n=8: Octagonal pyramid (smoother)
    - n=16: 16-gon pyramid (nearly conical)
    - n→∞: CONE (circular base, smooth curved surface)!
    
    Mathematical limits:
    
    1. Base shape:
       Regular n-gon → Circle as n→∞
       Perimeter P = n×a (fixed) ⇒ a → 0 but P constant
       Base radius: R = a/(2sin(π/n)) → P/(2π)  [circle radius]
    
    2. Base area:
       A_base = (n×a²) / (4tan(π/n)) → πR²  [circle area]
    
    3. Lateral surface:
       n discrete triangular faces → smooth conical surface
       A_lateral = (½)×P×s → πR×s  [cone lateral area]
       (where s = slant height)
    
    4. Volume:
       V = (⅓)×A_base×h → (⅓)×πR²×h  [cone volume]
    
    This limit process is fundamental to calculus:
    - Discrete → Continuous
    - Polygonal → Curved
    - Finite faces → Smooth surface
    
    The cone is the "perfect pyramid" with infinite sides!
    
    Just as:
    - Prism (n→∞) → Cylinder
    - Pyramid (n→∞) → Cone
    - Antiprism (n→∞) → Bicone
    
    AHA MOMENT #3: LATERAL FACES AS φ-TRIANGLES (Golden Pyramids)
    ==============================================================
    When can the lateral triangular faces be EQUILATERAL?
    
    For equilateral lateral triangles:
    - Base edge: a
    - Lateral edges (base vertex to apex): L
    - For equilateral triangle: L = a (all three edges equal!)
    
    But we also have: L = √(h² + R²)  where R = a/(2sin(π/n))
    
    Setting L = a:
        a = √(h² + R²)
        a² = h² + [a/(2sin(π/n))]²
        a²[1 - 1/(4sin²(π/n))] = h²
        h = a × √[1 - 1/(4sin²(π/n))]
    
    For n=3 (triangular base):
        sin(π/3) = √3/2
        h = a × √[1 - 1/3] = a × √(2/3) ≈ 0.816a
        
    This creates a REGULAR TETRAHEDRON (all 4 faces equilateral)!
    
    For n=4 (square base):
        sin(π/4) = √2/2, so 1/(4sin²(π/4)) = 1/2
        h = a × √(1/2) = a/√2
        
    This is impossible! (h < R means apex below base circle)
    
    But if we want GOLDEN RATIO in lateral faces:
        Lateral face: isosceles triangle with base a, sides L
        For φ-ratio: L/a = φ = (1+√5)/2 ≈ 1.618
        
    This gives: h = √(L² - R²) with constraints involving φ
    
    The Great Pyramid of Giza (approximately):
    - Lateral face angle: ≈ 51.84°
    - Slant height / half-base ≈ φ (golden ratio!)
    - Creates aesthetically "perfect" proportions
    
    Different n values permit different special proportions!
    
    HERMETIC NOTE - THE GEOMETRY OF ASCENSION:
    ==========================================
    The regular pyramid represents UNIVERSAL CONVERGENCE:
    
    - **n-fold Base**: The multiplicity of creation (3=trinity, 4=elements, 5=human, ...)
    - **Single Apex**: The divine unity (all paths lead to One)
    - **Triangular Faces**: Trinitarian bridges (base-vertex1-apex, base-vertex2-apex, ...)
    - **Height Axis**: The vertical pillar (axis mundi, world tree)
    
    Symbolism:
    - **Volume = ⅓**: Matter (1) reaching toward trinity/spirit (3)
    - **Slant Height**: The oblique path (not perpendicular ascent)
    - **n+1 Vertices**: The many (n) + the one (apex)
    - **Convergence**: "The way up and the way down are one and the same" (Heraclitus)
    
    In Sacred Architecture:
    - **Egyptian Pyramids**: Square base (4 elements), rising to Ra (sun/unity)
    - **Mayan Pyramids**: Often 9 levels (9 underworld realms) to celestial platform
    - **Ziggurats**: Stepped pyramids (terraced ascent to divine)
    - **Church Spires**: Pyramidal caps (prayers rising to heaven)
    
    The pyramid is FOCUSED INTENTION:
    - Wide base: Many enter
    - Narrow apex: Few reach
    - Slant faces: The difficult climb
    - Peak: The summit of realization
    
    As n increases:
    - More faces (more paths)
    - Smoother surface (easier climb?)
    - Approach to cone (infinite paths → continuous flow)
    
    The pyramid teaches: ALL directions on the base (all approaches to truth)
    eventually CONVERGE at the apex (singular truth). The shape itself is
    a mandala of convergence—every radius points to center, every edge
    flows to apex.
    
    This is the geometry of INITIATION—the many called, the few chosen,
    the one truth.
    """
    perimeter = sides * base_edge
    apothem = _apothem(sides, base_edge)
    base_area = _base_area(sides, base_edge)
    slant_height = math.sqrt(height ** 2 + apothem ** 2)
    lateral_area = 0.5 * perimeter * slant_height
    surface_area = base_area + lateral_area
    volume = (base_area * height) / 3.0
    circumradius = _circumradius(sides, base_edge)
    lateral_edge = math.sqrt(height ** 2 + circumradius ** 2)
    return RegularPyramidMetrics(
        sides=sides,
        base_edge=base_edge,
        height=height,
        slant_height=slant_height,
        base_apothem=apothem,
        base_area=base_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        base_perimeter=perimeter,
        base_circumradius=circumradius,
        lateral_edge=lateral_edge,
    )


def _build_vertices(sides: int, base_edge: float, height: float) -> List[Vec3]:
    radius = _circumradius(sides, base_edge)
    base_z = -height / 2.0
    apex_z = height / 2.0
    vertices = []
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        vertices.append((radius * math.cos(angle), radius * math.sin(angle), base_z))
    vertices.append((0.0, 0.0, apex_z))
    return vertices


def _build_edges(sides: int) -> List[Edge]:
    edges: List[Edge] = []
    for i in range(sides):
        edges.append((i, (i + 1) % sides))
        edges.append((i, sides))  # apex index is sides
    return edges


def _build_faces(sides: int) -> List[Face]:
    faces: List[Face] = [tuple(range(sides))]
    for i in range(sides):
        faces.append((i, (i + 1) % sides, sides))
    return faces


class RegularPyramidSolidServiceBase:
    """Base implementation for right regular n-gonal pyramids."""

    SIDES: int = 3
    NAME: str = 'Regular Pyramid'

    @classmethod
    def build(cls, base_edge: float = 1.0, height: float = 1.0) -> RegularPyramidSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if cls.SIDES < 3:
            raise ValueError('A pyramid base must have at least 3 sides')
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
                'slant_height': metrics.slant_height,
                'base_apothem': metrics.base_apothem,
                'base_area': metrics.base_area,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'base_perimeter': metrics.base_perimeter,
                'base_circumradius': metrics.base_circumradius,
                'lateral_edge': metrics.lateral_edge,
            },
            suggested_scale=max(base_edge, height),
        )
        return RegularPyramidSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, base_edge: float = 1.0, height: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return cls.build(base_edge, height).payload


class RegularPyramidSolidCalculatorBase:
    """Base calculator for right regular n-gonal pyramids."""

    SIDES: int = 3
    SERVICE: Type[RegularPyramidSolidServiceBase] = RegularPyramidSolidServiceBase

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_height', 'Slant Height', 'units', 4, True),
        ('base_apothem', 'Base Apothem', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('lateral_area', 'Lateral Area', 'units²', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('lateral_edge', 'Lateral Edge', 'units', 4, False),
        ('base_perimeter', 'Base Perimeter', 'units', 4, False),
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
        self._result: Optional[RegularPyramidSolidResult] = None
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
            apothem = _apothem(self.SIDES, self._base_edge)
            if value <= apothem:
                return False
            height = math.sqrt(value ** 2 - apothem ** 2)
            self._apply_dimensions(self._base_edge, height)
            return True
        if key == 'base_apothem':
            base_edge = _edge_from_apothem(self.SIDES, value)
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'base_area':
            base_edge = _edge_from_area(self.SIDES, value)
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'volume':
            base_area = _base_area(self.SIDES, self._base_edge)
            if base_area <= 0:
                return False
            height = (3.0 * value) / base_area
            self._apply_dimensions(self._base_edge, height)
            return True
            
        if key == 'lateral_area':
            # L = 0.5 * P * s_height
            # P = n * base_edge
            # s_height = 2*L / P
            perimeter = self.SIDES * self._base_edge
            if perimeter <= 0: return False
            slant_height = (2.0 * value) / perimeter
            
            # Now solve for height from slant_height
            # s^2 = h^2 + a^2 => h = sqrt(s^2 - a^2)
            apothem = _apothem(self.SIDES, self._base_edge)
            if slant_height < apothem: return False
            height = math.sqrt(slant_height**2 - apothem**2)
            self._apply_dimensions(self._base_edge, height)
            return True
            
        if key == 'surface_area':
            # S = BaseArea + LateralArea
            # L = S - BaseArea
            base_area = _base_area(self.SIDES, self._base_edge)
            if value <= base_area: return False
            lateral_area = value - base_area
            
            # Now solve for height via L logic above
            perimeter = self.SIDES * self._base_edge
            slant_height = (2.0 * lateral_area) / perimeter
            apothem = _apothem(self.SIDES, self._base_edge)
            if slant_height < apothem: return False
            height = math.sqrt(slant_height**2 - apothem**2)
            self._apply_dimensions(self._base_edge, height)
            return True
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

    def metrics(self) -> Optional[RegularPyramidMetrics]:
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
            'slant_height': result.metrics.slant_height,
            'base_apothem': result.metrics.base_apothem,
            'base_area': result.metrics.base_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'lateral_edge': result.metrics.lateral_edge,
            'base_perimeter': result.metrics.base_perimeter,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


class TriangularPyramidSolidService(RegularPyramidSolidServiceBase):
    """
    Triangular Pyramid Solid Service class definition.
    
    """
    SIDES = 3
    NAME = 'Equilateral Triangular Pyramid'


class PentagonalPyramidSolidService(RegularPyramidSolidServiceBase):
    """
    Pentagonal Pyramid Solid Service class definition.
    
    """
    SIDES = 5
    NAME = 'Regular Pentagonal Pyramid'


class HexagonalPyramidSolidService(RegularPyramidSolidServiceBase):
    """
    Hexagonal Pyramid Solid Service class definition.
    
    """
    SIDES = 6
    NAME = 'Regular Hexagonal Pyramid'


class HeptagonalPyramidSolidService(RegularPyramidSolidServiceBase):
    """
    Heptagonal Pyramid Solid Service class definition.
    
    """
    SIDES = 7
    NAME = 'Regular Heptagonal Pyramid'


class TriangularPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    """
    Triangular Pyramid Solid Calculator class definition.
    
    """
    SIDES = 3
    SERVICE = TriangularPyramidSolidService


class PentagonalPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    """
    Pentagonal Pyramid Solid Calculator class definition.
    
    """
    SIDES = 5
    SERVICE = PentagonalPyramidSolidService


class HexagonalPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    """
    Hexagonal Pyramid Solid Calculator class definition.
    
    """
    SIDES = 6
    SERVICE = HexagonalPyramidSolidService


class HeptagonalPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    """
    Heptagonal Pyramid Solid Calculator class definition.
    
    """
    SIDES = 7
    SERVICE = HeptagonalPyramidSolidService


__all__ = [
    'RegularPyramidMetrics',
    'RegularPyramidSolidResult',
    'RegularPyramidSolidServiceBase',
    'RegularPyramidSolidCalculatorBase',
    'TriangularPyramidSolidService',
    'TriangularPyramidSolidCalculator',
    'PentagonalPyramidSolidService',
    'PentagonalPyramidSolidCalculator',
    'HexagonalPyramidSolidService',
    'HexagonalPyramidSolidCalculator',
    'HeptagonalPyramidSolidService',
    'HeptagonalPyramidSolidCalculator',
]