"""Tesseract (hypercube) solid service and calculator.

THE FOUR-DIMENSIONAL HYPERCUBE:
===============================

DEFINITION:
-----------
A tesseract (or 8-cell) is the 4-dimensional analog of the cube—a regular
polytope in 4D space with 8 cubic cells, 24 square faces, 32 edges, and
16 vertices.

Just as:
- 1D: Line segment (2 points)
- 2D: Square (4 vertices, 4 edges)
- 3D: Cube (8 vertices, 12 edges, 6 faces)
- 4D: Tesseract (16 vertices, 32 edges, 24 faces, 8 cells)

DIMENSIONAL PATTERN:
--------------------
The n-cube (hypercube in n dimensions) follows beautiful recursive patterns:

Vertices: V(n) = 2^n
- Point (0D): 1 = 2^0
- Segment (1D): 2 = 2^1
- Square (2D): 4 = 2^2
- Cube (3D): 8 = 2^3
- Tesseract (4D): 16 = 2^4 ✓

Edges: E(n) = n × 2^(n-1)
- Point: 0
- Segment: 1 = 1×2^0
- Square: 4 = 2×2^1
- Cube: 12 = 3×2^2
- Tesseract: 32 = 4×2^3 ✓

Faces (2D): F(n) = (n choose 2) × 2^(n-2)
- Cube: 6 = (3 choose 2) × 2^1 = 3×2 = 6
- Tesseract: 24 = (4 choose 2) × 2^2 = 6×4 = 24 ✓

Cells (3D): C(n) = (n choose 3) × 2^(n-3)
- Tesseract: 8 = (4 choose 3) × 2^1 = 4×2 = 8 ✓

AHA MOMENT #1: DIMENSIONAL DOUBLING
====================================
Each dimension adds a NEW DEGREE OF FREEDOM by "sweeping" the previous
shape through the new axis!

Construction by extrusion:
- Point (0D) + sweep 1 unit → Segment (1D)
- Square (2D) + sweep 1 unit → Cube (3D)
- Cube (3D) + sweep 1 unit into 4D → Tesseract (4D)!

When you extrude a cube along the 4th axis (w-direction):
- Original cube at w=0
- Copy of cube at w=1
- Connect corresponding vertices with edges → 8 new edges
- Each edge of original cube sweeps out a square → 12 new faces
- Each face of original cube sweeps out a cube → 6 new cells
- Result: 2 cubes + 6 "side" cubes = 8 cubic cells total

The tesseract is TWO CUBES connected through hyperspace!

Analogy: A cube is two squares (top/bottom) connected by four side squares.
A tesseract is two cubes ("inner"/"outer" in Schlegel projection) connected
by six side cubes.

TESSERACT STRUCTURE:
====================

16 Vertices (coordinates in 4D):
- All combinations of (±1, ±1, ±1, ±1)
- Examples: (1,1,1,1), (1,1,1,-1), (1,1,-1,1), ...

32 Edges:
- Each vertex connects to 4 others (one per dimension)
- Total: 16×4 / 2 = 32

24 Square Faces:
- 6 faces per cube × 8 cubes? No! Faces are shared.
- Actually: (4 choose 2) × 2^2 = 6 × 4 = 24
- Each face lies in a 2D plane in 4-space

8 Cubic Cells:
- The "hypersurfaces" of the tesseract
- In 3D, cube has 6 square faces (2D boundaries)
- In 4D, tesseract has 8 cubic cells (3D boundaries)

AHA MOMENT #2: SCHLEGEL PROJECTION - 4D INTO 3D
================================================
We cannot visualize 4D objects directly, so we use PROJECTION!

The Schlegel diagram is like looking at the tesseract from "hyperspace
outside one cell" and projecting onto 3D space:

Analogy:
- Wire-frame cube drawing on paper = 3D cube projected to 2D
- One face of cube becomes outer boundary (square)
- Other faces appear inside as smaller squares/quadrilaterals
- Result: nested structure (small square inside large square)

For tesseract:
- One cubic cell becomes outer boundary (large cube)
- Other 7 cells appear inside as smaller/distorted cubes
- Result: CUBE WITHIN A CUBE (nested cubes)

The Schlegel projection creates:
- Outer cube (8 vertices): The boundary cell
- Inner cube (8 vertices): Projection of opposite cell
- 6 frustum shapes connecting them: The other 6 cells distorted

This is why our implementation has:
- `outer`: 8 vertices at scale 1.0
- `inner`: 8 vertices at scale 0.5
- Connector faces: Trapezoidal faces linking outer to inner

The "cube within cube" is the 3D SHADOW of the 4D tesseract!

AHA MOMENT #3: HYPERVOLUME AND HYPERSURFACE
============================================
In 4D, we measure HYPERVOLUME (4D content) and HYPERSURFACE (3D boundary)!

For a tesseract with edge length a:

Hypervolume: V₄ = a⁴
- Just as cube volume = a³, tesseract hypervolume = a⁴
- Counts 4D "space" enclosed

Hypersurface: S₃ = 8a³
- The tesseract has 8 cubic cells, each with volume a³
- Total 3D "surface" = 8a³
- This is like how cube has 6 faces, each area a²

Surface (2D faces): S₂ = 24a²
- 24 square faces, each area a²

Edge length (1D): E₁ = 32a
- 32 edges, each length a

The dimensional cascade:
- 0D: 16 vertices (points)
- 1D: 32 edges (lines, total length 32a)
- 2D: 24 faces (squares, total area 24a²)
- 3D: 8 cells (cubes, total volume 8a³)
- 4D: 1 hypercell (tesseract, hypervolume a⁴)

Each dimension's content is measured in a^n!

ROTATION IN 4D:
===============
A 4D object can rotate in SIX independent planes:
- xy-plane (like normal 3D rotation)
- xz-plane
- yz-plane
- xw-plane (rotation involving 4th dimension!)
- yw-plane
- zw-plane

In 3D, we rotate around axes (3 degrees of freedom: x, y, z).
In 4D, we rotate within planes (6 degrees of freedom: xy, xz, yz, xw, yw, zw).

When a tesseract rotates in 4D space and we view its 3D projection,
we see cubes morph, expand, contract, and transform in mind-bending ways!

HERMETIC NOTE - THE GEOMETRY OF HIGHER DIMENSIONS:
===================================================
The tesseract represents TRANSCENDENCE BEYOND ORDINARY SPACE:

- **Fourth Dimension**: Time? Hyperspace? Spiritual realm?
- **Nested Cubes**: Inner knowledge within outer manifestation
- **Sixteen Vertices**: 2^4 = complete exploration of 4 binary choices
- **Eight Cells**: Octave completion (8 = 2³, fundamental cycle)

Symbolism:
- **4D Space**: Dimensions beyond physical (astral, mental, spiritual)
- **Hypercube**: The mind's ability to conceive beyond sensory limits
- **Projection**: How higher truths appear when "flattened" to our realm
- **Rotation**: Shifting perspective reveals hidden aspects

In Mystical Traditions:
- **Platonic**: The realm of Forms (beyond physical 3D space)
- **Hermetic**: "As above, so below" - each dimension reflects higher
- **Theosophical**: The astral plane (4D space of thought-forms)
- **Modern**: Spacetime (3 space + 1 time dimension)

The tesseract is the geometry of WHAT LIES BEYOND—the shape of
possibilities we cannot directly perceive but can rationally construct.

It demonstrates that MATHEMATICS transcends physical limitation. We
cannot see 4D, yet we can reason about it, calculate it, project it.

The tesseract is the THRONE ROOM OF PURE REASON—a space our senses
cannot enter, but our minds can inhabit.

PHYSICAL ANALOGIES:
===================
While true 4D objects don't exist in our 3D space, the tesseract
appears metaphorically:

- **Spacetime**: Events in 4D spacetime (x,y,z,t)
- **Phase Space**: 4D state spaces in dynamical systems
- **Quantum**: 4D Hilbert space representations
- **Data**: 4D datasets (x,y,z + time or + value)

The tesseract is the archetypal HYPERSHAPE—the mind's eye viewing
dimensions beyond the physical.

HISTORICAL NOTE:
================
- **Hinton (1880s)**: Popularized 4D geometry and coined "tesseract"
- **Abbott (1884)**: "Flatland" - dimensional analogy (2D → 3D :: 3D → 4D)
- **Einstein (1905)**: Spacetime as 4D manifold
- **Dalí (1954)**: "Crucifixion (Corpus Hypercubus)" - tesseract cross painting
- **Marvel (2011-2019)**: Tesseract as "cosmic cube" containing Infinity Stone

The tesseract captures human fascination with realms beyond perception—
the geometry of the transcendent, the mathematical, the impossible-yet-real.

This implementation uses a Schlegel projection to represent the 4D tesseract
in 3D space, creating the characteristic "cube within a cube" structure.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Type

from ..shared.solid_payload import SolidLabel, SolidPayload, Vec3, Face
from .solid_geometry import (
    compute_surface_area,
    compute_volume,
    edges_from_faces,
    vec_length,
    vec_sub,
)
from .solid_property import SolidProperty


def _build_vertices() -> List[Vec3]:
    outer = [
        (-1.0, -1.0, -1.0),
        (1.0, -1.0, -1.0),
        (1.0, 1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
        (1.0, -1.0, 1.0),
        (1.0, 1.0, 1.0),
        (-1.0, 1.0, 1.0),
    ]
    inner = [(vx * 0.5, vy * 0.5, vz * 0.5) for vx, vy, vz in outer]
    return outer + inner


_BASE_VERTICES: List[Vec3] = _build_vertices()
_OUTER_FACES: List[Face] = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (1, 2, 6, 5),
    (2, 3, 7, 6),
    (3, 0, 4, 7),
]
_INNER_FACE_OFFSET = 8
_INNER_FACES: List[Face] = [
    tuple(vertex + _INNER_FACE_OFFSET for vertex in face)
    for face in _OUTER_FACES
]
_CUBE_EDGES: List[Tuple[int, int]] = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]
_CONNECTOR_FACES: List[Face] = [
    (u, v, v + _INNER_FACE_OFFSET, u + _INNER_FACE_OFFSET)
    for u, v in _CUBE_EDGES
]
_FACES: List[Face] = [*_OUTER_FACES, *_INNER_FACES, *_CONNECTOR_FACES]
_EDGES = edges_from_faces(_FACES)
edge_vec = vec_sub(_BASE_VERTICES[_EDGES[0][0]], _BASE_VERTICES[_EDGES[0][1]])
_BASE_EDGE_LENGTH = vec_length(edge_vec)
_BASE_SURFACE_AREA = compute_surface_area(_BASE_VERTICES, _FACES)
_BASE_VOLUME = compute_volume(_BASE_VERTICES, _FACES)
_FACE_SIDES: Dict[int, int] = {}
for face in _FACES:
    _FACE_SIDES[len(face)] = _FACE_SIDES.get(len(face), 0) + 1


@dataclass(frozen=True)
class TesseractMetrics:
    """
    Tesseract Metrics class definition.
    
    """
    edge_length: float
    surface_area: float
    volume: float
    face_count: int
    edge_count: int
    vertex_count: int
    face_sides: Dict[int, int]


@dataclass(frozen=True)
class TesseractSolidResult:
    """
    Tesseract Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: TesseractMetrics


