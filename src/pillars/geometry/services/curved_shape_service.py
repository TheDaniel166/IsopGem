"""Curved shape drawing services (annulus, crescent, vesica piscis, rose curve)."""
from __future__ import annotations

import math
from typing import Dict, List, Tuple


class AnnulusShapeService:
    """Builds drawing instructions for annuli."""

    @staticmethod
    def build(outer_radius: float, inner_radius: float | None = None) -> Dict:
        if outer_radius <= 0:
            return {"type": "empty"}

        primitives = [
            {
                "shape": "circle",
                "center": (0.0, 0.0),
                "radius": outer_radius,
                "pen": {"color": (14, 165, 233, 255), "width": 2.4},
                "brush": {"color": (191, 219, 254, 120)},
            }
        ]

        if inner_radius is not None and inner_radius > 0:
            primitives.append(
                {
                    "shape": "circle",
                    "center": (0.0, 0.0),
                    "radius": inner_radius,
                    "pen": {"color": (15, 23, 42, 180), "width": 1.8},
                    "brush": {"color": (248, 250, 252, 255)},
                }
            )

        return {"type": "composite", "primitives": primitives}


class CrescentShapeService:
    """Builds drawing instructions for crescents (lunes)."""

    @staticmethod
    def build(outer_radius: float, inner_radius: float | None, offset: float | None) -> Dict:
        if outer_radius <= 0:
            return {"type": "empty"}

        if inner_radius is None or offset is None or inner_radius <= 0:
            return {
                "type": "composite",
                "primitives": [
                    {
                        "shape": "circle",
                        "center": (0.0, 0.0),
                        "radius": outer_radius,
                        "pen": {"color": (59, 130, 246, 255), "width": 2.4},
                        "brush": {"color": (147, 197, 253, 90)},
                    }
                ],
            }

        outer_circle = {
            "shape": "circle",
            "center": (0.0, 0.0),
            "radius": outer_radius,
            "pen": {"color": (59, 130, 246, 255), "width": 0.0},
            "brush": {"color": (0, 0, 0, 255), "enabled": True},
        }

        inner_circle = {
            "shape": "circle",
            "center": (offset, 0.0),
            "radius": inner_radius,
            "pen": {"color": (0, 0, 0, 255), "width": 0.0},
            "brush": {"color": (0, 0, 0, 255), "enabled": True},
        }

        crescent = {
            "type": "boolean",
            "operation": "difference",
            "shape_a": outer_circle,
            "shape_b": inner_circle,
            "pen": {"color": (59, 130, 246, 255), "width": 2.4},
            "brush": {"color": (59, 130, 246, 120), "enabled": True},
        }

        primitives = [crescent]
        primitives.append(
            {
                "shape": "circle",
                "center": (offset, 0.0),
                "radius": inner_radius,
                "pen": {"color": (15, 23, 42, 100), "width": 1.0, "dashed": True},
                "brush": {"enabled": False},
            }
        )

        return {"type": "composite", "primitives": primitives}


class VesicaPiscisShapeService:
    """Builds drawing instructions for vesica piscis forms."""

    @staticmethod
    def build(radius: float, separation: float | None) -> Dict:
        if radius <= 0:
            return {"type": "empty"}

        half_sep = (separation or radius) / 2
        left_center = (-half_sep, 0.0)
        right_center = (half_sep, 0.0)

        primitives = [
            {
                "shape": "circle",
                "center": left_center,
                "radius": radius,
                "pen": {"color": (59, 130, 246, 255), "width": 2.0},
                "brush": {"color": (191, 219, 254, 90)},
            },
            {
                "shape": "circle",
                "center": right_center,
                "radius": radius,
                "pen": {"color": (99, 102, 241, 255), "width": 2.0},
                "brush": {"color": (199, 210, 254, 90)},
            },
        ]

        if separation is not None and 0 < separation <= 2 * radius:
            lens_points = VesicaPiscisShapeService._lens_points(radius, separation)
            if lens_points:
                primitives.append(
                    {
                        "shape": "polygon",
                        "points": lens_points,
                        "pen": {"color": (14, 165, 233, 200), "width": 1.5},
                        "brush": {"color": (125, 211, 252, 120)},
                    }
                )

        return {"type": "composite", "primitives": primitives}

    @staticmethod
    def _lens_points(radius: float, separation: float, steps: int = 90) -> List[Tuple[float, float]]:
        half_sep = separation / 2
        span = radius * radius - half_sep * half_sep
        if span <= 0:
            return []
        height = math.sqrt(span)
        left_center = (-half_sep, 0.0)
        right_center = (half_sep, 0.0)
        top_angle = math.atan2(height, half_sep)
        bottom_angle = -top_angle

        left_arc = VesicaPiscisShapeService._arc_samples(left_center, radius, top_angle, bottom_angle, steps)
        right_arc = VesicaPiscisShapeService._arc_samples(right_center, radius, bottom_angle, top_angle, steps)
        return left_arc + right_arc[1:]

    @staticmethod
    def _arc_samples(
        center: Tuple[float, float],
        radius: float,
        start: float,
        end: float,
        steps: int,
    ) -> List[Tuple[float, float]]:
        count = max(2, steps)
        points: List[Tuple[float, float]] = []
        for idx in range(count):
            t = idx / (count - 1)
            angle = start + (end - start) * t
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        return points


class RoseCurveShapeService:
    """Builds drawing instructions for rhodonea curves."""

    @staticmethod
    def build(amplitude: float, k_value: int) -> Dict:
        if amplitude <= 0 or k_value <= 0:
            return {"type": "empty"}

        points = RoseCurveShapeService._generate_points(amplitude, k_value)
        primitives = [
            {
                "shape": "polyline",
                "points": points,
                "pen": {"color": (236, 72, 153, 255), "width": 2.0},
            }
        ]
        return {"type": "composite", "primitives": primitives}

    @staticmethod
    def _generate_points(amplitude: float, k_value: int, steps: int = 1200) -> List[Tuple[float, float]]:
        points: List[Tuple[float, float]] = []
        total = max(steps, 360)
        for idx in range(total + 1):
            theta = 2 * math.pi * (idx / total)
            radius = amplitude * math.cos(k_value * theta)
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            points.append((x, y))
        return points
