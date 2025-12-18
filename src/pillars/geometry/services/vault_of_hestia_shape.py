"""Vault of Hestia sacred geometry service."""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class VaultOfHestiaShape(GeometricShape):
    """
    The Vault of Hestia: A Square containing an Inscribed Isosceles Triangle,
    containing an Incircle.
    
    Geometric Significance:
    - The semi-perimeter of the triangle is s * Phi.
    - The inradius of the circle is s / (2 * Phi).
    """

    @property
    def name(self) -> str:
        return "Vault of Hestia"

    @property
    def description(self) -> str:
        return "Square holding an Isosceles Triangle and its Incircle, generating the Golden Ratio."

    @property
    def calculation_hint(self) -> str:
        return "Enter the Side Length (s) of the square."

    def _init_properties(self):
        self.properties = {
            "side_length": ShapeProperty(
                name="Side Length (s)",
                key="side_length",
                unit="units",
                default=10.0,
            ),
            "triangle_leg": ShapeProperty(
                name="Triangle Leg",
                key="triangle_leg",
                unit="units",
                readonly=False,
            ),
            "inradius": ShapeProperty(
                name="Circle Radius (r)",
                key="inradius",
                unit="units",
                readonly=False,
            ),
            "phi_check": ShapeProperty(
                name="Phi Check (s/2r)",
                key="phi_check",
                unit="",
                readonly=True,
                precision=6,
            ),
            "triangle_area": ShapeProperty(
                name="Triangle Area",
                key="triangle_area",
                unit="units²",
                readonly=False,
            ),
            "circle_area": ShapeProperty(
                name="Circle Area",
                key="circle_area",
                unit="units²",
                readonly=False,
            ),
            "hestia_ratio": ShapeProperty(
                name="Hestia Ratio (A_circ/A_sq)",
                key="hestia_ratio",
                unit="",
                readonly=True,
                precision=6,
            ),
            "triangle_perimeter": ShapeProperty(
                name="Triangle Perimeter",
                key="triangle_perimeter",
                unit="units",
                readonly=True,
            ),
            "triangle_semi_perimeter": ShapeProperty(
                name="Triangle Semi-Perimeter (s*Phi)",
                key="triangle_semi_perimeter",
                unit="units",
                readonly=True,
            ),
            "circumradius": ShapeProperty(
                name="Triangle Circumradius (R)",
                key="circumradius",
                unit="units",
                readonly=False, # Editable
            ),
            "square_diagonal": ShapeProperty(
                name="Square Diagonal",
                key="square_diagonal",
                unit="units",
                readonly=False, # Editable
            ),
            "base_angle": ShapeProperty(
                name="Base Angle",
                key="base_angle",
                unit="deg",
                readonly=True,
            ),
            "void_area": ShapeProperty(
                name="Void Area (Sq - Circ)",
                key="void_area",
                unit="units²",
                readonly=True,
            ),
            "circle_diameter": ShapeProperty(
                name="Circle Diameter (d)",
                key="circle_diameter",
                unit="units",
                readonly=False,
            ),
            "circle_circumference": ShapeProperty(
                name="Circle Circumference",
                key="circle_circumference",
                unit="units",
                readonly=False,
            ),
            "square_area": ShapeProperty(
                name="Square Area",
                key="square_area",
                unit="units²",
                readonly=False,
            ),
            "area_sq_minus_tri": ShapeProperty(
                name="Area (Square - Triangle)",
                key="area_sq_minus_tri",
                unit="units²",
                readonly=True,
            ),
            "area_tri_minus_circ": ShapeProperty(
                name="Area (Triangle - Circle)",
                key="area_tri_minus_circ",
                unit="units²",
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if value <= 0:
            return False

        # Constants
        phi = (1 + math.sqrt(5)) / 2

        if property_key == "side_length":
            self.properties["side_length"].value = value
            self._update_metrics()
            return True
        
        elif property_key == "triangle_leg":
            # leg = s * sqrt(5) / 2  =>  s = leg * 2 / sqrt(5)
            s = value * 2 / math.sqrt(5)
            self.properties["side_length"].value = s
            self._update_metrics()
            return True
            
        elif property_key == "inradius":
            # r = s / (2 * phi)  =>  s = r * 2 * phi
            s = value * 2 * phi
            self.properties["side_length"].value = s
            self._update_metrics()
            return True
        
        elif property_key == "triangle_area":
            # Area = s^2 / 2  =>  s = sqrt(2 * Area)
            s = math.sqrt(2 * value)
            self.properties["side_length"].value = s
            self._update_metrics()
            return True
            
        elif property_key == "circle_area":
            # Area = pi * r^2  =>  r = sqrt(Area / pi)
            r = math.sqrt(value / math.pi)
            # s = r * 2 * phi
            s = r * 2 * phi
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "circumradius":
            # R = (5/8) * s => s = R * (8/5)
            s = value * 8 / 5
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "square_diagonal":
            # d = s * sqrt(2) => s = d / sqrt(2)
            s = value / math.sqrt(2)
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "circle_diameter":
            # d = 2r => r = d/2.  s = r * 2 * phi
            r = value / 2
            s = r * 2 * phi
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "circle_circumference":
            # C = 2 * pi * r => r = C / (2 * pi)
            r = value / (2 * math.pi)
            s = r * 2 * phi
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        elif property_key == "square_area":
            # A = s^2 => s = sqrt(A)
            s = math.sqrt(value)
            self.properties["side_length"].value = s
            self._update_metrics()
            return True

        return False

    def _update_metrics(self):
        s = self.properties["side_length"].value
        if not s:
            return

        # Constants
        phi = (1 + math.sqrt(5)) / 2
        
        # Triangle (Base=s, Height=s)
        # Leg = sqrt((s/2)^2 + s^2) = s * sqrt(1.25) = s * sqrt(5)/2
        leg = s * math.sqrt(5) / 2
        
        # Area = 1/2 * b * h = s^2 / 2
        tri_area = (s * s) / 2
        
        # Semiperimeter = s * phi
        # Inradius = Area / s_p = (s^2/2) / (s*phi) = s / (2*phi)
        r = s / (2 * phi)
        
        circle_area = math.pi * r * r
        square_area = s * s
        hestia_ratio = circle_area / square_area
        
        phi_check = s / (2 * r) if r > 0 else 0

        # New Calculations
        # Triangle Perimeter = leg + leg + base = 2*leg + s
        # leg = s * sqrt(5)/2
        tri_perimeter = (2 * leg) + s
        
        # Semi-Perimeter
        tri_semi_perimeter = tri_perimeter / 2
        
        # Circumradius (R)
        # For Isosceles Triangle with sides a, a, b (where a=leg, b=s)
        # R = a^2 / sqrt(4a^2 - b^2)
        # a^2 = (s^2 * 5) / 4
        # 4a^2 = 5s^2
        # sqrt(4a^2 - b^2) = sqrt(5s^2 - s^2) = sqrt(4s^2) = 2s
        # R = (5/4 s^2) / 2s = (5/8) * s
        circumradius = (5/8) * s
        
        # Square Diagonal = s * sqrt(2)
        square_diag = s * math.sqrt(2)
        
        # Base Angle = arctan(height / (base/2)) = arctan(s / (s/2)) = arctan(2)
        base_angle_rad = math.atan(2)
        base_angle_deg = math.degrees(base_angle_rad)
        
        # Void Area = Square Area - Circle Area
        void_area = square_area - circle_area

        # New Area Metrics
        # Square Area already calculated as 'square_area'
        
        # Circle metrics
        circ_diameter = 2 * r
        circ_circumference = 2 * math.pi * r
        
        # Area Differences
        area_sq_minus_tri = square_area - tri_area
        area_tri_minus_circ = tri_area - circle_area

        self.properties["triangle_leg"].value = leg
        self.properties["inradius"].value = r
        self.properties["triangle_area"].value = tri_area
        self.properties["circle_area"].value = circle_area
        self.properties["hestia_ratio"].value = hestia_ratio
        self.properties["phi_check"].value = phi_check
        
        self.properties["triangle_perimeter"].value = tri_perimeter
        self.properties["triangle_semi_perimeter"].value = tri_semi_perimeter
        self.properties["circumradius"].value = circumradius
        self.properties["square_diagonal"].value = square_diag
        self.properties["base_angle"].value = base_angle_deg
        self.properties["void_area"].value = void_area
        
        self.properties["circle_diameter"].value = circ_diameter
        self.properties["circle_circumference"].value = circ_circumference
        self.properties["square_area"].value = square_area
        self.properties["area_sq_minus_tri"].value = area_sq_minus_tri
        self.properties["area_tri_minus_circ"].value = area_tri_minus_circ

    def get_drawing_instructions(self) -> Dict:
        s = self.properties["side_length"].value
        if not s:
            return {"type": "empty"}

        # Coordinate System: Center of Square at (0,0)
        # Square: x = [-s/2, s/2], y = [-s/2, s/2]
        half_s = s / 2
        
        # Square Points
        sq_p1 = (-half_s, -half_s)
        sq_p2 = (half_s, -half_s)
        sq_p3 = (half_s, half_s)
        sq_p4 = (-half_s, half_s)
        square_poly = [sq_p1, sq_p2, sq_p3, sq_p4, sq_p1]
        
        # Triangle Points (Base at bottom, Apex at top)
        # Base: (-s/2, -s/2) to (s/2, -s/2)
        # Apex: (0, s/2)
        tri_p1 = (-half_s, -half_s)
        tri_p2 = (half_s, -half_s)
        tri_p3 = (0, half_s)
        triangle_poly = [tri_p1, tri_p2, tri_p3, tri_p1]
        
        # Circle
        # Radius r
        # Center y = bottom + r = -s/2 + r
        r = self.properties["inradius"].value
        cy = -half_s + r
        
        primitives = [
            # Square (Blue)
            {
                "shape": "polyline",
                "points": square_poly,
                "pen": {"color": (59, 130, 246, 255), "width": 2.0},
            },
            # Triangle (Orange)
            {
                "shape": "polyline",
                "points": triangle_poly,
                "pen": {"color": (249, 115, 22, 255), "width": 2.0},
            },
            # Circle (Teal)
            {
                "shape": "circle",
                "center": (0, cy),
                "radius": r,
                "pen": {"color": (20, 184, 166, 255), "width": 2.0},
            }
        ]
        
        return {
            "type": "composite",
            "primitives": primitives,
        }
        
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        labels: List[Tuple[str, float, float]] = []
        s = self.properties["side_length"].value
        if not s:
            return labels
            
        r = self.properties["inradius"].value
        ratio = self.properties["hestia_ratio"].value
        
        # Label s at bottom
        labels.append((f"s = {s:g}", 0, -s/2 * 1.05))
        
        # Label r at center (approx)
        cy = -s/2 + r
        if r:
            labels.append((f"r = {r:.3f}", 0, cy))
            
        # Label Ratio at top
        if ratio:
            labels.append((f"Ratio = {ratio:.5f}", 0, s/2 * 1.05))
            
        return labels
