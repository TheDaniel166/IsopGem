"""Ellipse (oval) shape calculator.

An ellipse is a conic section—the locus of points where the sum of distances to two
fixed points (foci) is constant. It is the most general form of a closed conic curve,
reducing to a circle when both foci coincide. Ellipses describe planetary orbits
(Kepler's First Law) and appear throughout physics, astronomy, and optics.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Eccentricity (From Circle to Line)
═══════════════════════════════════════════════════════════════════════════════════════

An ellipse is defined by two semi-axes:
• **Semi-major axis** a (half the longest diameter)
• **Semi-minor axis** b (half the shortest diameter), where a ≥ b

The **eccentricity** e measures how "stretched" the ellipse is:

  e = √(1 - b²/a²) = c/a

  where c = √(a² - b²) is the **focal distance** (center to focus)

**Eccentricity spectrum**:
• e = 0: Circle (b = a, foci coincide at center)
• 0 < e < 1: Ellipse (planetary orbits)
• e = 1: Parabola (escape trajectory, comet on one-time pass)
• e > 1: Hyperbola (interstellar object passing through solar system)

As e → 1 (b → 0), the ellipse becomes increasingly "needle-like," approaching a line
segment of length 2a.

**Defining property** (two-focus definition):
For any point P on the ellipse, if F₁ and F₂ are the foci:

  |PF₁| + |PF₂| = 2a    (constant sum)

This is the **gardener's ellipse** construction: tie a string of length 2a to two stakes
(foci), pull taut with a pencil, and trace the curve!

**Cartesian equation** (centered at origin, axes aligned):

  x²/a² + y²/b² = 1

**Parametric form**:
  x = a·cos(t),  y = b·sin(t),  t ∈ [0, 2π]

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Kepler's Planetary Orbits (Celestial Mechanics)
═══════════════════════════════════════════════════════════════════════════════════════

**Kepler's First Law** (1609): Planets orbit the Sun in elliptical paths, with the Sun
at one focus (the other focus is empty space).

Before Kepler:
• Aristotle/Ptolemy: Circular orbits with epicycles (circles upon circles)
• Copernicus: Heliocentric circles (still assumed perfect circles)
• Kepler realized: Mars's orbit is NOT a circle—it's an ellipse! (e ≈ 0.0934 for Mars)

This shattered the ancient dogma that celestial motion must be perfectly circular
(divine perfection = circles). The cosmos is elliptical!

**Orbital elements**:
• **Perihelion**: Closest approach to Sun = a(1-e)
• **Aphelion**: Farthest from Sun = a(1+e)
• **Semi-major axis** a determines orbital period via Kepler's Third Law:
    T² ∝ a³    (period squared proportional to semi-major axis cubed)

**Examples**:
• Earth: e = 0.0167 (nearly circular!)
• Mercury: e = 0.2056 (most eccentric planet)
• Pluto: e = 0.2488 (highly elliptical, crosses Neptune's orbit)
• Halley's Comet: e = 0.967 (very elongated, perihelion inside Venus, aphelion beyond Neptune)

**Why ellipses?** Newton's law of gravitation (F ∝ 1/r²) + conservation of energy/momentum
→ orbits are conic sections (ellipse, parabola, hyperbola depending on total energy).
Bound orbits (negative energy) → ellipses.

**Reflective property**: Light/sound emanating from one focus reflects off the ellipse
and converges to the other focus. This is used in:
• Whispering galleries (elliptical domes)
• Lithotripsy (kidney stone treatment: shock wave from one focus breaks stone at other)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: The Perimeter Problem (No Closed-Form Formula!)
═══════════════════════════════════════════════════════════════════════════════════════

**Area**: Simple! A = πab (generalization of πr² for circle when a=b=r)

**Perimeter**: No elementary closed-form formula exists!

The exact perimeter involves an **elliptic integral** (hence the name):

  P = 4a ∫₀^(π/2) √(1 - e²sin²θ) dθ    (complete elliptic integral of 2nd kind)

This cannot be expressed using elementary functions (polynomials, trig, exp, log).

**Approximations** (many exist, none exact!):

1) **Ramanujan's approximation** (1914):

  P ≈ π[3(a+b) - √((3a+b)(a+3b))]

  This is accurate to within ~0.5% for most ellipses!

2) **Infinite series** (exact but never terminates):

  P = 2πa · [1 - (1/2)²e² - (1·3/2·4)²(e⁴/3) - (1·3·5/2·4·6)²(e⁶/5) - ...]

3) **Limit cases**:
  • Circle (a=b): P = 2πa (exact!)
  • Line (b→0): P → 4a (approaches perimeter of degenerate "line segment" traversed twice)

**Why is this hard?** The arc length integral ds = √(dx²+dy²) for the ellipse leads to:

  ds = √((a²sin²t + b²cos²t)) dt    (no elementary antiderivative!)

This is a fundamental limitation—ellipses are "transcendental" in a deeper sense than
just containing π. Computing their perimeter requires infinite series or numerical
integration.

**Historical note**: This problem motivated the development of elliptic functions and
elliptic integrals in 18th-19th century (Euler, Legendre, Jacobi, Abel). These special
functions are now fundamental in number theory, cryptography, and string theory!

═══════════════════════════════════════════════════════════════════════════════════════
🪐 HERMETIC SIGNIFICANCE 🪐
═══════════════════════════════════════════════════════════════════════════════════════

The ellipse embodies **Duality, Balance, and Imperfect Perfection**:

• **Two Foci** (vs. One Center): The ellipse has TWO centers of attention, not one.
  This represents duality: masculine/feminine, heaven/earth, spirit/matter. The circle
  is monadic unity; the ellipse is dyadic relationship.

• **The Cosmic Egg**: Many creation myths describe the universe as born from an egg
  (Orphic Egg, Brahmanda, World Egg). The ellipse/ovoid is the primordial form—not
  perfectly spherical (which would be static) but slightly elongated (implying motion,
  potential, becoming).

• **Planetary Orbits as Divine Imperfection**: Kepler's discovery that orbits are
  elliptical was initially shocking—the heavens were supposed to be PERFECT (circles).
  But ellipses reveal a deeper truth: the cosmos is dynamic, not static. Eccentricity
  is not error—it's design. The ellipse is the geometry of *perpetual motion toward
  a center that is never reached* (the Sun at one focus, the empty focus as unrealized
  potential).

• **Stretched Circle**: The ellipse is what happens when circular perfection is
  subjected to a FORCE (stretching, gravity, perspective). It represents the descent
  of the ideal (circle) into manifestation (ellipse). In Neoplatonism, the One
  emanates into the Many—the circle becomes ellipse, then parabola, then hyperbola
  (increasingly open, less bound).

• **Fertility and Growth**: The egg shape (ovoid, slightly tapered ellipse) is the
  universal symbol of fertility, new life, potential. The ellipse contains the future
  (the as-yet-unhatched).

The ellipse teaches: **Perfection in motion is not static symmetry—it is dynamic balance
between two poles.** 🪐

═══════════════════════════════════════════════════════════════════════════════════════
"""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class EllipseShapeService:
    """Builds drawing instructions for ellipses (no calculations)."""

    @staticmethod
    def build(a: float, b: float) -> Dict:
        """
        Generate drawing instructions for an ellipse.

        Args:
            a: Semi-major axis
            b: Semi-minor axis

        Returns:
            DrawingInstructions dict
        """
        if not a or not b or a <= 0 or b <= 0:
            return {'type': 'empty'}

        points = EllipseShapeService._ellipse_points(a, b)
        axis_lines = [
            ((-a, 0), (a, 0)),
            ((0, -b), (0, b)),
        ]

        return {
            'type': 'polygon',
            'points': points,
            'axis_lines': axis_lines,
        }

    @staticmethod
    def _ellipse_points(a: float, b: float, steps: int = 180) -> List[Tuple[float, float]]:
        points: List[Tuple[float, float]] = []
        for i in range(steps):
            theta = 2 * math.pi * (i / steps)
            x = a * math.cos(theta)
            y = b * math.sin(theta)
            points.append((x, y))
        return points

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _reconcile_axes(self):
        """
        Compute all ellipse properties from semi-major and semi-minor axes.

        ELLIPSE DERIVATIONS:
        ====================

        Definition:
        -----------
        An ellipse is the locus of points where the sum of distances to two
        fixed points (foci) is constant.

        d₁ + d₂ = 2a (constant)

        **Parametric Form**:
        x(θ) = a·cos(θ)
        y(θ) = b·sin(θ)

        Where:
        - a: semi-major axis (half of longest diameter)
        - b: semi-minor axis (half of shortest diameter)
        - θ ∈ [0, 2π]: parametric angle (not polar angle!)

        **Area**: A = πab

        Derivation Method 1 (Scaling):
        - Circle of radius a has area πa²
        - Ellipse = circle scaled by factor b/a in one direction
        - A = πa² × (b/a) = πab ✓

        Derivation Method 2 (Integration):
        - Cartesian: (x/a)² + (y/b)² = 1 → y = b√(1 - x²/a²)
        - A = 4∫₀ᵃ b√(1 - x²/a²) dx
        - Substitution u = x/a: A = 4b∫₀¹ a√(1-u²) du = 4ab × π/4 = πab ✓

        Derivation Method 3 (Jacobian Transform):
        - From circle r = 1 via transform (x,y) = (ar cos θ, br sin θ)
        - Jacobian |J| = ab
        - A = ∫∫ ab dr dθ = ab·π ✓

        **Perimeter** (Ramanujan's Approximation):
        P ≈ π(a + b)[1 + 3h/(10 + √(4-3h))]
        where h = (a-b)²/(a+b)²

        Exact perimeter requires elliptic integral:
        P = 4a·E(e)
        where E(e) is complete elliptic integral of 2nd kind, e = eccentricity

        Ramanujan's formula is accurate to ~10⁻⁸ for all ellipses.

        **Eccentricity**: e = √(1 - b²/a²)

        Derivation:
        - Foci located at (±c, 0) where c² = a² - b²
        - Definition: e = c/a = √(a² - b²)/a = √(1 - b²/a²)
        - Range: 0 ≤ e < 1
          • e = 0: circle (b = a)
          • e → 1: highly elongated ellipse (b → 0)

        **Focal Distance**: c = √(a² - b²)

        Distance from center to each focus.
        For point (x,y) on ellipse:
        √[(x-c)² + y²] + √[(x+c)² + y²] = 2a (constant sum property)

        HERMETIC NOTE - THE COSMIC ELLIPSE:
        ====================================
        The ellipse represents **DIVINE PROPORTION IN MOTION**:

        - **Kepler's Discovery**: Planetary orbits are ellipses (not circles!)
        - **Two Foci**: Duality in unity (Sun at one focus, empty space at other)
        - **Eccentricity**: Deviation from perfect circle = incarnation into form
        - **Sum Constant**: Hidden perfection within apparent asymmetry

        In Sacred Traditions:
        - **Mandorla**: Almond-shaped aura around Christ/Buddha
        - **Vesica Piscis**: Intersection of circles forms ellipse-like lens
        - **Egg**: Primordial form, potential for new life
        - **Orbits**: Heavenly bodies trace ellipses (as above, so below)

        Kepler's Laws & Divine Harmony:
        - 1st Law: Elliptical orbits with Sun at focus
        - 2nd Law: Equal areas in equal times (conservation of angular momentum)
        - 3rd Law: T² ∝ a³ (period² ∝ semi-major axis³)

        The ellipse is the **circle in motion**, the **perfect form tilted**,
        the **eternal made temporal**. Where circle is unity, ellipse is duality;
        where circle is perfection, ellipse is perfection-in-process.

        Mathematical Properties:
        ------------------------
        1. **Conic Section**: Intersection of plane and cone (non-perpendicular)
        2. **Orthogonal Trajectories**: Confocal ellipses and hyperbolas
        3. **Optical Property**: Ray from one focus reflects to other focus
        4. **String Construction**: Loop of string around two pins traces ellipse
        5. **Affine Transform**: Any ellipse is affine image of unit circle

        In Nature & Technology:
        • **Planetary Orbits**: All planets, comets, asteroids
        • **Whispering Galleries**: Sound focus property (St. Paul's Cathedral)
        • **Elliptical Gears**: Non-circular rotation
        • **Medical**: Kidney stones broken by lithotripsy (dual focus property)

        References:
        -----------
        [1] Kepler, J. (1609). Astronomia Nova. (First elliptical orbit law)
        [2] Ramanujan, S. (1914). "Modular Equations and Approximations to π"
        [3] do Carmo, M. (1976). Differential Geometry of Curves and Surfaces.
        [4] Hilbert & Cohn-Vossen (1952). Geometry and the Imagination.
        """
        a = self.properties['semi_major_axis'].value
        b = self.properties['semi_minor_axis'].value
        if a is None and b is None:
            self._clear_dependents(reset_axes=False)
            return

        if a is None:
            a = b
        if b is None:
            b = a
        if a is None or b is None:
            self._clear_dependents(reset_axes=False)
            if a is not None:
                self.properties['semi_major_axis'].value = a
                self.properties['major_axis'].value = 2 * a
            if b is not None:
                self.properties['semi_minor_axis'].value = b
                self.properties['minor_axis'].value = 2 * b
            return

        if a < b:
            a, b = b, a
        if b <= 0:
            return

        self.properties['semi_major_axis'].value = a
        self.properties['semi_minor_axis'].value = b
        self.properties['major_axis'].value = 2 * a
        self.properties['minor_axis'].value = 2 * b

        area = math.pi * a * b
        self.properties['area'].value = area

        try:
            ecc = math.sqrt(1 - (b * b) / (a * a)) if a > 0 else 0
        except ValueError:
            ecc = 0
        self.properties['eccentricity'].value = ecc
        self.properties['focal_distance'].value = math.sqrt(max(a * a - b * b, 0.0))

        if (a + b) > 0:
            h = ((a - b) ** 2) / ((a + b) ** 2)
            perimeter = math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))
            self.properties['perimeter'].value = perimeter
        else:
            self.properties['perimeter'].value = None

    def _clear_dependents(self, reset_axes: bool = True):
        axis_keys = ('major_axis', 'minor_axis') if reset_axes else ()
        for key in (*axis_keys, 'area', 'perimeter', 'eccentricity', 'focal_distance'):
            self.properties[key].value = None

    @staticmethod
    def _ellipse_points(a: float, b: float, steps: int = 180) -> List[Tuple[float, float]]:
        points: List[Tuple[float, float]] = []
        for i in range(steps):
            theta = 2 * math.pi * (i / steps)
            x = a * math.cos(theta)
            y = b * math.sin(theta)
            points.append((x, y))
        return points