"""Triangle shape calculators."""
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .base_shape import GeometricShape, ShapeProperty


EPSILON = 1e-7


def _circumference_from_radius(radius: Optional[float]) -> Optional[float]:
    if radius is None:
        return None
    return 2 * math.pi * radius


def _clamp(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _valid_triangle_sides(a: float, b: float, c: float) -> bool:
    return all(side > 0 for side in (a, b, c)) and a + b > c - EPSILON and a + c > b - EPSILON and b + c > a - EPSILON


@dataclass
class TriangleSolution:
    """Computed metrics for a triangle defined by its three sides."""

    side_a: float
    side_b: float
    side_c: float
    area: float
    perimeter: float
    angle_a: float
    angle_b: float
    angle_c: float
    height_a: float
    height_b: float
    height_c: float
    inradius: float
    circumradius: float
    points: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]


def _triangle_solution_from_sides(a: float, b: float, c: float) -> TriangleSolution:
    if not _valid_triangle_sides(a, b, c):
        raise ValueError("Invalid triangle side lengths")

    s = (a + b + c) / 2.0
    area_sq = max(s * (s - a) * (s - b) * (s - c), 0.0)
    area = math.sqrt(area_sq)
    perimeter = a + b + c
    angle_a = math.degrees(math.acos(_clamp((b * b + c * c - a * a) / (2 * b * c))))
    angle_b = math.degrees(math.acos(_clamp((a * a + c * c - b * b) / (2 * a * c))))
    angle_c = 180.0 - angle_a - angle_b
    inradius = area / s if s > 0 else 0.0
    circumradius = (a * b * c) / (4 * area) if area > 0 else 0.0
    height_a = (2 * area) / a if a > 0 else 0.0
    height_b = (2 * area) / b if b > 0 else 0.0
    height_c = (2 * area) / c if c > 0 else 0.0

    base = c
    x_c = (b * b + c * c - a * a) / (2 * c)
    y_c_sq = max(b * b - x_c * x_c, 0.0)
    y_c = math.sqrt(y_c_sq)
    points = ((0.0, 0.0), (base, 0.0), (x_c, y_c))

    return TriangleSolution(
        side_a=a,
        side_b=b,
        side_c=c,
        area=area,
        perimeter=perimeter,
        angle_a=angle_a,
        angle_b=angle_b,
        angle_c=angle_c,
        height_a=height_a,
        height_b=height_b,
        height_c=height_c,
        inradius=inradius,
        circumradius=circumradius,
        points=points,
    )


def _centroid(points: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]) -> Tuple[float, float]:
    return (
        (points[0][0] + points[1][0] + points[2][0]) / 3.0,
        (points[0][1] + points[1][1] + points[2][1]) / 3.0,
    )


