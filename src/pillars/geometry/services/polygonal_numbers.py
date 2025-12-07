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
    return _outer_polygon_vertices(sides, index, spacing, rotation)


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
        outline = _outer_polygon_vertices(sides, layer, spacing, rotation)
        for px, py in _points_on_outline(outline, layer, seen):
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


__all__ = [
    "Point",
    "polygonal_number_value",
    "centered_polygonal_value",
    "polygonal_number_points",
    "max_radius",
]
