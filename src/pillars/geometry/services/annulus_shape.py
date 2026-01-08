"""Annulus (ring) shape calculator.

An annulus is a ring-shaped region bounded by two concentric circles—a "circle with
a hole." It is the 2D analog of a spherical shell or hollow cylinder. The annulus
appears in washer method integration (calculus), planetary ring systems, and mechanical
engineering (pipes, bearings, washers).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Area as Difference (The Subtraction Principle)
═══════════════════════════════════════════════════════════════════════════════════════

Given outer radius R and inner radius r (where R > r):

  Area = πR² - πr² = π(R² - r²)

This factors beautifully:

  A = π(R - r)(R + r) = πw·d_avg

  where:
    w = R - r    (ring width)
    d_avg = R + r    (average of inner and outer diameters... wait, that's not quite right!)

Actually, let's rewrite more carefully:

  A = π(R + r)(R - r) = 2π·((R+r)/2)·(R-r) = C_avg × w

  where:
    C_avg = 2π(R+r)/2 = π(R+r)    (average circumference)
    w = R - r    (width)

So: **Annulus area = average circumference × width**

This is intuitive: imagine "unrolling" the ring into a rectangular strip of height w
and length C_avg!

**Special case** (thin ring, R ≈ r):
  A ≈ 2πR·w    (circumference × width, like a ribbon)

This is the basis for **differential area** in polar coordinates:
  dA = r·dθ·dr    (infinitesimal annulus sector)

**Comparison to circle**:
• Circle: A = πR² (all interior space)
• Annulus: A = π(R²-r²) (exterior minus interior)
• Fraction filled: f = (R²-r²)/R² = 1 - (r/R)²

As r→0: Annulus → full circle (100% filled)
As r→R: Annulus → thin ring (area → 0)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Washer Method (Calculus of Volumes of Revolution)
═══════════════════════════════════════════════════════════════════════════════════════

The annulus is the cross-sectional "washer" used in calculus to compute volumes of
solids of revolution with HOLES.

**Disk method** (solid of revolution, no hole):
Rotate y = f(x) around x-axis:
  V = ∫ π[f(x)]² dx    (sum of circular disks)

**Washer method** (hollow solid):
Rotate region between y = f(x) (outer) and y = g(x) (inner) around x-axis:

  V = ∫ π([f(x)]² - [g(x)]²) dx = ∫ π(R² - r²) dx

  where R = f(x), r = g(x)

Each infinitesimal slice is an ANNULUS of area π(R² - r²) and thickness dx!

**Example**: Find volume of a torus (donut) with major radius R and minor radius a:
• Cross-section at distance x from center: annulus with R_outer = R + √(a²-x²),
  R_inner = R - √(a²-x²)
• Integrate from -a to a
• Result: V = 2π²Ra² (Pappus's theorem!)

**Shell method** (alternative):
Rotate around axis parallel to the curve:
  V = ∫ 2πx·h(x) dx    (sum of cylindrical shells)

Both methods use the annulus as fundamental building block—one as area (washer), one
as circumference (shell).

**Physical applications**:
• Hollow cylinder: V = π(R²-r²)h (annular base × height)
• Pipe wall: thickness t = R - r, volume ≈ 2πR·t·L (for thin walls)
• Heat conduction through cylindrical shells (insulation, pipes)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Planetary Rings and the Roche Limit
═══════════════════════════════════════════════════════════════════════════════════════

Planetary ring systems (Saturn, Jupiter, Uranus, Neptune) are ANNULAR structures:
• Inner edge: where particles orbit too close (fall into planet)
• Outer edge: where particles are too far (escape or form moons)
• The ring: stable annular zone between these limits

**Roche limit**: The distance d below which a moon/object will be torn apart by tidal
forces:

  d ≈ 2.44 R (M_planet / M_moon)^(1/3)

  where R = planet radius

For Saturn's rings:
• Inner edge (D ring): ~67,000 km from Saturn's center
• Outer edge (E ring): ~480,000 km
• Roche limit for ice: ~150,000 km (main rings lie inside this!)

This means: **Saturn's rings are the remnants of moons that wandered too close and
were shredded by tidal forces.** The annular gap is not arbitrary—it's the zone where
coalescence into a moon is impossible (tidal forces > self-gravity).

**Ring structure**:
• **Cassini Division**: Large gap in Saturn's rings (4,700 km wide) caused by orbital
  resonance with moon Mimas (2:1 resonance clears out particles)
• **Shepherd moons**: Small moons (Prometheus, Pandora) that gravitationally "herd"
  ring particles, maintaining sharp edges

**Mathematical model**:
Ring as ensemble of annular streamlines, each with orbital velocity v = √(GM/r).
Inner particles orbit faster (Kepler's 3rd law) → differential rotation → shearing.

Annuli appear in:
• Accretion disks (black holes, protostars): material spiraling inward through nested
  annular zones
• Tree rings: each annulus = one year of growth (dendrochronology)
• Bearings, washers, seals: engineering components with annular cross-sections

═══════════════════════════════════════════════════════════════════════════════════════
📍 HERMETIC SIGNIFICANCE 📍
═══════════════════════════════════════════════════════════════════════════════════════

The annulus embodies **Boundaries, Thresholds, and the Liminal Space**:

• **The Ring as Boundary**: The annulus defines an INSIDE (r < r_inner: the void) and
  an OUTSIDE (r > R_outer: the beyond), with the ring itself as the LIMINAL ZONE—the
  walkable path, the habitable margin. This is the geometry of *walls*, *moats*,
  *protective circles* (ring of salt, circle of standing stones).

• **Halo and Aureole**: In religious art, saints and deities are depicted with halos
  (annular rings of light). The halo marks the THRESHOLD between mortal and divine—
  the sacred radiation zone. The annulus separates the profane (outside) from the holy
  (inside, the saint's head/heart).

• **The Ouroboros Loop**: When the annulus is very thin (r ≈ R), it becomes a circular
  loop—the serpent eating its tail. But even as a loop, it has THICKNESS (the snake's
  body). The annulus is the "fattened circle," the serpent made corporeal.

• **Wedding Ring**: The ring as symbol of eternal bond (circle) but with an OPENING
  (the hole)—it encircles (encloses, protects) but also allows passage (the finger
  goes through). The annulus is *embrace* and *release* simultaneously. The hole is
  not absence—it's the space for the beloved.

• **Tree Rings and Time**: Each annulus in a tree trunk = one year of growth. The
  annular structure RECORDS TIME as nested layers. The void at center (pith) is the
  seed origin; the outermost ring is the present. The annulus maps *temporal distance
  from the origin* (like geological strata, archaeological tells).

• **Mandala Rings**: Tibetan mandalas often have concentric annular zones representing
  layers of consciousness or stages of spiritual attainment. The void at center is
  śūnyatā (emptiness); the rings are progressively denser manifestations.

The annulus teaches: **The sacred space is not solid—it is the ring around the void.** 📍

═══════════════════════════════════════════════════════════════════════════════════════
"""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class AnnulusShape(GeometricShape):
    """Represents a circular ring defined by outer and inner radii."""

    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Annulus"

    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "Ring-shaped object, a region bounded by two concentric circles"

    @property
    def calculation_hint(self) -> str:
        """
        Calculation hint logic.
        
        Returns:
            Result of calculation_hint operation.
        """
        return "Enter Outer Radius (R) + Inner Radius (r)"

    def _init_properties(self):
        self.properties = {
            "outer_radius": ShapeProperty(
                name="Outer Radius (R)",
                key="outer_radius",
                unit="units",
                formula=r'R'
            ),
            "inner_radius": ShapeProperty(
                name="Inner Radius (r)",
                key="inner_radius",
                unit="units",
                formula=r'r'
            ),
            "ring_width": ShapeProperty(
                name="Ring Width (R - r)",
                key="ring_width",
                unit="units",
                formula=r'w = R - r'
            ),
            "outer_diameter": ShapeProperty(
                name="Outer Diameter",
                key="outer_diameter",
                unit="units",
                formula=r'D = 2R'
            ),
            "inner_diameter": ShapeProperty(
                name="Inner Diameter",
                key="inner_diameter",
                unit="units",
                formula=r'd = 2r'
            ),
            "area": ShapeProperty(
                name="Ring Area",
                key="area",
                unit="units²",
                readonly=True,
                formula=r'A = \pi(R^2 - r^2)'
            ),
            "outer_circumference": ShapeProperty(
                name="Outer Circumference",
                key="outer_circumference",
                unit="units",
                readonly=True,
                formula=r'C_{outer} = 2\pi R'
            ),
            "inner_circumference": ShapeProperty(
                name="Inner Circumference",
                key="inner_circumference",
                unit="units",
                readonly=True,
                formula=r'C_{inner} = 2\pi r'
            ),
            "radius_ratio": ShapeProperty(
                name="Radius Ratio (R / r)",
                key="radius_ratio",
                readonly=True,
                precision=4,
                formula=r'\rho = \frac{R}{r}'
            ),
        }

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """
        Compute from property logic.
        
        Args:
            property_key: Description of property_key.
            value: Description of value.
        
        Returns:
            Result of calculate_from_property operation.
        """
        if value <= 0:
            return False

        if property_key == "outer_radius":
            inner = self.properties["inner_radius"].value
            if inner is not None and value <= inner:
                return False
            self.properties["outer_radius"].value = value
            self._update_metrics()
            return True

        if property_key == "inner_radius":
            outer = self.properties["outer_radius"].value
            if outer is not None and value >= outer:
                return False
            self.properties["inner_radius"].value = value
            self._update_metrics()
            return True

        if property_key == "ring_width":
            return self._apply_ring_width(value)

        if property_key == "outer_diameter":
            return self.calculate_from_property("outer_radius", value / 2)

        if property_key == "inner_diameter":
            return self.calculate_from_property("inner_radius", value / 2)

        return False

    def _apply_ring_width(self, width: float) -> bool:
        if width <= 0:
            return False
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        if outer is not None:
            new_inner = outer - width
            if new_inner <= 0 or new_inner >= outer:
                return False
            self.properties["inner_radius"].value = new_inner
            self._update_metrics()
            return True
        if inner is not None:
            new_outer = inner + width
            if new_outer <= inner:
                return False
            self.properties["outer_radius"].value = new_outer
            self._update_metrics()
            return True
        return False

    def _update_metrics(self):
        """
        Compute all annulus (ring) properties.

        ANNULUS DERIVATIONS:
        ====================

        Definition:
        -----------
        An annulus is the region between two concentric circles.

        **Ring Width**: w = R - r
        The radial distance between outer and inner circles.

        **Area**: A = π(R² - r²) = π(R + r)(R - r)

        Derivation Method 1 (Subtraction):
        - Outer circle area: A_outer = πR²
        - Inner circle area: A_inner = πr²
        - Ring area: A = A_outer - A_inner = π(R² - r²) ✓

        Derivation Method 2 (Integration):
        - Polar coordinates: A = ∫∫ ρ dρ dθ
        - A = ∫₀²π ∫ᵣᴿ ρ dρ dθ = ∫₀²π [ρ²/2]ᵣᴿ dθ
        - = ∫₀²π (R² - r²)/2 dθ = 2π(R² - r²)/2 = π(R² - r²) ✓

        Derivation Method 3 (Average Circumference):
        - Average radius: r_avg = (R + r)/2
        - Average circumference: C_avg = 2π·r_avg = π(R + r)
        - Ring width: w = R - r
        - Approximate area: A ≈ C_avg × w = π(R + r)(R - r) ✓
        (This becomes exact in the limit, derived from Pappus's theorem)

        **Factored Form**: A = πw(2r + w)
        Where w = R - r, so R = r + w:
        A = π[(r + w)² - r²] = π[r² + 2rw + w² - r²] = π(2rw + w²) = πw(2r + w)

        **Radius Ratio**: ρ = R/r
        - ρ > 1 always (R > r by definition)
        - ρ → 1: thin ring (R ≈ r)
        - ρ → ∞: ring approaches full disk

        HERMETIC NOTE - THE ETERNAL RING:
        ==================================
        The annulus represents **BOUNDARIES**, **LIMITS**, **CONTAINMENT**:

        - **Two Circles**: Inner and outer worlds, microcosm and macrocosm
        - **Ring**: Symbol of commitment, eternal bond, no beginning/end
        - **Moat**: Protection, sacred boundary between realms
        - **Orbit**: Path of celestial body around empty center

        In Sacred Traditions:
        - **Halo**: Ring of light around divine figures
        - **Mandala Rings**: Concentric circles defining sacred zones
        - **Wedding Ring**: Eternal love, unbroken circle
        - **Saturn's Rings**: Celestial annulus, cosmic boundary

        The annulus is the **circle made dual**, the **void surrounded by form**,
        the **empty center that defines the whole**. It represents the tension
        between inner and outer, the **space of transformation** between two states.

        In Architecture & Art:
        - **Colosseum**: Elliptical annulus for spectators
        - **Ring Forts**: Defensive circular earthworks
        - **Zen Ensō**: Brushstroke circle (often incomplete annulus)
        - **Target/Bullseye**: Concentric rings defining zones

        Mathematical Properties:
        ------------------------
        1. **Rotational Symmetry**: Infinite rotations leave it unchanged
        2. **Moment of Inertia**: I = (π/2)m(R² + r²) for uniform disk
        3. **Centroid**: Remains at geometric center (0,0)
        4. **Polar Second Moment**: J = (π/2)(R⁴ - r⁴)

        In Physics & Engineering:
        • **Washers**: Mechanical spacers and load distributors
        • **Bearings**: Ball bearings roll in annular tracks
        • **Toroids**: 3D revolution of annulus
        • **Accretion Disks**: Matter spiraling into black hole/star
        """
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value

        # Outer dependent values
        if outer is not None:
            self.properties["outer_diameter"].value = outer * 2
            self.properties["outer_circumference"].value = 2 * math.pi * outer
        else:
            self.properties["outer_diameter"].value = None
            self.properties["outer_circumference"].value = None

        # Inner dependent values
        if inner is not None:
            self.properties["inner_diameter"].value = inner * 2
            self.properties["inner_circumference"].value = 2 * math.pi * inner
        else:
            self.properties["inner_diameter"].value = None
            self.properties["inner_circumference"].value = None

        if outer is None or inner is None or inner <= 0 or outer <= inner:
            self.properties["ring_width"].value = None
            self.properties["area"].value = None
            self.properties["radius_ratio"].value = None
            return

        width = outer - inner
        self.properties["ring_width"].value = width
        self.properties["area"].value = math.pi * (outer * outer - inner * inner)
        self.properties["radius_ratio"].value = outer / inner if inner else None

    def get_drawing_instructions(self) -> Dict:
        """
        Retrieve drawing instructions logic.
        
        Returns:
            Result of get_drawing_instructions operation.
        """
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        if outer is None:
            return {"type": "empty"}

        primitives = [
            {
                "shape": "circle",
                "center": (0.0, 0.0),
                "radius": outer,
                "pen": {"color": (14, 165, 233, 255), "width": 2.4},
                "brush": {"color": (191, 219, 254, 120)},
            }
        ]
        if inner is not None and inner > 0:
            primitives.append(
                {
                    "shape": "circle",
                    "center": (0.0, 0.0),
                    "radius": inner,
                    "pen": {"color": (15, 23, 42, 180), "width": 1.8},
                    "brush": {"color": (248, 250, 252, 255)},
                }
            )

        return {
            "type": "composite",
            "primitives": primitives,
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """
        Retrieve label positions logic.
        
        Returns:
            Result of get_label_positions operation.
        """
        labels: List[Tuple[str, float, float]] = []
        outer = self.properties["outer_radius"].value
        inner = self.properties["inner_radius"].value
        if outer is None:
            return labels

        labels.append((self._fmt("R", outer), outer * 0.6, 0.05))

        if inner is not None and inner > 0:
            labels.append((self._fmt("r", inner), inner * 0.3, -0.2))

        width = self.properties["ring_width"].value
        if width is not None:
            labels.append((self._fmt("w", width), 0, outer + 0.2))

        area = self.properties["area"].value
        if area is not None:
            labels.append((self._fmt("A", area), 0, 0.2))

        ratio = self.properties["radius_ratio"].value
        if ratio is not None:
            labels.append((self._fmt("R/r", ratio), 0, -outer - 0.3))

        return labels

    @staticmethod
    def _fmt(symbol: str, value: float) -> str:
        return f"{symbol} = {value:.4f}".rstrip("0").rstrip(".")