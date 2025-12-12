"""Annulus (ring) shape calculator."""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class AnnulusShape(GeometricShape):
    """Represents a circular ring defined by outer and inner radii."""

    @property
    def name(self) -> str:
        return "Annulus"

    @property
    def description(self) -> str:
        return "Ring-shaped object, a region bounded by two concentric circles"

    @property
    def calculation_hint(self) -> str:
        return "Enter Outer Radius (R) + Inner Radius (r)"

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
            "ring_width": ShapeProperty(
                name="Ring Width (R - r)",
                key="ring_width",
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
            "area": ShapeProperty(
                name="Ring Area",
                key="area",
                unit="units²",
                readonly=True,
            ),
            "outer_circumference": ShapeProperty(
                name="Outer Circumference",
                key="outer_circumference",
                unit="units",
                readonly=True,
            ),
            "inner_circumference": ShapeProperty(
                name="Inner Circumference",
                key="inner_circumference",
                unit="units",
                readonly=True,
            ),
            "radius_ratio": ShapeProperty(
                name="Radius Ratio (R / r)",
                key="radius_ratio",
                readonly=True,
                precision=4,
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

        if property_key == "ring_width":
            return self._apply_ring_width(value)

        if property_key == "outer_diameter":
            return self.calculate_from_property("outer_radius", value / 2)

        if property_key == "inner_diameter":
            return self.calculate_from_property("inner_radius", value / 2)

        return False

    def _apply_ring_width(self, width: float) -> bool:
        if width <= 0:
            return False
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        if outer is not None:
            new_inner = outer - width
            if new_inner <= 0 or new_inner >= outer:
                return False
            self.properties["inner_radius"].value = new_inner
            self._update_metrics()
            return True
        if inner is not None:
            new_outer = inner + width
            if new_outer <= inner:
                return False
            self.properties["outer_radius"].value = new_outer
            self._update_metrics()
            return True
        return False

    def _update_metrics(self):
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value

        # Outer dependent values
        if outer is not None:
            self.properties["outer_diameter"].value = outer * 2
            self.properties["outer_circumference"].value = 2 * math.pi * outer
        else:
            self.properties["outer_diameter"].value = None
            self.properties["outer_circumference"].value = None

        # Inner dependent values
        if inner is not None:
            self.properties["inner_diameter"].value = inner * 2
            self.properties["inner_circumference"].value = 2 * math.pi * inner
        else:
            self.properties["inner_diameter"].value = None
            self.properties["inner_circumference"].value = None

        if outer is None or inner is None or inner <= 0 or outer <= inner:
            self.properties["ring_width"].value = None
            self.properties["area"].value = None
            self.properties["radius_ratio"].value = None
            return

        width = outer - inner
        self.properties["ring_width"].value = width
        self.properties["area"].value = math.pi * (outer * outer - inner * inner)
        self.properties["radius_ratio"].value = outer / inner if inner else None

    def get_drawing_instructions(self) -> Dict:
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        if outer is None:
            return {"type": "empty"}

        primitives = [
            {
                "shape": "circle",
                "center": (0.0, 0.0),
                "radius": outer,
                "pen": {"color": (14, 165, 233, 255), "width": 2.4},
                "brush": {"color": (191, 219, 254, 120)},
            }
        ]
        if inner is not None and inner > 0:
            primitives.append(
                {
                    "shape": "circle",
                    "center": (0.0, 0.0),
                    "radius": inner,
                    "pen": {"color": (15, 23, 42, 180), "width": 1.8},
                    "brush": {"color": (248, 250, 252, 255)},
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
        if outer is None:
            return labels

        labels.append((self._fmt("R", outer), outer * 0.6, 0.05))

        if inner is not None and inner > 0:
            labels.append((self._fmt("r", inner), inner * 0.3, -0.2))

        width = self.properties["ring_width"].value
        if width is not None:
            labels.append((self._fmt("w", width), 0, outer + 0.2))

        area = self.properties["area"].value
        if area is not None:
            labels.append((self._fmt("A", area), 0, -0.2))

        ratio = self.properties["radius_ratio"].value
        if ratio is not None:
            labels.append((self._fmt("R/r", ratio), 0, -outer - 0.3))

        return labels

    @staticmethod
    def _fmt(symbol: str, value: float) -> str:
        return f"{symbol} = {value:.4f}".rstrip("0").rstrip(".")
