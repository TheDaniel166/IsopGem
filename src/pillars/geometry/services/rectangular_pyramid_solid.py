"""Right rectangular pyramid solid service and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty


@dataclass(frozen=True)
class RectangularPyramidMetrics:
    """
    Rectangular Pyramid Metrics class definition.
    
    """
    base_length: float
    base_width: float
    height: float
    slant_length: float
    slant_width: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float
    base_diagonal: float
    lateral_edge: float


@dataclass(frozen=True)
class RectangularPyramidSolidResult:
    """
    Rectangular Pyramid Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: RectangularPyramidMetrics


def _compute_metrics(base_length: float, base_width: float, height: float) -> RectangularPyramidMetrics:
    """
    Calculate metrics for a right rectangular pyramid.
    
    THE RECTANGULAR PYRAMID - CONVERGENCE TO A POINT:
    ==================================================
    
    DEFINITION:
    -----------
    A rectangular pyramid is a pyramid with a rectangular base and apex
    directly above the center of the base. The four lateral faces are
    isosceles triangles (two pairs of congruent triangles).
    
    Components:
    - 1 rectangular base (length × width)
    - 4 triangular lateral faces (2 congruent pairs)
    - 1 apex (vertex at top)
    - 5 vertices total (4 base corners + 1 apex)
    - 8 edges (4 base edges + 4 lateral edges)
    - 5 faces (1 base + 4 triangular sides)
    
    Special case:
    - Square pyramid: length = width (all 4 lateral faces congruent)
    
    ESSENTIAL FORMULAS:
    -------------------
    
    Base Area:
        A_base = length × width
    
    Volume:
        V = (1/3) × A_base × h = (1/3) × length × width × h
        
        The famous "one-third" rule! See AHA MOMENT #1.
    
    Slant Heights (two different values!):
        s_length = √(h² + (width/2)²)   [slant along length direction]
        s_width = √(h² + (length/2)²)    [slant along width direction]
        
        These are the perpendicular distances from apex to midpoint of
        base edges. They differ unless length = width (square).
    
    Lateral Surface Area:
        For rectangular pyramid, compute area of 4 triangular faces:
        A_lateral = (length × s_length) + (width × s_width)
        
        Two triangles with base=length, height=s_length (area = ½ × base × height × 2)
        Two triangles with base=width, height=s_width
    
    Total Surface Area:
        A_total = A_base + A_lateral
    
    Lateral Edge (corner to apex):
        L_edge = √(h² + r²)  where r = √[(length/2)² + (width/2)²]
        
        Distance from base corner to apex (space diagonal of right triangle).
    
    Base Diagonal:
        d = √(length² + width²)
        
        Diagonal across rectangular base (2D Pythagorean theorem).
    
    AHA MOMENT #1: THE ONE-THIRD VOLUME FORMULA - DISSECTION PROOF
    ===============================================================
    Why is pyramid volume = (1/3) × base × height, not (1/2) or (1/1)?
    
    PROOF BY DISSECTION (Ancient method, used by Archimedes):
    
    Take a rectangular prism (box) with base area B and height h.
    Volume of prism: V_prism = B × h
    
    Now dissect this prism into THREE pyramids:
    1. Pyramid with base B at bottom, apex at top corner
    2. Pyramid with base B at top, apex at bottom corner (flipped)
    3. Pyramid connecting the two (irregular, but same volume by symmetry)
    
    All three pyramids have the SAME base area B and height h!
    By symmetry, they must have equal volumes.
    
    Therefore:
        3 × V_pyramid = V_prism = B × h
        V_pyramid = (1/3) × B × h
    
    This works for ANY pyramid (triangular, square, hexagonal, ...)
    as long as apex is directly above base center!
    
    Intuitive explanation:
    - Prism: Full "column" of material from base to top
    - Pyramid: Material "tapers" from full base to zero at apex
    - Volume is 1/3 of prism because material is "averaged" over tapering
    
    Calculus proof:
        V = ∫₀ʰ A(z) dz  where A(z) = B × (1 - z/h)² [area at height z]
        V = B × ∫₀ʰ (1 - z/h)² dz = B × h/3
    
    The "one-third" is the SIGNATURE of pyramidal convergence!
    
    AHA MOMENT #2: TWO SLANT HEIGHTS - ASYMMETRY IN 2D
    ===================================================
    Unlike a square pyramid (which has ONE slant height), the rectangular
    pyramid has TWO distinct slant heights:
    
        s_length = √(h² + (width/2)²)
        s_width = √(h² + (length/2)²)
    
    Why two?
    - Slant height is perpendicular distance from apex to BASE EDGE midpoint
    - The two pairs of opposite edges have different lengths (length ≠ width)
    - Therefore, the slant distances to them differ!
    
    Visualization:
    - Stand at apex, look down at base
    - Distance to midpoint of long edge ≠ distance to midpoint of short edge
    - Long edge is farther from center, so larger slant height
    
    The four triangular faces come in TWO pairs:
    - Pair 1: Base edge = length, slant height = s_length
    - Pair 2: Base edge = width, slant height = s_width
    
    Area calculation:
        A_lateral = 2 × (½ × length × s_length) + 2 × (½ × width × s_width)
                  = length × s_length + width × s_width
    
    This asymmetry creates DIRECTIONALITY:
    - Square pyramid: Symmetric (all directions equivalent)
    - Rectangular pyramid: Has "long axis" and "short axis"
    - Extreme rectangle (length >> width): Approaches "ridge" pyramid
    
    The rectangular pyramid demonstrates: Breaking rotational symmetry
    (square → rectangle) creates MULTIPLE characteristic lengths!
    
    AHA MOMENT #3: THE SPECTRUM FROM NEEDLE TO SQUARE TO SLAB
    ==========================================================
    The rectangular pyramid sits on a CONTINUUM of base shapes:
    
    length = width (SQUARE):
        - Symmetric pyramid (4-fold rotational symmetry)
        - All lateral faces congruent
        - One slant height: s = √(h² + (a/2)²)
        - Classic Egyptian pyramid form
    
    length ≈ width (Nearly square):
        - Slightly asymmetric
        - Two slant heights very close
        - Subtle directionality
    
    length >> width (Elongated, "ridge"):
        - Highly directional (like roof ridge)
        - s_length ≈ h (steep face along length)
        - s_width >> h (gentle slope along width)
        - Approaches "wedge" or "gable" shape
    
    length << width (Flattened, "slab"):
        - Opposite directionality
        - Wide flat pyramid (like mesa)
    
    width → 0 (Degenerate, "blade"):
        - Collapses to triangle (no longer 3D solid!)
        - Limit case: vertical blade
    
    The rectangular pyramid is the BRIDGE between symmetric and asymmetric:
    - Square (isotropic): No preferred direction
    - Rectangle (anisotropic): Preferred axes
    
    Physical examples:
    - Roof gables: Elongated rectangular pyramids
    - Mayan pyramids: Nearly square base (slight elongation)
    - Modern architecture: Asymmetric pyramidal structures
    
    HERMETIC NOTE - THE GEOMETRY OF FOCUSED CONVERGENCE:
    ====================================================
    The rectangular pyramid represents DIRECTED ASCENSION:
    
    - **Rectangular Base**: The manifest world (4 directions, 2 axes)
    - **Apex Point**: The divine unity (all paths converge)
    - **Four Faces**: Four elements rising to quintessence
    - **Two Slant Heights**: Dual nature (masculine/feminine, active/passive)
    
    Symbolism:
    - **Length ≠ Width**: Asymmetry of manifestation (time ≠ space, matter ≠ energy)
    - **Converging Edges**: All diversity returns to source
    - **Volume = ⅓**: The material (1) reaches toward trinity (3)
    - **Five Vertices**: Human form (4 limbs + 1 head/spirit)
    
    In Sacred Architecture:
    - **Obelisks**: Rectangular pyramidal cap (sun's ray, divine connection)
    - **Pyramidal Roofs**: Directing energy/prayer upward
    - **Keystones**: Inverted pyramid (energy descending)
    
    The rectangular pyramid is the geometry of COLLECTION and FOCUSING:
    - Base gathers from area (2D)
    - Apex concentrates to point (0D)
    - Volume occupies space (3D)
    
    This is the shape of FUNNELING:
    - Energy collection: solar concentrators, funnel
    - Water flow: drainage, rivers to delta
    - Social hierarchy: many at base, one at top
    - Spiritual path: diverse starting points, one destination
    
    The rectangular pyramid teaches: CONVERGENCE need not be symmetric.
    Different paths (length ≠ width) can still reach the same apex.
    The journey matters (different slant heights), but the destination is one.
    """
    half_length = base_length / 2.0
    half_width = base_width / 2.0
    slant_length = math.hypot(height, half_width)
    slant_width = math.hypot(height, half_length)
    base_area = base_length * base_width
    lateral_area = base_length * slant_length + base_width * slant_width
    surface_area = base_area + lateral_area
    volume = (base_area * height) / 3.0
    base_diagonal = math.hypot(base_length, base_width)
    lateral_edge = math.hypot(height, base_diagonal / 2.0)
    return RectangularPyramidMetrics(
        base_length=base_length,
        base_width=base_width,
        height=height,
        slant_length=slant_length,
        slant_width=slant_width,
        base_area=base_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        base_diagonal=base_diagonal,
        lateral_edge=lateral_edge,
    )


