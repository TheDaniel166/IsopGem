"""Triangle shape calculators."""
import math
from typing import Dict, List, Tuple
from .base_shape import GeometricShape, ShapeProperty


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
        self.properties['inradius'].value = side / (2 * math.sqrt(3))
        self.properties['circumradius'].value = side / math.sqrt(3)
        
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
        labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), 0, 0))
        
        return labels


class RightTriangleShape(GeometricShape):
    """Right triangle with one 90° angle."""
    
    @property
    def name(self) -> str:
        return "Right Triangle"
    
    @property
    def description(self) -> str:
        return "A triangle with one 90° angle"
    
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
                readonly=True
            ),
            'perimeter': ShapeProperty(
                name='Perimeter',
                key='perimeter',
                unit='units',
                readonly=True
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=True
            ),
        }
    
    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Calculate dependent properties."""
        if value <= 0:
            return False
        
        # Need both base and height to calculate other properties
        if property_key == 'base':
            self.properties['base'].value = value
        elif property_key == 'height':
            self.properties['height'].value = value
        else:
            return False
        
        base = self.properties['base'].value
        height = self.properties['height'].value
        
        if base is not None and height is not None:
            hypotenuse = math.sqrt(base**2 + height**2)
            self.properties['hypotenuse'].value = hypotenuse
            self.properties['perimeter'].value = base + height + hypotenuse
            self.properties['area'].value = (base * height) / 2
        
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
