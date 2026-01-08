"""Cube solid math utilities and calculator.

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
    (-1.0, -1.0, -1.0),
    (1.0, -1.0, -1.0),
    (1.0, 1.0, -1.0),
    (-1.0, 1.0, -1.0),
    (-1.0, -1.0, 1.0),
    (1.0, -1.0, 1.0),
    (1.0, 1.0, 1.0),
    (-1.0, 1.0, 1.0),
]

_FACES: List[Face] = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (1, 2, 6, 5),
    (2, 3, 7, 6),
    (3, 0, 4, 7),
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
_BASE_FACE_DIAGONAL = math.dist(_BASE_VERTICES[0], _BASE_VERTICES[2])
_BASE_SPACE_DIAGONAL = math.dist(_BASE_VERTICES[0], _BASE_VERTICES[6])
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS

# Topology constants
_TOPOLOGY = TOPOLOGY[PlatonicSolid.CUBE]
_DIHEDRAL_DEG = DIHEDRAL_ANGLES_DEG[PlatonicSolid.CUBE]
_SOLID_ANGLE_SR = SOLID_ANGLES_SR[PlatonicSolid.CUBE]

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
# MOI (solid) = k * ρ * V * a² where V scales as a³, so total scaling is a⁵
# At unit density, MOI = k * V * a² = k * base_vol * edge² (power 5)
_MOI_K_SOLID = MOMENT_INERTIA_SOLID_K[PlatonicSolid.CUBE]
_MOI_K_SHELL = MOMENT_INERTIA_SHELL_K[PlatonicSolid.CUBE]
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH

# Advanced constants (read-only)
_ANGULAR_DEFECT_DEG = ANGULAR_DEFECT_VERTEX_DEG[PlatonicSolid.CUBE]
_PACKING_DENSITY = PACKING_DENSITY[PlatonicSolid.CUBE]
_SYMMETRY_ORDER = SYMMETRY_GROUP_ORDER[PlatonicSolid.CUBE]
_ROTATION_ORDER = ROTATIONAL_SYMMETRY_ORDER[PlatonicSolid.CUBE]
_SYMMETRY_NAME = SYMMETRY_GROUP_NAME[PlatonicSolid.CUBE]
_DUAL_NAME = DUAL_SOLID_NAME[PlatonicSolid.CUBE]
_GOLDEN_FACTOR = GOLDEN_RATIO_FACTOR[PlatonicSolid.CUBE]


@dataclass(frozen=True)
class CubeMetrics:
    """Comprehensive metrics for a cube."""
    # Core dimensions
    edge_length: float
    face_area: float
    surface_area: float
    volume: float
    face_diagonal: float
    space_diagonal: float
    
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
    moment_inertia_solid: float = 0.0  # Solid body MOI about centroid
    moment_inertia_shell: float = 0.0  # Hollow shell MOI about centroid
    
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
class CubeSolidResult:
    """
    Cube Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: CubeMetrics


def _scaled_value(base_value: float, edge_length: float, power: float) -> float:
    scale = edge_length / _BASE_EDGE_LENGTH
    return base_value * (scale ** power)


def _scale_vertices(edge_length: float) -> List[Vec3]:
    scale = edge_length / _BASE_EDGE_LENGTH
    return [
        (vx * scale, vy * scale, vz * scale)
        for vx, vy, vz in _BASE_VERTICES
    ]


