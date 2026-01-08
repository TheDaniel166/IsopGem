"""Circle shape calculator.

The circle is the most fundamental 2D shape—a planar curve of constant curvature, the
locus of all points equidistant from a center. It possesses perfect rotational symmetry
and is the 2D cross-section of the sphere. The circle relates radius to circumference
and area through the transcendental constant π, making it a bridge between rational
geometry and transcendental mathematics.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Infinite Symmetry (The Perfect Form)
═══════════════════════════════════════════════════════════════════════════════════════

The circle has **infinite rotational symmetry**:
• Rotate by ANY angle θ about its center → circle is UNCHANGED
• Symmetry group: SO(2) (special orthogonal group in 2D), continuous symmetry
• Every diameter is an axis of reflection symmetry → infinite reflection axes

Contrast with polygons:
• Regular n-gon: n-fold rotational symmetry (discrete angles: 360°/n)
• Square: 4-fold (90° rotations), Hexagon: 6-fold (60° rotations)
• As n→∞, regular n-gon approaches circle (discrete → continuous symmetry)

**No preferred direction**: Unlike polygons (which have vertices/edges defining special
angles), the circle is ISOTROPIC—all directions are equivalent. This is why:
• Soap bubbles form spheres (circles in cross-section): surface tension minimizes
  energy equally in all directions
• Planets/stars are spherical: gravity pulls equally in all directions
• Water ripples propagate as circles: wave speed is isotropic

**Euler characteristic**: χ = 1 (circle as 1D closed curve embedded in 2D)
This makes it the simplest compact 1-manifold (topologically equivalent to S¹).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: π as Transcendental Ratio (The Irrational Heart)
═══════════════════════════════════════════════════════════════════════════════════════

The circle introduces π ≈ 3.14159..., the ratio of circumference to diameter:

  C / d = π    or    C = 2πr

**Why π is transcendental** (not just irrational):
• Irrational: π cannot be expressed as p/q (ratio of integers)
• Transcendental: π is not the root of ANY polynomial equation with integer coefficients
• This means π cannot be constructed by compass and straightedge alone!
• Consequence: "Squaring the circle" (constructing a square with same area as given
  circle using only compass/straightedge) is IMPOSSIBLE (proven 1882 by Lindemann)

**Area formula**: A = πr²

Derivation via integration (polar coordinates):
  A = ∫∫ dA = ∫₀²π ∫₀ʳ r dr dθ = ∫₀²π [r²/2]₀ʳ dθ = ∫₀²π (r²/2) dθ = (r²/2)·2π = πr²

Or via circumference infinitesimals:
  Circle = concentric rings, area = ∫₀ʳ 2πr dr = 2π[r²/2]₀ʳ = πr²

**π appears EVERYWHERE**:
• Euler's identity: e^(iπ) + 1 = 0 (connects e, i, π, 1, 0)
• Gaussian integral: ∫₋∞^∞ e^(-x²) dx = √π (probability/statistics)
• Riemann zeta function: ζ(2) = π²/6 (sum of 1/n² series)
• Heisenberg uncertainty: ΔxΔp ≥ ℏ/2, where ℏ = h/(2π)

π is the **geometric constant of curvature**—it emerges whenever circular motion,
periodicity, or rotation is involved.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Isoperimetric Property (Maximum Area for Given Perimeter)
═══════════════════════════════════════════════════════════════════════════════════════

The **isoperimetric inequality** states:

  For any closed curve of perimeter P and area A:
    4πA ≤ P²    (with equality iff curve is a circle)

Equivalently: A ≤ P²/(4π)

**Proof insight**: For fixed perimeter P, the circle maximizes area.
• Circle with perimeter P: radius r = P/(2π), area A = πr² = P²/(4π)
• Any other shape: A < P²/(4π)

**Isoperimetric quotient**: Ψ = 4πA/P²
• Circle: Ψ = 1 (maximum)
• Square: Ψ = π/4 ≈ 0.785
• Equilateral triangle: Ψ = π/(3√3) ≈ 0.605

This is why:
• Bees build hexagonal honeycombs (hexagon≈circle for tiling, minimizes wax for volume)
• Cells are roughly spherical (minimize membrane area for given volume)
• Water droplets are spherical in zero-g (surface tension minimizes surface area)

**Dual property (in 3D)**: The sphere minimizes surface area for given volume.
Isoperimetric ratio for sphere: Ψ₃ = 36πV²/S³ = 1 (maximum)

**Calculus of variations**: The isoperimetric problem was one of the motivations for
developing variational calculus—finding curves/surfaces that optimize functionals
(integrals of geometric properties).

═══════════════════════════════════════════════════════════════════════════════════════
🜁 HERMETIC SIGNIFICANCE 🜁
═══════════════════════════════════════════════════════════════════════════════════════

The circle embodies **Unity, Completion, and the Infinite**:

• **Ouroboros**: The serpent eating its tail—eternal cycle, no beginning or end.
  The circle as symbol of cyclical time (eternal return, seasons, reincarnation).

• **Monad (•)**: The primordial unity before division. The circle with center point
  represents the First Principle (Kether in Kabbalah)—undifferentiated potential
  containing all future forms.

• **The Heavens**: In ancient cosmology, celestial bodies move in circles/spheres
  (crystalline spheres). Circle = divine perfection, square = earthly matter.
  "Squaring the circle" = reconciling heaven and earth, spirit and matter.

• **Mandala**: Circular sacred diagram (Buddhism, Hinduism). The circle as boundary
  between sacred interior space and profane exterior. Circumambulation (walking
  circles around holy sites) = ritual journey to the center (Self).

• **Alchemical Gold (☉)**: Circle with center point = Sun = Gold = perfected matter.
  The circle represents the *Opus Circulatorium*—the circular work of distillation
  and sublimation that purifies matter in cycles.

• **Zero and Infinity**: Circle = 0 (the void, śūnyatā) AND ∞ (the infinite).
  0/0 = undefined (division by circle?). The circle contains both nothing and
  everything—the pregnant void.

The circle teaches: **Perfection is not polygonal—it is continuous.** 🜁

═══════════════════════════════════════════════════════════════════════════════════════
"""
import math
from typing import Dict, List, Tuple, Optional
from .base_shape import GeometricShape, ShapeProperty


