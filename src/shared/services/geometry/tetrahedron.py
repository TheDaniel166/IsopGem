
"""Equilateral tetrahedron solid math + payload builder.

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
from typing import Dict, List, Optional, Tuple

from .solid_payload import Edge, Face, SolidLabel, SolidPayload, Vec3
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


# Canonical tetrahedron coordinates centered at the origin with edge length 2*sqrt(2).
_BASE_VERTICES: Tuple[Vec3, ...] = (
    (1.0, 1.0, 1.0),
    (-1.0, -1.0, 1.0),
    (-1.0, 1.0, -1.0),
    (1.0, -1.0, -1.0),
)
_BASE_EDGE_LENGTH = 2 * math.sqrt(2.0)
_EDGES: Tuple[Edge, ...] = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
)
_FACES: Tuple[Face, ...] = (
    (0, 1, 2),
    (0, 1, 3),
    (0, 2, 3),
    (1, 2, 3),
)

# Topology constants
_TOPOLOGY = TOPOLOGY[PlatonicSolid.TETRAHEDRON]
_DIHEDRAL_DEG = DIHEDRAL_ANGLES_DEG[PlatonicSolid.TETRAHEDRON]
_SOLID_ANGLE_SR = SOLID_ANGLES_SR[PlatonicSolid.TETRAHEDRON]

# Base metrics for scaling
_BASE_HEIGHT = math.sqrt(2.0 / 3.0) * _BASE_EDGE_LENGTH
_BASE_FACE_AREA = (math.sqrt(3.0) / 4.0) * _BASE_EDGE_LENGTH ** 2
_BASE_SURFACE_AREA = 4.0 * _BASE_FACE_AREA
_BASE_VOLUME = _BASE_EDGE_LENGTH ** 3 / (6.0 * math.sqrt(2.0))
_BASE_INRADIUS = _BASE_EDGE_LENGTH * math.sqrt(6.0) / 12.0
_BASE_MIDRADIUS = _BASE_EDGE_LENGTH * math.sqrt(2.0) / 4.0
_BASE_CIRCUMRADIUS = _BASE_EDGE_LENGTH * math.sqrt(6.0) / 4.0
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS

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
_MOI_K_SOLID = MOMENT_INERTIA_SOLID_K[PlatonicSolid.TETRAHEDRON]
_MOI_K_SHELL = MOMENT_INERTIA_SHELL_K[PlatonicSolid.TETRAHEDRON]
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH

# Advanced constants (read-only)
_ANGULAR_DEFECT_DEG = ANGULAR_DEFECT_VERTEX_DEG[PlatonicSolid.TETRAHEDRON]
_PACKING_DENSITY = PACKING_DENSITY[PlatonicSolid.TETRAHEDRON]
_SYMMETRY_ORDER = SYMMETRY_GROUP_ORDER[PlatonicSolid.TETRAHEDRON]
_ROTATION_ORDER = ROTATIONAL_SYMMETRY_ORDER[PlatonicSolid.TETRAHEDRON]
_SYMMETRY_NAME = SYMMETRY_GROUP_NAME[PlatonicSolid.TETRAHEDRON]
_DUAL_NAME = DUAL_SOLID_NAME[PlatonicSolid.TETRAHEDRON]
_GOLDEN_FACTOR = GOLDEN_RATIO_FACTOR[PlatonicSolid.TETRAHEDRON]


@dataclass(frozen=True)
class TetrahedronMetrics:
    """Comprehensive metrics for an equilateral tetrahedron."""
    
    # Core dimensions
    edge_length: float
    height: float
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
class TetrahedronSolidResult:
    """Bundled payload + metrics so callers can choose what they need."""
    payload: SolidPayload
    metrics: TetrahedronMetrics


def _scale_vertices(edge_length: float) -> List[Vec3]:
    scale = edge_length / _BASE_EDGE_LENGTH
    return [(vx * scale, vy * scale, vz * scale) for vx, vy, vz in _BASE_VERTICES]


def _compute_metrics(edge_length: float) -> TetrahedronMetrics:
    """
    Compute all geometric metrics for a regular tetrahedron from edge length.

    CORE DIMENSION FORMULAS & DERIVATIONS:
    ========================================

    Face Area: A_face = (√3/4)a²
    ----------------------------
    Each face is an equilateral triangle with side length a.
    For equilateral triangle:
    - Height of triangle = (√3/2)a
    - Area = (1/2) × base × height
           = (1/2) × a × (√3/2)a
           = (√3/4)a² ✓

    Surface Area: A = 4 × (√3/4)a² = √3 a²
    ----------------------------------------
    Tetrahedron has 4 identical equilateral triangle faces.
    Total surface area = 4 × (√3/4)a² = √3 a²

    Height: h = √(2/3) × a
    -----------------------
    Place tetrahedron with base on xy-plane, apex directly above centroid.
    Base is equilateral triangle with vertices forming a 2D centroid.

    Derivation using Pythagorean theorem in 3D:
    1. Centroid of base triangle is at distance r from each vertex
    2. For equilateral triangle: r = a/√3 (circumradius of triangle)
    3. Edge from apex to base vertex: length = a
    4. Using Pythagoras: a² = h² + r²
       a² = h² + (a/√3)²
       a² = h² + a²/3
       h² = a² - a²/3 = 2a²/3
       h = √(2/3) × a ✓

    Volume: V = a³/(6√2)
    --------------------
    Volume of pyramid = (1/3) × base_area × height

    For tetrahedral:
    V = (1/3) × (√3/4)a² × √(2/3)a
      = (1/3) × (√3/4) × √(2/3) × a³
      = (1/12) × √3 × √(2/3) × a³
      = (1/12) × √3 × √2/√3 × a³
      = (1/12) × √2 × a³
      = a³/(6√2) ✓

    Alternative via closed form:
    V = a³√2/12 = a³/(6√2) ✓

    AHA MOMENT #1: THE SIMPLEST PLATONIC SOLID
    ============================================
    The tetrahedron is the ONLY Platonic solid that cannot be decomposed
    into simpler polyhedra without introducing new vertex types.
    
    All other Platonic solids can be built from tetrahedra:
    - Octahedron = 8 tetrahedra arranged around a common vertex
    - Cube = 6 tetrahedra + 1 central octahedron (stella octangula decomposition)
    - Icosahedron = 20 tetrahedra arranged around vertices
    - Dodecahedron = dual of icosahedron, inherits tetrahedral substructure
    
    The tetrahedron is the ATOMIC UNIT of Platonic geometry—irreducible,
    fundamental, and generative. It is the 3D simplex: the minimal volume
    bounded by flat faces (0-simplex = point, 1-simplex = line, 2-simplex = triangle,
    3-simplex = tetrahedron).
    
    This is why it represents FIRE—the primal element from which all others emerge.

    SPHERE RADII FORMULAS & DERIVATIONS:
    =====================================

    Inradius (Inscribed Sphere): r = a√6/12 = a/(2√6)
    --------------------------------------------------
    The inscribed sphere touches the center of each face.

    Derivation using volume-to-surface-area ratio:
    For any polyhedron: r = 3V/A

    r = 3 × [a³/(6√2)] / [√3 a²]
      = 3a³/(6√2) × 1/(√3 a²)
      = 3a/(6√2 × √3)
      = a/(2√6)
      = a√6/12 ✓

    Geometric interpretation:
    - Distance from centroid to any face
    - Centroid at (1/4) of height from base
    - Inradius = (1/4)h for tetrahedron
    - r = (1/4) × √(2/3)a = √(2/3)a/4 = a√6/12 ✓

    Midradius (Midsphere): ρ = a√2/4 = a/(2√2)
    -------------------------------------------
    The midsphere touches the midpoint of each edge.

    Derivation via canonical coordinates:
    Using canonical vertices at (±1, ±1, ±1) with alternating signs,
    the edge length = 2√2, and edge midpoint is at (0, 0, 1).
    Distance from origin = 1.
    For general edge length a: scale factor = a/(2√2)
    Midradius = 1 × a/(2√2) = a/(2√2) = a√2/4 ✓

    Circumradius (Circumscribed Sphere): R = a√6/4
    -----------------------------------------------
    The circumscribed sphere passes through all 4 vertices.

    Derivation using height and centroid position:
    - Centroid is at (1/4)h from base, or (3/4)h from apex
    - Distance from centroid to apex vertex = R
    - R = (3/4)h = (3/4) × √(2/3)a
      = (3/4) × a√(2/3)
      = (3a/4) × √2/√3
      = (3a/4) × √(2/3)
      = a√6/4 ✓

    Alternative via base vertex distance:
    - Distance from centroid to base vertex = R
    - Centroid at height h/4 above base
    - Base vertex at distance a/√3 from base centroid (horizontal)
    - R² = (h/4)² + (a/√3)²
      = (√(2/3)a/4)² + (a/√3)²
      = (2a²/3)/16 + a²/3
      = a²/24 + a²/3
      = a²/24 + 8a²/24 = 9a²/24 = 3a²/8
    - R = a√(3/8) = a√3/(2√2) = a√6/4 ✓

    AHA MOMENT #2: SELF-DUAL PERFECTION
    =====================================
    The tetrahedron is SELF-DUAL: its dual polyhedron is another tetrahedron!
    
    When you connect the face centers of a tetrahedron, you get another
    tetrahedron rotated 180° and scaled by 1/3. This creates the "Merkaba"
    or "Star Tetrahedron"—two interpenetrating tetrahedra forming a 3D
    Star of David.
    
    Only the tetrahedron possesses this perfect self-symmetry among Platonic
    solids. All others have distinct duals:
    - Cube ↔ Octahedron (reciprocal duals)
    - Dodecahedron ↔ Icosahedron (reciprocal duals)
    - Tetrahedron ↔ Tetrahedron (SELF-DUAL)
    
    This self-reference is the geometric expression of the alchemical principle
    "As within, so without"—the tetrahedron contains its own reflection.

    AHA MOMENT #3: THE 1:3 RATIO
    =============================
    The tetrahedron has R/r = 3 EXACTLY—the only Platonic solid with this
    simple integer ratio!
    
    R/r = (a√6/4) / (a√6/12) = (a√6/4) × (12/a√6) = 12/4 = 3
    
    All other Platonic solids have irrational R/r ratios:
    - Cube: R/r = √3 ≈ 1.732
    - Octahedron: R/r = √3 ≈ 1.732
    - Dodecahedron: R/r ≈ 1.258 (φ-based)
    - Icosahedron: R/r ≈ 1.258 (φ-based)
    
    The 3:1 ratio reflects the Trinity principle—three persons in one essence.
    The circumsphere (manifestation) is exactly three times the insphere (essence).
    This perfect integer relationship makes the tetrahedron the most "pure"
    and "simple" of all Platonic solids.

    HERMETIC NOTE - THE FIRE ELEMENT:
    ==================================
    The tetrahedron represents FIRE in Platonic solid cosmology:

    Symbolism:
    - 4 triangular faces = upward aspiration, ascent
    - Sharpest vertices (largest angular defect = 180°)
    - Smallest volume-to-surface ratio (most "surface-like")
    - Self-dual (its dual is another tetrahedron, rotated)

    Spiritual Correspondences:
    - Insphere (r = a√6/12): The inner flame, spiritual heat
    - Midsphere (ρ = a√2/4): The radiant boundary
    - Circumsphere (R = a√6/4): The sphere of emanation

    Ratios: r : ρ : R = √6/12 : √2/4 : √6/4
                      = 1 : √3 : 3

    Dihedral Angle:
    - Exactly arccos(1/3) ≈ 70.53°
    - This is close to the tetrahedral bond angle in chemistry
    - sp³ hybridization (methane, diamond lattice)

    Packing Density:
    - Cannot fill space (leaves gaps)
    - Represents Fire's inability to be "contained"
    - Aspires upward, cannot be "stacked" perfectly
    """
    # Core dimensions
    height = math.sqrt(2.0 / 3.0) * edge_length
    face_area_val = (math.sqrt(3.0) / 4.0) * edge_length ** 2
    surface_area_val = 4.0 * face_area_val
    volume_val = edge_length ** 3 / (6.0 * math.sqrt(2.0))

    # Sphere radii
    inradius_val = edge_length * math.sqrt(6.0) / 12.0   # r = a√6/12
    midradius_val = edge_length * math.sqrt(2.0) / 4.0    # ρ = a√2/4
    circumradius_val = edge_length * math.sqrt(6.0) / 4.0  # R = a√6/4 = 3r ✓
    
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
    # MOI scales as edge^5 for solid (mass * a^2 where mass ~ volume ~ a^3)
    scale = edge_length / _BASE_EDGE_LENGTH
    moi_solid = _BASE_MOI_SOLID * (scale ** 5.0)
    moi_shell = _BASE_MOI_SHELL * (scale ** 4.0)
    
    return TetrahedronMetrics(
        edge_length=edge_length,
        height=height,
        face_area=face_area_val,
        surface_area=surface_area_val,
        volume=volume_val,
        inradius=inradius_val,
        midradius=midradius_val,
        circumradius=circumradius_val,
        incircle_circumference=2.0 * math.pi * inradius_val,
        midsphere_circumference=2.0 * math.pi * midradius_val,
        circumcircle_circumference=2.0 * math.pi * circumradius_val,
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


class TetrahedronSolidService:
    """Generates payloads for equilateral tetrahedra."""

    @staticmethod
    def build(edge_length: float = 1.0) -> TetrahedronSolidResult:
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
        vertices = _scale_vertices(edge_length)
        from .geometry_visuals import compute_dual_payload

        metadata = {
            # Core
            'edge_length': metrics.edge_length,
            'height': metrics.height,
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
        }
        labels = [
            SolidLabel(text=f"a = {edge_length:.3f}", position=(0.0, 0.0, 0.0)),
            SolidLabel(text=f"V = {metrics.volume:.3f}", position=(0.0, -metrics.height * 0.25, 0.0)),
        ]
        payload = SolidPayload(
            vertices=vertices,
            edges=list(_EDGES),
            faces=[tuple(face) for face in _FACES],
            labels=labels,
            metadata=metadata,
            suggested_scale=edge_length,
        )
        payload.dual = compute_dual_payload(payload)
        return TetrahedronSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(edge_length: float = 1.0) -> SolidPayload:
        """Convenience accessor when only the payload is required."""
        return TetrahedronSolidService.build(edge_length).payload




__all__ = [
    'TetrahedronMetrics',
    'TetrahedronSolidResult',
    'TetrahedronSolidService',
]