def _compute_metrics(edge_length: float) -> CubeMetrics:
    """
    Compute all geometric metrics for a cube from edge length.

    CORE DIMENSION FORMULAS & DERIVATIONS:
    ========================================

    Face Area: A_face = a²
    -----------------------
    Each face is a square with side length a.
    Area of square = side² = a²

    Surface Area: A = 6a²
    ---------------------
    Cube has 6 identical square faces.
    Total surface area = 6 × a² = 6a²

    Volume: V = a³
    ---------------
    Volume of rectangular prism = length × width × height
    For cube: all dimensions equal = a × a × a = a³

    Face Diagonal: d_face = a√2
    ----------------------------
    Diagonal of square face using Pythagorean theorem:
    d² = a² + a² = 2a²
    d = a√2

    Space Diagonal: d_space = a√3
    ------------------------------
    Diagonal through cube connecting opposite vertices.
    Using 3D Pythagorean theorem:
    d² = a² + a² + a² = 3a²
    d = a√3

    AHA MOMENT #1: PERFECT SYMMETRY
    =================================
    The cube is the ONLY Platonic solid where all face angles, dihedral angles,
    and coordinate alignments are 90°—the angle of perfect orthogonality.
    
    This creates three independent, perpendicular axes of fourfold rotational
    symmetry (through opposite face centers). No other Platonic solid achieves
    this perfect Cartesian alignment.
    
    The cube is the geometric embodiment of the coordinate system itself:
    - 3 pairs of parallel faces → 3 perpendicular planes
    - 8 vertices → 8 octants of 3D space (±x, ±y, ±z combinations)
    - 12 edges → 12 coordinate-aligned segments (4 per axis)

    SPHERE RADII FORMULAS & DERIVATIONS:
    =====================================

    Inradius (Inscribed Sphere): r = a/2
    -------------------------------------
    The inscribed sphere touches the center of each face.
    Distance from cube center to face center = half edge length.
    r = a/2

    Geometric Intuition:
    - Place cube with vertices at (±a/2, ±a/2, ±a/2)
    - Center at origin (0,0,0)
    - Face centers at (±a/2, 0, 0), (0, ±a/2, 0), (0, 0, ±a/2)
    - Distance from origin to any face center = a/2 ✓

    Derivation using volume-to-surface-area ratio:
    For any polyhedron with an inscribed sphere: r = 3V/A
    
    r = 3 × a³ / (6a²)
      = 3a³ / 6a²
      = a/2 ✓
    
    This confirms the geometric result and shows the cube's elegant simplicity:
    the ratio 3V/A reduces perfectly to half the edge length.

    Midradius (Midsphere): ρ = a√2/2
    ---------------------------------
    The midsphere touches the midpoint of each edge.
    
    Edge midpoint calculation (for canonical cube centered at origin):
    Midpoint of bottom front edge: (0, -a/2, -a/2)
    Distance from origin = √(0² + (a/2)² + (a/2)²)
                        = √(a²/4 + a²/4)
                        = √(a²/2)
                        = a/√2
                        = a√2/2 ✓

    Rationalized form:
    ρ = a/√2 × (√2/√2) = a√2/2
    
    Numerical value: ρ ≈ 0.7071067812a

    Alternative derivation via face diagonal:
    - Face diagonal = a√2
    - Edge midpoint lies at distance (face_diagonal / 2) from center
    - ρ = a√2 / 2 ✓

    Circumradius (Circumscribed Sphere): R = a√3/2
    -----------------------------------------------
    The circumscribed sphere passes through all 8 vertices.
    
    Canonical vertex at (a/2, a/2, a/2):
    Distance from origin = √((a/2)² + (a/2)² + (a/2)²)
                        = √(3 × a²/4)
                        = √(3a²/4)
                        = a√3/2 ✓

    Rationalized form already optimal.
    Numerical value: R ≈ 0.8660254038a

    Alternative Derivation via Space Diagonal:
    - Space diagonal connects opposite vertices
    - Length = a√3 (derived above)
    - Circumradius = half the space diagonal = a√3/2 ✓

    SPHERE RATIO RELATIONSHIPS:
    ===========================
    r : ρ : R = a/2 : a√2/2 : a√3/2
               = 1 : √2 : √3
    
    Key ratios:
    - R/r = (a√3/2) / (a/2) = √3 ≈ 1.732
      The circumradius is exactly √3 times the inradius!
    - ρ/r = (a√2/2) / (a/2) = √2 ≈ 1.414
    - R/ρ = (a√3/2) / (a√2/2) = √3/√2 = √(3/2) ≈ 1.225

    AHA MOMENT #2: PYTHAGOREAN PROGRESSION
    ========================================
    The cube's three radii form a Pythagorean sequence:
    
    r : ρ : R = 1 : √2 : √3
    
    These are the square roots of the first three integers—the most fundamental
    sequence in geometry! This pattern reflects the cube's dimensional hierarchy:
    - Inradius (r = a/2): Distance along ONE axis (1D) → factor of √1 = 1
    - Midradius (ρ = a√2/2): Distance across TWO axes (2D) → factor of √2
    - Circumradius (R = a√3/2): Distance through THREE axes (3D) → factor of √3
    
    Each radius encodes the dimensionality it spans. No other Platonic solid
    exhibits such a clean progression from 1D through 3D.

    Dihedral Angle: 90° (π/2 radians)
    ==================================
    The dihedral angle is the angle between two adjacent faces along a shared edge.
    
    For the cube, this is trivially 90° because all faces are perpendicular to
    each other by construction (orthogonal coordinate planes).
    
    Formal derivation via face normals:
    Consider two adjacent square faces:
    - Bottom face (z = -a/2): normal = (0, 0, -1)
    - Front face (y = -a/2): normal = (0, -1, 0)
    
    Dot product of outward normals:
    (0, 0, -1) · (0, -1, 0) = 0
    
    Angle between normals: arccos(0) = 90°
    
    The dihedral angle is π minus the angle between outward normals:
    θ = π - π/2 = π/2 = 90° ✓

    AHA MOMENT #3: THE ONLY RIGHT-ANGLED PLATONIC SOLID
    =====================================================
    The cube is the ONLY Platonic solid with a right-angle (90°) dihedral.
    
    All other Platonic solids have acute or obtuse dihedrals:
    - Tetrahedron: ≈ 70.53° (acute)
    - Octahedron: ≈ 109.47° (obtuse)
    - Dodecahedron: ≈ 116.57° (obtuse)
    - Icosahedron: ≈ 138.19° (obtuse)
    
    The 90° dihedral is the geometric signature of the cube's space-filling
    property: only right angles allow perfect tessellation with no gaps.
    This makes the cube the ONLY Platonic solid that can tile 3D space.
    
    The cube is the "building block" of reality—literally!

    HERMETIC NOTE - THE EARTH ELEMENT:
    ====================================
    The cube represents EARTH in Platonic solid cosmology:

    Symbolism:
    - 6 faces = 6 directions of space (±x, ±y, ±z) = perfect containment
    - 90° angles everywhere = absolute stability and grounding
    - Packing density = 1.0 (fills space perfectly, no voids)
    - Only space-filling Platonic solid = foundation of all structure
    - Dual to octahedron (Air) = Earth as complement to Air

    Spiritual Correspondences:
    - Insphere (r = a/2): The kernel, the seed, potential compressed to unity
    - Midsphere (ρ = a√2/2): The growing boundary, expansion into 2D plane
    - Circumsphere (R = a√3/2): Full manifestation, actualization in 3D space

    The 1:√2:√3 progression encodes the unfolding of dimensionality:
    - Unity (√1) → the point (0D principle)
    - Duality (√2) → the diagonal (1D + 1D = 2D surface)
    - Trinity (√3) → the body (1D + 1D + 1D = 3D volume)

    Connection to Octahedron (Dual):
    - Cube vertices → Octahedron face centers
    - Cube face centers → Octahedron vertices
    - Cube edges → Octahedron edges (both have 12)
    
    This duality expresses the hermetic axiom: "As above, so below."
    Earth (Cube) and Air (Octahedron) are reciprocal manifestations—
    one dense and filling, the other sparse and flowing.

    Packing & Crystallography:
    - The cube is the fundamental unit of the cubic lattice
    - Salt crystals (NaCl), galena (PbS), pyrite (FeS₂) all form cubic structures
    - The physical universe's most stable configuration
    - Represents the principle of ORDER imposed on chaos
    """
    # Core dimensions (scale as area ~ a², volume ~ a³)
    face_area_val = _scaled_value(_BASE_FACE_AREA, edge_length, 2.0)
    surface_area_val = _scaled_value(_BASE_SURFACE_AREA, edge_length, 2.0)
    volume_val = _scaled_value(_BASE_VOLUME, edge_length, 3.0)

    # Sphere radii (scale linearly ~ a)
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
    
    return CubeMetrics(
        edge_length=edge_length,
        face_area=face_area_val,
        surface_area=surface_area_val,
        volume=volume_val,
        face_diagonal=_scaled_value(_BASE_FACE_DIAGONAL, edge_length, 1.0),
        space_diagonal=_scaled_value(_BASE_SPACE_DIAGONAL, edge_length, 1.0),
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


class CubeSolidService:
    """Generates payloads for cubes."""

    @staticmethod
    def build(edge_length: float = 1.0) -> CubeSolidResult:
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
                SolidLabel(text=f"V = {metrics.volume:.3f}", position=(0.0, -edge_length * 0.5, 0.0)),
            ],
            metadata={
                # Core
                'edge_length': metrics.edge_length,
                'face_area': metrics.face_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'face_diagonal': metrics.face_diagonal,
                'space_diagonal': metrics.space_diagonal,
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
        
        # Determine dual scale?
        # For reciprocal duals (canonical): dual_edge ~ 1/edge.
        # But for visualization, we usually want them to intersect nicely (e.g. sharing midsphere).
        # Our `compute_dual_payload` uses simple centroids.
        # Centroids of cube faces form an Octahedron.
        # Radius of centroids = base inradius.
        # Inradius of Cube = a/2.
        # Circumradius of Dual Octahedron = a/2.
        # Inradius of Dual Octahedron = (a/2) / sqrt(3) ???
        # If they share the midsphere (canonical duality), the edges are tangent to midsphere.
        # Our centroid method produces a dual vertices at distance = Inradius.
        # So the Dual is "inside". This avoids collision.
        # Let's keep scale=1.0 for now, meaning it's the "Polar Dual wrt Inscribed Sphere"?
        # No, it's the dual formed by centers of faces.
        # For Cube (size a), faces at +/- a/2. Centroids at (+/- a/2, 0, 0) etc.
        # Vertices of dual are at dist a/2.
        # Circumsphere of dual = Insphere of primal.
        # This makes the dual STRICTLY INSIDE the primal.
        # Visually good for "ghost".
        
        payload.dual = compute_dual_payload(payload)
        
        return CubeSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(edge_length: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            edge_length: Description of edge_length.
        
        Returns:
            Result of payload operation.
        """
        return CubeSolidService.build(edge_length).payload


class CubeSolidCalculator:
    """Bidirectional cube calculator with comprehensive properties."""

    _FORMULAS = {
        'face_area': r"A_f = a^2",
        'surface_area': r"A = 6a^2",
        'volume': r"V = a^3",
        'face_diagonal': r"d_f = a\sqrt{2}",
        'space_diagonal': r"d_s = a\sqrt{3}",
        'inradius': r"r = \frac{a}{2}",
        'midradius': r"\rho = \frac{a\sqrt{2}}{2}",
        'circumradius': r"R = \frac{a\sqrt{3}}{2}",
        'incircle_circumference': r"C_{in} = 2\pi r",
        'midsphere_circumference': r"C_{mid} = 2\pi \rho",
        'circumcircle_circumference': r"C_{circ} = 2\pi R",
        'face_inradius': r"r_f = \frac{a}{2}",
        'face_circumradius': r"R_f = \frac{a}{\sqrt{2}}",
        'insphere_surface_area': r"A_{in} = 4\pi r^2",
        'insphere_volume': r"V_{in} = \frac{4}{3}\pi r^3",
        'midsphere_surface_area': r"A_{mid} = 4\pi \rho^2",
        'midsphere_volume': r"V_{mid} = \frac{4}{3}\pi \rho^3",
        'circumsphere_surface_area': r"A_{circ} = 4\pi R^2",
        'circumsphere_volume': r"V_{circ} = \frac{4}{3}\pi R^3",
    }

    # Properties that can be used as input (editable, with power for scaling)
    _EDITABLE_PROPERTIES = (
        # (key, label, unit, precision, power, base_value)
        ('edge_length', 'Edge Length', 'units', 4, 1.0, _BASE_EDGE_LENGTH),
        ('face_area', 'Face Area', 'units²', 4, 2.0, _BASE_FACE_AREA),
        ('surface_area', 'Surface Area', 'units²', 4, 2.0, _BASE_SURFACE_AREA),
        ('volume', 'Volume', 'units³', 4, 3.0, _BASE_VOLUME),
        ('face_diagonal', 'Face Diagonal', 'units', 4, 1.0, _BASE_FACE_DIAGONAL),
        ('space_diagonal', 'Space Diagonal', 'units', 4, 1.0, _BASE_SPACE_DIAGONAL),
        ('inradius', 'Inradius', 'units', 4, 1.0, _BASE_INRADIUS),
        ('midradius', 'Midsphere Radius', 'units', 4, 1.0, _BASE_MIDRADIUS),
        ('circumradius', 'Circumradius', 'units', 4, 1.0, _BASE_CIRCUMRADIUS),
        ('incircle_circumference', 'Insphere Circumference', 'units', 4, 1.0, _BASE_INCIRC_CIRC),
        ('midsphere_circumference', 'Midsphere Circumference', 'units', 4, 1.0, _BASE_MID_CIRC),
        ('circumcircle_circumference', 'Circumsphere Circumference', 'units', 4, 1.0, _BASE_CIRCUM_CIRC),
        ('face_inradius', 'Face Inradius', 'units', 4, 1.0, _BASE_FACE_INRADIUS),
        ('face_circumradius', 'Face Circumradius', 'units', 4, 1.0, _BASE_FACE_CIRCUMRADIUS),
        ('insphere_surface_area', 'Insphere Surface Area', 'units²', 4, 2.0, _BASE_INSPHERE_SA),
        ('insphere_volume', 'Insphere Volume', 'units³', 4, 3.0, _BASE_INSPHERE_VOL),
        ('midsphere_surface_area', 'Midsphere Surface Area', 'units²', 4, 2.0, _BASE_MIDSPHERE_SA),
        ('midsphere_volume', 'Midsphere Volume', 'units³', 4, 3.0, _BASE_MIDSPHERE_VOL),
        ('circumsphere_surface_area', 'Circumsphere Surface Area', 'units²', 4, 2.0, _BASE_CIRCUMSPHERE_SA),
        ('circumsphere_volume', 'Circumsphere Volume', 'units³', 4, 3.0, _BASE_CIRCUMSPHERE_VOL),
        # Advanced (bidirectional)
        ('moment_inertia_solid', 'Moment of Inertia (Solid)', 'units⁵', 6, 5.0, _BASE_MOI_SOLID),
        ('moment_inertia_shell', 'Moment of Inertia (Shell)', 'units⁴', 6, 4.0, _BASE_MOI_SHELL),
    )

    # Read-only properties (constants or derived, not invertible)
    _READONLY_PROPERTIES = (
        # (key, label, unit, precision)
        ('faces', 'Faces', '', 0),
        ('edges', 'Edges', '', 0),
        ('vertices', 'Vertices', '', 0),
        ('face_sides', 'Face Sides', '', 0),
        ('vertex_valence', 'Vertex Valence', '', 0),
        ('dihedral_angle_deg', 'Dihedral Angle', '°', 2),
        ('solid_angle_sr', 'Solid Angle', 'sr', 4),
        ('sphericity', 'Sphericity', '', 4),
        ('isoperimetric_quotient', 'Isoperimetric Quotient', '', 4),
        ('surface_to_volume_ratio', 'Surface/Volume Ratio', '1/units', 4),
        # Advanced (read-only)
        ('angular_defect_vertex_deg', 'Angular Defect (Vertex)', '°', 2),
        ('total_angular_defect_deg', 'Total Angular Defect', '°', 0),
        ('euler_characteristic', 'Euler Characteristic', '', 0),
        ('packing_density', 'Packing Density', '', 4),
        ('symmetry_group_order', 'Symmetry Group Order', '', 0),
        ('rotational_symmetry_order', 'Rotational Symmetry Order', '', 0),
        ('symmetry_group_name', 'Symmetry Group', '', 0),
        ('dual_solid_name', 'Dual Solid', '', 0),
        ('golden_ratio_factor', 'Golden Ratio Factor', '', 4),
    )

    def __init__(self, edge_length: float = 1.0):
        # Build editable properties
        """
          init   logic.
        
        Args:
            edge_length: Description of edge_length.
        
        """
        self._properties: Dict[str, SolidProperty] = {}
        self._edge_solvers: Dict[str, callable] = {}
        
        for key, label, unit, precision, power, base_value in self._EDITABLE_PROPERTIES:
            self._properties[key] = SolidProperty(
                name=label,
                key=key,
                unit=unit,
                precision=precision,
                editable=True,
                formula=self._FORMULAS.get(key),
            )
            self._edge_solvers[key] = self._build_solver(base_value, power)
        
        # Build readonly properties
        for key, label, unit, precision in self._READONLY_PROPERTIES:
            self._properties[key] = SolidProperty(
                name=label,
                key=key,
                unit=unit,
                precision=precision,
                editable=False,
                formula=self._FORMULAS.get(key),
            )
        
        self._result: Optional[CubeSolidResult] = None
        if edge_length > 0:
            self._apply_edge(edge_length)

    @staticmethod
    def _build_solver(base_value: float, power: float):
        def solver(value: Optional[float]) -> Optional[float]:
            """
            Solver logic.
            
            Args:
                value: Description of value.
            
            Returns:
                Result of solver operation.
            """
            if value is None or value <= 0 or base_value <= 0:
                return None
            scale = (value / base_value) ** (1.0 / power)
            return scale * _BASE_EDGE_LENGTH
        return solver

    def properties(self) -> List[SolidProperty]:
        """Return all properties in display order."""
        order = [key for key, *_ in self._EDITABLE_PROPERTIES] + \
                [key for key, *_ in self._READONLY_PROPERTIES]
        return [self._properties[key] for key in order if key in self._properties]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """Set a property and recalculate all others."""
        if key not in self._edge_solvers or value is None or value <= 0:
            return False
        solver = self._edge_solvers[key]
        edge_length = solver(value)
        if edge_length is None or not math.isfinite(edge_length) or edge_length <= 0:
            return False
        self._apply_edge(edge_length)
        return True

    def clear(self):
        """
        Clear logic.
        
        """
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

    def metrics(self) -> Optional[CubeMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_edge(self, edge_length: float):
        result = CubeSolidService.build(edge_length)
        self._result = result
        m = result.metrics
        
        # Update all property values
        values = {
            'edge_length': m.edge_length,
            'face_area': m.face_area,
            'surface_area': m.surface_area,
            'volume': m.volume,
            'face_diagonal': m.face_diagonal,
            'space_diagonal': m.space_diagonal,
            'inradius': m.inradius,
            'midradius': m.midradius,
            'circumradius': m.circumradius,
            'incircle_circumference': m.incircle_circumference,
            'midsphere_circumference': m.midsphere_circumference,
            'circumcircle_circumference': m.circumcircle_circumference,
            'face_inradius': m.face_inradius,
            'face_circumradius': m.face_circumradius,
            'insphere_surface_area': m.insphere_surface_area,
            'insphere_volume': m.insphere_volume,
            'midsphere_surface_area': m.midsphere_surface_area,
            'midsphere_volume': m.midsphere_volume,
            'circumsphere_surface_area': m.circumsphere_surface_area,
            'circumsphere_volume': m.circumsphere_volume,
            # Constants
            'faces': m.faces,
            'edges': m.edges,
            'vertices': m.vertices,
            'face_sides': m.face_sides,
            'vertex_valence': m.vertex_valence,
            'dihedral_angle_deg': m.dihedral_angle_deg,
            'solid_angle_sr': m.solid_angle_sr,
            # Quality
            'sphericity': m.sphericity,
            'isoperimetric_quotient': m.isoperimetric_quotient,
            'surface_to_volume_ratio': m.surface_to_volume_ratio,
            # Advanced
            'moment_inertia_solid': m.moment_inertia_solid,
            'moment_inertia_shell': m.moment_inertia_shell,
            'angular_defect_vertex_deg': m.angular_defect_vertex_deg,
            'total_angular_defect_deg': m.total_angular_defect_deg,
            'euler_characteristic': m.euler_characteristic,
            'packing_density': m.packing_density,
            'symmetry_group_order': m.symmetry_group_order,
            'rotational_symmetry_order': m.rotational_symmetry_order,
            'symmetry_group_name': m.symmetry_group_name,
            'dual_solid_name': m.dual_solid_name,
            'golden_ratio_factor': m.golden_ratio_factor,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'CubeMetrics',
    'CubeSolidResult',
    'CubeSolidService',
    'CubeSolidCalculator',
]