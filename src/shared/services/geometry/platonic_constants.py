"""Platonic Solid Constants and Formulas.

This module provides shared constants, formulas, and helper functions
for all five Platonic solids. Each solid is defined by its Schläfli symbol {p, q}
where p = sides per face, q = faces meeting at each vertex.

The Five Platonic Solids:
- Tetrahedron {3, 3}: 4 triangular faces, 4 vertices, 6 edges
- Cube {4, 3}: 6 square faces, 8 vertices, 12 edges
- Octahedron {3, 4}: 8 triangular faces, 6 vertices, 12 edges
- Dodecahedron {5, 3}: 12 pentagonal faces, 20 vertices, 30 edges
- Icosahedron {3, 5}: 20 triangular faces, 12 vertices, 30 edges
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict


# Golden ratio (φ)
PHI = (1 + math.sqrt(5)) / 2


class PlatonicSolid(Enum):
    """Enumeration of the five Platonic solids."""
    TETRAHEDRON = "tetrahedron"
    CUBE = "cube"
    OCTAHEDRON = "octahedron"
    DODECAHEDRON = "dodecahedron"
    ICOSAHEDRON = "icosahedron"


@dataclass(frozen=True)
class PlatonicTopology:
    """Topological constants for a Platonic solid."""
    p: int  # Sides per face (Schläfli p)
    q: int  # Faces meeting at vertex (Schläfli q)
    faces: int  # F
    vertices: int  # V
    edges: int  # E
    
    @property
    def euler_characteristic(self) -> int:
        """V - E + F = 2 for convex polyhedra."""
        return self.vertices - self.edges + self.faces


# Topological constants for each solid
TOPOLOGY: Dict[PlatonicSolid, PlatonicTopology] = {
    PlatonicSolid.TETRAHEDRON: PlatonicTopology(p=3, q=3, faces=4, vertices=4, edges=6),
    PlatonicSolid.CUBE: PlatonicTopology(p=4, q=3, faces=6, vertices=8, edges=12),
    PlatonicSolid.OCTAHEDRON: PlatonicTopology(p=3, q=4, faces=8, vertices=6, edges=12),
    PlatonicSolid.DODECAHEDRON: PlatonicTopology(p=5, q=3, faces=12, vertices=20, edges=30),
    PlatonicSolid.ICOSAHEDRON: PlatonicTopology(p=3, q=5, faces=20, vertices=12, edges=30),
}


# Dihedral angles in radians (angle between adjacent faces)
# Formula: arccos(cos(π/q) / sin(π/p))
def _dihedral_angle(p: int, q: int) -> float:
    """Calculate dihedral angle for Schläfli symbol {p, q}."""
    return math.pi - 2 * math.asin(math.cos(math.pi / q) / math.sin(math.pi / p))


DIHEDRAL_ANGLES_RAD: Dict[PlatonicSolid, float] = {
    PlatonicSolid.TETRAHEDRON: math.acos(1/3),  # ≈ 70.53°
    PlatonicSolid.CUBE: math.pi / 2,  # 90°
    PlatonicSolid.OCTAHEDRON: math.acos(-1/3),  # ≈ 109.47°
    PlatonicSolid.DODECAHEDRON: math.acos(-math.sqrt(5)/5),  # ≈ 116.57°
    PlatonicSolid.ICOSAHEDRON: math.acos(-math.sqrt(5)/3),  # ≈ 138.19°
}

DIHEDRAL_ANGLES_DEG: Dict[PlatonicSolid, float] = {
    solid: math.degrees(angle) for solid, angle in DIHEDRAL_ANGLES_RAD.items()
}


# =============================================================================
# Face Geometry Helpers
# =============================================================================

def face_inradius(edge_length: float, p: int) -> float:
    """Inradius of a regular p-gon face.
    
    Formula: a / (2 * tan(π/p))
    """
    return edge_length / (2 * math.tan(math.pi / p))


def face_circumradius(edge_length: float, p: int) -> float:
    """Circumradius of a regular p-gon face.
    
    Formula: a / (2 * sin(π/p))
    """
    return edge_length / (2 * math.sin(math.pi / p))


def face_area(edge_length: float, p: int) -> float:
    """Area of a regular p-gon face.
    
    Formula: (p * a² * cot(π/p)) / 4
    """
    cot_pi_p = 1 / math.tan(math.pi / p)
    return (p * edge_length * edge_length * cot_pi_p) / 4


def edge_from_face_inradius(r: float, p: int) -> float:
    """Derive edge length from face inradius."""
    return 2 * r * math.tan(math.pi / p)


def edge_from_face_circumradius(R: float, p: int) -> float:
    """Derive edge length from face circumradius."""
    return 2 * R * math.sin(math.pi / p)


def edge_from_face_area(A: float, p: int) -> float:
    """Derive edge length from face area."""
    cot_pi_p = 1 / math.tan(math.pi / p)
    return math.sqrt(4 * A / (p * cot_pi_p))


# =============================================================================
# Sphere Geometry Helpers
# =============================================================================

def sphere_surface_area(radius: float) -> float:
    """Surface area of a sphere: 4πr²"""
    return 4 * math.pi * radius * radius


def sphere_volume(radius: float) -> float:
    """Volume of a sphere: (4/3)πr³"""
    return (4/3) * math.pi * radius ** 3


def radius_from_sphere_surface_area(sa: float) -> float:
    """Derive radius from sphere surface area."""
    return math.sqrt(sa / (4 * math.pi))


def radius_from_sphere_volume(vol: float) -> float:
    """Derive radius from sphere volume."""
    return (3 * vol / (4 * math.pi)) ** (1/3)


# =============================================================================
# Quality Metrics
# =============================================================================

def sphericity(volume: float, surface_area: float) -> float:
    """Sphericity: how close to a sphere.
    
    Formula: (π^(1/3) * (6V)^(2/3)) / S
    Value is 1.0 for a perfect sphere, less for other shapes.
    """
    numerator = (math.pi ** (1/3)) * ((6 * volume) ** (2/3))
    return numerator / surface_area


def isoperimetric_quotient(volume: float, surface_area: float) -> float:
    """Isoperimetric quotient (IQ).
    
    Formula: (36π * V²) / S³
    Value is 1.0 for a perfect sphere.
    """
    return (36 * math.pi * volume * volume) / (surface_area ** 3)


def surface_to_volume_ratio(surface_area: float, volume: float) -> float:
    """Surface area to volume ratio."""
    return surface_area / volume if volume > 0 else 0.0


# Solid angle at each vertex (in steradians)
# Formula: q * arccos(cos(π/p) / sin(π/p)) - (q-2)π
# Or more simply, using the defect: 4π / V
SOLID_ANGLES_SR: Dict[PlatonicSolid, float] = {
    PlatonicSolid.TETRAHEDRON: math.pi,  # π steradians
    PlatonicSolid.CUBE: math.pi / 2,  # π/2 steradians
    PlatonicSolid.OCTAHEDRON: 2 * math.pi / 3,  # 2π/3 steradians
    PlatonicSolid.DODECAHEDRON: math.pi / 5,  # π/5 steradians
    PlatonicSolid.ICOSAHEDRON: math.pi / 3,  # π/3 steradians
}


# =============================================================================
# Advanced Physics: Moment of Inertia
# =============================================================================

# Moment of inertia for SOLID (filled) Platonic solids about centroid
# Formula: I = k * m * a² where a = edge length, m = mass
# k coefficients from academic literature (normalized: I = k·ρ·V·a² for density ρ=1)
MOMENT_INERTIA_SOLID_K: Dict[PlatonicSolid, float] = {
    PlatonicSolid.TETRAHEDRON: 1/20,  # 0.05
    PlatonicSolid.CUBE: 1/6,  # 0.1667
    PlatonicSolid.OCTAHEDRON: 1/10,  # 0.1
    PlatonicSolid.DODECAHEDRON: (39 + 3*math.sqrt(5)) / 200,  # ≈ 0.228
    PlatonicSolid.ICOSAHEDRON: (1 + 2*math.sqrt(5)) / 20,  # ≈ 0.274
}

# Moment of inertia for SHELL (hollow) Platonic solids about centroid
# Formula: I = k' * (total mass) * a² for thin shell
MOMENT_INERTIA_SHELL_K: Dict[PlatonicSolid, float] = {
    PlatonicSolid.TETRAHEDRON: 1/12,  # ≈ 0.083
    PlatonicSolid.CUBE: 1/3,  # ≈ 0.333
    PlatonicSolid.OCTAHEDRON: 1/6,  # ≈ 0.167
    PlatonicSolid.DODECAHEDRON: (3 + math.sqrt(5)) / 12,  # ≈ 0.436
    PlatonicSolid.ICOSAHEDRON: (1 + math.sqrt(5)) / 6,  # ≈ 0.539
}


# =============================================================================
# Angular Defect (Descartes' Theorem)
# =============================================================================

# Angular defect at each vertex = 2π - sum of face angles at vertex
# For regular polyhedra: defect = 2π - q*(π - 2π/p) = 2π - q*π*(1 - 2/p)
def angular_defect_vertex(p: int, q: int) -> float:
    """Angular defect at a vertex in radians."""
    face_angle = math.pi * (p - 2) / p  # Interior angle of regular p-gon
    return 2 * math.pi - q * face_angle


ANGULAR_DEFECT_VERTEX_RAD: Dict[PlatonicSolid, float] = {
    solid: angular_defect_vertex(topo.p, topo.q)
    for solid, topo in TOPOLOGY.items()
}

ANGULAR_DEFECT_VERTEX_DEG: Dict[PlatonicSolid, float] = {
    solid: math.degrees(angle) for solid, angle in ANGULAR_DEFECT_VERTEX_RAD.items()
}

# Total angular defect (Descartes' theorem): always 4π (720°) for convex polyhedra
TOTAL_ANGULAR_DEFECT_RAD = 4 * math.pi
TOTAL_ANGULAR_DEFECT_DEG = 720.0


# =============================================================================
# Packing Density
# =============================================================================

# Densest known packings of Platonic solids in 3D Euclidean space
# Values from Torquato & Jiao (2009) research
PACKING_DENSITY: Dict[PlatonicSolid, float] = {
    PlatonicSolid.TETRAHEDRON: 0.8563,  # 85.63%
    PlatonicSolid.CUBE: 1.0,  # 100% (tiles space perfectly)
    PlatonicSolid.OCTAHEDRON: 0.9474,  # 94.74%
    PlatonicSolid.DODECAHEDRON: 0.9045,  # 90.45%
    PlatonicSolid.ICOSAHEDRON: 0.8363,  # 83.63%
}


# =============================================================================
# Symmetry Groups
# =============================================================================

# Full symmetry group order (including reflections)
SYMMETRY_GROUP_ORDER: Dict[PlatonicSolid, int] = {
    PlatonicSolid.TETRAHEDRON: 24,  # Td
    PlatonicSolid.CUBE: 48,  # Oh
    PlatonicSolid.OCTAHEDRON: 48,  # Oh (same as cube - duals)
    PlatonicSolid.DODECAHEDRON: 120,  # Ih
    PlatonicSolid.ICOSAHEDRON: 120,  # Ih (same as dodeca - duals)
}

# Rotational symmetry group order (chiral/orientation-preserving only)
ROTATIONAL_SYMMETRY_ORDER: Dict[PlatonicSolid, int] = {
    PlatonicSolid.TETRAHEDRON: 12,  # A4 (alternating group)
    PlatonicSolid.CUBE: 24,  # S4 (symmetric group)
    PlatonicSolid.OCTAHEDRON: 24,  # S4
    PlatonicSolid.DODECAHEDRON: 60,  # A5
    PlatonicSolid.ICOSAHEDRON: 60,  # A5
}

# Symmetry group names
SYMMETRY_GROUP_NAME: Dict[PlatonicSolid, str] = {
    PlatonicSolid.TETRAHEDRON: "Td",
    PlatonicSolid.CUBE: "Oh",
    PlatonicSolid.OCTAHEDRON: "Oh",
    PlatonicSolid.DODECAHEDRON: "Ih",
    PlatonicSolid.ICOSAHEDRON: "Ih",
}


# =============================================================================
# Dual Polyhedra
# =============================================================================

# Mapping from each Platonic solid to its dual
DUAL_SOLID: Dict[PlatonicSolid, PlatonicSolid] = {
    PlatonicSolid.TETRAHEDRON: PlatonicSolid.TETRAHEDRON,  # Self-dual
    PlatonicSolid.CUBE: PlatonicSolid.OCTAHEDRON,
    PlatonicSolid.OCTAHEDRON: PlatonicSolid.CUBE,
    PlatonicSolid.DODECAHEDRON: PlatonicSolid.ICOSAHEDRON,
    PlatonicSolid.ICOSAHEDRON: PlatonicSolid.DODECAHEDRON,
}

DUAL_SOLID_NAME: Dict[PlatonicSolid, str] = {
    solid: dual.value.title() for solid, dual in DUAL_SOLID.items()
}


# =============================================================================
# Golden Ratio Relationships
# =============================================================================

# Golden ratio factor: how φ relates to solid's geometry
# For dodecahedron/icosahedron, many ratios involve φ
GOLDEN_RATIO_FACTOR: Dict[PlatonicSolid, float] = {
    PlatonicSolid.TETRAHEDRON: 0.0,  # No φ relationship
    PlatonicSolid.CUBE: 0.0,  # No φ relationship
    PlatonicSolid.OCTAHEDRON: 0.0,  # No φ relationship
    PlatonicSolid.DODECAHEDRON: PHI,  # Edge/diagonal = 1/φ
    PlatonicSolid.ICOSAHEDRON: PHI,  # Contains 3 orthogonal golden rectangles
}


# =============================================================================
# Bidirectional Solver Helpers
# =============================================================================

@dataclass(frozen=True)
class ScalingProperty:
    """Defines how a property scales with edge length.
    
    For a property P that scales as P = k * a^power:
    - To get P from edge: P = base_value * (a / base_edge)^power
    - To get edge from P: a = base_edge * (P / base_value)^(1/power)
    """
    name: str
    key: str
    unit: str
    precision: int
    power: float  # 1 for linear, 2 for area, 3 for volume
    base_value: float  # Value when edge = base_edge
    editable: bool = True  # Can this property be used as input?
    
    def scale(self, base_edge: float, edge_length: float) -> float:
        """Scale base value to given edge length."""
        ratio = edge_length / base_edge
        return self.base_value * (ratio ** self.power)
    
    def solve_edge(self, value: float, base_edge: float) -> float:
        """Solve for edge length given this property's value."""
        if self.base_value <= 0 or value <= 0:
            return 0.0
        ratio = value / self.base_value
        return base_edge * (ratio ** (1 / self.power))