class _BaseSSSTriangleShape(GeometricShape):
    """Base class for triangle calculators driven by three sides (SSS)."""

    def __init__(self):
        self._solution: Optional[TriangleSolution] = None
        super().__init__()

    def _init_properties(self):
        self.properties = {
            'side_a': ShapeProperty(name='Side a (BC)', key='side_a', unit='units'),
            'side_b': ShapeProperty(name='Side b (AC)', key='side_b', unit='units'),
            'side_c': ShapeProperty(name='Side c (AB)', key='side_c', unit='units'),
            'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True),
            'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True),
            'angle_a_deg': ShapeProperty(name='∠A (°)', key='angle_a_deg', unit='°', readonly=True, precision=2),
            'angle_b_deg': ShapeProperty(name='∠B (°)', key='angle_b_deg', unit='°', readonly=True, precision=2),
            'angle_c_deg': ShapeProperty(name='∠C (°)', key='angle_c_deg', unit='°', readonly=True, precision=2),
            'height_a': ShapeProperty(name='Height to a', key='height_a', unit='units', readonly=True),
            'height_b': ShapeProperty(name='Height to b', key='height_b', unit='units', readonly=True),
            'height_c': ShapeProperty(name='Height to c', key='height_c', unit='units', readonly=True),
            'inradius': ShapeProperty(name='Inradius', key='inradius', unit='units', readonly=True),
            'circumradius': ShapeProperty(name='Circumradius', key='circumradius', unit='units', readonly=True),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if property_key not in {'side_a', 'side_b', 'side_c'}:
            return False
        if value <= 0:
            return False
        previous = self.properties[property_key].value
        self.properties[property_key].value = value
        if not self._try_solve():
            self.properties[property_key].value = previous
            return False
        return True

    def _try_solve(self) -> bool:
        a = self.properties['side_a'].value
        b = self.properties['side_b'].value
        c = self.properties['side_c'].value
        if a is None or b is None or c is None:
            self._clear_solution()
            return True
        if not _valid_triangle_sides(a, b, c):
            return False
        solution = _triangle_solution_from_sides(a, b, c)
        if not self._validate_solution(solution):
            return False
        self._apply_solution(solution)
        return True

    def _validate_solution(self, solution: TriangleSolution) -> bool:
        return True

    def _apply_solution(self, solution: TriangleSolution):
        self._solution = solution
        self.properties['perimeter'].value = solution.perimeter
        self.properties['area'].value = solution.area
        self.properties['angle_a_deg'].value = solution.angle_a
        self.properties['angle_b_deg'].value = solution.angle_b
        self.properties['angle_c_deg'].value = solution.angle_c
        self.properties['height_a'].value = solution.height_a
        self.properties['height_b'].value = solution.height_b
        self.properties['height_c'].value = solution.height_c
        self.properties['inradius'].value = solution.inradius
        self.properties['circumradius'].value = solution.circumradius
        self.properties['incircle_circumference'].value = _circumference_from_radius(solution.inradius)
        self.properties['circumcircle_circumference'].value = _circumference_from_radius(solution.circumradius)

    def _clear_solution(self):
        self._solution = None
        for key in (
            'perimeter', 'area', 'angle_a_deg', 'angle_b_deg', 'angle_c_deg',
            'height_a', 'height_b', 'height_c', 'inradius', 'circumradius',
            'incircle_circumference', 'circumcircle_circumference'
        ):
            self.properties[key].value = None

    def get_drawing_instructions(self) -> Dict:
        if not self._solution:
            return {'type': 'empty'}
        return {
            'type': 'polygon',
            'points': list(self._solution.points),
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        if not self._solution:
            return []
        centroid = _centroid(self._solution.points)
        labels = [
            (f"A = {self._solution.area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.2),
            (f"P = {self._solution.perimeter:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] - 0.2),
        ]
        points = self._solution.points
        angle_labels = [
            (f"α = {self._solution.angle_a:.1f}°", points[0][0], points[0][1] - 0.3),
            (f"β = {self._solution.angle_b:.1f}°", points[1][0], points[1][1] - 0.3),
            (f"γ = {self._solution.angle_c:.1f}°", points[2][0], points[2][1] + 0.3),
        ]
        labels.extend(angle_labels)
        return labels


class EquilateralTriangleShape(GeometricShape):
    """Equilateral triangle with all sides equal."""
    
    @property
    def name(self) -> str:
        return "Equilateral Triangle"
    
    @property
    def description(self) -> str:
        return "A triangle with all three sides equal and all angles 60°"
    
    def _init_properties(self):
        """Initialize equilateral triangle properties."""
        self.properties = {
            'side': ShapeProperty(
                name='Side Length',
                key='side',
                unit='units',
                readonly=False
            ),
            'height': ShapeProperty(
                name='Height',
                key='height',
                unit='units',
                readonly=False
            ),
            'perimeter': ShapeProperty(
                name='Perimeter',
                key='perimeter',
                unit='units',
                readonly=False
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=False
            ),
            'inradius': ShapeProperty(
                name='Inradius',
                key='inradius',
                unit='units',
                readonly=False
            ),
            'circumradius': ShapeProperty(
                name='Circumradius',
                key='circumradius',
                unit='units',
                readonly=False
            ),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
            ),
        }
    
    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Calculate all properties from any given property."""
        if value <= 0:
            return False
        
        # Calculate side from the input property
        if property_key == 'side':
            side = value
        elif property_key == 'height':
            side = (2 * value) / math.sqrt(3)
        elif property_key == 'perimeter':
            side = value / 3
        elif property_key == 'area':
            side = math.sqrt((4 * value) / math.sqrt(3))
        elif property_key == 'inradius':
            side = value * 2 * math.sqrt(3)
        elif property_key == 'circumradius':
            side = value * math.sqrt(3)
        else:
            return False
        
        # Calculate all properties from side
        self.properties['side'].value = side
        self.properties['height'].value = (side * math.sqrt(3)) / 2
        self.properties['perimeter'].value = 3 * side
        self.properties['area'].value = (math.sqrt(3) / 4) * side * side
        inradius = side / (2 * math.sqrt(3))
        circumradius = side / math.sqrt(3)
        self.properties['inradius'].value = inradius
        self.properties['circumradius'].value = circumradius
        self.properties['incircle_circumference'].value = _circumference_from_radius(inradius)
        self.properties['circumcircle_circumference'].value = _circumference_from_radius(circumradius)
        
        return True
    
    def get_drawing_instructions(self) -> Dict:
        """Get drawing instructions for the equilateral triangle."""
        side = self.get_property('side')
        
        if side is None:
            return {'type': 'empty'}
        
        height = (side * math.sqrt(3)) / 2
        
        # Points for equilateral triangle (centered)
        return {
            'type': 'polygon',
            'points': [
                (0, height * 2/3),  # Top vertex
                (-side/2, -height * 1/3),  # Bottom left
                (side/2, -height * 1/3),  # Bottom right
            ],
            'show_height': True,
            'show_incircle': True,
            'show_circumcircle': True,
        }
    
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """Get label positions for the triangle."""
        side = self.get_property('side')
        
        if side is None:
            return []
        
        height = (side * math.sqrt(3)) / 2
        labels = []
        
        # Side label
        labels.append((f's = {side:.4f}'.rstrip('0').rstrip('.'), 0, -height * 1/3 - 0.3))
        
        # Height label
        h = self.get_property('height')
        labels.append((f'h = {h:.4f}'.rstrip('0').rstrip('.'), -0.3, 0))
        
        # Area label
        area = self.get_property('area')
        labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), 0, 0.2))
        
        return labels


class RightTriangleShape(GeometricShape):
    """Right triangle with one 90° angle."""
    
    @property
    def name(self) -> str:
        return "Right Triangle"
    
    @property
    def description(self) -> str:
        return "A triangle with one 90° angle"

    @property
    def calculation_hint(self) -> str:
        return "Enter 2 sides, or 1 side + area"
    
    def _init_properties(self):
        """Initialize right triangle properties."""
        self.properties = {
            'base': ShapeProperty(
                name='Base (a)',
                key='base',
                unit='units',
                readonly=False
            ),
            'height': ShapeProperty(
                name='Height (b)',
                key='height',
                unit='units',
                readonly=False
            ),
            'hypotenuse': ShapeProperty(
                name='Hypotenuse (c)',
                key='hypotenuse',
                unit='units',
                readonly=False
            ),
            'perimeter': ShapeProperty(
                name='Perimeter',
                key='perimeter',
                unit='units',
                readonly=False
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=False
            ),
            'inradius': ShapeProperty(
                name='Inradius',
                key='inradius',
                unit='units',
                readonly=True,
            ),
            'circumradius': ShapeProperty(
                name='Circumradius',
                key='circumradius',
                unit='units',
                readonly=True,
            ),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
            ),
        }
    

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Calculate dependent properties."""
        if value <= 0:
            return False
        
        # Set the incoming value
        if property_key in self.properties:
            self.properties[property_key].value = value
        else:
            return False
        
        # Retrieve all values
        base = self.properties['base'].value
        height = self.properties['height'].value
        hyp = self.properties['hypotenuse'].value
        area = self.properties['area'].value
        perimeter = self.properties['perimeter'].value

        # Solver loop (run twice to propagate derived values)
        for _ in range(2):
            # 1. Base + Height known?
            if base and height:
                hyp = math.sqrt(base**2 + height**2)
                area = (base * height) / 2
                perimeter = base + height + hyp

            # 2. Base + Area -> Height
            if base and area and not height:
                height = (2 * area) / base
            # 3. Height + Area -> Base
            if height and area and not base:
                base = (2 * area) / height
            
            # 4. Base + Hypotenuse -> Height
            if base and hyp and not height:
                if hyp > base:
                    height = math.sqrt(hyp**2 - base**2)
            # 5. Height + Hypotenuse -> Base
            if height and hyp and not base:
                if hyp > height:
                    base = math.sqrt(hyp**2 - height**2)

            # 6. Area + Hypotenuse -> Base/Height (a+b known from c and A)
            if area and hyp and (not base or not height):
                # (a+b)^2 = c^2 + 4A
                sum_ab_sq = hyp**2 + 4 * area
                diff_ab_sq = hyp**2 - 4 * area
                if diff_ab_sq >= 0:
                    sum_ab = math.sqrt(sum_ab_sq)
                    diff_ab = math.sqrt(diff_ab_sq)
                    # a = (sum + diff)/2, b = (sum - diff)/2
                    base = (sum_ab + diff_ab) / 2
                    height = (sum_ab - diff_ab) / 2

            # 7. Perimeter + Base -> Height (P = a + b + c -> c = P - a - b -> c^2 = (P-a-b)^2 -> a^2+b^2 = ...)
            # b = ((P-a)^2 - a^2) / (2*(P-a))
            if perimeter and base and not height:
                K = perimeter - base
                if K > 0 and K**2 > base**2:
                     height = (K**2 - base**2) / (2 * K)
            
            # 8. Perimeter + Height -> Base
            if perimeter and height and not base:
                K = perimeter - height
                if K > 0 and K**2 > height**2:
                     base = (K**2 - height**2) / (2 * K)
        
        # Update state if solved
        if base and height:
            self.properties['base'].value = base
            self.properties['height'].value = height
        
        if base is not None and height is not None:
            hypotenuse = math.sqrt(base**2 + height**2)
            self.properties['hypotenuse'].value = hypotenuse
            self.properties['perimeter'].value = base + height + hypotenuse
            self.properties['area'].value = (base * height) / 2
            solution = _triangle_solution_from_sides(base, height, hypotenuse)
            self.properties['inradius'].value = solution.inradius
            self.properties['circumradius'].value = solution.circumradius
            self.properties['incircle_circumference'].value = _circumference_from_radius(solution.inradius)
            self.properties['circumcircle_circumference'].value = _circumference_from_radius(solution.circumradius)
        
        return True
    
    def get_drawing_instructions(self) -> Dict:
        """Get drawing instructions for the right triangle."""
        base = self.get_property('base')
        height = self.get_property('height')
        
        if base is None or height is None:
            return {'type': 'empty'}
        
        return {
            'type': 'polygon',
            'points': [
                (0, 0),  # Right angle corner
                (base, 0),  # Base corner
                (0, height),  # Height corner
            ],
            'show_right_angle': True,
        }
    
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """Get label positions for the triangle."""
        base = self.get_property('base')
        height = self.get_property('height')
        
        if base is None or height is None:
            return []
        
        labels = []
        
        # Base label
        labels.append((f'a = {base:.4f}'.rstrip('0').rstrip('.'), base/2, -0.3))
        
        # Height label
        labels.append((f'b = {height:.4f}'.rstrip('0').rstrip('.'), -0.3, height/2))
        
        # Hypotenuse label
        hyp = self.get_property('hypotenuse')
        if hyp:
            labels.append((f'c = {hyp:.4f}'.rstrip('0').rstrip('.'), base/2 + 0.2, height/2 + 0.2))
        
        # Area label
        area = self.get_property('area')
        if area:
            labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), base/3, height/3))
        
        return labels


