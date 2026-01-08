"""Seed of Life shape calculator."""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class SeedOfLifeShape(GeometricShape):
    """The Seed of Life: 7 circles in hexagonal symmetry."""

    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Seed of Life"

    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "Seven circles arranged with six-fold symmetry, forming a pattern of creation."

    @property
    def calculation_hint(self) -> str:
        """
        Calculation hint logic.
        
        Returns:
            Result of calculation_hint operation.
        """
        return "Calculate from Radius, Area, or Width"

    def _init_properties(self):
        self.properties = {
            "radius": ShapeProperty(
                name="Circle Radius",
                key="radius",
                unit="units",
                default=10.0,
                formula=r"r",
            ),
            "diameter": ShapeProperty(
                name="Circle Diameter",
                key="diameter",
                unit="units",
                readonly=False,
                formula=r"d = 2r",
            ),
            "total_width": ShapeProperty(
                name="Total Width (Extents)",
                key="total_width",
                unit="units",
                readonly=False,
                formula=r"W = 4r",
            ),
            "circle_area": ShapeProperty(
                name="Single Circle Area",
                key="circle_area",
                unit="units²",
                readonly=False,
                formula=r"A_{\circ} = \pi r^2",
            ),
            "total_area": ShapeProperty(
                name="Total Enclosed Area",
                key="total_area",
                unit="units²",
                readonly=True,
            ),
            "circle_circumference": ShapeProperty(
                name="Circle Circumference",
                key="circle_circumference",
                unit="units",
                readonly=False,
                formula=r"C_{\circ} = 2\pi r",
            ),
            "vesica_height": ShapeProperty(
                name="Vesica Height",
                key="vesica_height",
                unit="units",
                readonly=True,
                formula=r"h_v = r\sqrt{3}",
            ),
            "vesica_area": ShapeProperty(
                name="Vesica (Petal) Area",
                key="vesica_area",
                unit="units²",
                readonly=False,
                formula=r"A_v = r^2\left(\tfrac{2\pi}{3} - \tfrac{\sqrt{3}}{2}\right)",
            ),
            "flower_area": ShapeProperty(
                name="Flower (Rosette) Area",
                key="flower_area",
                unit="units²",
                readonly=False,
                formula=r"A_{flower} = 6A_v",
            ),
            "flower_perimeter": ShapeProperty(
                name="Flower Perimeter",
                key="flower_perimeter",
                unit="units",
                readonly=True,
                formula=r"P_{flower} = 4\pi r",
            ),
            "outer_perimeter": ShapeProperty(
                name="Outer Perimeter",
                key="outer_perimeter",
                unit="units",
                readonly=True,
                formula=r"P_{outer} = 4\pi r",
            ),
            "enclosing_circle_area": ShapeProperty(
                name="Enclosing Circle Area",
                key="enclosing_circle_area",
                unit="units²",
                readonly=True,
                formula=r"A_{encl} = \pi(2r)^2",
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """
        Compute from property logic.
        
        Args:
            property_key: Description of property_key.
            value: Description of value.
        
        Returns:
            Result of calculate_from_property operation.
        """
        if value <= 0:
            return False

        if property_key == "radius":
            self.properties["radius"].value = value
            self._update_metrics()
            return True

        # Diameter = 2 * r
        if property_key == "diameter":
            return self.calculate_from_property("radius", value / 2.0)

        # Total Width = 4 * r
        if property_key == "total_width":
            return self.calculate_from_property("radius", value / 4.0)

        # Area = pi * r^2
        if property_key == "circle_area":
            return self.calculate_from_property("radius", math.sqrt(value / math.pi))

        # Circumference = 2 * pi * r
        if property_key == "circle_circumference":
            return self.calculate_from_property("radius", value / (2 * math.pi))

        # Vesica Area = r^2 * (2pi/3 - sqrt(3)/2)
        # r = sqrt(Area / (2pi/3 - sqrt(3)/2))
        if property_key == "vesica_area":
            factor = (2 * math.pi / 3) - (math.sqrt(3) / 2)
            return self.calculate_from_property("radius", math.sqrt(value / factor))

        # Flower Area = 6 * Vesica Area
        if property_key == "flower_area":
            return self.calculate_from_property("vesica_area", value / 6.0)

        return False

    def _update_metrics(self):
        r = self.properties["radius"].value
        if r is None:
            for key in self.properties:
                if key != "radius":
                    self.properties[key].value = None
            return

        self.properties["diameter"].value = 2 * r
        self.properties["total_width"].value = 4 * r
        self.properties["circle_area"].value = math.pi * r * r
        self.properties["circle_circumference"].value = 2 * math.pi * r
        self.properties["vesica_height"].value = r * math.sqrt(3)
        
        # Derived calculations
        # Vesica Area
        vesica_factor = (2 * math.pi / 3) - (math.sqrt(3) / 2)
        v_area = r * r * vesica_factor
        self.properties["vesica_area"].value = v_area
        self.properties["flower_area"].value = 6 * v_area
        
        # Perimeters
        # Both Flower and Outer (Cloud) perimeter = 4 * pi * r
        # This equals the circumference of the enclosing circle (radius 2r)
        p_val = 4 * math.pi * r
        self.properties["flower_perimeter"].value = p_val
        self.properties["outer_perimeter"].value = p_val
        
        # Enclosing Circle (Radius 2r)
        self.properties["enclosing_circle_area"].value = math.pi * (2 * r) ** 2

        self.properties["total_area"].value = None

    def get_drawing_instructions(self) -> Dict:
        """
        Retrieve drawing instructions logic.
        
        Returns:
            Result of get_drawing_instructions operation.
        """
        r = self.properties["radius"].value
        if r is None:
            return {"type": "empty"}

        primitives = []
        
        # Style
        # Central circle: Gold/Sun
        # Outer circles: Blue/Water or White/Light?
        
        # 1. Central Circle
        primitives.append({
            "shape": "circle",
            "center": (0.0, 0.0),
            "radius": r,
            "pen": {"color": (234, 179, 8, 255), "width": 2.0}, # Yellow-600
            "brush": {"color": (254, 240, 138, 50)}, # Yellow-200 transparent
        })

        # 2. Six surrounding circles
        # Centers are at (r, theta) for theta = 0, 60, 120...
        cyan_pen = {"color": (6, 182, 212, 255), "width": 2.0} # Cyan-500
        cyan_brush = {"color": (165, 243, 252, 50)} # Cyan-200 transparent

        for i in range(6):
            angle_deg = i * 60
            angle_rad = math.radians(angle_deg)
            cx = r * math.cos(angle_rad)
            cy = r * math.sin(angle_rad)
            
            primitives.append({
                "shape": "circle",
                "center": (cx, cy),
                "radius": r,
                "pen": cyan_pen,
                "brush": cyan_brush,
            })

        return {
            "type": "composite",
            "primitives": primitives,
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """
        Retrieve label positions logic.
        
        Returns:
            Result of get_label_positions operation.
        """
        labels = []
        r = self.properties["radius"].value
        if r is None:
            return labels
        
        # Label Radius on the central circle
        labels.append((f"r={r:.2f}", r/2, 0.0))
        
        return labels