__all__ = [
    'PHI',
    'PlatonicSolid',
    'PlatonicTopology',
    'TOPOLOGY',
    'DIHEDRAL_ANGLES_RAD',
    'DIHEDRAL_ANGLES_DEG',
    'SOLID_ANGLES_SR',
    # Advanced constants
    'MOMENT_INERTIA_SOLID_K',
    'MOMENT_INERTIA_SHELL_K',
    'ANGULAR_DEFECT_VERTEX_RAD',
    'ANGULAR_DEFECT_VERTEX_DEG',
    'TOTAL_ANGULAR_DEFECT_RAD',
    'TOTAL_ANGULAR_DEFECT_DEG',
    'PACKING_DENSITY',
    'SYMMETRY_GROUP_ORDER',
    'ROTATIONAL_SYMMETRY_ORDER',
    'SYMMETRY_GROUP_NAME',
    'DUAL_SOLID',
    'DUAL_SOLID_NAME',
    'GOLDEN_RATIO_FACTOR',
    # Classes
    'ScalingProperty',
    # Helper functions
    'angular_defect_vertex',
    'face_inradius',
    'face_circumradius',
    'face_area',
    'edge_from_face_inradius',
    'edge_from_face_circumradius',
    'edge_from_face_area',
    'sphere_surface_area',
    'sphere_volume',
    'radius_from_sphere_surface_area',
    'radius_from_sphere_volume',
    'sphericity',
    'isoperimetric_quotient',
    'surface_to_volume_ratio',
]