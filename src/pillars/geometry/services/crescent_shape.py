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
        return "Lune/Crescent formed by two intersecting circles"

    @property
    def calculation_hint(self) -> str:
        return "Enter 2 Radii + Shift Distance"

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
        # Allow any non-negative offset provided circles are valid
        return offset >= 0

    @staticmethod
    def _circle_overlap_area(r1: float, r2: float, d: float) -> float:
        # Case 1: Disjoint (d >= r1 + r2) -> No overlap
        if d >= r1 + r2:
            return 0.0
        
        # Case 2: One inside other (d <= |r1 - r2|) -> Overlap is area of smaller circle
        # Note: We enforce r1 > r2 in _has_valid_geometry, so r2 is smaller.
        if d <= abs(r1 - r2):
            return math.pi * min(r1, r2) ** 2

        # Case 3: Intersection
        alpha = math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)) * 2
        beta = math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2)) * 2
        area1 = 0.5 * r1 * r1 * (alpha - math.sin(alpha))
        area2 = 0.5 * r2 * r2 * (beta - math.sin(beta))
        return area1 + area2

    @staticmethod
    def _crescent_perimeter(r1: float, r2: float, d: float) -> float:
        # Case 1: Disjoint (d >= r1 + r2) -> Inner circle is completely outside Outer
        # Result is just the Outer circle (minus nothing).
        if d >= r1 + r2:
            return 2 * math.pi * r1
            
        # Case 2: One inside other (d <= |r1 - r2|) -> Hole inside Outer
        # Result is Outer + Inner perimeters (Annulus-like)
        if d <= abs(r1 - r2):
            return 2 * math.pi * r1 + 2 * math.pi * r2
            
        # Case 3: Intersection
        # Arc of Outer (major) + Arc of Inner (minor)
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

        if inner is None or offset is None:
             # Just draw outer circle
            return {
                "type": "composite",
                "primitives": [
                    {
                        "shape": "circle",
                        "center": (0.0, 0.0),
                        "radius": outer,
                        "pen": {"color": (59, 130, 246, 255), "width": 2.4},
                        "brush": {"color": (147, 197, 253, 90)},
                    }
                ]
            }

        # Define Outer Circle
        outer_circle = {
            "shape": "circle",
            "center": (0.0, 0.0),
            "radius": outer,
            "pen": {"color": (59, 130, 246, 255), "width": 0.0}, # Pen handled by boolean container
            "brush": {"color": (0, 0, 0, 255), "enabled": True}, # Fill required for path op
        }
        
        # Define Inner Circle (The Cutter)
        inner_circle = {
            "shape": "circle",
            "center": (offset, 0.0),
            "radius": inner,
            "pen": {"color": (0, 0, 0, 255), "width": 0.0},
            "brush": {"color": (0, 0, 0, 255), "enabled": True},
        }

        # The result (Crescent)
        crescent = {
            "type": "boolean",
            "operation": "difference",
            "shape_a": outer_circle,
            "shape_b": inner_circle,
            "pen": {"color": (59, 130, 246, 255), "width": 2.4}, # Blue Border
            "brush": {"color": (59, 130, 246, 120), "enabled": True}, # Blue Fill
        }

        primitives = [crescent]
        
        # Optional: Dashed outline of the cutter for reference?
        # User requested "The Crescent", implies just the result mostly.
        # But seeing the invisible inner circle boundary is helpful.
        primitives.append({
             "shape": "circle",
             "center": (offset, 0.0),
             "radius": inner,
             "pen": {"color": (15, 23, 42, 100), "width": 1.0, "dashed": True},
             "brush": {"enabled": False}
        })

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
            labels.append((self._fmt("A", crescent_area), -outer * 0.3, 0.2))

        return labels

    @staticmethod
    def _fmt(symbol: str, value: float) -> str:
        return f"{symbol} = {value:.4f}".rstrip("0").rstrip(".")
