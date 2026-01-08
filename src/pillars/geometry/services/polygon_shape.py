"""Regular polygon shape calculator.

A regular polygon is an n-sided figure with all sides equal and all angles equal. It
possesses n-fold rotational symmetry and represents discrete approximations to the
continuous circle. As n→∞, the regular polygon converges to the circle, bridging
the discrete world of integers with the continuous realm of curves.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Interior and Exterior Angles (The 360° Walk)
═══════════════════════════════════════════════════════════════════════════════════════

For a regular n-gon:

**Interior angle**: θ_interior = ((n-2)×180°)/n
• Derivation: An n-gon can be divided into (n-2) triangles from a central vertex.
  Total angle sum = (n-2)×180°. For regular polygon, divide by n vertices.
• Rewrite: θ_interior = 180° - 360°/n

**Exterior angle**: θ_exterior = 360°/n
• Interior + Exterior = 180° (supplementary angles)
• KEY INSIGHT: Sum of ALL exterior angles = 360° (for ANY polygon!)

Why? Imagine walking around the perimeter of a polygon:
• Start facing along edge 1
• At each vertex, you turn by the exterior angle
• After n vertices, you've completed ONE FULL ROTATION = 360°
• This is true even for irregular polygons!

**Examples**:
• Triangle (n=3): interior = 60°, exterior = 120°
• Square (n=4): interior = 90°, exterior = 90°
• Pentagon (n=5): interior = 108°, exterior = 72°
• Hexagon (n=6): interior = 120°, exterior = 60°
• Octagon (n=8): interior = 135°, exterior = 45°
• Dodecagon (n=12): interior = 150°, exterior = 30°

As n→∞:
• Interior angle → 180° (straight line)
• Exterior angle → 0° (no turning)
• Polygon → Circle (infinitesimal exterior angles sum to 360° via integration!)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Apothem, Circumradius, and the Dual Geometry
═══════════════════════════════════════════════════════════════════════════════════════

A regular n-gon inscribed in a circle of radius R has two key radii:

**Circumradius** R: distance from center to vertex
**Apothem** a: distance from center to edge midpoint (perpendicular to edge)

For side length s:
• s = 2R·sin(π/n)    [chord formula]
• a = R·cos(π/n)    [perpendicular drop from center to edge]
• Alternatively: s = 2a·tan(π/n)

**Area formula**:
  A = (1/2)×perimeter×apothem = (1/2)×(ns)×a = (ns²)/(4tan(π/n))

Or in terms of circumradius:
  A = (nR²/2)·sin(2π/n)

As n→∞:
• sin(2π/n) → 2π/n    (small angle approximation)
• A → (nR²/2)×(2π/n) = πR²    (circle area!)

**Duality**: Every regular n-gon has a DUAL regular n-gon:
• Original: vertices connected by edges
• Dual: place vertex at center of each edge, connect them
• Result: The dual of a regular n-gon is ANOTHER regular n-gon, rotated 180°/n
• Example: Square's dual is a square rotated 45°
• Self-dual polygons: n must divide 360° evenly into 90° chunks (n=4 only!)

**Platonic solid duality**: This 2D duality extends to 3D:
• Tetrahedron ↔ Tetrahedron (self-dual)
• Cube ↔ Octahedron
• Dodecahedron ↔ Icosahedron

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Diagonals and Combinatorial Explosion
═══════════════════════════════════════════════════════════════════════════════════════

A diagonal connects two non-adjacent vertices. For an n-gon:

**Number of diagonals**: D = n(n-3)/2

Derivation:
• From each vertex, you can draw (n-3) diagonals (exclude the vertex itself and its
  two adjacent vertices connected by edges)
• Total: n(n-3), but this counts each diagonal TWICE (once from each endpoint)
• So D = n(n-3)/2

**Examples**:
• Triangle (n=3): D = 0 (no diagonals, triangle is "complete")
• Square (n=4): D = 2 (two diagonals crossing at center)
• Pentagon (n=5): D = 5 (pentagram!)
• Hexagon (n=6): D = 9
• Octagon (n=8): D = 20
• Decagon (n=10): D = 35

As n grows, diagonals EXPLODE:
• D ~ n²/2 (quadratic growth)
• For n=100: D = 4850 diagonals!

**Diagonal lengths** (multiple distinct lengths for n>6):
• Triangle: no diagonals
• Square: 1 length (all diagonals equal: d = s√2)
• Pentagon: 1 length (all diagonals equal: d = s·φ, golden ratio!)
• Hexagon: 2 lengths (short and long diagonals)
• Heptagon: 2 lengths
• Octagon: 3 lengths
• For general n: (floor(n/2)-1) distinct diagonal lengths

**Star polygons** (n/k notation):
• Connect every k-th vertex: {n/k}
• Pentagon diagonals form pentagram: {5/2}
• Hexagon: {6/2} degenerates to two triangles, but {6/3} is hexagram (Star of David)
• Heptagon: {7/2} and {7/3} are two distinct star heptagrams

This combinatorial structure underlies graph theory and network topology.

═══════════════════════════════════════════════════════════════════════════════════════
⬢ HERMETIC SIGNIFICANCE ⬢
═══════════════════════════════════════════════════════════════════════════════════════

Polygons encode **Number Symbolism and Geometric Archetypes**:

• **Pentagon (n=5)**: The human microcosm (5 limbs: 2 arms, 2 legs, 1 head), five
  senses, five elements (classical + æther). Pentagon diagonals form the PENTAGRAM
  (☆), ancient symbol of protection and golden ratio (φ everywhere in 5-fold geometry).
  Venus traces a pentagram in the sky over 8 years (5:8 orbital resonance with Earth).

• **Hexagon (n=6)**: The structure of honeycombs (optimal packing), benzene rings
  (carbon chemistry), snowflakes (6-fold ice crystal symmetry). Six = 2×3 (marriage
  of duality and trinity). Hexagram (Star of David, Seal of Solomon) = union of
  upward/downward triangles → *As Above, So Below*.

• **Heptagon (n=7)**: Seven days of week, seven classical planets, seven chakras,
  seven heavens. Heptagon is NON-CONSTRUCTIBLE (like π), cannot be drawn with compass
  and straightedge → it represents the *transcendent* (beyond rational construction).

• **Octagon (n=8)**: Eight directions (compass rose), Buddhist Eightfold Path, eight
  trigrams of I Ching. Octagon mediates between square (4) and circle (∞) → it's
  used in Islamic architecture to transition from square chamber to circular dome.

• **Enneagon (n=9)**: Nine = 3² (trinity of trinities), completeness before new cycle
  (10). Dante's nine circles of Hell, nine months of gestation, nine Muses.

• **Dodecagon (n=12)**: Twelve zodiac signs, twelve apostles, twelve tribes, twelve
  hours. Dodecahedron (12 pentagonal faces) was Plato's form for the COSMOS itself
  (the "fifth element" beyond the four terrestrial).

Polygons teach: **Discrete number creates geometric form; form embodies number's meaning.** ⬢

═══════════════════════════════════════════════════════════════════════════════════════
"""
import math
from typing import Dict, List, Tuple
from .base_shape import GeometricShape, ShapeProperty


