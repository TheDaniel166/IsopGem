"""Helpers for generating polygonal and centered polygonal number layouts."""
from __future__ import annotations

import math
from typing import List, Sequence, Tuple

Point = Tuple[float, float]
_ROTATION = 0.0


def polygonal_number_value(sides: int, index: int) -> int:
    """Return the standard polygonal number value for a given polygon and index.

    Uses the closed form P_s(n) = ((s-2)n^2 - (s-4)n) / 2.
    """
    sides = max(3, int(sides))
    index = max(1, int(index))
    return ((sides - 2) * index * index - (sides - 4) * index) // 2


def centered_polygonal_value(sides: int, index: int) -> int:
    """Return the centered polygonal number value for a given polygon and index.

    Uses the closed form C_s(n) = s * n * (n - 1) / 2 + 1.
    """
    sides = max(3, int(sides))
    index = max(1, int(index))
    return (sides * index * (index - 1)) // 2 + 1


def polygonal_number_points(
    sides: int,
    index: int,
    spacing: float = 1.0,
    centered: bool = False,
    rotation: float = _ROTATION,
) -> List[Point]:
    """Generate dot coordinates for polygonal or centered polygonal numbers.

    - Polygonal: shared-corner gnomon growth (layers expand from one vertex).
    - Centered: concentric ring growth.
    """
    sides = max(3, int(sides))
    index = max(1, int(index))
    spacing = max(0.1, float(spacing))

    if centered:
        return _centered_polygonal_points(sides, index, spacing, rotation)
    return _corner_polygonal_points(sides, index, spacing, rotation)


def polygonal_outline_points(
    sides: int,
    index: int,
    spacing: float = 1.0,
    rotation: float = _ROTATION,
) -> List[Point]:
    """Return the outer polygon outline for the given polygonal number order."""
    sides = max(3, int(sides))
    index = max(1, int(index))
    spacing = max(0.1, float(spacing))
    return _outer_polygon_vertices(sides, index - 1, spacing, rotation)


def max_radius(spacing: float, index: int) -> float:
    """Maximum radius used by the generator for concentric layouts."""
    index = max(1, int(index))
    spacing = max(0.1, float(spacing))
    return (index - 1) * spacing if index > 1 else spacing


def _polygonal_ring_count(sides: int, layer: int) -> int:
    # Growth (gnomon) for standard polygonal numbers: (s-2) * n - (s-3)
    return max(1, (sides - 2) * layer - (sides - 3))


def _centered_ring_count(sides: int, layer: int) -> int:
    # Growth for centered polygonal numbers: s * (n - 1)
    return max(1, sides * (layer - 1))


def _centered_polygonal_points(sides: int, index: int, spacing: float, rotation: float) -> List[Point]:
    points: List[Point] = [(0.0, 0.0)]
    if index == 1:
        return points

    for layer in range(2, index + 1):
        ring_count = _centered_ring_count(sides, layer)
        radius = (layer - 1) * spacing
        points.extend(_points_on_polygon(sides, ring_count, radius, rotation))

    return points


def _corner_polygonal_points(sides: int, index: int, spacing: float, rotation: float) -> List[Point]:
    target = polygonal_number_value(sides, index)
    points: List[Point] = []
    seen = set()

    # Base case: first layer is a single point
    points.append((0.0, 0.0))
    seen.add((0.0, 0.0))
    if target == 1:
        return points

    for layer in range(2, index + 1):
        # Layer k corresponds to a polygon of side length k-1
        size = layer - 1
        outline = _outer_polygon_vertices(sides, size, spacing, rotation)
        for px, py in _points_on_outline(outline, size, seen):
            points.append((px, py))
            if len(points) >= target:
                return points

    return points[:target]


def _outer_polygon_vertices(sides: int, layer: int, spacing: float, rotation: float) -> List[Point]:
    step = layer * spacing
    angle_step = (2 * math.pi) / sides
    vertices: List[Point] = [(0.0, 0.0)]
    x, y = 0.0, 0.0
    heading = rotation
    for _ in range(sides):
        x += math.cos(heading) * step
        y += math.sin(heading) * step
        vertices.append((x, y))
        heading += angle_step
    return vertices


def _points_on_outline(vertices: List[Point], steps_per_edge: int, seen: set) -> List[Point]:
    points: List[Point] = []
    if steps_per_edge <= 0:
        return points
    for i in range(len(vertices) - 1):
        v0 = vertices[i]
        v1 = vertices[i + 1]
        dx = (v1[0] - v0[0]) / steps_per_edge
        dy = (v1[1] - v0[1]) / steps_per_edge
        for k in range(steps_per_edge):
            px = v0[0] + dx * k
            py = v0[1] + dy * k
            key = (round(px, 6), round(py, 6))
            if key in seen:
                continue
            seen.add(key)
            points.append((px, py))
    return points


