"""Circle shape calculator."""
import math
from typing import Dict, List, Tuple
from .base_shape import GeometricShape, ShapeProperty


class CircleShape(GeometricShape):
    """Circle shape with bidirectional property calculations."""
    
    @property
    def name(self) -> str:
        return "Circle"
    
    @property
    def description(self) -> str:
        return "A perfectly round 2D shape with all points equidistant from center"
    
    def _init_properties(self):
        """Initialize circle properties."""
        self.properties = {
            'radius': ShapeProperty(
                name='Radius',
                key='radius',
                unit='units',
                readonly=False
            ),
            'diameter': ShapeProperty(
                name='Diameter',
                key='diameter',
                unit='units',
                readonly=False
            ),
            'circumference': ShapeProperty(
                name='Circumference',
                key='circumference',
                unit='units',
                readonly=False
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=False
            ),
        }
    
    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Calculate all properties from any given property."""
        if value <= 0:
            return False
        
        # Calculate radius from the input property
        if property_key == 'radius':
            radius = value
        elif property_key == 'diameter':
            radius = value / 2
        elif property_key == 'circumference':
            radius = value / (2 * math.pi)
        elif property_key == 'area':
            radius = math.sqrt(value / math.pi)
        else:
            return False
        
        # Now calculate all other properties from radius
        self.properties['radius'].value = radius
        self.properties['diameter'].value = radius * 2
        self.properties['circumference'].value = 2 * math.pi * radius
        self.properties['area'].value = math.pi * radius * radius
        
        return True
    
    def get_drawing_instructions(self) -> Dict:
        """Get drawing instructions for the circle."""
        radius = self.get_property('radius')
        
        if radius is None:
            return {'type': 'empty'}
        
        # Center the circle in a normalized coordinate system
        # The viewport will scale this appropriately
        return {
            'type': 'circle',
            'center_x': 0,
            'center_y': 0,
            'radius': radius,
            'show_radius_line': True,
            'show_diameter_line': True,
        }
    
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """Get label positions for the circle."""
        radius = self.get_property('radius')
        
        if radius is None:
            return []
        
        labels = []
        
        # Radius label (on the radius line)
        labels.append((f'r = {radius:.4f}'.rstrip('0').rstrip('.'), radius / 2, 0.1))
        
        # Diameter label (at the top)
        diameter = self.get_property('diameter')
        labels.append((f'd = {diameter:.4f}'.rstrip('0').rstrip('.'), 0, radius + 0.2))
        
        # Area label (in center)
        area = self.get_property('area')
        labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), 0, -0.3))
        
        # Circumference label (outside bottom)
        circ = self.get_property('circumference')
        labels.append((f'C = {circ:.4f}'.rstrip('0').rstrip('.'), 0, -radius - 0.4))
        
        return labels
