"""Crescent (lune) shape calculator."""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class CrescentShape(GeometricShape):
    """Represents the lune carved from an outer circle by an offset smaller circle."""

    @property
    def name(self) -> str:
        return "Crescent"

    @property
    def description(self) -> str:
        return "Lune carved by two intersecting circles with offset and overlap metrics"

    def _init_properties(self):
        self.properties = {
            "outer_radius": ShapeProperty(
                name="Outer Radius (R)",
                key="outer_radius",
                unit="units",
            ),
            "inner_radius": ShapeProperty(
                name="Inner Radius (r)",
                key="inner_radius",
                unit="units",
            ),
            "offset": ShapeProperty(
                name="Center Offset (d)",
                key="offset",
                unit="units",
            ),
            "outer_diameter": ShapeProperty(
                name="Outer Diameter",
                key="outer_diameter",
                unit="units",
            ),
            "inner_diameter": ShapeProperty(
                name="Inner Diameter",
                key="inner_diameter",
                unit="units",
            ),
            "intersection_area": ShapeProperty(
                name="Overlap Area",
                key="intersection_area",
                unit="units²",
                readonly=True,
            ),
            "crescent_area": ShapeProperty(
                name="Crescent Area",
                key="crescent_area",
                unit="units²",
                readonly=True,
            ),
            "perimeter": ShapeProperty(
                name="Crescent Perimeter",
                key="perimeter",
                unit="units",
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if value <= 0:
            return False

        if property_key == "outer_radius":
            inner = self.properties["inner_radius"].value
            if inner is not None and value <= inner:
                return False
            self.properties["outer_radius"].value = value
            self._update_metrics()
            return True

        if property_key == "inner_radius":
            outer = self.properties["outer_radius"].value
            if outer is not None and value >= outer:
                return False
            self.properties["inner_radius"].value = value
            self._update_metrics()
            return True

        if property_key == "offset":
            outer = self.properties["outer_radius"].value
            inner = self.properties["inner_radius"].value
            if outer is None or inner is None:
                return False
            if not self._is_valid_offset(outer, inner, value):
                return False
            self.properties["offset"].value = value
            self._update_metrics()
            return True

        if property_key == "outer_diameter":
            return self.calculate_from_property("outer_radius", value / 2)

        if property_key == "inner_diameter":
            return self.calculate_from_property("inner_radius", value / 2)

        return False

    def _update_metrics(self):
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        offset = self.properties["offset"].value

        self.properties["outer_diameter"].value = outer * 2 if outer else None
        self.properties["inner_diameter"].value = inner * 2 if inner else None

        if not self._has_valid_geometry(outer, inner, offset):
            self.properties["intersection_area"].value = None
            self.properties["crescent_area"].value = None
            self.properties["perimeter"].value = None
            return

        assert outer is not None and inner is not None and offset is not None
        overlap = self._circle_overlap_area(outer, inner, offset)
        crescent_area = math.pi * outer * outer - overlap
        perimeter = self._crescent_perimeter(outer, inner, offset)

        self.properties["intersection_area"].value = overlap
        self.properties["crescent_area"].value = crescent_area
        self.properties["perimeter"].value = perimeter

    @staticmethod
    def _has_valid_geometry(outer, inner, offset) -> bool:
        if outer is None or inner is None or offset is None:
            return False
        if outer <= inner:
            return False
        return CrescentShape._is_valid_offset(outer, inner, offset)

    @staticmethod
    def _is_valid_offset(outer: float, inner: float, offset: float) -> bool:
        # Require partial overlap but no containment to preserve a crescent shape
        return abs(outer - inner) < offset < (outer + inner)

    @staticmethod
    def _circle_overlap_area(r1: float, r2: float, d: float) -> float:
        if d <= 0:
            return 0.0
        if d >= r1 + r2:
            return 0.0
        if d <= abs(r1 - r2):
            return math.pi * min(r1, r2) ** 2

        alpha = math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)) * 2
        beta = math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2)) * 2
        area1 = 0.5 * r1 * r1 * (alpha - math.sin(alpha))
        area2 = 0.5 * r2 * r2 * (beta - math.sin(beta))
        return area1 + area2

    @staticmethod
    def _crescent_perimeter(r1: float, r2: float, d: float) -> float:
        if d <= 0:
            return 0.0
        alpha = math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)) * 2
        beta = math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2)) * 2
        outer_arc = (2 * math.pi - alpha) * r1
        inner_arc = beta * r2
        return outer_arc + inner_arc

    def get_drawing_instructions(self) -> Dict:
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        offset = self.properties["offset"].value
        if outer is None:
            return {"type": "empty"}

        primitives = [
            {
                "shape": "circle",
                "center": (0.0, 0.0),
                "radius": outer,
                "pen": {"color": (59, 130, 246, 255), "width": 2.4},
                "brush": {"color": (147, 197, 253, 90)},
            }
        ]
        if inner is not None and offset is not None:
            primitives.append(
                {
                    "shape": "circle",
                    "center": (offset, 0.0),
                    "radius": inner,
                    "pen": {"color": (248, 113, 113, 255), "width": 2.0},
                    "brush": {"color": (254, 205, 211, 90)},
                }
            )
            primitives.append(
                {
                    "shape": "line",
                    "start": (0.0, 0.0),
                    "end": (offset, 0.0),
                    "pen": {"color": (15, 23, 42, 200), "width": 1.2, "dashed": True},
                }
            )

        return {
            "type": "composite",
            "primitives": primitives,
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        labels: List[Tuple[str, float, float]] = []
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        offset = self.properties["offset"].value
        if outer is None:
            return labels

        labels.append((self._fmt("R", outer), outer * 0.65, 0.1))
        if inner is not None:
            labels.append((self._fmt("r", inner), (offset or 0) + inner * 0.4, 0.1))
        if offset is not None:
            labels.append((self._fmt("d", offset), offset / 2, -0.25))

        crescent_area = self.properties["crescent_area"].value
        if crescent_area is not None:
            labels.append((self._fmt("A", crescent_area), -outer * 0.3, 0))

        return labels

    @staticmethod
    def _fmt(symbol: str, value: float) -> str:
        return f"{symbol} = {value:.4f}".rstrip("0").rstrip(".")
