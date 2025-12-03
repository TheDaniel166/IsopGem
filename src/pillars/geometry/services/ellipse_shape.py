"""Ellipse (oval) shape calculator."""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class EllipseShape(GeometricShape):
    """Ellipse defined by its semi-major and semi-minor axes."""

    @property
    def name(self) -> str:
        return "Oval (Ellipse)"

    @property
    def description(self) -> str:
        return "Smooth conic with semi-major/minor axes, eccentricity, and foci"

    def _init_properties(self):
        self.properties = {
            'semi_major_axis': ShapeProperty(
                name='Semi-major Axis (a)',
                key='semi_major_axis',
                unit='units',
                readonly=False,
            ),
            'semi_minor_axis': ShapeProperty(
                name='Semi-minor Axis (b)',
                key='semi_minor_axis',
                unit='units',
                readonly=False,
            ),
            'major_axis': ShapeProperty(
                name='Major Axis (2a)',
                key='major_axis',
                unit='units',
                readonly=False,
            ),
            'minor_axis': ShapeProperty(
                name='Minor Axis (2b)',
                key='minor_axis',
                unit='units',
                readonly=False,
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=True,
            ),
            'perimeter': ShapeProperty(
                name='Perimeter (Ramanujan)',
                key='perimeter',
                unit='units',
                readonly=True,
            ),
            'eccentricity': ShapeProperty(
                name='Eccentricity (e)',
                key='eccentricity',
                readonly=True,
                precision=4,
            ),
            'focal_distance': ShapeProperty(
                name='Focal Distance (c)',
                key='focal_distance',
                unit='units',
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if value <= 0:
            return False

        if property_key == 'semi_major_axis':
            self.properties['semi_major_axis'].value = value
            self._reconcile_axes()
            return True
        if property_key == 'semi_minor_axis':
            self.properties['semi_minor_axis'].value = value
            self._reconcile_axes()
            return True
        if property_key == 'major_axis':
            self.properties['semi_major_axis'].value = value / 2
            self._reconcile_axes()
            return True
        if property_key == 'minor_axis':
            self.properties['semi_minor_axis'].value = value / 2
            self._reconcile_axes()
            return True

        return False

    def get_drawing_instructions(self) -> Dict:
        a = self.properties['semi_major_axis'].value
        b = self.properties['semi_minor_axis'].value
        if not a or not b:
            return {'type': 'empty'}

        points = self._ellipse_points(a, b)
        axis_lines = [
            ((-a, 0), (a, 0)),
            ((0, -b), (0, b)),
        ]

        return {
            'type': 'polygon',
            'points': points,
            'axis_lines': axis_lines,
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        a = self.properties['semi_major_axis'].value
        b = self.properties['semi_minor_axis'].value
        if not a or not b:
            return []

        labels: List[Tuple[str, float, float]] = []
        labels.append((f"a = {a:.4f}".rstrip('0').rstrip('.'), a * 0.5, 0.25))
        labels.append((f"b = {b:.4f}".rstrip('0').rstrip('.'), 0.25, b * 0.5))

        ecc = self.properties['eccentricity'].value
        if ecc is not None:
            labels.append((f"e = {ecc:.4f}".rstrip('0').rstrip('.'), 0, -b * 0.4))

        area = self.properties['area'].value
        if area is not None:
            labels.append((f"A = {area:.4f}".rstrip('0').rstrip('.'), 0, 0))

        return labels

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _reconcile_axes(self):
        a = self.properties['semi_major_axis'].value
        b = self.properties['semi_minor_axis'].value
        if a is None and b is None:
            self._clear_dependents(reset_axes=False)
            return

        if a is None:
            a = b
        if b is None:
            b = a
        if a is None or b is None:
            self._clear_dependents(reset_axes=False)
            if a is not None:
                self.properties['semi_major_axis'].value = a
                self.properties['major_axis'].value = 2 * a
            if b is not None:
                self.properties['semi_minor_axis'].value = b
                self.properties['minor_axis'].value = 2 * b
            return

        if a < b:
            a, b = b, a
        if b <= 0:
            return

        self.properties['semi_major_axis'].value = a
        self.properties['semi_minor_axis'].value = b
        self.properties['major_axis'].value = 2 * a
        self.properties['minor_axis'].value = 2 * b

        area = math.pi * a * b
        self.properties['area'].value = area

        try:
            ecc = math.sqrt(1 - (b * b) / (a * a)) if a > 0 else 0
        except ValueError:
            ecc = 0
        self.properties['eccentricity'].value = ecc
        self.properties['focal_distance'].value = math.sqrt(max(a * a - b * b, 0.0))

        if (a + b) > 0:
            h = ((a - b) ** 2) / ((a + b) ** 2)
            perimeter = math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))
            self.properties['perimeter'].value = perimeter
        else:
            self.properties['perimeter'].value = None

    def _clear_dependents(self, reset_axes: bool = True):
        axis_keys = ('major_axis', 'minor_axis') if reset_axes else ()
        for key in (*axis_keys, 'area', 'perimeter', 'eccentricity', 'focal_distance'):
            self.properties[key].value = None

    @staticmethod
    def _ellipse_points(a: float, b: float, steps: int = 180) -> List[Tuple[float, float]]:
        points: List[Tuple[float, float]] = []
        for i in range(steps):
            theta = 2 * math.pi * (i / steps)
            x = a * math.cos(theta)
            y = b * math.sin(theta)
            points.append((x, y))
        return points