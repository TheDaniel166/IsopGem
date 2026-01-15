
"""Octahedron solid math utilities and calculator.

Enhanced with comprehensive bidirectional properties including:
- Topology (faces, edges, vertices)
- Dihedrals and solid angles
- Face geometry (inradius, circumradius)
- Sphere metrics (inscribed/circumscribed surface area and volume)
- Quality metrics (sphericity, isoperimetric quotient)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from .solid_payload import SolidLabel, SolidPayload
from .solid_geometry import (
    Face,
    Vec3,
    compute_surface_area,
    compute_volume,
    edges_from_faces,
    plane_distance_from_origin,
    polygon_area,
    vec_length,
)
from .solid_property import SolidProperty
from .platonic_constants import (
    PlatonicSolid,
    TOPOLOGY,
    DIHEDRAL_ANGLES_DEG,
    SOLID_ANGLES_SR,
    MOMENT_INERTIA_SOLID_K,
    MOMENT_INERTIA_SHELL_K,
    ANGULAR_DEFECT_VERTEX_DEG,
    TOTAL_ANGULAR_DEFECT_DEG,
    PACKING_DENSITY,
    SYMMETRY_GROUP_ORDER,
    ROTATIONAL_SYMMETRY_ORDER,
    SYMMETRY_GROUP_NAME,
    DUAL_SOLID_NAME,
    GOLDEN_RATIO_FACTOR,
    face_inradius,
    face_circumradius,
    sphere_surface_area,
    sphere_volume,
    sphericity,
    isoperimetric_quotient,
    surface_to_volume_ratio,
)


_BASE_VERTICES: List[Vec3] = [
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, -1.0),
]

_FACES: List[Face] = [
    (0, 2, 4),
    (2, 1, 4),
    (1, 3, 4),
    (3, 0, 4),
    (2, 0, 5),
    (1, 2, 5),
    (3, 1, 5),
    (0, 3, 5),
]

_EDGES = edges_from_faces(_FACES)
_BASE_EDGE_LENGTH = math.dist(_BASE_VERTICES[_EDGES[0][0]], _BASE_VERTICES[_EDGES[0][1]])
_BASE_FACE_AREA = polygon_area(_BASE_VERTICES, _FACES[0])
_BASE_SURFACE_AREA = compute_surface_area(_BASE_VERTICES, _FACES)
_BASE_VOLUME = compute_volume(_BASE_VERTICES, _FACES)
_BASE_INRADIUS = plane_distance_from_origin(_BASE_VERTICES, _FACES[0])
_mid_edge = (
    (_BASE_VERTICES[_EDGES[0][0]][0] + _BASE_VERTICES[_EDGES[0][1]][0]) / 2.0,
    (_BASE_VERTICES[_EDGES[0][0]][1] + _BASE_VERTICES[_EDGES[0][1]][1]) / 2.0,
    (_BASE_VERTICES[_EDGES[0][0]][2] + _BASE_VERTICES[_EDGES[0][1]][2]) / 2.0,
)
_BASE_MIDRADIUS = vec_length(_mid_edge)
_BASE_CIRCUMRADIUS = vec_length(_BASE_VERTICES[0])
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS

# Topology constants
_TOPOLOGY = TOPOLOGY[PlatonicSolid.OCTAHEDRON]
_DIHEDRAL_DEG = DIHEDRAL_ANGLES_DEG[PlatonicSolid.OCTAHEDRON]
_SOLID_ANGLE_SR = SOLID_ANGLES_SR[PlatonicSolid.OCTAHEDRON]

# Face geometry at base edge
_BASE_FACE_INRADIUS = face_inradius(_BASE_EDGE_LENGTH, _TOPOLOGY.p)
_BASE_FACE_CIRCUMRADIUS = face_circumradius(_BASE_EDGE_LENGTH, _TOPOLOGY.p)

# Sphere metrics at base edge
_BASE_INSPHERE_SA = sphere_surface_area(_BASE_INRADIUS)
_BASE_MIDSPHERE_SA = sphere_surface_area(_BASE_MIDRADIUS)
_BASE_CIRCUMSPHERE_SA = sphere_surface_area(_BASE_CIRCUMRADIUS)
_BASE_INSPHERE_VOL = sphere_volume(_BASE_INRADIUS)
_BASE_MIDSPHERE_VOL = sphere_volume(_BASE_MIDRADIUS)
_BASE_CIRCUMSPHERE_VOL = sphere_volume(_BASE_CIRCUMRADIUS)

# Advanced physics: Moment of Inertia base values
_MOI_K_SOLID = MOMENT_INERTIA_SOLID_K[PlatonicSolid.OCTAHEDRON]
_MOI_K_SHELL = MOMENT_INERTIA_SHELL_K[PlatonicSolid.OCTAHEDRON]
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH

# Advanced constants (read-only)
_ANGULAR_DEFECT_DEG = ANGULAR_DEFECT_VERTEX_DEG[PlatonicSolid.OCTAHEDRON]
_PACKING_DENSITY = PACKING_DENSITY[PlatonicSolid.OCTAHEDRON]
_SYMMETRY_ORDER = SYMMETRY_GROUP_ORDER[PlatonicSolid.OCTAHEDRON]
_ROTATION_ORDER = ROTATIONAL_SYMMETRY_ORDER[PlatonicSolid.OCTAHEDRON]
_SYMMETRY_NAME = SYMMETRY_GROUP_NAME[PlatonicSolid.OCTAHEDRON]
_DUAL_NAME = DUAL_SOLID_NAME[PlatonicSolid.OCTAHEDRON]
_GOLDEN_FACTOR = GOLDEN_RATIO_FACTOR[PlatonicSolid.OCTAHEDRON]


@dataclass(frozen=True)
class OctahedronMetrics:
    """Comprehensive metrics for a regular octahedron."""
    # Core dimensions
    edge_length: float
    face_area: float
    surface_area: float
    volume: float
    
    # Sphere radii
    inradius: float
    midradius: float
    circumradius: float
    
    # Sphere circumferences
    incircle_circumference: float
    midsphere_circumference: float
    circumcircle_circumference: float
    
    # Topology (constants)
    faces: int = _TOPOLOGY.faces
    edges: int = _TOPOLOGY.edges
    vertices: int = _TOPOLOGY.vertices
    face_sides: int = _TOPOLOGY.p
    vertex_valence: int = _TOPOLOGY.q
    
    # Angles (constants)
    dihedral_angle_deg: float = _DIHEDRAL_DEG
    solid_angle_sr: float = _SOLID_ANGLE_SR
    
    # Face geometry
    face_inradius: float = 0.0
    face_circumradius: float = 0.0
    
    # Inscribed sphere
    insphere_surface_area: float = 0.0
    insphere_volume: float = 0.0
    
    # Midsphere
    midsphere_surface_area: float = 0.0
    midsphere_volume: float = 0.0
    
    # Circumscribed sphere
    circumsphere_surface_area: float = 0.0
    circumsphere_volume: float = 0.0
    
    # Quality metrics
    sphericity: float = 0.0
    isoperimetric_quotient: float = 0.0
    surface_to_volume_ratio: float = 0.0
    
    # =========================================================================
    # ADVANCED PROPERTIES
    # =========================================================================
    
    # Physics: Moment of Inertia (assumes unit density)
    moment_inertia_solid: float = 0.0
    moment_inertia_shell: float = 0.0
    
    # Topology: Angular Defect
    angular_defect_vertex_deg: float = _ANGULAR_DEFECT_DEG
    total_angular_defect_deg: float = TOTAL_ANGULAR_DEFECT_DEG
    euler_characteristic: int = 2
    
    # Packing
    packing_density: float = _PACKING_DENSITY
    
    # Symmetry
    symmetry_group_order: int = _SYMMETRY_ORDER
    rotational_symmetry_order: int = _ROTATION_ORDER
    symmetry_group_name: str = _SYMMETRY_NAME
    
    # Dual
    dual_solid_name: str = _DUAL_NAME
    
    # Golden ratio
    golden_ratio_factor: float = _GOLDEN_FACTOR


@dataclass(frozen=True)
class OctahedronSolidResult:
    """
    Octahedron Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: OctahedronMetrics


