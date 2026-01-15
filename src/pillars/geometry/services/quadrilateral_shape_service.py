"""Quadrilateral drawing services (no property solving)."""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple


EPSILON = 1e-7


def _clamp(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def _circle_intersections(
    c1: Tuple[float, float],
    r1: float,
    c2: Tuple[float, float],
    r2: float,
) -> List[Tuple[float, float]]:
    """Return intersection points for two circles if they exist."""
    x1, y1 = c1
    x2, y2 = c2
    dx = x2 - x1
    dy = y2 - y1
    d = math.hypot(dx, dy)
    if d < EPSILON:
        return []
    if d > r1 + r2 + EPSILON:
        return []
    if d < abs(r1 - r2) - EPSILON:
        return []

    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h_sq = r1 * r1 - a * a
    if h_sq < -EPSILON:
        return []
    h_sq = max(h_sq, 0.0)
    h = math.sqrt(h_sq)
    xm = x1 + a * dx / d
    ym = y1 + a * dy / d

    rx = -dy * (h / d)
    ry = dx * (h / d)
    p1 = (xm + rx, ym + ry)
    p2 = (xm - rx, ym - ry)
    if _distance(p1, p2) < EPSILON:
        return [p1]
    return [p1, p2]


class QuadrilateralShapeService:
    """Builds drawing instructions for quadrilateral families."""

    @staticmethod
    def build_parallelogram(base: float, side: float, angle_deg: float) -> Dict:
        if base <= 0 or side <= 0 or not (0 < angle_deg < 180):
            return {"type": "empty"}
        rad = math.radians(angle_deg)
        points = (
            (0.0, 0.0),
            (base, 0.0),
            (base + side * math.cos(rad), side * math.sin(rad)),
            (side * math.cos(rad), side * math.sin(rad)),
        )
        return {"type": "polygon", "points": list(points)}

    @staticmethod
    def build_rhombus(side: float, angle_deg: float) -> Dict:
        if side <= 0 or not (0 < angle_deg < 180):
            return {"type": "empty"}
        rad = math.radians(angle_deg)
        points = (
            (0.0, 0.0),
            (side, 0.0),
            (side + side * math.cos(rad), side * math.sin(rad)),
            (side * math.cos(rad), side * math.sin(rad)),
        )
        return {"type": "polygon", "points": list(points)}

    @staticmethod
    def build_trapezoid(
        base_major: float,
        base_minor: float,
        height: float,
        leg_left: Optional[float] = None,
        leg_right: Optional[float] = None,
    ) -> Dict:
        if base_major <= 0 or base_minor <= 0 or height <= 0:
            return {"type": "empty"}
        if base_major < base_minor:
            base_major, base_minor = base_minor, base_major

        diff = base_major - base_minor
        offset_left = None
        if leg_left is not None and leg_left >= height:
            offset_left = math.sqrt(max(leg_left * leg_left - height * height, 0.0))
        elif diff is not None:
            offset_left = diff / 2
        offset_left = offset_left or 0.0

        top_left_x = offset_left
        top_right_x = top_left_x + base_minor
        points = (
            (0.0, 0.0),
            (base_major, 0.0),
            (top_right_x, height),
            (top_left_x, height),
        )
        return {"type": "polygon", "points": list(points)}

    @staticmethod
    def build_isosceles_trapezoid(base_major: float, base_minor: float, height: float) -> Dict:
        if base_major <= 0 or base_minor <= 0 or height <= 0:
            return {"type": "empty"}
        if base_major < base_minor:
            base_major, base_minor = base_minor, base_major
        offset = (base_major - base_minor) / 2 if base_minor else 0.0
        points = (
            (0.0, 0.0),
            (base_major, 0.0),
            (offset + base_minor, height),
            (offset, height),
        )
        return {"type": "polygon", "points": list(points)}

    @staticmethod
    def build_kite(equal_side: float, unequal_side: float, angle_deg: float, *, convex: bool = True) -> Dict:
        if equal_side <= 0 or unequal_side <= 0:
            return {"type": "empty"}
        if convex and not (0 < angle_deg < 180):
            return {"type": "empty"}
        if not convex and not (180 < angle_deg < 360):
            return {"type": "empty"}

        theta = math.radians(angle_deg)
        a = equal_side
        b = unequal_side
        A = (0.0, 0.0)
        B = (a, 0.0)
        D = (a * math.cos(theta), a * math.sin(theta))

        intersections = _circle_intersections(B, b, D, b)
        if not intersections:
            return {"type": "empty"}

        if convex:
            chosen = max(intersections, key=lambda p: p[1])
        else:
            chosen = max(intersections, key=lambda p: -abs(p[1]))

        C = chosen
        points = (A, B, C, D)
        return {"type": "polygon", "points": list(points)}

    @staticmethod
    def build_cyclic_quadrilateral(
        side_a: float,
        side_b: float,
        side_c: float,
        side_d: float,
        circumradius: float,
    ) -> Dict:
        if min(side_a, side_b, side_c, side_d, circumradius) <= 0:
            return {"type": "empty"}

        thetas: List[float] = []
        for side in (side_a, side_b, side_c, side_d):
            ratio = _clamp(side / (2 * circumradius), -1.0, 1.0)
            thetas.append(2 * math.asin(ratio))

        points: List[Tuple[float, float]] = []
        angle_cursor = 0.0
        for theta in thetas:
            x = circumradius * math.cos(angle_cursor)
            y = circumradius * math.sin(angle_cursor)
            points.append((x, y))
            angle_cursor += theta

        return {"type": "polygon", "points": points}

    @staticmethod
    def build_tangential_quadrilateral(
        side_a: float,
        side_b: float,
        side_c: float,
        side_d: float,
        inradius: float,
    ) -> Dict:
        if min(side_a, side_b, side_c, side_d) <= 0:
            return {"type": "empty"}
        base = max(side_a, side_c)
        top = min(side_a, side_c)
        height = inradius * 2 if inradius > 0 else min(side_a, side_c) / 2
        offset = (base - top) / 2
        points = (
            (0.0, 0.0),
            (base, 0.0),
            (offset + top, height),
            (offset, height),
        )
        return {"type": "polygon", "points": list(points)}

    @staticmethod
    def build_quadrilateral_solver(p: float, q: float, angle_deg: float) -> Dict:
        if p <= 0 or q <= 0 or not (0 < angle_deg < 180):
            return {"type": "empty"}
        rad = math.radians(angle_deg)
        half_p = p / 2
        half_q = q / 2
        vec_q = (math.cos(rad), math.sin(rad))
        A = (-half_p, 0.0)
        C = (half_p, 0.0)
        B = (half_q * vec_q[0], half_q * vec_q[1])
        D = (-half_q * vec_q[0], -half_q * vec_q[1])
        return {"type": "polygon", "points": [A, B, C, D]}