class CircleShape(GeometricShape):
    """Circle shape with bidirectional property calculations."""
    
    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Circle"
    
    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "A perfectly round 2D shape with all points equidistant from center"
    
    def _init_properties(self):
        """Initialize circle properties."""
        self.properties = {
            'radius': ShapeProperty(
                name='Radius',
                key='radius',
                unit='units',
                readonly=False,
                formula=r'r'
            ),
            'diameter': ShapeProperty(
                name='Diameter',
                key='diameter',
                unit='units',
                readonly=False,
                formula=r'd = 2r'
            ),
            'circumference': ShapeProperty(
                name='Circumference',
                key='circumference',
                unit='units',
                readonly=False,
                formula=r'C = 2\pi r = \pi d'
            ),
            'area': ShapeProperty(
                name='Area',
                key='area',
                unit='units²',
                readonly=False,
                formula=r'A = \pi r^2 = \frac{\pi d^2}{4}'
            ),
            'central_angle_deg': ShapeProperty(
                name='Central Angle',
                key='central_angle_deg',
                unit='°',
                readonly=False,
                precision=2,
                formula=r'\theta \text{ (in degrees)}'
            ),
            'arc_length': ShapeProperty(
                name='Arc Length',
                key='arc_length',
                unit='units',
                readonly=False,
                formula=r's = r\theta = \frac{\pi r \theta}{180°}'
            ),
            'chord_length': ShapeProperty(
                name='Chord Length',
                key='chord_length',
                unit='units',
                readonly=False,
                formula=r'c = 2r\sin\left(\frac{\theta}{2}\right)'
            ),
            'sagitta': ShapeProperty(
                name='Sagitta (Chord Height)',
                key='sagitta',
                unit='units',
                readonly=False,
                formula=r'h = r\left(1 - \cos\left(\frac{\theta}{2}\right)\right)'
            ),
            'sector_area': ShapeProperty(
                name='Sector Area',
                key='sector_area',
                unit='units²',
                readonly=True,
                formula=r'A_{sector} = \frac{\pi r^2 \theta}{360°} = \frac{r^2\theta}{2}'
            ),
            'segment_area': ShapeProperty(
                name='Segment Area',
                key='segment_area',
                unit='units²',
                readonly=True,
                formula=r'A_{segment} = \frac{r^2}{2}(\theta - \sin\theta)'
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
        """
        Compute all circle properties from radius.

        CIRCLE DERIVATIONS:
        ===================

        Definition:
        -----------
        A circle is the set of all points in a plane equidistant from a center point.
        Distance from center to any point on circle = radius r.

        **Diameter**: d = 2r
        The longest chord passing through the center.

        **Circumference**: C = 2πr = πd
        
        Derivation:
        - Arc length for full circle (θ = 2π): s = rθ = r(2π) = 2πr
        - Alternatively: limit of perimeter of inscribed regular n-gons as n→∞
        - π ≈ 3.14159265359... (Ludolph's number, Archimedes' constant)

        **Area**: A = πr²
        
        Derivation Method 1 (Integration):
        - Polar coordinates: A = ∫∫ r dr dθ
        - A = ∫₀²π ∫₀ʳ r' dr' dθ = ∫₀²π [r'²/2]₀ʳ dθ = ∫₀²π r²/2 dθ = πr²

        Derivation Method 2 (Limit of Polygons):
        - Regular n-gon with circumradius r: A_n = (n/2)r²sin(2π/n)
        - lim(n→∞) A_n = lim(n→∞) (n/2)r²sin(2π/n)
        - Using lim(x→0) sin(x)/x = 1: = πr²

        Derivation Method 3 (Infinitesimal Rings):
        - Divide circle into concentric rings of width dr
        - Ring at radius r' has circumference 2πr', area dA = 2πr'·dr
        - A = ∫₀ʳ 2πr' dr' = 2π[r'²/2]₀ʳ = πr²

        HERMETIC NOTE - THE PERFECT FORM:
        ==================================
        The circle represents **UNITY**, **ETERNITY**, **THE DIVINE**:

        - **No beginning, no end**: Infinite rotational symmetry
        - **All points equal**: Perfect democracy of form
        - **π transcendental**: Cannot be expressed as ratio (divine irrationality)
        - **Sphere in 2D**: Projection of celestial perfection

        In Sacred Traditions:
        - **Sun/Moon**: Circle as symbol of celestial bodies
        - **Wheel of Dharma**: Eternal cycle, no attachment to form
        - **Ouroboros**: Serpent eating tail, unity of beginning/end
        - **Mandala**: Circle as container of sacred space
        - **Halo**: Divine radiance, perfection of saints

        π Appears Throughout Creation:
        - Orbital periods (Kepler's laws involve π)
        - Wave phenomena (sin/cos = circular motion projected)
        - Probability (Gaussian distribution involves π)
        - Quantum mechanics (angular momentum quantization)
        """
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
        """
        Compute chord, arc, sector, and segment properties.

        CIRCLE SEGMENT DERIVATIONS:
        ===========================

        **Arc Length**: s = rθ (θ in radians)
        
        Derivation:
        - Definition of radian: angle subtended by arc of length r
        - For angle θ: arc length = (θ/2π) × circumference = (θ/2π) × 2πr = rθ

        **Chord Length**: c = 2r·sin(θ/2)
        
        Derivation:
        - Drop perpendicular from center to chord midpoint
        - Forms right triangle: hypotenuse = r, opposite = c/2, angle = θ/2
        - sin(θ/2) = (c/2)/r → c = 2r·sin(θ/2)

        **Sagitta** (Versine, Chord Height): h = r(1 - cos(θ/2))
        
        Derivation:
        - Same right triangle: adjacent side = r - h
        - cos(θ/2) = (r-h)/r → r·cos(θ/2) = r - h → h = r(1 - cos(θ/2))
        - Alternative form: h = r·vers(θ/2) where vers(α) = 1 - cos(α)

        **Sector Area**: A_sector = (1/2)r²θ
        
        Derivation Method 1 (Proportion):
        - Sector is fraction of full circle: A_sector/A_circle = θ/2π
        - A_sector = (θ/2π)·πr² = (1/2)r²θ

        Derivation Method 2 (Integration):
        - Polar coordinates: A = (1/2)∫r² dθ = (1/2)r²∫₀θ dθ' = (1/2)r²θ

        **Segment Area**: A_segment = (1/2)r²(θ - sin(θ))
        
        Derivation:
        - Segment = Sector - Triangle
        - Triangle area = (1/2) × base × height = (1/2) × c × (r·cos(θ/2))
        - Using c = 2r·sin(θ/2): A_tri = (1/2)·2r·sin(θ/2)·r·cos(θ/2)
        - = r²·sin(θ/2)·cos(θ/2) = (r²/2)·sin(θ) [using sin(2α) = 2sin(α)cos(α)]
        - A_segment = (1/2)r²θ - (1/2)r²·sin(θ) = (1/2)r²(θ - sin(θ))

        HERMETIC NOTE - THE LUNAR CRESCENT:
        ====================================
        Circle segments represent **PHASES**, **GROWTH**, **WAXING/WANING**:

        - **Crescent Moon**: Segment as symbol of lunar phases
        - **Sagitta**: The "arrow" piercing the firmament
        - **Chord**: Bridge between two points on the eternal circle
        - **Sector**: Pie-slice of cosmic territory

        In Architecture:
        - **Arches**: Circular segments support structures
        - **Gothic Windows**: Pointed arches from overlapping circles
        - **Domes**: Segments rotated to create 3D space

        In Cosmology:
        - **Eclipses**: Shadow as circle segment
        - **Moon Phases**: Illuminated portion = variable segment
        - **Horizon**: Circle segment visible from any point on Earth
        """
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
