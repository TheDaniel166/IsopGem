"""Terraced step pyramid solid service and calculator.

THE STEP PYRAMID - TERRACED ASCENSION:
=======================================

DEFINITION:
-----------
A step pyramid (or ziggurat) is a pyramid composed of multiple horizontal
terraces (tiers), each smaller than the one below, creating a stepped profile
instead of smooth sloping faces.

Think: Stacked square platforms of decreasing size, like a wedding cake or
the ancient pyramids of Saqqara (Egypt) and Mesopotamian ziggurats.

Structure:
- Multiple square tiers (typically 3-7 tiers)
- Each tier is a square frustum
- Bottom tier has largest base edge
- Top tier has smallest edge (platform)
- Total height divided equally among tiers

Components (for t tiers):
- (t+1) square faces (one per tier level)
- 4t vertical step faces (sides of each tier)
- 4(t+1) horizontal edges per level
- 4t vertical edges connecting tiers

Example: 3-tier step pyramid
- Bottom: Large square (base_edge)
- Middle: Medium square
- Top: Small square (top_edge)
- 4 faces (base + 3 tiers)
- 12 vertical step faces (3 tiers \u00d7 4 sides)

ESSENTIAL FORMULAS:
-------------------

Tier Edge Interpolation:
    edge_i = base_edge - (base_edge - top_edge) \u00d7 (i / tiers)
    
    where i = 0, 1, 2, ..., tiers
    i=0: base_edge (bottom)
    i=tiers: top_edge (top)

Volume (sum of frustum volumes):
    V = step_height \u00d7 \u03a3(edge_i\u00b2)  for i = 0 to tiers-1
    
    where step_height = total_height / tiers
    
    This is approximate! Each tier is actually a thin frustum, not prism.

Lateral Surface Area (all vertical step faces):
    A_lateral = 4 \u00d7 step_height \u00d7 \u03a3(edge_i)  for i = 0 to tiers-1
    
    Perimeter of each tier \u00d7 step height, summed over all tiers

Total Surface Area:
    A_total = A_base + A_top + A_lateral

AHA MOMENT #1: ZIGGURAT AS \"QUANTIZED\" PYRAMID
================================================
The step pyramid is a DISCRETE approximation of the continuous pyramid!

Smooth pyramid:
- Infinite infinitesimal layers
- Continuous slope from base to apex
- Lateral faces are smooth triangles
- Volume integral: V = \u222b A(z) dz

Step pyramid:
- Finite number of tiers (discrete layers)
- Discontinuous \"staircase\" profile
- Lateral surface is NOT smooth (stepped)\n- Volume sum: V = \u03a3 A_i \u00d7 \u0394h

As tiers \u2192 \u221e:\n    Step pyramid \u2192 Smooth pyramid (limit of Riemann sum)\n\nThis is QUANTIZATION:\n- Smooth curve approximated by horizontal steps\n- Like pixels approximating smooth image\n- Or quantum energy levels approximating continuous spectrum\n\nPhysical analogy:\n- Smooth pyramid = classical smooth trajectory\n- Step pyramid = quantized energy levels (discrete tiers)\n- As tiers increase, step approximation \u2192 smooth limit\n\nThe step pyramid is geometry demonstrating:\n    \u222b \u2248 \u03a3  (integral is limit of sum)\n\nAHA MOMENT #2: STEP PYRAMID AS RITUAL ARCHITECTURE\n==================================================\nWhy build STEPPED pyramids instead of smooth ones?\n\n1. **Construction practicality**:\n   - Easier to build horizontal terraces than smooth slopes\n   - Each tier is a platform (work area for next tier)\n   - Can build tier-by-tier, pausing between levels\n   - No need for continuous smooth masonry\n\n2. **Symbolic terraces**:\n   - Each tier = spiritual level/realm/heaven\n   - 7 tiers = 7 heavens, 7 planets, 7 chakras\n   - 9 tiers = 9 underworld levels (Mayan, Chinese)\n   - Ascent is STAGED, not continuous (initiation levels)\n\n3. **Functional platforms**:\n   - Each terrace can be used (gardens, temples, offerings)\n   - Top platform = temple/shrine (accessible, not pointy)\n   - Processional ascent (climb tier by tier)\n   - Multiple sacred spaces at different elevations\n\nHistorical examples:\n\n- **Djoser's Step Pyramid (Egypt, ~2630 BCE)**:\n  * 6 tiers, height 62m\n  * First monumental stone building\n  * Prototype for smooth pyramids (Giza came later!)\n  * Architect: Imhotep (deified as god of wisdom)\n\n- **Ziggurats (Mesopotamia)**:\n  * 3-7 tiers, temple on top\n  * Tower of Babel (likely ziggurat)\n  * Stairway to heaven (literal!)\n  * Each tier painted different color (cosmic layers)\n\n- **Mesoamerican Pyramids**:\n  * Aztec: Often 4-7 tiers + temple\n  * Maya: 9 tiers (9 lords of night/underworld)\n  * Used for human sacrifice, astronomical observation\n  * Living structures (renovated, expanded)\n\nThe step pyramid is ACCESSIBLE divinity:\n- Smooth pyramid: Unreachable apex (god's domain)\n- Step pyramid: Climbable tiers (human can ascend!)\n- Top platform: Meeting place (heaven \u2194 earth interface)\n\nAHA MOMENT #3: STEP PYRAMID AS RIEMANN SUM VISUALIZATION\n=========================================================\nThe step pyramid is a GEOMETRIC PROOF of integral calculus!\n\nRiemann sum for pyramid volume:\n    V = \u222b\u2080\u02b0 A(z) dz  where A(z) = A_base \u00d7 (1 - z/h)\u00b2\n\nApproximate with n tiers:\n    V \u2248 \u03a3_{i=0}^{n-1} A(z_i) \u00d7 \u0394h\n    \n    where z_i = i \u00d7 (h/n), \u0394h = h/n\n\nEach term A(z_i) \u00d7 \u0394h is volume of ONE TIER (frustum \u2248 prism for small \u0394h)!\n\nAs n increases:\n- More tiers, thinner steps\n- Step pyramid \u2192 smooth pyramid\n- Riemann sum \u2192 definite integral\n- V_approx \u2192 V_exact = (\u2153) \u00d7 A_base \u00d7 h\n\nVisual understanding:\n- Each tier = rectangular strip under curve\n- More tiers = better approximation of curved area\n- Limit (infinite tiers) = exact area under curve\n\nThis is how calculus WORKS:\n- Smooth curve \u2248 sum of rectangles (Riemann)\n- Integral = limit of sum as rectangles \u2192 infinitesimal\n- Physical shape (step pyramid) embodies this convergence!\n\nThe step pyramid is CALCULUS IN STONE:\n- Built by civilizations without formal calculus\n- Yet embodies the principle of integration\n- Demonstrates: Finite sum approximates infinite integral\n\nModern applications:\n- Computer graphics: Smooth surfaces as polygonal meshes (finite tiers)\n- Numerical integration: Approximate integrals by discrete sums\n- Physics: Discrete time steps approximating continuous motion\n\nThe step pyramid teaches: THE DISCRETE CAN APPROXIMATE THE CONTINUOUS,\nand in the limit, BECOME IT.\n\nHERMETIC NOTE - THE GEOMETRY OF GRADUAL ASCENSION:\n==================================================\nThe step pyramid represents STAGED INITIATION:\n\n- **Multiple Tiers**: Progressive levels of consciousness/enlightenment\n- **Horizontal Platforms**: Stable plateaus (rest, consolidation)\n- **Vertical Steps**: Transitions between levels (challenges, tests)\n- **Top Platform**: Final achievement (temple, meeting with divine)\n\nSymbolism:\n- **Each Tier**: Degree of initiation (Masonic degrees, yogic chakras)\n- **Step Count**: Sacred numbers (3, 7, 9, 12)\n- **Ascent**: The Path (sequential, not instantaneous)\n- **Visible Levels**: Hierarchy made manifest (cosmos has structure)\n\nIn Mystery Traditions:\n- **Egyptian**: 7 tiers = 7 ba souls, 7 gates of Duat\n- **Babylonian**: Ziggurat = cosmic mountain (earth \u2192 heaven bridge)\n- **Aztec/Maya**: Pyramid = sacred mountain (axis mundi)\n- **Buddhist**: Stupa tiers = stages toward nirvana\n\nThe step pyramid is THE LADDER:\n- Jacob's Ladder (angels ascending/descending)\n- Tree of Life (10 sephiroth = 10 tiers?)\n- Masonic ladder (degrees of attainment)\n- Chakra system (7 levels of energy)\n\nThis is the geometry of GRADUAL PERFECTION:\n- Enlightenment is not instantaneous leap\n- But tier-by-tier climb\n- Each level must be mastered before next\n- The journey honors each stage as necessary\n\nThe step pyramid teaches: THERE IS NO SHORTCUT TO THE TOP.\nEvery tier must be traversed. Every platform must be honored.\nThe discrete steps are not approximation of smooth path\u2014\nthey ARE the path! The quantization is not error, but reality.\n\nThe smooth pyramid is the IDEAL (perfect form).\nThe step pyramid is the REAL (human journey).\nAnd in the limit, real approaches ideal.\n\nThis is sacred geometry as PEDAGOGY\u2014the shape that teaches\nhow discrete becomes continuous, how many becomes one, how\nclimber becomes climbed-to.\n"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, cast

from ..shared.solid_payload import Face, SolidLabel, SolidPayload
from .solid_property import SolidProperty


@dataclass(frozen=True)
class StepPyramidMetrics:
    """
    Step Pyramid Metrics class definition.
    
    """
    base_edge: float
    top_edge: float
    height: float
    tiers: int
    step_height: float
    base_area: float
    top_area: float
    lateral_area: float
    surface_area: float
    volume: float
    tier_edges: List[float]


@dataclass(frozen=True)
class StepPyramidSolidResult:
    """
    Step Pyramid Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: StepPyramidMetrics


