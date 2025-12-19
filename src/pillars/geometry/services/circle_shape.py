"""Circle shape calculator."""
import math
from typing import Dict, List, Tuple, Optional
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
            'central_angle_deg': ShapeProperty(
                name='Central Angle',
                key='central_angle_deg',
                unit='°',
                readonly=False,
                precision=2
            ),
            'arc_length': ShapeProperty(
                name='Arc Length',
                key='arc_length',
                unit='units',
                readonly=False
            ),
            'chord_length': ShapeProperty(
                name='Chord Length',
                key='chord_length',
                unit='units',
                readonly=False
            ),
            'sagitta': ShapeProperty(
                name='Sagitta (Chord Height)',
                key='sagitta',
                unit='units',
                readonly=False
            ),
            'sector_area': ShapeProperty(
                name='Sector Area',
                key='sector_area',
                unit='units²',
                readonly=True
            ),
            'segment_area': ShapeProperty(
                name='Segment Area',
                key='segment_area',
                unit='units²',
                readonly=True
            ),
        }
    
    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Calculate all properties from any given property."""
        if value <= 0:
            return False
        
        # Calculate radius from the input property
        if property_key == 'radius':
            radius = value
            self._update_base_from_radius(radius)
            return True
        if property_key == 'diameter':
            radius = value / 2
            self._update_base_from_radius(radius)
            return True
        if property_key == 'circumference':
            radius = value / (2 * math.pi)
            self._update_base_from_radius(radius)
            return True
        if property_key == 'area':
            radius = math.sqrt(value / math.pi)
            self._update_base_from_radius(radius)
            return True

        # Chord-related properties require a known radius
        radius = self.properties['radius'].value
        if radius is None or radius <= 0:
            return False

        if property_key == 'central_angle_deg':
            angle_rad = math.radians(value)
            self.properties['central_angle_deg'].value = value
            self._update_chord_metrics(radius, angle_rad)
            return True

        if property_key == 'arc_length':
            angle_rad = value / radius
            self.properties['central_angle_deg'].value = math.degrees(angle_rad)
            self._update_chord_metrics(radius, angle_rad)
            return True

        if property_key == 'chord_length':
            if value <= 0 or value > 2 * radius:
                return False
            ratio = min(1.0, max(-1.0, value / (2 * radius)))
            angle_rad = 2 * math.asin(ratio)
            self.properties['central_angle_deg'].value = math.degrees(angle_rad)
            self._update_chord_metrics(radius, angle_rad)
            return True

        if property_key == 'sagitta':
            if value <= 0 or value >= 2 * radius:
                return False
            ratio = 1 - (value / radius)
            ratio = min(1.0, max(-1.0, ratio))
            angle_rad = 2 * math.acos(ratio)
            self.properties['central_angle_deg'].value = math.degrees(angle_rad)
            self._update_chord_metrics(radius, angle_rad)
            return True
        
        return False
    
    def get_drawing_instructions(self) -> Dict:
        """Get drawing instructions for the circle."""
        radius = self.get_property('radius')
        
        if radius is None:
            return {'type': 'empty'}
        
        angle_deg = self.properties['central_angle_deg'].value
        chord_points = None
        if angle_deg and angle_deg > 0:
            angle_rad = math.radians(angle_deg)
            half = angle_rad / 2
            x = radius * math.sin(half)
            y = radius * math.cos(half)
            chord_points = [(-x, y), (x, y)]

        return {
            'type': 'circle',
            'center_x': 0,
            'center_y': 0,
            'radius': radius,
            'show_radius_line': True,
            'show_diameter_line': True,
            'chord_points': chord_points,
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
        
        # Area label (shifted up)
        area = self.get_property('area')
        labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), 0, 0.2))
        
        # Circumference label (outside bottom)
        circ = self.get_property('circumference')
        labels.append((f'C = {circ:.4f}'.rstrip('0').rstrip('.'), 0, -radius - 0.4))
        
        angle_deg = self.properties['central_angle_deg'].value
        chord_length = self.get_property('chord_length')
        if angle_deg and chord_length:
            labels.append((f"Chord={chord_length:.4f}".rstrip('0').rstrip('.'), 0, radius * 0.4))
            labels.append((f"θ={angle_deg:.2f}°", 0, radius * 0.15))
        
        return labels

    def _update_base_from_radius(self, radius: float):
        self.properties['radius'].value = radius
        self.properties['diameter'].value = radius * 2
        self.properties['circumference'].value = 2 * math.pi * radius
        self.properties['area'].value = math.pi * radius * radius
        angle_deg = self.properties['central_angle_deg'].value
        if angle_deg:
            self._update_chord_metrics(radius, math.radians(angle_deg))
        else:
            self._clear_chord_metrics()

    def _clear_chord_metrics(self):
        for key in ('arc_length', 'chord_length', 'sagitta', 'sector_area', 'segment_area'):
            self.properties[key].value = None

    def _update_chord_metrics(self, radius: float, angle_rad: float):
        if angle_rad <= 0:
            self._clear_chord_metrics()
            return
        arc_length = radius * angle_rad
        chord_length = 2 * radius * math.sin(angle_rad / 2)
        sagitta = radius * (1 - math.cos(angle_rad / 2))
        sector_area = 0.5 * radius * radius * angle_rad
        segment_area = 0.5 * radius * radius * (angle_rad - math.sin(angle_rad))

        self.properties['arc_length'].value = arc_length
        self.properties['chord_length'].value = chord_length
        self.properties['sagitta'].value = sagitta
        self.properties['sector_area'].value = sector_area
        self.properties['segment_area'].value = segment_area