class IsoscelesTriangleShape(GeometricShape):
    """Isosceles triangle defined by base and equal legs."""

    def __init__(self):
        self._solution: Optional[TriangleSolution] = None
        super().__init__()

    @property
    def name(self) -> str:
        return "Isosceles Triangle"

    @property
    def description(self) -> str:
        return "Two equal legs with base/apex metrics and sacred height"

    @property
    def calculation_hint(self) -> str:
        return "Enter Base + Leg, or Base/Leg + Height"

    def _init_properties(self):
        self.properties = {
            'base': ShapeProperty(name='Base (b)', key='base', unit='units'),
            'leg': ShapeProperty(name='Equal Leg (ℓ)', key='leg', unit='units'),
            'height': ShapeProperty(name='Height', key='height', unit='units'),
            'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True),
            'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True),
            'apex_angle_deg': ShapeProperty(name='Apex Angle (°)', key='apex_angle_deg', unit='°', readonly=True, precision=2),
            'base_angle_deg': ShapeProperty(name='Base Angle (°)', key='base_angle_deg', unit='°', readonly=True, precision=2),
            'inradius': ShapeProperty(name='Inradius', key='inradius', unit='units', readonly=True),
            'circumradius': ShapeProperty(name='Circumradius', key='circumradius', unit='units', readonly=True),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if property_key not in {'base', 'leg', 'height'}:
            return False
        if value <= 0:
            return False
        previous = self.properties[property_key].value
        self.properties[property_key].value = value
        if not self._resolve_geometry():
            self.properties[property_key].value = previous
            return False
        return True

    def _resolve_geometry(self) -> bool:
        base = self.properties['base'].value
        leg = self.properties['leg'].value
        height = self.properties['height'].value

        solved = False
        if base and leg:
            if base >= 2 * leg:
                self._clear_solution()
                return False
            half_base = base / 2
            leg_sq = leg * leg
            new_height_sq = leg_sq - half_base * half_base
            if new_height_sq <= 0:
                self._clear_solution()
                return False
            self.properties['height'].value = math.sqrt(new_height_sq)
            solved = True
        elif base and height:
            half_base = base / 2
            leg_val = math.sqrt(half_base * half_base + height * height)
            self.properties['leg'].value = leg_val
            solved = True
        elif leg and height:
            under = leg * leg - height * height
            if under <= 0:
                self._clear_solution()
                return False
            base_val = 2 * math.sqrt(under)
            self.properties['base'].value = base_val
            solved = True
        else:
            self._clear_solution(clear_dimensions=False)
            return True

        if solved:
            base = self.properties['base'].value
            leg = self.properties['leg'].value
            if base is None or leg is None:
                self._clear_solution(clear_dimensions=False)
                return True
            solution = _triangle_solution_from_sides(leg, leg, base)
            self._apply_solution(solution)
        return True

    def _apply_solution(self, solution: TriangleSolution):
        self._solution = solution
        self.properties['perimeter'].value = solution.perimeter
        self.properties['area'].value = solution.area
        self.properties['apex_angle_deg'].value = solution.angle_c
        self.properties['base_angle_deg'].value = solution.angle_a
        self.properties['inradius'].value = solution.inradius
        self.properties['circumradius'].value = solution.circumradius
        self.properties['incircle_circumference'].value = _circumference_from_radius(solution.inradius)
        self.properties['circumcircle_circumference'].value = _circumference_from_radius(solution.circumradius)

    def _clear_solution(self, clear_dimensions: bool = False):
        self._solution = None
        for key in (
            'perimeter', 'area', 'apex_angle_deg', 'base_angle_deg', 'inradius',
            'circumradius', 'incircle_circumference', 'circumcircle_circumference'
        ):
            self.properties[key].value = None
        if clear_dimensions:
            for key in ('base', 'leg', 'height'):
                self.properties[key].value = None

    def get_drawing_instructions(self) -> Dict:
        if not self._solution:
            return {'type': 'empty'}
        return {
            'type': 'polygon',
            'points': list(self._solution.points),
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        if not self._solution:
            return []
        centroid = _centroid(self._solution.points)
        labels = [
            (f"A = {self._solution.area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.2),
            (f"P = {self._solution.perimeter:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] - 0.2),
        ]
        base = self.properties['base'].value or 0.0
        labels.append((f"b = {base:.4f}".rstrip('0').rstrip('.'), base / 2, -0.4))
        return labels


class ScaleneTriangleShape(_BaseSSSTriangleShape):
    """General triangle with three unequal sides."""

    @property
    def name(self) -> str:
        return "Scalene Triangle"

    @property
    def description(self) -> str:
        return "Three unequal sides with full SSS breakdown"

    @property
    def calculation_hint(self) -> str:
        return "Enter 3 sides (SSS)"

    def _validate_solution(self, solution: TriangleSolution) -> bool:
        sides = (solution.side_a, solution.side_b, solution.side_c)
        return min(abs(sides[i] - sides[j]) for i in range(3) for j in range(i + 1, 3)) > 1e-4


class AcuteTriangleShape(_BaseSSSTriangleShape):
    """Triangle where all angles are acute."""

    @property
    def name(self) -> str:
        return "Acute Triangle"

    @property
    def description(self) -> str:
        return "All interior angles are less than 90°"

    def _validate_solution(self, solution: TriangleSolution) -> bool:
        return all(angle < 90.0 - 1e-3 for angle in (solution.angle_a, solution.angle_b, solution.angle_c))


class ObtuseTriangleShape(_BaseSSSTriangleShape):
    """Triangle with one obtuse angle."""

    @property
    def name(self) -> str:
        return "Obtuse Triangle"

    @property
    def description(self) -> str:
        return "One angle greater than 90° with exterior altitude context"

    def _validate_solution(self, solution: TriangleSolution) -> bool:
        return max(solution.angle_a, solution.angle_b, solution.angle_c) > 90.0 + 1e-3


class HeronianTriangleShape(_BaseSSSTriangleShape):
    """Triangle with integer sides and integer area."""

    def _init_properties(self):
        super()._init_properties()
        self.properties['heronian_flag'] = ShapeProperty(
            name='Heronian (1=True)',
            key='heronian_flag',
            readonly=True,
            precision=0,
        )

    @property
    def name(self) -> str:
        return "Heronian Triangle"

    @property
    def description(self) -> str:
        return "Integer-sided triangle with integer area via Heron"

    def _apply_solution(self, solution: TriangleSolution):
        super()._apply_solution(solution)
        is_int_area = math.isclose(solution.area, round(solution.area), abs_tol=1e-6)
        is_int_sides = all(math.isclose(side, round(side), abs_tol=1e-6) for side in (solution.side_a, solution.side_b, solution.side_c))
        self.properties['heronian_flag'].value = 1.0 if (is_int_area and is_int_sides) else 0.0


class IsoscelesRightTriangleShape(GeometricShape):
    """45°-45°-90° triangle with equal legs."""

    @property
    def name(self) -> str:
        return "Isosceles Right Triangle (45-45-90)"

    @property
    def description(self) -> str:
        return "Special right triangle with √2 proportions"

    @property
    def calculation_hint(self) -> str:
        return "Calculate from any field (1-DoF)"

    def _init_properties(self):
        self.properties = {
            'leg': ShapeProperty(name='Leg (ℓ)', key='leg', unit='units'),
            'hypotenuse': ShapeProperty(name='Hypotenuse', key='hypotenuse', unit='units'),
            'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True),
            'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True),
            'height': ShapeProperty(name='Altitude', key='height', unit='units', readonly=True),
            'inradius': ShapeProperty(name='Inradius', key='inradius', unit='units', readonly=True),
            'circumradius': ShapeProperty(name='Circumradius', key='circumradius', unit='units', readonly=True),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if property_key not in {'leg', 'hypotenuse'}:
            return False
        if value <= 0:
            return False
        if property_key == 'leg':
            leg = value
        else:
            leg = value / math.sqrt(2)
        self._populate_from_leg(leg)
        return True

    def _populate_from_leg(self, leg: float):
        hyp = leg * math.sqrt(2)
        self.properties['leg'].value = leg
        self.properties['hypotenuse'].value = hyp
        self.properties['height'].value = leg
        self.properties['perimeter'].value = 2 * leg + hyp
        self.properties['area'].value = (leg * leg) / 2
        solution = _triangle_solution_from_sides(leg, leg, hyp)
        self.properties['inradius'].value = solution.inradius
        self.properties['circumradius'].value = solution.circumradius
        self.properties['incircle_circumference'].value = _circumference_from_radius(solution.inradius)
        self.properties['circumcircle_circumference'].value = _circumference_from_radius(solution.circumradius)

    def get_drawing_instructions(self) -> Dict:
        leg = self.properties['leg'].value
        if leg is None:
            return {'type': 'empty'}
        return {
            'type': 'polygon',
            'points': [(0, 0), (leg, 0), (0, leg)],
            'show_right_angle': True,
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        leg = self.properties['leg'].value
        hyp = self.properties['hypotenuse'].value
        if leg is None or hyp is None:
            return []
        area = self.properties['area'].value or 0.0
        return [
            (f"ℓ = {leg:.4f}".rstrip('0').rstrip('.'), leg / 2, -0.3),
            (f"c = {hyp:.4f}".rstrip('0').rstrip('.'), leg * 0.4, leg * 0.6),
            (f"A = {area:.4f}".rstrip('0').rstrip('.'), leg * 0.3, leg * 0.2),
        ]


class ThirtySixtyNinetyTriangleShape(GeometricShape):
    """30°-60°-90° triangle with √3 ratios."""

    @property
    def name(self) -> str:
        return "30-60-90 Triangle"

    @property
    def description(self) -> str:
        return "Special right triangle with short:long:hyp = 1:√3:2"

    @property
    def calculation_hint(self) -> str:
        return "Calculate from any field (1-DoF)"

    def _init_properties(self):
        self.properties = {
            'short_leg': ShapeProperty(name='Short Leg (opposite 30°)', key='short_leg', unit='units'),
            'long_leg': ShapeProperty(name='Long Leg (opposite 60°)', key='long_leg', unit='units'),
            'hypotenuse': ShapeProperty(name='Hypotenuse', key='hypotenuse', unit='units'),
            'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True),
            'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True),
            'inradius': ShapeProperty(name='Inradius', key='inradius', unit='units', readonly=True),
            'circumradius': ShapeProperty(name='Circumradius', key='circumradius', unit='units', readonly=True),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if property_key not in {'short_leg', 'long_leg', 'hypotenuse'}:
            return False
        if value <= 0:
            return False
        if property_key == 'short_leg':
            short = value
        elif property_key == 'long_leg':
            short = value / math.sqrt(3)
        else:
            short = value / 2
        self._populate_from_short(short)
        return True

    def _populate_from_short(self, short: float):
        long = short * math.sqrt(3)
        hyp = short * 2
        self.properties['short_leg'].value = short
        self.properties['long_leg'].value = long
        self.properties['hypotenuse'].value = hyp
        self.properties['perimeter'].value = short + long + hyp
        self.properties['area'].value = (short * long) / 2
        solution = _triangle_solution_from_sides(short, long, hyp)
        self.properties['inradius'].value = solution.inradius
        self.properties['circumradius'].value = solution.circumradius
        self.properties['incircle_circumference'].value = _circumference_from_radius(solution.inradius)
        self.properties['circumcircle_circumference'].value = _circumference_from_radius(solution.circumradius)

    def get_drawing_instructions(self) -> Dict:
        short = self.properties['short_leg'].value
        long = self.properties['long_leg'].value
        if short is None or long is None:
            return {'type': 'empty'}
        return {
            'type': 'polygon',
            'points': [(0, 0), (short, 0), (0, long)],
            'show_right_angle': True,
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        short = self.properties['short_leg'].value
        long = self.properties['long_leg'].value
        area = self.properties['area'].value
        if short is None or long is None or area is None:
            return []
        return [
            (f"s = {short:.4f}".rstrip('0').rstrip('.'), short / 2, -0.3),
            (f"ℓ = {long:.4f}".rstrip('0').rstrip('.'), -0.4, long / 2),
            (f"A = {area:.4f}".rstrip('0').rstrip('.'), short * 0.3, long * 0.3),
        ]


class GoldenTriangleShape(GeometricShape):
    """Isosceles triangle aligned to the golden ratio."""

    PHI = (1 + math.sqrt(5)) / 2

    def __init__(self):
        self._solution: Optional[TriangleSolution] = None
        super().__init__()

    @property
    def name(self) -> str:
        return "Golden Triangle"

    @property
    def description(self) -> str:
        return "Isosceles triangle with golden ratio sides (72-72-36)"

    @property
    def calculation_hint(self) -> str:
        return "Calculate from any field (1-DoF)"

    def _init_properties(self):
        self.properties = {
            'equal_leg': ShapeProperty(name='Equal Leg', key='equal_leg', unit='units'),
            'base': ShapeProperty(name='Base', key='base', unit='units'),
            'height': ShapeProperty(name='Height', key='height', unit='units', readonly=True),
            'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True),
            'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True),
            'apex_angle_deg': ShapeProperty(name='Apex Angle (°)', key='apex_angle_deg', unit='°', readonly=True, precision=2),
            'inradius': ShapeProperty(name='Inradius', key='inradius', unit='units', readonly=True),
            'circumradius': ShapeProperty(name='Circumradius', key='circumradius', unit='units', readonly=True),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if property_key not in {'equal_leg', 'base'}:
            return False
        if value <= 0:
            return False
        if property_key == 'equal_leg':
            equal_leg = value
            base = equal_leg / self.PHI
        else:
            base = value
            equal_leg = base * self.PHI
        self._populate(equal_leg, base)
        return True

    def _populate(self, leg: float, base: float):
        self.properties['equal_leg'].value = leg
        self.properties['base'].value = base
        solution = _triangle_solution_from_sides(leg, leg, base)
        self._solution = solution
        self.properties['height'].value = solution.height_c
        self.properties['perimeter'].value = solution.perimeter
        self.properties['area'].value = solution.area
        self.properties['apex_angle_deg'].value = solution.angle_c
        self.properties['inradius'].value = solution.inradius
        self.properties['circumradius'].value = solution.circumradius
        self.properties['incircle_circumference'].value = _circumference_from_radius(solution.inradius)
        self.properties['circumcircle_circumference'].value = _circumference_from_radius(solution.circumradius)

    def get_drawing_instructions(self) -> Dict:
        if not self._solution:
            return {'type': 'empty'}
        return {'type': 'polygon', 'points': list(self._solution.points)}

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        if not self._solution:
            return []
        centroid = _centroid(self._solution.points)
        return [
            (f"φ = {self.PHI:.4f}", centroid[0], centroid[1] + 0.2),
            (f"A = {self._solution.area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] - 0.2),
        ]


class TriangleSolverShape(GeometricShape):
    """General-purpose triangle solver supporting common input combinations."""

    def __init__(self):
        self._solution: Optional[TriangleSolution] = None
        super().__init__()

    @property
    def name(self) -> str:
        return "Triangle Solver"

    @property
    def description(self) -> str:
        return "Accepts sides/angles using SSS, SAS, ASA/AAS, or SSA relationships"

    def _init_properties(self):
        self.properties = {
            'side_a': ShapeProperty(name='Side a (BC)', key='side_a', unit='units'),
            'side_b': ShapeProperty(name='Side b (AC)', key='side_b', unit='units'),
            'side_c': ShapeProperty(name='Side c (AB)', key='side_c', unit='units'),
            'angle_a_deg': ShapeProperty(name='Angle A (°)', key='angle_a_deg', unit='°', precision=2),
            'angle_b_deg': ShapeProperty(name='Angle B (°)', key='angle_b_deg', unit='°', precision=2),
            'angle_c_deg': ShapeProperty(name='Angle C (°)', key='angle_c_deg', unit='°', precision=2),
            'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True),
            'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True),
            'inradius': ShapeProperty(name='Inradius', key='inradius', unit='units', readonly=True),
            'circumradius': ShapeProperty(name='Circumradius', key='circumradius', unit='units', readonly=True),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        if property_key not in {'side_a', 'side_b', 'side_c', 'angle_a_deg', 'angle_b_deg', 'angle_c_deg'}:
            return False
        if property_key.startswith('side'):
            if value <= 0:
                return False
        else:
            if not (0 < value < 180):
                return False
        previous = self.properties[property_key].value
        self.properties[property_key].value = value
        if not self._attempt_solution():
            self.properties[property_key].value = previous
            return False
        return True

    def _attempt_solution(self) -> bool:
        a = self.properties['side_a'].value
        b = self.properties['side_b'].value
        c = self.properties['side_c'].value
        A = self.properties['angle_a_deg'].value
        B = self.properties['angle_b_deg'].value
        C = self.properties['angle_c_deg'].value

        try:
            solution = self._solve_general(a, b, c, A, B, C)
        except ValueError:
            self._clear_solution()
            return False

        if solution is None:
            self._clear_solution()
            return True
        self._solution = solution
        self.properties['perimeter'].value = solution.perimeter
        self.properties['area'].value = solution.area
        self.properties['inradius'].value = solution.inradius
        self.properties['circumradius'].value = solution.circumradius
        self.properties['incircle_circumference'].value = _circumference_from_radius(solution.inradius)
        self.properties['circumcircle_circumference'].value = _circumference_from_radius(solution.circumradius)
        self.properties['angle_a_deg'].value = solution.angle_a
        self.properties['angle_b_deg'].value = solution.angle_b
        self.properties['angle_c_deg'].value = solution.angle_c
        self.properties['side_a'].value = solution.side_a
        self.properties['side_b'].value = solution.side_b
        self.properties['side_c'].value = solution.side_c
        return True

    def _clear_solution(self):
        self._solution = None
        for key in (
            'perimeter', 'area', 'inradius', 'circumradius',
            'incircle_circumference', 'circumcircle_circumference'
        ):
            self.properties[key].value = None

    @staticmethod
    def _solve_general(a, b, c, A, B, C) -> Optional[TriangleSolution]:
        if a and b and c:
            return _triangle_solution_from_sides(a, b, c)

        # SAS cases
        sas_cases = [
            (a, b, C, 'c'),
            (a, c, B, 'b'),
            (b, c, A, 'a'),
        ]
        for s1, s2, angle, missing_key in sas_cases:
            if s1 and s2 and angle:
                rad = math.radians(angle)
                if angle <= 0 or angle >= 180:
                    continue
                missing = math.sqrt(max(s1 * s1 + s2 * s2 - 2 * s1 * s2 * math.cos(rad), 0.0))
                sides = {'a': a, 'b': b, 'c': c}
                sides[missing_key] = missing
                return _triangle_solution_from_sides(sides['a'], sides['b'], sides['c'])

        # ASA / AAS cases
        angles = {'A': A, 'B': B, 'C': C}
        known_angles = [ang for ang in angles.values() if ang is not None]
        if len(known_angles) >= 2:
            total_known = sum(known_angles)
            missing_angle_key = None
            for key, value in angles.items():
                if value is None:
                    missing_angle_key = key
                    break
            missing_value = 180 - total_known if missing_angle_key else 180 - total_known
            if missing_angle_key and missing_value > 0:
                angles[missing_angle_key] = missing_value
            if all(value and value > 0 for value in angles.values()) and abs(sum(angles.values()) - 180) < 1e-4:
                sides = {'a': a, 'b': b, 'c': c}
                for key, side in sides.items():
                    if side:
                        reference_angle = angles[key.upper()]
                        scale = side / math.sin(math.radians(reference_angle))
                        for target_key in sides.keys():
                            sides[target_key] = scale * math.sin(math.radians(angles[target_key.upper()]))
                        return _triangle_solution_from_sides(sides['a'], sides['b'], sides['c'])

        # SSA cases (ambiguous)
        ssa_cases = [
            ('a', a, b, B, 'b', 'B'),
            ('a', a, c, C, 'c', 'C'),
            ('b', b, a, A, 'a', 'A'),
            ('b', b, c, C, 'c', 'C'),
            ('c', c, a, A, 'a', 'A'),
            ('c', c, b, B, 'b', 'B'),
        ]
        for base_key, base_side, other_side, other_angle, other_key, other_angle_key in ssa_cases:
            base_angle = {'a': A, 'b': B, 'c': C}[base_key]
            if not (base_side and other_side and base_angle and base_angle > 0):
                continue
            sin_value = math.sin(math.radians(base_angle)) * other_side / base_side
            if sin_value < -1 or sin_value > 1:
                continue
            angle_candidate = math.degrees(math.asin(_clamp(sin_value)))
            alt_candidate = 180 - angle_candidate
            for candidate in (angle_candidate, alt_candidate):
                third_angle = 180 - base_angle - candidate
                if candidate <= 0 or third_angle <= 0:
                    continue
                angles_full = {'A': A, 'B': B, 'C': C}
                angles_full[base_key.upper()] = base_angle
                angles_full[other_angle_key] = candidate
                missing_key = next(k for k in ('A', 'B', 'C') if angles_full.get(k) is None)
                angles_full[missing_key] = third_angle
                sides = {'a': a, 'b': b, 'c': c}
                ref_side = base_side
                ref_angle = angles_full[base_key.upper()]
                scale = ref_side / math.sin(math.radians(ref_angle))
                for label in ('A', 'B', 'C'):
                    sides[label.lower()] = scale * math.sin(math.radians(angles_full[label]))
                return _triangle_solution_from_sides(sides['a'], sides['b'], sides['c'])

        return None

    def get_drawing_instructions(self) -> Dict:
        if not self._solution:
            return {'type': 'empty'}
        return {'type': 'polygon', 'points': list(self._solution.points)}

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        if not self._solution:
            return []
        centroid = _centroid(self._solution.points)
        return [
            (f"A = {self._solution.area:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] + 0.2),
            (f"P = {self._solution.perimeter:.4f}".rstrip('0').rstrip('.'), centroid[0], centroid[1] - 0.2),
        ]