def _scaled_value(base_value: float, edge_length: float, power: float) -> float:
    scale = edge_length / _BASE_EDGE_LENGTH
    return base_value * (scale ** power)


def _scale_vertices(edge_length: float) -> List[Vec3]:
    scale = edge_length / _BASE_EDGE_LENGTH
    return [(vx * scale, vy * scale, vz * scale) for vx, vy, vz in _BASE_VERTICES]


def _compute_metrics(edge_length: float) -> OctahedronMetrics:
    """
    Compute all geometric metrics for a regular octahedron from edge length.

    CORE DIMENSION FORMULAS & DERIVATIONS:
    ========================================

    Face Area: A_face = (√3/4)a²
    ----------------------------
    Each face is an equilateral triangle with side length a.
    For equilateral triangle:
    - Height = (√3/2)a
    - Area = (1/2) × base × height
           = (1/2) × a × (√3/2)a
           = (√3/4)a² ✓

    Surface Area: A = 8 × (√3/4)a² = 2√3 a²
    ----------------------------------------
    Octahedron has 8 identical equilateral triangle faces.
    Total surface area = 8 × (√3/4)a² = 2√3 a²

    Volume: V = (√2/3)a³
    --------------------
    View the octahedron as two congruent square pyramids joined base-to-base.
    
    The equatorial "belt" forms a square with diagonal = distance between
    opposite vertices along the equator. For edge length a, this diagonal
    is a√2 (by the Pythagorean theorem on the square formed by 4 edges).
    Therefore, the square side length is (a√2)/√2 = a.
    Square base area = a².

    The distance between top and bottom vertices (poles) is a√2.
    Each pyramid has height h = (a√2)/2 = a/√2.

    Volume of one pyramid = (1/3) × base_area × height
                          = (1/3) × a² × (a/√2)
                          = a³/(3√2)
    
    Two pyramids:
    V = 2 × a³/(3√2) = 2a³/(3√2) × (√2/√2) = (2√2/6)a³ = (√2/3)a³ ✓

    Alternative derivation via canonical coordinates:
    Vertices at (±1,0,0), (0,±1,0), (0,0,±1)
    have edge length √2 and volume 4/3.
    Scaling by a/√2 gives V = (4/3)(a/√2)³ = (4/3)(a³/2√2) = (√2/3)a³ ✓

    AHA MOMENT #1: DUAL PYRAMID DECOMPOSITION
    ===========================================
    The octahedron is perfectly symmetric top-to-bottom. The equatorial square
    divides it into two identical pyramids. This is the inverse of the cube:
    - Cube: 6 square faces, 8 vertices
    - Octahedron: 8 triangular faces, 6 vertices
    The octahedron IS the dual of the cube!

    SPHERE RADII FORMULAS & DERIVATIONS:
    =====================================

    Inradius (Inscribed Sphere): r = a/√6 = a√6/6
    ----------------------------------------------
    The inscribed sphere touches the center of each face.

    Derivation using volume-to-surface-area ratio:
    For any polyhedron with an inscribed sphere: r = 3V/A

    r = 3 × [(√2/3)a³] / [2√3 a²]
      = (√2 a³) / (2√3 a²)
      = (√2 a) / (2√3)
      = a√2 / (2√3)
      = a / √6 ✓

    Rationalized form:
    r = a/√6 × (√6/√6) = a√6/6

    Geometric derivation (canonical coordinates):
    For the canonical octahedron with edge √2, a face plane equation is
    x + y + z = 1 (for the upper-front-right face).
    Distance from origin to plane = 1/√(1²+1²+1²) = 1/√3.
    
    For edge length a, scale factor = a/√2:
    r = (a/√2) × (1/√3) = a/√6 ✓

    Numerical value: r ≈ 0.4082482905a

    Midradius (Midsphere): ρ = a/2
    -------------------------------
    The midsphere touches the midpoint of each edge.

    Edge midpoint calculation for canonical vertices:
    Edge from (1,0,0) to (0,1,0) → midpoint (1/2, 1/2, 0)
    Distance from origin = √((1/2)² + (1/2)² + 0²) = √(1/2) = 1/√2
    
    For edge length a, scale by a/√2:
    ρ = (a/√2) × (1/√2) = a/2 ✓

    AHA MOMENT #2: PERFECT MIDPOINT
    =================================
    The midradius ρ = a/2 is exactly half the edge length!
    This is unique among the Platonic solids. It reflects the octahedron's
    perfect balance: edge midpoints lie at the "golden middle" between
    center and vertices.

    Circumradius (Circumscribed Sphere): R = a/√2 = a√2/2
    -------------------------------------------------------
    The circumscribed sphere passes through all 6 vertices.
    
    Canonical vertices are at distance 1 from origin.
    For edge length a, scale factor = a/√2:
    R = (a/√2) × 1 = a/√2 ✓

    Rationalized form:
    R = a/√2 × (√2/√2) = a√2/2

    Numerical value: R ≈ 0.7071067812a

    SPHERE RATIO RELATIONSHIPS:
    ===========================
    r : ρ : R = a√6/6 : a/2 : a√2/2
               = √6/6 : 1/2 : √2/2
               = √6 : 3 : 3√2
               ≈ 0.408 : 0.500 : 0.707

    Simplifying via common factor a/6:
    r : ρ : R = √6 : 3 : 3√2
    
    Key ratios:
    - R/r = (a√2/2) / (a√6/6) = 3√2/√6 = 3√(2/6) = 3/√3 = √3
      The circumradius is exactly √3 times the inradius!
    - ρ/r = (a/2) / (a√6/6) = 3/√6 = √(9/6) = √(3/2)
    - R/ρ = (a√2/2) / (a/2) = √2

    AHA MOMENT #3: THE √3 RATIO
    =============================
    R/r = √3 encodes the octahedron's threefold symmetry.
    The number 3 appears throughout:
    - 3 axes of fourfold rotation (through opposite vertices)
    - Each vertex is the meeting point of 4 triangular faces
    - 3 square cross-sections (through 4 edges each)

    Dihedral Angle: arccos(-1/3) ≈ 109.47°
    ========================================
    The dihedral angle is the angle between two adjacent faces along a shared edge.

    Consider two triangular faces meeting at an edge.
    Face normals for canonical octahedron faces:
    - Upper front right face (0, 2, 4): vertices (1,0,0), (0,1,0), (0,0,1)
      Normal = (1,1,1)/√3
    - Upper front left face (2, 1, 4): vertices (0,1,0), (-1,0,0), (0,0,1)
      Normal = (-1,1,1)/√3

    Dot product of normals:
    (1,1,1)·(-1,1,1) / 3 = (-1 + 1 + 1) / 3 = 1/3

    The dihedral angle θ is π minus the angle between outward normals:
    cos(θ) = -1/3
    θ = arccos(-1/3) ≈ 109.47° ✓

    This is the supplement of the tetrahedral angle arccos(1/3) ≈ 70.53°.
    This makes sense: the octahedron and tetrahedron are related by
    "stellation" operations.

    HERMETIC NOTE - THE AIR ELEMENT:
    ==================================
    The octahedron represents AIR in Platonic solid cosmology:

    Symbolism:
    - 8 triangular faces = balance of ascent and descent (4 up, 4 down)
    - Dual of the cube (earth) = air as the counterpoint to solidity
    - 6 vertices on 3 perpendicular axes = omnidirectional flow
    - Midradius ρ = a/2 (exactly half edge) = air's perfect mediation
    - Dihedral angle ≈109.47° (obtuse) = gentle, flowing angles

    Spiritual Correspondences:
    - Insphere (r ≈ 0.408a): The breath within, the vital center
    - Midsphere (ρ = 0.5a): The mediating boundary, perfect balance
    - Circumsphere (R ≈ 0.707a): The sphere of circulation

    The R/r = √3 ratio reflects Air's role as the mediator between
    the gross (Earth/Cube) and the subtle (Fire/Tetrahedron).

    Connection to Cube (Dual):
    - Octahedron vertices → Cube face centers
    - Octahedron faces → Cube vertices
    - Octahedron edges → Cube edges (same count: 12)
    This duality expresses the esoteric principle: "That which is above
    is like that which is below" — Air and Earth as complements.

    Packing:
    - Cannot fill 3D space alone
    - Packing density ≈ 0.7236 (when arranged optimally)
    - Represents Air's need for space to flow, inability to compress
      into a rigid lattice like the cube
    """
    # Core dimensions
    face_area_val = _scaled_value(_BASE_FACE_AREA, edge_length, 2.0)
    surface_area_val = _scaled_value(_BASE_SURFACE_AREA, edge_length, 2.0)
    volume_val = _scaled_value(_BASE_VOLUME, edge_length, 3.0)
    
    # Sphere radii
    inradius_val = _scaled_value(_BASE_INRADIUS, edge_length, 1.0)
    midradius_val = _scaled_value(_BASE_MIDRADIUS, edge_length, 1.0)
    circumradius_val = _scaled_value(_BASE_CIRCUMRADIUS, edge_length, 1.0)
    
    # Face geometry
    face_inradius_val = face_inradius(edge_length, _TOPOLOGY.p)
    face_circumradius_val = face_circumradius(edge_length, _TOPOLOGY.p)
    
    # Sphere metrics
    insphere_sa = sphere_surface_area(inradius_val)
    midsphere_sa = sphere_surface_area(midradius_val)
    circumsphere_sa = sphere_surface_area(circumradius_val)
    insphere_vol = sphere_volume(inradius_val)
    midsphere_vol = sphere_volume(midradius_val)
    circumsphere_vol = sphere_volume(circumradius_val)
    
    # Quality metrics
    sph = sphericity(volume_val, surface_area_val)
    iq = isoperimetric_quotient(volume_val, surface_area_val)
    sv_ratio = surface_to_volume_ratio(surface_area_val, volume_val)
    
    # Advanced physics: Moment of Inertia (unit density)
    moi_solid = _scaled_value(_BASE_MOI_SOLID, edge_length, 5.0)
    moi_shell = _scaled_value(_BASE_MOI_SHELL, edge_length, 4.0)
    
    return OctahedronMetrics(
        edge_length=edge_length,
        face_area=face_area_val,
        surface_area=surface_area_val,
        volume=volume_val,
        inradius=inradius_val,
        midradius=midradius_val,
        circumradius=circumradius_val,
        incircle_circumference=_scaled_value(_BASE_INCIRC_CIRC, edge_length, 1.0),
        midsphere_circumference=_scaled_value(_BASE_MID_CIRC, edge_length, 1.0),
        circumcircle_circumference=_scaled_value(_BASE_CIRCUM_CIRC, edge_length, 1.0),
        face_inradius=face_inradius_val,
        face_circumradius=face_circumradius_val,
        insphere_surface_area=insphere_sa,
        insphere_volume=insphere_vol,
        midsphere_surface_area=midsphere_sa,
        midsphere_volume=midsphere_vol,
        circumsphere_surface_area=circumsphere_sa,
        circumsphere_volume=circumsphere_vol,
        sphericity=sph,
        isoperimetric_quotient=iq,
        surface_to_volume_ratio=sv_ratio,
        # Advanced
        moment_inertia_solid=moi_solid,
        moment_inertia_shell=moi_shell,
    )


