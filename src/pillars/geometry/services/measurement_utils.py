"""3D measurement utilities for geometry viewport.

Provides distance, area, and volume calculations for 3D polygons.
"""
from __future__ import annotations

import math
from typing import List, Tuple

Vec3 = Tuple[float, float, float]


def distance_3d(v1: Vec3, v2: Vec3) -> float:
    """Calculate Euclidean distance between two 3D points."""
    dx = v2[0] - v1[0]
    dy = v2[1] - v1[1]
    dz = v2[2] - v1[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def cross_product(v1: Vec3, v2: Vec3) -> Vec3:
    """Calculate cross product of two vectors."""
    return (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    )


def vector_magnitude(v: Vec3) -> float:
    """Calculate magnitude of a vector."""
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def subtract_vectors(v1: Vec3, v2: Vec3) -> Vec3:
    """Subtract v2 from v1."""
    return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])


def triangle_area_3d(v0: Vec3, v1: Vec3, v2: Vec3) -> float:
    """Calculate area of a 3D triangle using cross product.
    
    Area = 0.5 * |AB × AC|
    """
    ab = subtract_vectors(v1, v0)
    ac = subtract_vectors(v2, v0)
    cross = cross_product(ab, ac)
    return 0.5 * vector_magnitude(cross)


def polygon_area_3d(vertices: List[Vec3]) -> float:
    """Calculate area of a 3D polygon by triangulation.
    
    Assumes polygon is convex or at least star-shaped from first vertex.
    Triangulates from first vertex to all other edges.
    """
    if len(vertices) < 3:
        return 0.0
    
    total_area = 0.0
    v0 = vertices[0]
    for i in range(1, len(vertices) - 1):
        v1 = vertices[i]
        v2 = vertices[i + 1]
        total_area += triangle_area_3d(v0, v1, v2)
    
    return total_area


def signed_tetrahedron_volume(v0: Vec3, v1: Vec3, v2: Vec3, v3: Vec3) -> float:
    """Calculate signed volume of a tetrahedron.
    
    Uses the formula: V = (1/6) * |a · (b × c)|
    where a, b, c are edge vectors from v0.
    """
    a = subtract_vectors(v1, v0)
    b = subtract_vectors(v2, v0)
    c = subtract_vectors(v3, v0)
    
    cross = cross_product(b, c)
    dot = a[0] * cross[0] + a[1] * cross[1] + a[2] * cross[2]
    
    return dot / 6.0


def polyhedron_volume(vertices: List[Vec3], faces: List[Tuple[int, ...]]) -> float:
    """Calculate volume of a closed polyhedron.
    
    Uses divergence theorem: decomposes into tetrahedra from origin.
    Works for any closed, non-self-intersecting polyhedron.
    """
    origin: Vec3 = (0.0, 0.0, 0.0)
    total_volume = 0.0
    
    for face_indices in faces:
        if len(face_indices) < 3:
            continue
        
        # Triangulate face from first vertex
        v0 = vertices[face_indices[0]]
        for i in range(1, len(face_indices) - 1):
            v1 = vertices[face_indices[i]]
            v2 = vertices[face_indices[i + 1]]
            # Tetrahedron: origin, v0, v1, v2
            total_volume += signed_tetrahedron_volume(origin, v0, v1, v2)
    
    return abs(total_volume)


def polyhedron_surface_area(vertices: List[Vec3], faces: List[Tuple[int, ...]]) -> float:
    """Calculate total surface area of a polyhedron."""
    total_area = 0.0
    
    for face_indices in faces:
        face_verts = [vertices[i] for i in face_indices]
        total_area += polygon_area_3d(face_verts)
    
    return total_area


__all__ = [
    'distance_3d',
    'triangle_area_3d',
    'polygon_area_3d',
    'polyhedron_volume',
    'polyhedron_surface_area',
]