DIAGONAL_COLOR_PALETTE: List[Tuple[int, int, int, int]] = [
    (239, 68, 68, 255),    # red
    (16, 185, 129, 255),   # green
    (59, 130, 246, 255),   # blue
    (234, 179, 8, 255),    # amber
    (139, 92, 246, 255),   # violet
    (248, 113, 113, 255),  # light red
]


class RegularPolygonShape(GeometricShape):
    """Regular polygon with n equal sides and angles."""
    
    def __init__(self, num_sides: int = 6):
        """
        Initialize regular polygon.
        
        Args:
            num_sides: Number of sides (must be >= 3)
        """
        self.num_sides = max(3, num_sides)
        self._diagonal_keys: Dict[int, str] = {}
        self._diagonal_key_to_skip: Dict[str, int] = {}
        super().__init__()
    
    @property
    def name(self) -> str:
        # Special names for common polygons
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
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
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return f"A regular polygon with {self.num_sides} equal sides and angles"
    
    def _init_properties(self):
        """Initialize regular polygon properties."""
        self._diagonal_keys = {}
        self._diagonal_key_to_skip = {}
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
                formula=r'P = ns'
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=False,
                formula=r'A = \frac{ns^2}{4\tan(\pi/n)}'
            ),
            'wedge_area': ShapeProperty(
                name='Wedge Area (sector)',
                key='wedge_area',
                unit='units²',
                readonly=True,
                formula=r'A_{wedge} = \frac{\pi r^2}{n}'
            ),
            'apothem': ShapeProperty(
                name='Apothem',
                key='apothem',
                unit='units',
                readonly=False,
                formula=r'a = \frac{s}{2\tan(\pi/n)}'
            ),
            'circumradius': ShapeProperty(
                name='Circumradius',
                key='circumradius',
                unit='units',
                readonly=False,
                formula=r'R = \frac{s}{2\sin(\pi/n)}'
            ),
            'incircle_circumference': ShapeProperty(
                name='Incircle Circumference',
                key='incircle_circumference',
                unit='units',
                readonly=True,
                formula=r'C_{in} = 2\pi a'
            ),
            'circumcircle_circumference': ShapeProperty(
                name='Circumcircle Circumference',
                key='circumcircle_circumference',
                unit='units',
                readonly=True,
                formula=r'C_{out} = 2\pi R'
            ),
            'interior_angle': ShapeProperty(
                name='Interior Angle',
                key='interior_angle',
                unit='°',
                readonly=True,
                formula=r'\theta_{int} = \frac{(n-2) \cdot 180°}{n}'
            ),
            'exterior_angle': ShapeProperty(
                name='Exterior Angle',
                key='exterior_angle',
                unit='°',
                readonly=True,
                formula=r'\theta_{ext} = \frac{360°}{n}'
            ),
        }

        for skip in self._diagonal_skip_range():
            key = f'diagonal_skip_{skip}'
            self.properties[key] = ShapeProperty(
                name=f'Diagonal (skip {skip})',
                key=key,
                unit='units',
                readonly=False,
            )
            self._diagonal_keys[skip] = key
            self._diagonal_key_to_skip[key] = skip
    
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
        elif property_key in self._diagonal_key_to_skip:
            skip = self._diagonal_key_to_skip[property_key]
            numerator = math.sin(math.pi / n)
            denominator = math.sin(skip * math.pi / n)
            if abs(denominator) < 1e-9:
                return False
            side = value * (numerator / denominator)
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
        self.properties['wedge_area'].value = area / n if area is not None else None
        
        # Circumradius (distance from center to vertex)
        circumradius = side / (2 * math.sin(math.pi / n))
        self.properties['circumradius'].value = circumradius
        self.properties['incircle_circumference'].value = 2 * math.pi * apothem
        self.properties['circumcircle_circumference'].value = 2 * math.pi * circumradius
        
        diagonal_lengths = self._diagonal_lengths(circumradius)
        for skip, key in self._diagonal_keys.items():
            self.properties[key].value = diagonal_lengths.get(skip)
        
        # Angles
        interior_angle = ((n - 2) * 180) / n
        self.properties['interior_angle'].value = interior_angle
        self.properties['exterior_angle'].value = 180 - interior_angle
        
        return True
    
    def get_drawing_instructions(self) -> Dict:
        """Get drawing instructions for the regular polygon."""
        circumradius = self.get_property('circumradius')
        if circumradius is None:
             circumradius = 1.0 # Fallback for initial view or invalid state

        points = self._polygon_points(circumradius)
        diagonal_groups = self._build_diagonal_groups(points)
        return {
            'type': 'polygon',
            'points': points,
            'show_circumcircle': True,
            'diagonal_groups': diagonal_groups,
        }
    
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """Get label positions for the polygon (static diagram positions)."""
        labels: List[Tuple[str, float, float]] = []
        
        # Use actual circumradius for label placement if available, else 1.0
        cr = self.get_property('circumradius') or 1.0
        
        # Side label (bottom)
        side = self.get_property('side')
        if side is not None:
            labels.append((f's = {side:.4f}'.rstrip('0').rstrip('.'), 0, -cr - 0.3))
        
        # Diagonals
        
        # Area label (shifted up)
        area = self.get_property('area')
        if area is not None:
            labels.append((f'A = {area:.4f}'.rstrip('0').rstrip('.'), 0, 0.2))
        
        # Number of sides label (shifted down)
        labels.append((f'n = {self.num_sides}', 0, -0.3))
        
        return labels

    def _polygon_points(self, radius: float) -> List[Tuple[float, float]]:
        points: List[Tuple[float, float]] = []
        for i in range(self.num_sides):
            angle = (2 * math.pi * i / self.num_sides) - (math.pi / 2)
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
        return points

    def _build_diagonal_groups(self, points: List[Tuple[float, float]]) -> List[Dict]:
        n = len(points)
        max_skip = n // 2
        if max_skip < 2:
            return []
        groups: List[Dict] = []
        palette_len = len(DIAGONAL_COLOR_PALETTE)
        for index, skip in enumerate(range(2, max_skip + 1)):
            color = DIAGONAL_COLOR_PALETTE[index % palette_len]
            segments = []
            seen_pairs = set()
            for i in range(n):
                j = (i + skip) % n
                pair = tuple(sorted((i, j)))
                if pair in seen_pairs or i == j:
                    continue
                seen_pairs.add(pair)
                segments.append({'start': points[i], 'end': points[j]})
            if segments:
                groups.append({'skip': skip, 'color': color, 'segments': segments})
        return groups

    def _diagonal_skip_range(self) -> range:
        return range(2, (self.num_sides // 2) + 1)

    def _diagonal_lengths(self, circumradius: float) -> Dict[int, float]:
        lengths: Dict[int, float] = {}
        for skip in self._diagonal_skip_range():
            lengths[skip] = 2 * circumradius * math.sin(skip * math.pi / self.num_sides)
        return lengths