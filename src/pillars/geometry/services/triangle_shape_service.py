"""Triangle drawing service (no calculations beyond layout)."""
from __future__ import annotations

import math
from typing import Dict

from .triangle_math import triangle_points_from_sides, valid_triangle_sides


class TriangleShapeService:
    """Builds drawing instructions for triangle variants."""

    @staticmethod
    def build_from_sides(
        side_a: float,
        side_b: float,
        side_c: float,
        *,
        show_incircle: bool = False,
        show_circumcircle: bool = False,
        show_right_angle: bool = False,
    ) -> Dict:
        if not valid_triangle_sides(side_a, side_b, side_c):
            return {"type": "empty"}

        try:
            points = triangle_points_from_sides(side_a, side_b, side_c)
        except ValueError:
            return {"type": "empty"}

        payload: Dict = {
            "type": "polygon",
            "points": list(points),
        }

        if show_incircle:
            payload["show_incircle"] = True
        if show_circumcircle:
            payload["show_circumcircle"] = True
        if show_right_angle:
            payload["show_right_angle"] = True

        return payload

    @staticmethod
    def build_equilateral(side: float) -> Dict:
        if side <= 0:
            return {"type": "empty"}

        height = (side * math.sqrt(3)) / 2
        points = [
            (0.0, height * 2 / 3),
            (-side / 2, -height / 3),
            (side / 2, -height / 3),
        ]

        return {
            "type": "polygon",
            "points": points,
            "show_incircle": True,
            "show_circumcircle": True,
            "show_height": True,
        }

    @staticmethod
    def build_right(base: float, height: float) -> Dict:
        if base <= 0 or height <= 0:
            return {"type": "empty"}

        return {
            "type": "polygon",
            "points": [(0.0, 0.0), (base, 0.0), (0.0, height)],
            "show_right_angle": True,
        }