def _interpolate_edges(base_edge: float, top_edge: float, tiers: int) -> List[float]:
    if tiers <= 0:
        return [base_edge]
    return [base_edge - (base_edge - top_edge) * (i / tiers) for i in range(tiers + 1)]


def _build_vertices(edge_sizes: List[float], height: float) -> List[tuple[float, float, float]]:
    tiers = len(edge_sizes) - 1
    step_height = height / tiers if tiers else height
    vertices: List[tuple[float, float, float]] = []
    for level, edge in enumerate(edge_sizes):
        half = edge / 2.0
        z = -height / 2.0 + step_height * level
        vertices.extend([
            (-half, -half, z),
            (half, -half, z),
            (half, half, z),
            (-half, half, z),
        ])
    return vertices


def _build_edges(tiers: int) -> List[tuple[int, int]]:
    edges: List[tuple[int, int]] = []
    levels = tiers + 1
    for level in range(levels):
        base = level * 4
        edges.extend([
            (base + 0, base + 1),
            (base + 1, base + 2),
            (base + 2, base + 3),
            (base + 3, base + 0),
        ])
    for level in range(tiers):
        base_lower = level * 4
        base_upper = (level + 1) * 4
        for corner in range(4):
            edges.append((base_lower + corner, base_upper + corner))
    return edges


