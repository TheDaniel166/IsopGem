"""Triangle math helpers shared by Canon solvers and services."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

EPSILON = 1e-7


def _clamp(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def valid_triangle_sides(a: float, b: float, c: float) -> bool:
    return (
        all(side > 0 for side in (a, b, c))
        and a + b > c - EPSILON
        and a + c > b - EPSILON
        and b + c > a - EPSILON
    )


@dataclass(frozen=True)
class TriangleMetrics:
    """Computed metrics for a triangle defined by its three sides."""

    side_a: float
    side_b: float
    side_c: float
    area: float
    perimeter: float
    angle_a: float
    angle_b: float
    angle_c: float
    height_a: float
    height_b: float
    height_c: float
    inradius: float
    circumradius: float
    points: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]


def triangle_points_from_sides(a: float, b: float, c: float) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    """Return triangle vertex coordinates with side c on the x-axis."""
    if not valid_triangle_sides(a, b, c):
        raise ValueError("Invalid triangle side lengths")

    base = c
    x_c = (b * b + c * c - a * a) / (2 * c)
    y_c_sq = max(b * b - x_c * x_c, 0.0)
    y_c = math.sqrt(y_c_sq)
    return ((0.0, 0.0), (base, 0.0), (x_c, y_c))


def triangle_metrics_from_sides(a: float, b: float, c: float) -> TriangleMetrics:
    """Compute core triangle metrics from side lengths."""
    if not valid_triangle_sides(a, b, c):
        raise ValueError("Invalid triangle side lengths")

    s = (a + b + c) / 2.0
    area_sq = max(s * (s - a) * (s - b) * (s - c), 0.0)
    area = math.sqrt(area_sq)
    perimeter = a + b + c

    angle_a = math.degrees(math.acos(_clamp((b * b + c * c - a * a) / (2 * b * c))))
    angle_b = math.degrees(math.acos(_clamp((a * a + c * c - b * b) / (2 * a * c))))
    angle_c = 180.0 - angle_a - angle_b

    inradius = area / s if s > 0 else 0.0
    circumradius = (a * b * c) / (4 * area) if area > 0 else 0.0

    height_a = (2 * area) / a if a > 0 else 0.0
    height_b = (2 * area) / b if b > 0 else 0.0
    height_c = (2 * area) / c if c > 0 else 0.0

    points = triangle_points_from_sides(a, b, c)

    return TriangleMetrics(
        side_a=a,
        side_b=b,
        side_c=c,
        area=area,
        perimeter=perimeter,
        angle_a=angle_a,
        angle_b=angle_b,
        angle_c=angle_c,
        height_a=height_a,
        height_b=height_b,
        height_c=height_c,
        inradius=inradius,
        circumradius=circumradius,
        points=points,
    )
