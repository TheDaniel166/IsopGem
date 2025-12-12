"""Vesica Piscis shape calculator."""
import math
from typing import Dict, List, Sequence, Tuple

from .base_shape import GeometricShape, ShapeProperty


class VesicaPiscisShape(GeometricShape):
    """Lens formed by two equal-radius circles."""

    @property
    def name(self) -> str:
        return "Vesica Piscis"

    @property
    def description(self) -> str:
        return "Lens shape formed by the intersection of two congruent disks"

    @property
    def calculation_hint(self) -> str:
        return "Calculate from any field (1-DoF)"

    def _init_properties(self):
        self.properties = {
            "radius": ShapeProperty(
                name="Circle Radius",
                key="radius",
                unit="units",
            ),
            "diameter": ShapeProperty(
                name="Diameter",
                key="diameter",
                unit="units",
            ),
            "separation": ShapeProperty(
                name="Center Separation",
                key="separation",
                unit="units",
            ),
            "lens_height": ShapeProperty(
                name="Lens Height",
                key="lens_height",
                unit="units",
                readonly=True,
            ),
            "lens_area": ShapeProperty(
                name="Lens Area",
                key="lens_area",
                unit="units²",
                readonly=True,
            ),
            "perimeter": ShapeProperty(
                name="Lens Perimeter",
                key="perimeter",
                unit="units",
                readonly=True,
            ),
            "apex_angle": ShapeProperty(
                name="Arc Angle (°)",
                key="apex_angle",
                unit="°",
                readonly=True,
                precision=2,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if value <= 0:
            return False

        if property_key == "radius":
            self.properties["radius"].value = value
            self.properties["diameter"].value = value * 2
            self._update_metrics()
            return True

        if property_key == "diameter":
            return self.calculate_from_property("radius", value / 2)

        if property_key == "separation":
            radius = self.properties["radius"].value
            if radius is None:
                return False
            if not (0 < value <= 2 * radius):
                return False
            self.properties["separation"].value = value
            self._update_metrics()
            return True

        return False

    def _update_metrics(self):
        radius = self.properties["radius"].value
        separation = self.properties["separation"].value
        if radius is None:
            for key in ("lens_height", "lens_area", "perimeter", "apex_angle"):
                self.properties[key].value = None
            return

        if separation is None:
            for key in ("lens_height", "lens_area", "perimeter", "apex_angle"):
                self.properties[key].value = None
            return

        if not (0 < separation <= 2 * radius):
            for key in ("lens_height", "lens_area", "perimeter", "apex_angle"):
                self.properties[key].value = None
            return

        half_sep = separation / 2
        height = 2 * math.sqrt(max(radius * radius - half_sep * half_sep, 0.0))
        area = self._circle_overlap_area(radius, separation)
        angle = 2 * math.acos(min(1.0, max(-1.0, separation / (2 * radius))))
        perimeter = 2 * radius * angle

        self.properties["lens_height"].value = height
        self.properties["lens_area"].value = area
        self.properties["perimeter"].value = perimeter
        self.properties["apex_angle"].value = math.degrees(angle)

    @staticmethod
    def _circle_overlap_area(radius: float, separation: float) -> float:
        if separation <= 0:
            return math.pi * radius * radius
        if separation >= 2 * radius:
            return 0.0
        part = math.acos(separation / (2 * radius))
        area = 2 * radius * radius * part - 0.5 * separation * math.sqrt(4 * radius * radius - separation * separation)
        return area

    def get_drawing_instructions(self) -> Dict:
        radius = self.properties["radius"].value
        separation = self.properties["separation"].value
        if radius is None:
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
            lens_points = self._lens_points(radius, separation)
            if lens_points:
                primitives.append(
                    {
                        "shape": "polygon",
                        "points": lens_points,
                        "pen": {"color": (14, 165, 233, 200), "width": 1.5},
                        "brush": {"color": (125, 211, 252, 120)},
                    }
                )

        return {
            "type": "composite",
            "primitives": primitives,
        }

    def _lens_points(self, radius: float, separation: float, steps: int = 90) -> List[Tuple[float, float]]:
        half_sep = separation / 2
        span = radius * radius - half_sep * half_sep
        if span <= 0:
            return []
        height = math.sqrt(span)
        left_center = (-half_sep, 0.0)
        right_center = (half_sep, 0.0)
        top_angle = math.atan2(height, half_sep)
        bottom_angle = -top_angle

        left_arc = self._arc_samples(left_center, radius, top_angle, bottom_angle, steps)
        right_arc = self._arc_samples(right_center, radius, bottom_angle, top_angle, steps)
        return left_arc + right_arc[1:]

    @staticmethod
    def _arc_samples(center: Tuple[float, float], radius: float, start: float, end: float, steps: int) -> List[Tuple[float, float]]:
        count = max(2, steps)
        points: List[Tuple[float, float]] = []
        for idx in range(count):
            t = idx / (count - 1)
            angle = start + (end - start) * t
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        return points

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        labels: List[Tuple[str, float, float]] = []
        radius = self.properties["radius"].value
        separation = self.properties["separation"].value
        if radius is None:
            return labels

        labels.append((self._fmt("r", radius), -radius * 0.2, radius * 0.1))
        if separation is not None:
            labels.append((self._fmt("d", separation), 0, -0.25))
        area = self.properties["lens_area"].value
        if area is not None:
            labels.append((self._fmt("A", area), 0, 0))
        angle = self.properties["apex_angle"].value
        if angle is not None:
            label_y = radius * 0.6 if separation else radius * 0.5
            labels.append((self._fmt("θ", angle), 0, label_y))
        return labels

    @staticmethod
    def _fmt(symbol: str, value: float) -> str:
        return f"{symbol} = {value:.4f}".rstrip("0").rstrip(".")