def _build_faces(tiers: int) -> List[Face]:
    faces: List[Face] = []
    faces.append(cast(Face, (0, 1, 2, 3)))
    levels = tiers + 1
    top_base = (levels - 1) * 4
    faces.append(cast(Face, (top_base + 0, top_base + 1, top_base + 2, top_base + 3)))
    for level in range(tiers):
        base_lower = level * 4
        base_upper = (level + 1) * 4
        faces.append(cast(Face, (base_lower + 0, base_lower + 1, base_upper + 1, base_upper + 0)))
        faces.append(cast(Face, (base_lower + 1, base_lower + 2, base_upper + 2, base_upper + 1)))
        faces.append(cast(Face, (base_lower + 2, base_lower + 3, base_upper + 3, base_upper + 2)))
        faces.append(cast(Face, (base_lower + 3, base_lower + 0, base_upper + 0, base_upper + 3)))
    return faces


def _compute_metrics(base_edge: float, top_edge: float, height: float, tiers: int) -> StepPyramidMetrics:
    if tiers <= 0:
        raise ValueError('Tiers must be at least 1')
    if top_edge <= 0 or base_edge <= 0 or height <= 0:
        raise ValueError('Dimensions must be positive')
    if top_edge >= base_edge:
        raise ValueError('Top edge must be smaller than base edge for a step pyramid')
    step_height = height / tiers
    edges = [base_edge - (base_edge - top_edge) * (i / tiers) for i in range(tiers)]
    tier_edges = edges + [top_edge]
    base_area = base_edge ** 2
    top_area = top_edge ** 2
    lateral_area = 4.0 * step_height * sum(edges)
    volume = step_height * sum(edge ** 2 for edge in edges)
    surface_area = lateral_area + base_area + top_area
    return StepPyramidMetrics(
        base_edge=base_edge,
        top_edge=top_edge,
        height=height,
        tiers=tiers,
        step_height=step_height,
        base_area=base_area,
        top_area=top_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        tier_edges=tier_edges,
    )


