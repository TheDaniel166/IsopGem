"""Utility math helpers for solid geometry computations."""
from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple
import math

Vec3 = Tuple[float, float, float]
Vertex = Vec3
Edge = Tuple[int, int]
Face = Sequence[int]


def vec_add(a: Vec3, b: Vec3) -> Vec3:
    """
    Vec add logic.
    
    Args:
        a: Description of a.
        b: Description of b.
    
    Returns:
        Result of vec_add operation.
    """
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec_sub(a: Vec3, b: Vec3) -> Vec3:
    """
    Vec sub logic.
    
    Args:
        a: Description of a.
        b: Description of b.
    
    Returns:
        Result of vec_sub operation.
    """
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_scale(a: Vec3, scalar: float) -> Vec3:
    """
    Vec scale logic.
    
    Args:
        a: Description of a.
        scalar: Description of scalar.
    
    Returns:
        Result of vec_scale operation.
    """
    return (a[0] * scalar, a[1] * scalar, a[2] * scalar)


def vec_dot(a: Vec3, b: Vec3) -> float:
    """
    Vec dot logic.
    
    Args:
        a: Description of a.
        b: Description of b.
    
    Returns:
        Result of vec_dot operation.
    """
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec_cross(a: Vec3, b: Vec3) -> Vec3:
    """
    Vec cross logic.
    
    Args:
        a: Description of a.
        b: Description of b.
    
    Returns:
        Result of vec_cross operation.
    """
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec_length(a: Vec3) -> float:
    """
    Vec length logic.
    
    Args:
        a: Description of a.
    
    Returns:
        Result of vec_length operation.
    """
    return math.sqrt(vec_dot(a, a))


def vec_normalize(a: Vec3) -> Vec3:
    """
    Vec normalize logic.
    
    Args:
        a: Description of a.
    
    Returns:
        Result of vec_normalize operation.
    """
    length = vec_length(a)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (a[0] / length, a[1] / length, a[2] / length)


def polygon_area(vertices: Sequence[Vec3], face: Face) -> float:
    """
    Polygon area logic.
    
    Args:
        vertices: Description of vertices.
        face: Description of face.
    
    Returns:
        Result of polygon_area operation.
    """
    if len(face) < 3:
        return 0.0
    origin = vertices[face[0]]
    area = 0.0
    for i in range(1, len(face) - 1):
        v1 = vec_sub(vertices[face[i]], origin)
        v2 = vec_sub(vertices[face[i + 1]], origin)
        area += vec_length(vec_cross(v1, v2)) / 2.0
    return area


def face_normal(vertices: Sequence[Vec3], face: Face) -> Vec3:
    """
    Face normal logic.
    
    Args:
        vertices: Description of vertices.
        face: Description of face.
    
    Returns:
        Result of face_normal operation.
    """
    if len(face) < 3:
        return (0.0, 0.0, 0.0)
    v0 = vertices[face[0]]
    v1 = vertices[face[1]]
    v2 = vertices[face[2]]
    normal = vec_cross(vec_sub(v1, v0), vec_sub(v2, v0))
    return normal


def plane_distance_from_origin(vertices: Sequence[Vec3], face: Face) -> float:
    """
    Plane distance from origin logic.
    
    Args:
        vertices: Description of vertices.
        face: Description of face.
    
    Returns:
        Result of plane_distance_from_origin operation.
    """
    normal = face_normal(vertices, face)
    unit = vec_normalize(normal)
    if unit == (0.0, 0.0, 0.0):
        return 0.0
    point = vertices[face[0]]
    return abs(vec_dot(unit, point))


def compute_surface_area(vertices: Sequence[Vec3], faces: Sequence[Face]) -> float:
    """
    Compute surface area logic.
    
    Args:
        vertices: Description of vertices.
        faces: Description of faces.
    
    Returns:
        Result of compute_surface_area operation.
    """
    return sum(polygon_area(vertices, face) for face in faces)


def compute_volume(vertices: Sequence[Vec3], faces: Sequence[Face]) -> float:
    """
    Compute volume logic.
    
    Args:
        vertices: Description of vertices.
        faces: Description of faces.
    
    Returns:
        Result of compute_volume operation.
    """
    volume = 0.0
    for face in faces:
        if len(face) < 3:
            continue
        v0 = vertices[face[0]]
        for i in range(1, len(face) - 1):
            v1 = vertices[face[i]]
            v2 = vertices[face[i + 1]]
            volume += abs(vec_dot(v0, vec_cross(v1, v2)))
    return volume / 6.0


def edges_from_faces(faces: Sequence[Face]) -> List[Tuple[int, int]]:
    """
    Edges from faces logic.
    
    Args:
        faces: Description of faces.
    
    Returns:
        Result of edges_from_faces operation.
    """
    edge_set = set()
    for face in faces:
        if len(face) < 2:
            continue
        for i in range(len(face)):
            a = face[i]
            b = face[(i + 1) % len(face)]
            if a == b:
                continue
            edge = tuple(sorted((a, b)))
            edge_set.add(edge)
    return sorted(edge_set)


def face_centroid(vertices: Sequence[Vec3], face: Face) -> Vec3:
    """
    Face centroid logic.
    
    Args:
        vertices: Description of vertices.
        face: Description of face.
    
    Returns:
        Result of face_centroid operation.
    """
    if not face:
        return (0.0, 0.0, 0.0)
    accumulator = (0.0, 0.0, 0.0)
    for idx in face:
        accumulator = vec_add(accumulator, vertices[idx])
    scale = 1.0 / len(face)
    return vec_scale(accumulator, scale)


def angle_around_axis(point: Vec3, axis: Vec3, ref_axis: Vec3) -> float:
    """
    Angle around axis logic.
    
    Args:
        point: Description of point.
        axis: Description of axis.
        ref_axis: Description of ref_axis.
    
    Returns:
        Result of angle_around_axis operation.
    """
    axis = vec_normalize(axis)
    # Ensure reference axis is not parallel to axis
    ref = ref_axis
    if vec_length(vec_cross(axis, ref)) < 1e-6:
        ref = (0.0, 1.0, 0.0)
        if vec_length(vec_cross(axis, ref)) < 1e-6:
            ref = (1.0, 0.0, 0.0)
    u = vec_cross(axis, ref)
    if vec_length(u) < 1e-6:
        u = (1.0, 0.0, 0.0)
    u = vec_normalize(u)
    v = vec_cross(axis, u)
    x = vec_dot(point, u)
    y = vec_dot(point, v)
    return math.atan2(y, x)


__all__ = [
    'Vec3',
    'Vertex',
    'Edge',
    'Face',
    'vec_add',
    'vec_sub',
    'vec_scale',
    'vec_dot',
    'vec_cross',
    'vec_length',
    'vec_normalize',
    'polygon_area',
    'face_normal',
    'plane_distance_from_origin',
    'compute_surface_area',
    'compute_volume',
    'edges_from_faces',
    'face_centroid',
    'angle_around_axis',
]