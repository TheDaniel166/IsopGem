"""Square and Rectangle shape calculators."""
import math
from typing import Dict, List, Tuple
from .base_shape import GeometricShape, ShapeProperty


class SquareShape(GeometricShape):
    """Square shape with bidirectional property calculations."""
    
    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Square"
    
    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "A regular quadrilateral with all sides equal and all angles 90°"
    
    def _init_properties(self):
        """Initialize square properties."""
        self.properties = {
            'side': ShapeProperty(
                name='Side Length',
                key='side',
                unit='units',
                readonly=False,
                formula=r's'
            ),
            'perimeter': ShapeProperty(
                name='Perimeter',
                key='perimeter',
                unit='units',
                readonly=False,
                formula=r'P = 4s'
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=False,
                formula=r'A = s^2'
            ),
            'diagonal': ShapeProperty(
                name='Diagonal',
                key='diagonal',
                unit='units',
                readonly=False,
                formula=r'd = s\sqrt{2}'
            ),
        }
    
    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Calculate all properties from any given property."""
        if value <= 0:
            return False
        
        # Calculate side from the input property
        if property_key == 'side':
            side = value
        elif property_key == 'perimeter':
            side = value / 4
        elif property_key == 'area':
            side = math.sqrt(value)
        elif property_key == 'diagonal':
            side = value / math.sqrt(2)
        else:
            return False
        
        # Calculate all properties from side
        self.properties['side'].value = side
        self.properties['perimeter'].value = 4 * side
        self.properties['area'].value = side * side
        self.properties['diagonal'].value = side * math.sqrt(2)
        
        return True
    
    def get_drawing_instructions(self) -> Dict:
        """Get drawing instructions for the square."""
        side = self.get_property('side')
        
        if side is None:
            return {'type': 'empty'}
        
        half = side / 2
        
        return {
            'type': 'polygon',
            'points': [
                (-half, -half),
                (half, -half),
                (half, half),
                (-half, half),
            ],
            'show_diagonals': True,
        }
    
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """Get label positions for the square."""
        side = self.get_property('side')
        
        if side is None:
            return []
        
        half = side / 2
        labels = []
        
        # Side label
        labels.append((f's = {side:.4f}'.rstrip('0').rstrip('.'), 0, -half - 0.3))
        
        # Area label (shifted up)
        area = self.get_property('area')
        labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), 0, 0.2))
        
        # Diagonal label
        diagonal = self.get_property('diagonal')
        labels.append((f'd = {diagonal:.4f}'.rstrip('0').rstrip('.'), half + 0.2, half + 0.2))
        
        return labels


class RectangleShape(GeometricShape):
    """Rectangle shape with bidirectional property calculations."""
    
    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Rectangle"
    
    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "A quadrilateral with opposite sides equal and all angles 90°"
    
    def _init_properties(self):
        """Initialize rectangle properties."""
        self.properties = {
            'length': ShapeProperty(
                name='Length',
                key='length',
                unit='units',
                readonly=False,
                formula=r'l'
            ),
            'width': ShapeProperty(
                name='Width',
                key='width',
                unit='units',
                readonly=False,
                formula=r'w'
            ),
            'perimeter': ShapeProperty(
                name='Perimeter',
                key='perimeter',
                unit='units',
                readonly=False,
                formula=r'P = 4s'
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=False,
                formula=r'A = s^2'
            ),
            'diagonal': ShapeProperty(
                name='Diagonal',
                key='diagonal',
                unit='units',
                readonly=False,
                formula=r'd = s\sqrt{2}'
            ),
        }
    
    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Calculate dependent properties."""
        if value <= 0:
            return False
        
        # Determine which property is being set
        if property_key == 'length':
            self.properties['length'].value = value
        elif property_key == 'width':
            self.properties['width'].value = value
        elif property_key == 'area':
            self.properties['area'].value = value
        elif property_key == 'perimeter':
            self.properties['perimeter'].value = value
        elif property_key == 'diagonal':
            self.properties['diagonal'].value = value
        else:
            return False

        # Attempt to resolve missing dimensions
        length = self.properties['length'].value
        width = self.properties['width'].value
        area = self.properties['area'].value
        perimeter = self.properties['perimeter'].value
        diagonal = self.properties['diagonal'].value
        


        # Try to derive width if length is known
        if length and not width:
            if area:
                width = area / length
            elif perimeter:
                val = (perimeter / 2) - length
                if val > 0: width = val
            elif diagonal:
                if diagonal > length:
                    width = math.sqrt(diagonal**2 - length**2)

        # Try to derive length if width is known
        if width and not length:
            if area:
                length = area / width
            elif perimeter:
                val = (perimeter / 2) - width
                if val > 0: length = val
            elif diagonal:
                if diagonal > width:
                    length = math.sqrt(diagonal**2 - width**2)
        
        # If we have both dimensions, update them and recalculate everything
        if length and width:
            self.properties['length'].value = length
            self.properties['width'].value = width
            self.properties['perimeter'].value = 2 * (length + width)
            self.properties['area'].value = length * width
            self.properties['diagonal'].value = math.sqrt(length**2 + width**2)
        
        return True
    
    def get_drawing_instructions(self) -> Dict:
        """Get drawing instructions for the rectangle."""
        length = self.get_property('length')
        width = self.get_property('width')
        
        if length is None or width is None:
            return {'type': 'empty'}
        
        half_l = length / 2
        half_w = width / 2
        
        return {
            'type': 'polygon',
            'points': [
                (-half_l, -half_w),
                (half_l, -half_w),
                (half_l, half_w),
                (-half_l, half_w),
            ],
            'show_diagonals': True,
        }
    
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """Get label positions for the rectangle."""
        length = self.get_property('length')
        width = self.get_property('width')
        
        if length is None or width is None:
            return []
        
        half_l = length / 2
        half_w = width / 2
        labels = []
        
        # Length label
        labels.append((f'l = {length:.4f}'.rstrip('0').rstrip('.'), 0, -half_w - 0.3))
        
        # Width label
        labels.append((f'w = {width:.4f}'.rstrip('0').rstrip('.'), -half_l - 0.3, 0))
        
        # Area label (shifted up)
        area = self.get_property('area')
        if area:
            labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), 0, 0.2))
        
        # Diagonal label
        diagonal = self.get_property('diagonal')
        if diagonal:
            labels.append((f'd = {diagonal:.4f}'.rstrip('0').rstrip('.'), half_l + 0.2, half_w + 0.2))
        
        return labels