def _build_payload(base_edge: float, top_edge: float, height: float, tiers: int) -> SolidPayload:
    edge_sizes = _interpolate_edges(base_edge, top_edge, tiers)
    vertices = _build_vertices(edge_sizes, height)
    edges = _build_edges(tiers)
    faces = _build_faces(tiers)
    metrics = _compute_metrics(base_edge, top_edge, height, tiers)
    labels = [
        SolidLabel(text=f"a₀ = {metrics.base_edge:.2f}", position=(-metrics.base_edge / 2.0, 0.0, -metrics.height / 2.0)),
        SolidLabel(text=f"aₜ = {metrics.top_edge:.2f}", position=(0.0, metrics.top_edge / 2.0, metrics.height / 2.0)),
        SolidLabel(text=f"tiers = {metrics.tiers}", position=(0.0, 0.0, 0.0)),
    ]
    return SolidPayload(
        vertices=vertices,
        edges=edges,
        faces=faces,
        labels=labels,
        metadata={
            'base_edge': metrics.base_edge,
            'top_edge': metrics.top_edge,
            'height': metrics.height,
            'tiers': metrics.tiers,
            'step_height': metrics.step_height,
            'base_area': metrics.base_area,
            'top_area': metrics.top_area,
            'lateral_area': metrics.lateral_area,
            'surface_area': metrics.surface_area,
            'volume': metrics.volume,
            'tier_edges': metrics.tier_edges,
        },
        suggested_scale=max(base_edge, height),
    )


class StepPyramidSolidService:
    """Generates payloads for terraced square pyramids."""

    @staticmethod
    def build(base_edge: float = 200.0, top_edge: float = 60.0, height: float = 120.0, tiers: int = 5) -> StepPyramidSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
            tiers: Description of tiers.
        
        Returns:
            Result of build operation.
        """
        metrics = _compute_metrics(base_edge, top_edge, height, tiers)
        payload = _build_payload(base_edge, top_edge, height, tiers)
        return StepPyramidSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(base_edge: float = 200.0, top_edge: float = 60.0, height: float = 120.0, tiers: int = 5) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
            tiers: Description of tiers.
        
        Returns:
            Result of payload operation.
        """
        return StepPyramidSolidService.build(base_edge, top_edge, height, tiers).payload


class StepPyramidSolidCalculator:
    """Calculator for terraced step pyramids."""

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 3, True),
        ('top_edge', 'Top Edge', 'units', 3, True),
        ('height', 'Height', 'units', 3, True),
        ('tiers', 'Tiers', '', 0, True),
        ('step_height', 'Step Height', 'units', 3, False),
        ('base_area', 'Base Area', 'units²', 3, False),
        ('top_area', 'Top Area', 'units²', 3, False),
        ('lateral_area', 'Lateral Area', 'units²', 3, False),
        ('surface_area', 'Surface Area', 'units²', 3, False),
        ('volume', 'Volume', 'units³', 3, False),
    )

    def __init__(self, base_edge: float = 200.0, top_edge: float = 60.0, height: float = 120.0, tiers: int = 5):
        """
          init   logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
            tiers: Description of tiers.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge
        self._top_edge = top_edge
        self._height = height
        self._tiers = max(1, int(round(tiers)))
        self._result: Optional[StepPyramidSolidResult] = None
        self._apply_dimensions(self._base_edge, self._top_edge, self._height, self._tiers)

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
            self._apply_dimensions(value, self._top_edge, self._height, self._tiers)
            return True
        if key == 'top_edge':
            if value >= self._base_edge:
                return False
            self._apply_dimensions(self._base_edge, value, self._height, self._tiers)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_edge, self._top_edge, value, self._tiers)
            return True
        if key == 'tiers':
            tiers = max(1, int(round(value)))
            self._apply_dimensions(self._base_edge, self._top_edge, self._height, tiers)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_edge = 200.0
        self._top_edge = 60.0
        self._height = 120.0
        self._tiers = 5
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

    def metrics(self) -> Optional[StepPyramidMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_edge: float, top_edge: float, height: float, tiers: int):
        if base_edge <= 0 or top_edge <= 0 or height <= 0 or tiers <= 0 or top_edge >= base_edge:
            return
        self._base_edge = base_edge
        self._top_edge = top_edge
        self._height = height
        self._tiers = tiers
        result = StepPyramidSolidService.build(base_edge, top_edge, height, tiers)
        self._result = result
        values = {
            'base_edge': result.metrics.base_edge,
            'top_edge': result.metrics.top_edge,
            'height': result.metrics.height,
            'tiers': float(result.metrics.tiers),
            'step_height': result.metrics.step_height,
            'base_area': result.metrics.base_area,
            'top_area': result.metrics.top_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'StepPyramidMetrics',
    'StepPyramidSolidResult',
    'StepPyramidSolidService',
    'StepPyramidSolidCalculator',
]