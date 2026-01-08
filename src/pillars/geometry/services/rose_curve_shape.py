"""Rose (Rhodonea) curve calculator."""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class RoseCurveShape(GeometricShape):
    """Rhodonea curve defined by r = a · cos(kθ)."""

    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Rose Curve"

    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "Sinusoid characterized by polar equation r = cos(kθ)"

    @property
    def calculation_hint(self) -> str:
        """
        Calculation hint logic.
        
        Returns:
            Result of calculation_hint operation.
        """
        return "Enter Numerator (n) and Denominator (d) and harmonic k"

    def _init_properties(self):
        self.properties = {
            "amplitude": ShapeProperty(
                name="Amplitude (a)",
                key="amplitude",
                unit="units",
                formula=r"a",
            ),
            "k_value": ShapeProperty(
                name="Harmonic (k)",
                key="k_value",
                unit="",
                precision=0,
                formula=r"k",
            ),
            "petal_count": ShapeProperty(
                name="Petal Count",
                key="petal_count",
                readonly=True,
                precision=0,
                formula=r"p = \begin{cases}k,&k\text{ odd}\\2k,&k\text{ even}\end{cases}",
            ),
            "max_radius": ShapeProperty(
                name="Max Radius",
                key="max_radius",
                unit="units",
                readonly=True,
                formula=r"r_{max} = a",
            ),
            "total_area": ShapeProperty(
                name="Total Area",
                key="total_area",
                unit="units²",
                readonly=True,
                formula=r"A = \tfrac{1}{2}a^2 p",
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

        if property_key == "amplitude":
            self.properties["amplitude"].value = value
            self._update_metrics()
            return True

        if property_key == "k_value":
            k = max(1, int(round(value)))
            self.properties["k_value"].value = k
            self._update_metrics()
            return True

        return False

    def _update_metrics(self):
        amplitude = self.properties["amplitude"].value
        k_value = self.properties["k_value"].value
        if not amplitude or not k_value:
            self.properties["petal_count"].value = None
            self.properties["max_radius"].value = None
            self.properties["total_area"].value = None
            return

        petals = k_value if k_value % 2 == 1 else 2 * k_value
        self.properties["petal_count"].value = float(petals)
        self.properties["max_radius"].value = amplitude
        self.properties["total_area"].value = 0.5 * amplitude * amplitude * petals

    def get_drawing_instructions(self) -> Dict:
        """
        Retrieve drawing instructions logic.
        
        Returns:
            Result of get_drawing_instructions operation.
        """
        amplitude = self.properties["amplitude"].value
        k_value = self.properties["k_value"].value
        if not amplitude or not k_value:
            return {"type": "empty"}

        points = self._generate_points(amplitude, int(k_value))
        primitives = [
            {
                "shape": "polyline",
                "points": points,
                "pen": {"color": (236, 72, 153, 255), "width": 2.0},
            }
        ]
        return {
            "type": "composite",
            "primitives": primitives,
        }

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

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """
        Retrieve label positions logic.
        
        Returns:
            Result of get_label_positions operation.
        """
        labels: List[Tuple[str, float, float]] = []
        amplitude = self.properties["amplitude"].value
        k_value = self.properties["k_value"].value
        if amplitude:
            labels.append((self._fmt("a", amplitude), amplitude * 0.7, 0.2))
        if k_value and amplitude:
            labels.append((self._fmt("k", k_value), -amplitude * 0.7, 0.2))
        petals = self.properties["petal_count"].value
        if petals is not None and amplitude:
            labels.append((self._fmt("petals", petals), 0, amplitude * 0.3))
        area = self.properties["total_area"].value
        if area is not None and amplitude:
            labels.append((self._fmt("A", area), 0, -amplitude * 0.3))
        return labels

    @staticmethod
    def _fmt(symbol: str, value: float) -> str:
        return f"{symbol} = {value:.4f}".rstrip("0").rstrip(".")