def _points_on_polygon(sides: int, count: int, radius: float, rotation: float) -> List[Point]:
    if count <= 0:
        return []
    sides = max(3, int(sides))
    radius = max(0.1, float(radius))

    angle_step = (2 * math.pi) / sides
    vertices: List[Point] = [
        (radius * math.cos(rotation + i * angle_step), radius * math.sin(rotation + i * angle_step))
        for i in range(sides)
    ]
    vertices.append(vertices[0])

    side_length = 2 * radius * math.sin(math.pi / sides)
    perimeter = side_length * sides
    step = perimeter / count

    points: List[Point] = []
    for k in range(count):
        distance = min(k * step, perimeter - 1e-9)
        edge_idx = int(distance // side_length)
        local = (distance % side_length) / side_length
        v0 = vertices[edge_idx]
        v1 = vertices[edge_idx + 1]
        x = v0[0] + (v1[0] - v0[0]) * local
        y = v0[1] + (v1[1] - v0[1]) * local
        points.append((x, y))

    return points[:count]



def star_number_value(index: int) -> int:
    """Return the star number value (centered hexagram) for a given index."""
    index = max(1, int(index))
    return 6 * index * (index - 1) + 1


def generalized_star_number_value(points_count: int, index: int) -> int:
    """Return the star number value for a p-gram (p points) at a given index.
    
    Formula: S(p, n) = p * n * (n - 1) + 1
    (Similar to centered polygonal numbers, but with geometry of rays)
    """
    points_count = max(3, int(points_count))
    index = max(1, int(index))
    return points_count * index * (index - 1) + 1


def star_number_points(
    index: int,
    spacing: float = 1.0,
    rotation: float = _ROTATION,
) -> List[Point]:
    """Generate dot coordinates for star numbers (centered hexagrams)."""
    return generalized_star_number_points(6, index, spacing, rotation)


def generalized_star_number_points(
    points_count: int,
    index: int,
    spacing: float = 1.0,
    rotation: float = _ROTATION,
) -> List[Point]:
    """Generate dot coordinates for generalized star numbers (centered p-grams).
    
    Constructed as a centered p-gon plus p triangles (rays) on its edges.
    """
    points_count = max(3, int(points_count))
    
    # 1. Base: Centered Polygon of size index
    points = _centered_polygonal_points(points_count, index, spacing, rotation)
    
    if index <= 1:
        return points

    # 2. Add p Triangles to the tips
    # Boundary layer of the core polygon
    boundary_radius = (index - 1) * spacing
    boundary_vertices = []
    angle_step = (2 * math.pi) / points_count
    
    for i in range(points_count):
        angle = rotation + i * angle_step
        boundary_vertices.append((
            boundary_radius * math.cos(angle),
            boundary_radius * math.sin(angle)
        ))
    boundary_vertices.append(boundary_vertices[0]) # Close loop

    # Triangle logic (same as hexagram but adapting angles)
    # For a p-gon, the interior angle is (p-2)*180/p.
    # The exterior angle (turn) is 360/p (angle_step).
    # We want the triangle to point OUT.
    # 
    # For hexagon (p=6), angle_step = 60 deg. Triangle needed 60 deg vector.
    # For pentagon (p=5), angle_step = 72 deg.
    # If we use equilateral triangles, the 'star' rays will be sharp (36 deg gaps?).
    # Standard star polygons (Schlafli {p/2}?) or just "star figures"?
    # The user likely means "Star Figures" where we attach triangles to the sides.
    # If we attach EQUILATERAL triangles, the tips might overlap if p < 6?
    # No, for p=5 (pentagon), interior angle is 108 deg. 360 - 108 - 60 - 60 = 132 gap. 
    # For p=3 (triangle), interior 60. 360 - 60 - 60 - 60 = 180 (flat?).
    # So P=3 is just a bigger triangle?
    # P=4 (square), interior 90. 360 - 90 - 60 - 60 = 150 gap.
    # P=6 (hexagon), interior 120. 360 - 120 - 60 - 60 = 120 gap (perfect tiling if hex grid).
    
    # We will assume EQUILATERAL triangles added to the sides, as that fits the "Star Number" pattern logic
    # (n rows of dots).
    
    for side in range(points_count):
        p_start = boundary_vertices[side]
        p_end = boundary_vertices[side + 1]
        
        dx_edge = (p_end[0] - p_start[0]) / (index - 1)
        dy_edge = (p_end[1] - p_start[1]) / (index - 1)
        
        # Outward vector: Rotate edge vector by -60 degrees relative to traversal?
        # Polygon traversal is CCW. Outward is to the right? No, "outer" polygon.
        # Let's check hex logic again.
        # Hex points: P_i. CCW.
        # Vector P_i -> P_{i+1}. 
        # Standard angle 0 -> 60. Edge vector (cos 60, sin 60).
        # We need vector (1, 0) rotated by something?
        # The triangle "up" vector should be -60 deg rotation of the edge vector (Right Hand Rule z-down? No).
        # CCW turn is positive. Right turn is negative.
        # So yes, rotate -60 deg ( -pi/3 ).
        
        basis_u = (dx_edge, dy_edge)
        s60 = math.sin(-math.pi / 3)
        c60 = math.cos(-math.pi / 3)
        basis_v = (
            basis_u[0] * c60 - basis_u[1] * s60,
            basis_u[0] * s60 + basis_u[1] * c60
        )
        
        num_rows = index - 1
        for r in range(1, num_rows + 1):
            points_in_row = (index) - r
            for c in range(points_in_row):
                px = p_start[0] + basis_v[0] * r + basis_u[0] * c
                py = p_start[1] + basis_v[1] * r + basis_u[1] * c
                points.append((px, py))

    return points


__all__ = [
    "Point",
    "polygonal_number_value",
    "centered_polygonal_value",
    "star_number_value",
    "polygonal_number_points",
    "star_number_points",
    "max_radius",
]
