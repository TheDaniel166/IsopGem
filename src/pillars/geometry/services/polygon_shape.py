"""Regular polygon shape calculator."""
import math
from typing import Dict, List, Tuple
from .base_shape import GeometricShape, ShapeProperty


class RegularPolygonShape(GeometricShape):
    """Regular polygon with n equal sides and angles."""
    
    def __init__(self, num_sides: int = 6):
        """
        Initialize regular polygon.
        
        Args:
            num_sides: Number of sides (must be >= 3)
        """
        self.num_sides = max(3, num_sides)
        super().__init__()
    
    @property
    def name(self) -> str:
        # Special names for common polygons
        names = {
            3: "Equilateral Triangle",
            4: "Square",
            5: "Regular Pentagon",
            6: "Regular Hexagon",
            7: "Regular Heptagon",
            8: "Regular Octagon",
            9: "Regular Nonagon",
            10: "Regular Decagon",
            12: "Regular Dodecagon",
        }
        return names.get(self.num_sides, f"Regular {self.num_sides}-gon")
    
    @property
    def description(self) -> str:
        return f"A regular polygon with {self.num_sides} equal sides and angles"
    
    def _init_properties(self):
        """Initialize regular polygon properties."""
        self.properties = {
            'side': ShapeProperty(
                name='Side Length',
                key='side',
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
            'apothem': ShapeProperty(
                name='Apothem',
                key='apothem',
                unit='units',
                readonly=False
            ),
            'circumradius': ShapeProperty(
                name='Circumradius',
                key='circumradius',
                unit='units',
                readonly=False
            ),
            'diagonal': ShapeProperty(
                name='Shortest Diagonal',
                key='diagonal',
                unit='units',
                readonly=False
            ),
            'interior_angle': ShapeProperty(
                name='Interior Angle',
                key='interior_angle',
                unit='°',
                readonly=True
            ),
            'exterior_angle': ShapeProperty(
                name='Exterior Angle',
                key='exterior_angle',
                unit='°',
                readonly=True
            ),
        }
    
    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Calculate all properties from any given property."""
        if value <= 0:
            return False
        
        n = self.num_sides
        
        # Calculate side from the input property
        if property_key == 'side':
            side = value
        elif property_key == 'perimeter':
            side = value / n
        elif property_key == 'area':
            # area = (n * s²) / (4 * tan(π/n))
            side = math.sqrt((4 * value * math.tan(math.pi / n)) / n)
        elif property_key == 'apothem':
            # apothem = s / (2 * tan(π/n))
            side = 2 * value * math.tan(math.pi / n)
        elif property_key == 'circumradius':
            # circumradius = s / (2 * sin(π/n))
            side = 2 * value * math.sin(math.pi / n)
        elif property_key == 'diagonal':
            # For shortest diagonal: d = s * √(2 - 2*cos(2π/n))
            # Solving for s: s = d / √(2 - 2*cos(2π/n))
            diagonal_factor = math.sqrt(2 - 2 * math.cos(2 * math.pi / n))
            side = value / diagonal_factor
        else:
            return False
        
        # Calculate all properties from side
        self.properties['side'].value = side
        self.properties['perimeter'].value = n * side
        
        # Apothem (perpendicular distance from center to side)
        apothem = side / (2 * math.tan(math.pi / n))
        self.properties['apothem'].value = apothem
        
        # Area
        area = (n * side * apothem) / 2
        self.properties['area'].value = area
        
        # Circumradius (distance from center to vertex)
        circumradius = side / (2 * math.sin(math.pi / n))
        self.properties['circumradius'].value = circumradius
        
        # Shortest diagonal (connecting vertices separated by one vertex)
        # Formula: d = s * √(2 - 2*cos(2π/n))
        # This gives the diagonal that skips one vertex
        diagonal = side * math.sqrt(2 - 2 * math.cos(2 * math.pi / n))
        self.properties['diagonal'].value = diagonal
        
        # Angles
        interior_angle = ((n - 2) * 180) / n
        self.properties['interior_angle'].value = interior_angle
        self.properties['exterior_angle'].value = 180 - interior_angle
        
        return True
    
    def get_drawing_instructions(self) -> Dict:
        """Get drawing instructions for the regular polygon."""
        # Render a normalized, static diagram (unit circumradius)
        # so the visual shape stays constant and only labels update.
        circumradius = 1.0
        
        # Generate vertices
        points = []
        for i in range(self.num_sides):
            angle = (2 * math.pi * i / self.num_sides) - (math.pi / 2)  # Start at top
            x = circumradius * math.cos(angle)
            y = circumradius * math.sin(angle)
            points.append((x, y))
        
        return {
            'type': 'polygon',
            'points': points,
            'show_circumcircle': True,
            'show_apothem': True,
            'show_diagonal': True,  # Show shortest diagonal
            'show_longest_diagonal': True,
        }
    
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """Get label positions for the polygon (static diagram positions)."""
        labels: List[Tuple[str, float, float]] = []
        
        # Use unit circumradius for consistent label placement
        cr = 1.0
        
        # Side label (bottom)
        side = self.get_property('side')
        if side is not None:
            labels.append((f's = {side:.4f}'.rstrip('0').rstrip('.'), 0, -cr - 0.3))
        
        # Diagonals
        diagonal = self.get_property('diagonal')
        if diagonal is not None:
            labels.append((f'd_min = {diagonal:.4f}'.rstrip('0').rstrip('.'), cr * 0.8, cr * 0.2))
        
        longest_diagonal = self.get_property('longest_diagonal') if 'longest_diagonal' in self.properties else None
        if longest_diagonal is not None:
            labels.append((f'd_max = {longest_diagonal:.4f}'.rstrip('0').rstrip('.'), -cr * 0.8, cr * 0.2))
        
        # Area label (center)
        area = self.get_property('area')
        if area is not None:
            labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), 0, 0))
        
        # Number of sides label
        labels.append((f'n = {self.num_sides}', 0, -0.2))
        
        return labels
