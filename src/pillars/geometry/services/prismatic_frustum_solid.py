"""Prismatic frustum solid service and calculator.

A prismatic frustum is a prism with one base removed and replaced by a smaller similar
polygon parallel to the original base. This creates a truncated prism with trapezoidal
lateral faces instead of rectangular ones. Like the pyramid frustum, it interpolates
between the full prism (when top edge = 0) and the limiting case (when top edge = bottom
edge, yielding a standard prism).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Frustum = Prism-Minus-Prism (Truncation Geometry)
═══════════════════════════════════════════════════════════════════════════════════════

Construction by subtraction:
• Start with a tall regular prism: base edge a₁, height H
• At height h from the bottom, slice horizontally and KEEP THE BOTTOM PART
• The top face has edge a₂ < a₁ (scaled by similarity)

The frustum is what remains: a truncated prism with:
• **Bottom base**: Regular n-gon with edge a₁
• **Top base**: Regular n-gon with edge a₂ (similar, smaller)
• **Height**: h (vertical separation between bases)
• **Lateral faces**: n congruent isosceles TRAPEZOIDS (not rectangles!)

**Volume formula** (simpler than pyramid frustum!):
For a prism, V = A_base × h regardless of base shape (Cavalieri's principle).

For frustum, we can think of it as:
V = (A₁ + A₂)/2 × h  (average base area times height)

But actually, the EXACT formula is NOT the average for general frustums. For regular
polygon bases:

V = h/3 · (A₁ + A₂ + √(A₁·A₂))

Wait, that's the pyramid frustum formula (Heronian mean). For a PRISMATIC frustum
with vertical edges (not slanted), the volume is actually:

V_frustum = h · (A₁ + A₂ + √(A₁·A₂))/3  (Prismoidal formula)

OR, if the lateral edges are not vertical but radially outward (true frustum), then:

V = h/2 · (A₁ + A₂)  (average of base areas)

This depends on the exact construction. The most common prismatic frustum has VERTICAL
faces (parallel to the axis), so volume is simply the average base area times height.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Trapezoidal Lateral Faces (Parallel vs. Slanted Edges)
═══════════════════════════════════════════════════════════════════════════════════════

Each lateral face of a prismatic frustum is an isosceles trapezoid:
• **Parallel sides**: Bottom edge a₁, top edge a₂
• **Legs**: Lateral edges connecting corresponding vertices

The lateral edge length l depends on the construction:

1) **Vertical frustum** (right frustum): Lateral edges are VERTICAL (parallel to axis).
   • l = h (height)
   • Face area: A_face = (a₁ + a₂)/2 × h
   • Total lateral area: A_lateral = n · (a₁ + a₂)/2 × h

2) **Radial frustum** (conical taper): Lateral edges point radially outward.
   • Top and bottom vertices sit on circles of radii R₁ and R₂
   • Radial offset: ΔR = R₁ - R₂
   • Lateral edge: l = √(h² + ΔR²) (3D Pythagorean theorem)
   • Slant height (perpendicular to base edge): s = √(h² + (apothem₁ - apothem₂)²)

The VERTICAL frustum is more common in architecture (columns, cooling towers), while
the RADIAL frustum appears in crystal habits and truncated pyramids.

**Truncation ratio** ρ = a₂/a₁:
• ρ = 0: Full prism (top shrinks to a point—actually becomes a pyramid!)
• ρ = 1: Standard prism (no truncation)
• 0 < ρ < 1: True frustum (intermediate state)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Architectural Ubiquity (Columns, Towers, Entasis)
═══════════════════════════════════════════════════════════════════════════════════════

Prismatic frustums are EVERYWHERE in sacred and functional architecture:

**Greek Columns (Doric/Ionic/Corinthian)**:
• Columns have *entasis*—a slight convex taper (widest at 1/3 height)
• The frustum captures this taper as a discrete approximation
• Bottom diameter > top diameter creates visual stability (prevents optical illusion
  of narrowing when viewed from below)

**Egyptian Pylons and Obelisks**:
• Pylon towers: trapezoidal (frustum) cross-sections for earthquake resistance
• Obelisks: square prismatic frustums with pyramidal caps

**Modern Cooling Towers (Hyperboloid of Revolution)**:
• Cross-section is a hyperboloid, but can be approximated by stacked frustums
• The frustum's strength-to-weight ratio makes it ideal for tall structures

**Crystal Habits (Mineralogy)**:
• Quartz, beryl, and tourmaline crystals often exhibit prismatic habits with
  terminated (truncated) ends—natural prismatic frustums

**Mathematical insight**:
The frustum is the BRIDGE between two symmetry scales:
• Bottom base: large n-fold symmetry (circumradius R₁)
• Top base: small n-fold symmetry (circumradius R₂)
• Frustum: interpolates continuously between the two (self-similar scaling)

As ρ → 0, the frustum → pyramid (1 point of convergence).
As ρ → 1, the frustum → prism (parallel translation with no convergence).
The frustum PARAMETERIZES the spectrum from convergent (pyramid) to parallel (prism).

═══════════════════════════════════════════════════════════════════════════════════════
🏛️ HERMETIC SIGNIFICANCE 🏛️
═══════════════════════════════════════════════════════════════════════════════════════

The prismatic frustum embodies **Gradual Refinement and Convergence**:

• **Taper as Ascent**: The frustum narrows as it rises, symbolizing the refinement of
  matter into spirit. The base (large, earthly) converges toward the apex (small,
  celestial). This is the geometric signature of the *Path of Return*—the Many
  converging back into the One.

• **Truncation as Incompleteness**: Unlike the pyramid (which reaches the singular apex),
  the frustum is CUT SHORT—it represents the *incomplete ascent*, the aspirant who has
  not yet reached enlightenment. The flat top is the "platform of initiation" where
  further work must be done.

• **Stability Through Width**: The frustum is MORE STABLE than the full prism (lower
  center of gravity due to taper) and more PRACTICAL than the pyramid (flat top provides
  a working platform). It is the form of *pragmatic wisdom*—not the ideal (pyramid) but
  the functional (frustum).

• **Egyptian Pylon as Gateway**: The trapezoid-shaped pylon towers flanking temple
  entrances are 2D projections of the frustum. They symbolize the *narrowing of the
  path* as one enters sacred space—the wide worldly entrance converges to the narrow
  holy of holies.

• **Crystalline Termination**: In mineralogy, the frustum appears when crystal growth
  is interrupted—the truncated pyramid or prism represents *frozen potential*. The
  crystal "intended" to grow further but was halted. This is the geometry of the
  *unfinished Work*—the Opus Interruptus.

The prismatic frustum teaches: **Perfection is a process, not a state.** 🏛️

═══════════════════════════════════════════════════════════════════════════════════════
"""
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
class PrismaticFrustumMetrics:
    """
    Prismatic Frustum Metrics class definition.
    
    """
    sides: int
    bottom_edge: float
    top_edge: float
    height: float
    bottom_area: float
    top_area: float
    bottom_perimeter: float
    top_perimeter: float
    bottom_apothem: float
    top_apothem: float
    bottom_circumradius: float
    top_circumradius: float
    lateral_edge_length: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class PrismaticFrustumSolidResult:
    """
    Prismatic Frustum Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: PrismaticFrustumMetrics


class PrismaticFrustumSolidService:
    """Generates payloads for truncated regular prisms with similar parallel bases."""

    SIDES: int = 6

    @classmethod
    def build(
        cls,
        bottom_edge: float = 3.0,
        top_edge: float = 1.75,
        height: float = 4.0,
    ) -> PrismaticFrustumSolidResult:
        """
        Build logic.
        
        Args:
            bottom_edge: Description of bottom_edge.
            top_edge: Description of top_edge.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if cls.SIDES < 3:
            raise ValueError('A prism base must have at least 3 sides')
        if bottom_edge <= 0 or top_edge <= 0 or height <= 0:
            raise ValueError('Edge lengths and height must be positive')

        bottom_area = _regular_area(cls.SIDES, bottom_edge)
        top_area = _regular_area(cls.SIDES, top_edge)
        bottom_perimeter = cls.SIDES * bottom_edge
        top_perimeter = cls.SIDES * top_edge
        bottom_apothem = _regular_apothem(cls.SIDES, bottom_edge)
        top_apothem = _regular_apothem(cls.SIDES, top_edge)
        bottom_radius = _regular_circumradius(cls.SIDES, bottom_edge)
        top_radius = _regular_circumradius(cls.SIDES, top_edge)
        radial_delta = abs(bottom_radius - top_radius)
        lateral_edge = math.sqrt(height ** 2 + radial_delta ** 2)

        vertices = _build_vertices(cls.SIDES, bottom_edge, top_edge, height)
        faces = _build_faces(cls.SIDES)
        edges = _build_edges(cls.SIDES)
        surface_area = compute_surface_area(vertices, faces)
        lateral_area = surface_area - (bottom_area + top_area)
        volume = compute_volume(vertices, faces)

        labels = [
            SolidLabel(text=f"a₁ = {bottom_edge:.3f}", position=(bottom_apothem, 0.0, -height / 2.0)),
            SolidLabel(text=f"a₂ = {top_edge:.3f}", position=(top_apothem * 0.7, 0.0, height / 2.0)),
            SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
        ]

        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=labels,
            metadata={
                'sides': cls.SIDES,
                'bottom_edge': bottom_edge,
                'top_edge': top_edge,
                'height': height,
                'bottom_area': bottom_area,
                'top_area': top_area,
                'bottom_perimeter': bottom_perimeter,
                'top_perimeter': top_perimeter,
                'bottom_apothem': bottom_apothem,
                'top_apothem': top_apothem,
                'lateral_edge_length': lateral_edge,
                'lateral_area': lateral_area,
                'surface_area': surface_area,
                'volume': volume,
            },
            suggested_scale=max(bottom_edge, height),
        )

        metrics = PrismaticFrustumMetrics(
            sides=cls.SIDES,
            bottom_edge=bottom_edge,
            top_edge=top_edge,
            height=height,
            bottom_area=bottom_area,
            top_area=top_area,
            bottom_perimeter=bottom_perimeter,
            top_perimeter=top_perimeter,
            bottom_apothem=bottom_apothem,
            top_apothem=top_apothem,
            bottom_circumradius=bottom_radius,
            top_circumradius=top_radius,
            lateral_edge_length=lateral_edge,
            lateral_area=lateral_area,
            surface_area=surface_area,
            volume=volume,
        )
        return PrismaticFrustumSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, bottom_edge: float = 3.0, top_edge: float = 1.75, height: float = 4.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            bottom_edge: Description of bottom_edge.
            top_edge: Description of top_edge.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return cls.build(bottom_edge=bottom_edge, top_edge=top_edge, height=height).payload


