"""Square and Rectangle shape calculators.

The square is the regular 4-gon—a quadrilateral with all sides equal and all angles 90°.
It is the simplest regular polygon that tiles the plane (triangles need orientation
alternation). The square embodies stability, order, and rationality, serving as the
fundamental unit of measurement (area measured in "square units").

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Four-Fold Symmetry (The Cardinal Cross)
═══════════════════════════════════════════════════════════════════════════════════════

The square has **dihedral symmetry group D₄**, order 8:

• **4 rotational symmetries**: Identity, 90°, 180°, 270° (4-fold axis)
• **4 reflection symmetries**: 2 through opposite edge midpoints (horizontal/vertical),
  2 through opposite vertices (diagonal axes)
• Total: 8 symmetry operations

Compare to other quadrilaterals:
• Rectangle: D₂ (order 4) → 2 rotations + 2 reflections (no diagonal symmetry)
• Rhombus: D₂ (order 4) → 2 rotations + 2 reflections (diagonal axes only)
• Square: D₄ (order 8) → combines both edge AND diagonal reflection symmetry!

**The Cardinal Directions**:
• Square orientation defines NSEW (North/South/East/West) in cartesian geometry
• Four corners = four elements (🜂 Earth, 🜁 Air, 🜄 Water, 🜃 Fire)
• Four seasons, four phases of moon, four gospels, four noble truths

**Tessellation**: Squares tile the plane perfectly (no gaps, no overlaps):
• Each vertex has 4 squares meeting (vertex angle sum: 4×90° = 360°)
• This is the SIMPLEST monohedral tiling (one shape type)
• Grid/lattice structure: foundation of cartesian coordinates, graph paper, pixels

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: The √2 Diagonal (The First Irrational)
═══════════════════════════════════════════════════════════════════════════════════════

For a square with side length s, the diagonal length d is:

  d = s√2    (Pythagorean theorem: d² = s² + s² = 2s²)

**Historical significance**: √2 ≈ 1.414213... was the first irrational number discovered
(attributed to Hippasus, Pythagorean school, ~500 BCE).

Proof of irrationality (by contradiction):
• Assume √2 = p/q (rational, in lowest terms)
• Then 2 = p²/q², so p² = 2q²
• Therefore p² is even, so p is even (p = 2k)
• Then (2k)² = 2q², so 4k² = 2q², so q² = 2k²
• Therefore q² is even, so q is even
• Contradiction! Both p and q are even, but we assumed lowest terms.
• Hence √2 is irrational (cannot be expressed as ratio of integers)

This discovery **shattered the Pythagorean belief** that "all is number" (meaning
rational numbers). Irrational numbers forced expansion of mathematics beyond ratios.

**A4 paper ratio**: International paper sizes (A0, A1, A2...) use 1:√2 ratio!
• When you fold A4 in half → A5 (aspect ratio preserved: 1/√2 : 1 = 1 : √2)
• This self-similar scaling property makes photocopying/resizing lossless

**Silver ratio**: δₛ = 1 + √2 ≈ 2.414 (related to octagon, not as famous as golden φ)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Square as Fundamental Unit (The Measure of All)
═══════════════════════════════════════════════════════════════════════════════════════

**Area measurement**: We measure area in "square units" (cm², m², km²) because:
• The square is the UNIT CELL of cartesian space
• Rectangles are stretched squares: A = length × width
• Any polygon can be decomposed into squares (approximately) via grid overlay

**Pythagorean theorem visualization**:
For a right triangle with legs a and b, hypotenuse c:
  a² + b² = c²

This is literally about SQUARES:
• a²: area of square built on side a
• b²: area of square built on side b
• c²: area of square built on hypotenuse c
• The theorem states: area(square on a) + area(square on b) = area(square on c)

Euclid's visual proof (Elements, Book I, Proposition 47) uses actual squares drawn
on each side of a right triangle!

**Square numbers**: 1, 4, 9, 16, 25, 36, 49, 64, 81, 100...
• n² = n×n (n rows of n dots arranged in square)
• Sum of first n odd numbers = n²:
    1 = 1²
    1+3 = 4 = 2²
    1+3+5 = 9 = 3²
    1+3+5+7 = 16 = 4²
  (Visual: each odd number forms an L-shaped border around the previous square)

**Manhattan distance**: In grid cities (NYC), distance is measured by square grid:
  d = |Δx| + |Δy| (taxicab geometry)
  vs. Euclidean distance d = √(Δx² + Δy²)

Squares define the **digital world**: pixels, voxels, chess boards, Minecraft blocks.
The square is the atomic unit of discrete space.

═══════════════════════════════════════════════════════════════════════════════════════
🝆 HERMETIC SIGNIFICANCE 🝆
═══════════════════════════════════════════════════════════════════════════════════════

The square embodies **Manifestation, Stability, and the Material Plane**:

• **Earth Element (🜃)**: The square represents solidity, foundation, the four corners
  of the world. In alchemy, square = material realm (vs. circle = spiritual realm).
  The alchemical symbol for salt (🜔) is a square bisected by a horizontal line—
  matter crystallized.

• **Squaring the Circle**: The impossible compass-and-straightedge construction
  symbolizes the philosopher's quest to EMBODY spirit (circle/π) in matter (square).
  Not mathematically possible, but spiritually necessary—the incarnation paradox.

• **Tetragrammaton (יהוה)**: The four-letter name of God (YHWH). Four = manifestation
  into the world (three = divine trinity in heaven, four = embodied in creation).
  The square is the *extension* of the triangle into materiality.

• **Temple Foundation**: Sacred architecture uses square bases:
  - Ka'aba (Mecca): cube (6 squares)
  - New Jerusalem (Revelation): perfect square city, 12,000 stadia per side
  - Roman castrum (military camp): square with cross roads (cardo/decumanus)
  The square provides STABLE FOUNDATION for vertical ascent (axis mundi).

• **Checker/Chess Board**: 8×8 = 64 squares (2⁶) represents the cosmic game board,
  alternating black/white (yin/yang, good/evil, light/dark dualities). Life as
  strategic movement across the grid of fate.

• **The Four Worlds (Kabbalah)**: Atziluth, Briah, Yetzirah, Assiah—emanation,
  creation, formation, action. The square as descent through four planes from
  divine unity to physical multiplicity.

The square teaches: **To manifest is to LIMIT the infinite into definite form.** 🝆

═══════════════════════════════════════════════════════════════════════════════════════
"""
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