def _build_vertices(base_length: float, base_width: float, height: float) -> List[tuple[float, float, float]]:
    half_length = base_length / 2.0
    half_width = base_width / 2.0
    base_z = -height / 2.0
    apex_z = height / 2.0
    return [
        (-half_length, -half_width, base_z),
        (half_length, -half_width, base_z),
        (half_length, half_width, base_z),
        (-half_length, half_width, base_z),
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


class RectangularPyramidSolidService:
    """Generates payloads for right rectangular pyramids."""

    @staticmethod
    def build(base_length: float = 1.0, base_width: float = 1.0, height: float = 1.0) -> RectangularPyramidSolidResult:
        """
        Build logic.
        
        Args:
            base_length: Description of base_length.
            base_width: Description of base_width.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if base_length <= 0 or base_width <= 0 or height <= 0:
            raise ValueError("Base length, base width, and height must be positive")
        metrics = _compute_metrics(base_length, base_width, height)
        payload = SolidPayload(
            vertices=_build_vertices(base_length, base_width, height),
            edges=list(_BASE_EDGES),
            faces=[tuple(face) for face in _BASE_FACES],
            labels=[
                SolidLabel(text=f"a = {base_length:.3f}", position=(-base_length / 2.0, 0.0, -height / 2.0)),
                SolidLabel(text=f"b = {base_width:.3f}", position=(0.0, -base_width / 2.0, -height / 2.0)),
                SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
                'base_length': metrics.base_length,
                'base_width': metrics.base_width,
                'height': metrics.height,
                'slant_length': metrics.slant_length,
                'slant_width': metrics.slant_width,
                'base_area': metrics.base_area,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'base_diagonal': metrics.base_diagonal,
                'lateral_edge': metrics.lateral_edge,
            },
            suggested_scale=max(base_length, base_width, height),
        )
        return RectangularPyramidSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(base_length: float = 1.0, base_width: float = 1.0, height: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_length: Description of base_length.
            base_width: Description of base_width.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return RectangularPyramidSolidService.build(base_length, base_width, height).payload


class RectangularPyramidSolidCalculator:
    """Calculator for right rectangular pyramids."""

    _PROPERTY_DEFINITIONS = (
        ('base_length', 'Base Length', 'units', 4, True),
        ('base_width', 'Base Width', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_length', 'Slant Height (length faces)', 'units', 4, True),
        ('slant_width', 'Slant Height (width faces)', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
        ('base_diagonal', 'Base Diagonal', 'units', 4, False),
        ('lateral_edge', 'Lateral Edge', 'units', 4, False),
    )

    def __init__(self, base_length: float = 1.0, base_width: float = 1.0, height: float = 1.0):
        """
          init   logic.
        
        Args:
            base_length: Description of base_length.
            base_width: Description of base_width.
            height: Description of height.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_length = base_length if base_length > 0 else 1.0
        self._base_width = base_width if base_width > 0 else 1.0
        self._height = height if height > 0 else 1.0
        self._result: Optional[RectangularPyramidSolidResult] = None
        self._apply_dimensions(self._base_length, self._base_width, self._height)

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
        if key == 'base_length':
            self._apply_dimensions(value, self._base_width, self._height)
            return True
        if key == 'base_width':
            self._apply_dimensions(self._base_length, value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_length, self._base_width, value)
            return True
        if key == 'slant_length':
            half_width = self._base_width / 2.0
            if value <= half_width:
                return False
            height = math.sqrt(value ** 2 - half_width ** 2)
            self._apply_dimensions(self._base_length, self._base_width, height)
            return True
        if key == 'slant_width':
            half_length = self._base_length / 2.0
            if value <= half_length:
                return False
            height = math.sqrt(value ** 2 - half_length ** 2)
            self._apply_dimensions(self._base_length, self._base_width, height)
            return True
        if key == 'volume':
            base_area = self._base_length * self._base_width
            if base_area <= 0:
                return False
            height = (3.0 * value) / base_area
            self._apply_dimensions(self._base_length, self._base_width, height)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_length = 1.0
        self._base_width = 1.0
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

    def metrics(self) -> Optional[RectangularPyramidMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_length: float, base_width: float, height: float):
        if base_length <= 0 or base_width <= 0 or height <= 0:
            return
        self._base_length = base_length
        self._base_width = base_width
        self._height = height
        result = RectangularPyramidSolidService.build(base_length, base_width, height)
        self._result = result
        values = {
            'base_length': result.metrics.base_length,
            'base_width': result.metrics.base_width,
            'height': result.metrics.height,
            'slant_length': result.metrics.slant_length,
            'slant_width': result.metrics.slant_width,
            'base_area': result.metrics.base_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'base_diagonal': result.metrics.base_diagonal,
            'lateral_edge': result.metrics.lateral_edge,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'RectangularPyramidMetrics',
    'RectangularPyramidSolidResult',
    'RectangularPyramidSolidService',
    'RectangularPyramidSolidCalculator',
]