class TesseractSolidService:
    """Service for generating Schlegel projection of a tesseract."""

    @staticmethod
    def build(edge_length: float = 2.0) -> TesseractSolidResult:
        """
        Build logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of build operation.
        """
        if edge_length <= 0:
            raise ValueError('Edge length must be positive')
        scale = edge_length / _BASE_EDGE_LENGTH
        vertices: List[Vec3] = [
            (vx * scale, vy * scale, vz * scale)
            for vx, vy, vz in _BASE_VERTICES
        ]
        faces: List[Face] = list(_FACES)
        edges = list(_EDGES)
        surface_area = compute_surface_area(vertices, faces)
        volume = compute_volume(vertices, faces)
        bbox_max_z = max(v[2] for v in vertices)
        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=[
                SolidLabel(text=f"e = {edge_length:.3f}", position=(0.0, 0.0, bbox_max_z + edge_length * 0.25)),
            ],
            metadata={
                'edge_length': edge_length,
                'surface_area': surface_area,
                'volume': volume,
                'face_count': len(faces),
                'edge_count': len(edges),
                'vertex_count': len(vertices),
                'face_sides': dict(_FACE_SIDES),
            },
            suggested_scale=edge_length,
        )
        metrics = TesseractMetrics(
            edge_length=edge_length,
            surface_area=surface_area,
            volume=volume,
            face_count=len(faces),
            edge_count=len(edges),
            vertex_count=len(vertices),
            face_sides=dict(_FACE_SIDES),
        )
        return TesseractSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(edge_length: float = 2.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of payload operation.
        """
        return TesseractSolidService.build(edge_length).payload


class TesseractSolidCalculator:
    """Simple calculator enabling edge/area/volume control for the tesseract."""

    SERVICE: Type[TesseractSolidService] = TesseractSolidService

    _PROPERTY_DEFINITIONS = (
        ('edge_length', 'Edge Length', 'units', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
        ('face_count', 'Faces', '', 0, False),
        ('edge_count', 'Edges', '', 0, False),
        ('vertex_count', 'Vertices', '', 0, False),
    )

    def __init__(self, edge_length: float = 2.0):
        """
          init   logic.
        
        Args:
            edge_length: Description of edge_length.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._edge_length = edge_length if edge_length > 0 else 2.0
        self._result: TesseractSolidResult | None = None
        self._apply_edge_length(self._edge_length)

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: float | None) -> bool:
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
        if key == 'edge_length':
            self._apply_edge_length(value)
            return True
        if key == 'volume' and _BASE_VOLUME > 0:
            scale = (value / _BASE_VOLUME) ** (1.0 / 3.0)
            target_edge = _BASE_EDGE_LENGTH * scale
            self._apply_edge_length(target_edge)
            return True
        if key == 'surface_area' and _BASE_SURFACE_AREA > 0:
            scale = math.sqrt(value / _BASE_SURFACE_AREA)
            target_edge = _BASE_EDGE_LENGTH * scale
            self._apply_edge_length(target_edge)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._edge_length = 2.0
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> SolidPayload | None:
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

    def metrics(self) -> TesseractMetrics | None:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_edge_length(self, edge_length: float):
        if edge_length <= 0:
            return
        result = self.SERVICE.build(edge_length=edge_length)
        self._result = result
        values = {
            'edge_length': result.metrics.edge_length,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'face_count': float(result.metrics.face_count),
            'edge_count': float(result.metrics.edge_count),
            'vertex_count': float(result.metrics.vertex_count),
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'TesseractMetrics',
    'TesseractSolidResult',
    'TesseractSolidService',
    'TesseractSolidCalculator',
]