class OctahedronSolidService:
    """Generates payloads for regular octahedra."""

    @staticmethod
    def build(edge_length: float = 1.0) -> OctahedronSolidResult:
        """
        Build logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of build operation.
        """
        if edge_length <= 0:
            raise ValueError("Edge length must be positive")
        metrics = _compute_metrics(edge_length)
        from .geometry_visuals import compute_dual_payload

        payload = SolidPayload(
            vertices=_scale_vertices(edge_length),
            edges=list(_EDGES),
            faces=[tuple(face) for face in _FACES],
            labels=[
                SolidLabel(text=f"a = {edge_length:.3f}", position=(0.0, 0.0, 0.0)),
                SolidLabel(text=f"V = {metrics.volume:.3f}", position=(0.0, -edge_length * 0.35, 0.0)),
            ],
            metadata={
                # Core
                'edge_length': metrics.edge_length,
                'face_area': metrics.face_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                # Sphere radii
                'inradius': metrics.inradius,
                'midradius': metrics.midradius,
                'circumradius': metrics.circumradius,
                'incircle_circumference': metrics.incircle_circumference,
                'midsphere_circumference': metrics.midsphere_circumference,
                'circumcircle_circumference': metrics.circumcircle_circumference,
                # Topology
                'faces': metrics.faces,
                'edges': metrics.edges,
                'vertices': metrics.vertices,
                'face_sides': metrics.face_sides,
                'vertex_valence': metrics.vertex_valence,
                # Angles
                'dihedral_angle_deg': metrics.dihedral_angle_deg,
                'solid_angle_sr': metrics.solid_angle_sr,
                # Face geometry
                'face_inradius': metrics.face_inradius,
                'face_circumradius': metrics.face_circumradius,
                # Sphere metrics
                'insphere_surface_area': metrics.insphere_surface_area,
                'insphere_volume': metrics.insphere_volume,
                'midsphere_surface_area': metrics.midsphere_surface_area,
                'midsphere_volume': metrics.midsphere_volume,
                'circumsphere_surface_area': metrics.circumsphere_surface_area,
                'circumsphere_volume': metrics.circumsphere_volume,
                # Quality
                'sphericity': metrics.sphericity,
                'isoperimetric_quotient': metrics.isoperimetric_quotient,
                'surface_to_volume_ratio': metrics.surface_to_volume_ratio,
            },
            suggested_scale=edge_length,
        )
        payload.dual = compute_dual_payload(payload)
        return OctahedronSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(edge_length: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of payload operation.
        """
        return OctahedronSolidService.build(edge_length).payload




__all__ = [
    'OctahedronMetrics',
    'OctahedronSolidResult',
    'OctahedronSolidService',
]