def _build_vertices(sides: int, bottom_edge: float, top_edge: float, height: float) -> List[Vec3]:
    bottom_radius = _regular_circumradius(sides, bottom_edge)
    top_radius = _regular_circumradius(sides, top_edge)
    half_height = height / 2.0
    vertices: List[Vec3] = []
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        vertices.append((bottom_radius * cos_val, bottom_radius * sin_val, -half_height))
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        vertices.append((top_radius * cos_val, top_radius * sin_val, half_height))
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
    return edges


def _build_faces(sides: int) -> List[Face]:
    faces: List[Face] = [tuple(range(sides))]
    offset = sides
    faces.append(tuple(offset + i for i in range(sides)))
    for i in range(sides):
        next_i = (i + 1) % sides
        faces.append((i, next_i, offset + next_i, offset + i))
    return faces


class PrismaticFrustumSolidCalculator:
    """Calculator with bidirectional updates for prismatic frustums."""

    _PROPERTY_DEFINITIONS = (
        ('bottom_edge', 'Bottom Edge', 'units', 4, True),
        ('top_edge', 'Top Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('bottom_area', 'Bottom Area', 'units²', 4, False),
        ('top_area', 'Top Area', 'units²', 4, False),
        ('bottom_perimeter', 'Bottom Perimeter', 'units', 4, False),
        ('top_perimeter', 'Top Perimeter', 'units', 4, False),
        ('lateral_edge_length', 'Lateral Edge Length', 'units', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
    )

    def __init__(self, bottom_edge: float = 3.0, top_edge: float = 1.75, height: float = 4.0):
        """
          init   logic.
        
        Args:
            bottom_edge: Description of bottom_edge.
            top_edge: Description of top_edge.
            height: Description of height.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._bottom_edge = bottom_edge if bottom_edge > 0 else 3.0
        self._top_edge = top_edge if top_edge > 0 else 1.75
        self._height = height if height > 0 else 4.0
        self._result: Optional[PrismaticFrustumSolidResult] = None
        self._apply_dimensions(self._bottom_edge, self._top_edge, self._height)

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
        if key == 'bottom_edge':
            self._apply_dimensions(value, self._top_edge, self._height)
            return True
        if key == 'top_edge':
            self._apply_dimensions(self._bottom_edge, value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._bottom_edge, self._top_edge, value)
            return True
        if key == 'volume':
            base_bottom = _regular_area(PrismaticFrustumSolidService.SIDES, self._bottom_edge)
            base_top = _regular_area(PrismaticFrustumSolidService.SIDES, self._top_edge)
            term = base_bottom + base_top + math.sqrt(base_bottom * base_top)
            if term <= 0:
                return False
            height = (3.0 * value) / term
            self._apply_dimensions(self._bottom_edge, self._top_edge, height)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._bottom_edge = 3.0
        self._top_edge = 1.75
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

    def metrics(self) -> Optional[PrismaticFrustumMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, bottom_edge: float, top_edge: float, height: float):
        if bottom_edge <= 0 or top_edge <= 0 or height <= 0:
            return
        self._bottom_edge = bottom_edge
        self._top_edge = top_edge
        self._height = height
        result = PrismaticFrustumSolidService.build(bottom_edge, top_edge, height)
        self._result = result
        values = {
            'bottom_edge': result.metrics.bottom_edge,
            'top_edge': result.metrics.top_edge,
            'height': result.metrics.height,
            'bottom_area': result.metrics.bottom_area,
            'top_area': result.metrics.top_area,
            'bottom_perimeter': result.metrics.bottom_perimeter,
            'top_perimeter': result.metrics.top_perimeter,
            'lateral_edge_length': result.metrics.lateral_edge_length,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'PrismaticFrustumMetrics',
    'PrismaticFrustumSolidResult',
    'PrismaticFrustumSolidService',
    'PrismaticFrustumSolidCalculator',
]