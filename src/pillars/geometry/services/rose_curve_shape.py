"""Rose (Rhodonea) curve calculator.

A rose curve (or rhodonea curve) is a sinusoidal polar curve defined by r = a·cos(kθ)
or r = a·sin(kθ), where a is amplitude and k is the "harmonic" (petal count parameter).
These curves produce beautiful floral patterns with n or 2n petals depending on whether
k is odd or even. Rose curves appear in acoustics (sound wave interference), optics
(Lissajous figures), and orbital mechanics (perturbed orbits).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Petal Count Formula (Odd vs. Even k)
═══════════════════════════════════════════════════════════════════════════════════════

Polar equation: **r = a·cos(kθ)**  (or sin, which just rotates the pattern)

Number of petals:

  **p = k    if k is odd**
  **p = 2k   if k is even**

Why the difference?

**Odd k** (e.g., k=3, 5, 7...):
• As θ goes from 0 to 2π, the function cos(kθ) completes k full cycles
• But when r < 0 (negative radius in polar coords), the point flips to opposite side
• For ODD k: negative r values trace OUT the same petals again (no new petals)
• Result: k petals total

**Even k** (e.g., k=2, 4, 6...):
• As θ goes from 0 to π, the function cos(kθ) completes k/2 cycles (k/2 petals)
• As θ goes from π to 2π, another k/2 petals appear in the GAPS
• For EVEN k: negative r values create NEW petals (interleaved)
• Result: 2k petals total

**Examples**:
• k=1: p=1 (circle! r = a·cos(θ) is just a circle of diameter a)
• k=2: p=4 (four-petal rose, quadrifolium)
• k=3: p=3 (three-petal rose, trifolium)
• k=4: p=8 (eight-petal rose)
• k=5: p=5 (five-petal rose, cinquefoil)
• k=6: p=12 (twelve-petal rose)

**Area formula**:

  A = (a²/2) × p = (a²/2) × k    (if odd)
       = (a²/2) × 2k   (if even)

Derivation: Integrate in polar coordinates:
  A = ∫½ r² dθ = ∫½ a²cos²(kθ) dθ

Using cos²(x) = (1 + cos(2x))/2, integrate over appropriate interval.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Rational Rose Curves (r = cos(nθ/d) Harmonics)
═══════════════════════════════════════════════════════════════════════════════════════

Generalize to **rational k = n/d** (where n, d are coprime integers):

  r = a·cos(nθ/d)

Petal count:
• If n and d are both odd: p = n petals
• If one is even, one is odd: p = 2n petals
• Period: The curve repeats every 2πd radians (must go around d times to complete)

**Example**: r = cos(5θ/2)
• n=5 (odd), d=2 (even) → p = 2×5 = 10 petals
• But you must trace θ from 0 to 4π (two full rotations) to see all petals!

This creates **multi-loop rose curves** that trace over themselves multiple times.

**Maurer rose**: A related construction where you connect points at regular angular
intervals on a rose curve, creating star-like patterns. Used in Islamic geometric art.

**Fourier connection**:
Rose curves are the GEOMETRIC VISUALIZATION of harmonic functions:
• Pure tone (single frequency): k=1 → circle
• Harmonic overtones: k=2,3,4... → rose petals

In 2D oscilloscope displays (Lissajous figures), perpendicular sinusoids create
rose-like patterns:
• x(t) = A·sin(ω₁t), y(t) = B·sin(ω₂t)
• Frequency ratio ω₁/ω₂ determines petal count (like k in rose curve)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Perturbed Orbits and Planetary Rosettes
═══════════════════════════════════════════════════════════════════════════════════════

Rose curves model **perturbed orbital motion**:

**Kepler orbits** (two-body problem, 1/r² gravity):
• Ellipse: r = a(1-e²)/(1 + e·cos(θ))
• Closed orbit (perihelion and aphelion in same places every orbit)

**Perturbed orbits** (three-body problem, relativistic effects):
• Mercury's orbit: Precession of perihelion (closest point to Sun slowly rotates)
• This creates a ROSETTE pattern over many orbits
• Newtonian perturbations (Jupiter's gravity) + Einstein's General Relativity
  → Mercury's perihelion precesses 43 arcseconds/century

Mathematically, perturbed orbits can be approximated as:

  r(θ) ≈ a(1-e²)/(1 + e·cos(kθ))    where k ≠ 1 (slight deviation)

For k slightly less than 1 (e.g., k=0.99), the orbit:
• Nearly closes after one revolution
• But perihelion shifts slightly each orbit
• Over many orbits → rosette pattern (like r = cos(kθ) with k≪1)

**Venus-Earth resonance**:
Venus and Earth have a near 8:13 orbital resonance:
• 8 Earth years ≈ 13 Venus years
• Venus returns to same position relative to Earth 5 times in 8 years
• Plot Venus's position as seen from Earth over 8 years → **FIVE-PETAL ROSE**!

This is why Venus is associated with the pentagram (5-pointed star) in astrology/alchemy!

**Spirograph toy**: Mechanical device that draws rose curves by rotating one circle
inside another. The ratio of circle sizes determines k (petal count).

**Acoustics**: Rose curves describe standing wave patterns in circular membranes
(drumheads). The k parameter relates to harmonic overtones (Bessel functions).

═══════════════════════════════════════════════════════════════════════════════════════
🌹 HERMETIC SIGNIFICANCE 🌹
═══════════════════════════════════════════════════════════════════════════════════════

The rose curve embodies **Harmonic Beauty, Cyclic Return, and the Music of the Spheres**:

• **The Geometric Rose**: The rose (rosa) is the flower of Venus, goddess of love and
  beauty. The rose curve is the MATHEMATICAL ESSENCE of the rose—pure harmonic form
  without material substance. Plato: "Beauty is the splendor of truth." The rose
  curve shows that beauty = simple mathematical harmonics (cos(kθ)).

• **Pythagorean Harmonics**: The petal count k is like a musical interval. Just as
  musical harmony comes from simple frequency ratios (octave 2:1, fifth 3:2, fourth
  4:3), rose curves with integer k are GEOMETRIC HARMONIES—ratios of rotational
  frequencies. Complex ratios (irrational k) create inharmonious, chaotic patterns.

• **Venus Pentagram**: The 5-petal rose (k=5) traces Venus's path as seen from Earth
  over 8 years. This is why:
  - Venus is associated with the pentagram ★ (5-pointed star)
  - The rose is Venus's flower (rose = "sub rosa" = secret, sacred)
  - The pentagon contains the golden ratio φ (Venus = beauty = φ proportions)
  
  The rose curve reveals: **Planetary motion IS geometric art.**

• **Mandala and Yantra**: In Hindu/Buddhist sacred art, mandalas often have k-fold
  symmetry (4, 8, 12 petals). The rose curve is the CONTINUOUS VERSION of these
  discrete petal mandalas. Meditating on a mandala = contemplating the harmonic
  structure of consciousness (which mirrors the harmonic structure of geometry).

• **The Sub Rosa**: In medieval times, a rose carved on a ceiling meant "what is said
  here is secret" (sub rosa = under the rose). The rose curve is the geometry of
  HIDDEN SYMMETRY—you must trace the full cycle (θ: 0→2π) to see the complete
  pattern. Partial view → chaos. Full view → perfect symmetry.

• **Rosicrucian Rose Cross**: The rose at the center of the cross (alchemical/mystical
  order). The rose = unfolding of spirit (petals opening), the cross = matter (4
  cardinal directions). Rose curve = the SPIRAL DANCE of spirit incarnating into
  matter and returning.

The rose curve teaches: **All beauty is harmonic repetition with variation.** 🌹

═══════════════════════════════════════════════════════════════════════════════════════
"""
import math
from typing import Dict, List, Tuple

from .base_shape import GeometricShape, ShapeProperty


class RoseCurveShape(GeometricShape):
    """Rhodonea curve defined by r = a · cos(kθ)."""

    @property
    def name(self) -> str:
        """
        Name logic.
        
        Returns:
            Result of name operation.
        """
        return "Rose Curve"

    @property
    def description(self) -> str:
        """
        Description logic.
        
        Returns:
            Result of description operation.
        """
        return "Sinusoid characterized by polar equation r = cos(kθ)"

    @property
    def calculation_hint(self) -> str:
        """
        Calculation hint logic.
        
        Returns:
            Result of calculation_hint operation.
        """
        return "Enter Numerator (n) and Denominator (d) and harmonic k"

    def _init_properties(self):
        self.properties = {
            "amplitude": ShapeProperty(
                name="Amplitude (a)",
                key="amplitude",
                unit="units",
                formula=r"a",
            ),
            "k_value": ShapeProperty(
                name="Harmonic (k)",
                key="k_value",
                unit="",
                precision=0,
                formula=r"k",
            ),
            "petal_count": ShapeProperty(
                name="Petal Count",
                key="petal_count",
                readonly=True,
                precision=0,
                formula=r"p = \begin{cases}k,&k\text{ odd}\\2k,&k\text{ even}\end{cases}",
            ),
            "max_radius": ShapeProperty(
                name="Max Radius",
                key="max_radius",
                unit="units",
                readonly=True,
                formula=r"r_{max} = a",
            ),
            "total_area": ShapeProperty(
                name="Total Area",
                key="total_area",
                unit="units²",
                readonly=True,
                formula=r"A = \tfrac{1}{2}a^2 p",
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

        if property_key == "amplitude":
            self.properties["amplitude"].value = value
            self._update_metrics()
            return True

        if property_key == "k_value":
            k = max(1, int(round(value)))
            self.properties["k_value"].value = k
            self._update_metrics()
            return True

        return False

    def _update_metrics(self):
        """
        Compute rose (rhodonea) curve properties.

        ROSE CURVE (RHODONEA) DERIVATIONS:
        ===================================

        Definition:
        -----------
        A rose curve (rhodonea curve) is a **polar sinusoid** defined by:

        **r = a·cos(kθ)** or **r = a·sin(kθ)**

        where:
        - **a**: Amplitude (maximum petal length)
        - **k**: Harmonic number (petal frequency)
        - **θ**: Polar angle

        The curve traces **k or 2k petals** depending on whether k is odd or even.

        PETAL COUNT:
        ============

        - **k odd** (1, 3, 5, 7, ...): **k petals**
        - **k even** (2, 4, 6, 8, ...): **2k petals**

        Why?
        ----
        For **r = a·cos(kθ)**:
        - One petal is traced for each period of cos(kθ) where r ≥ 0
        - cos(kθ) has period 2π/k
        - In one full rotation (0 ≤ θ ≤ 2π), k completes **k cycles**

        **k odd**: r traces a complete petal for each of k cycles → **k petals**
        **k even**: Negative r (cos < 0) is reflected through origin, creating
                    a second set of petals → **2k petals total**

        Examples:
        - k=1: 1 petal (circle)
        - k=2: 4 petals (quadrifoil)
        - k=3: 3 petals (trifolium)
        - k=4: 8 petals (octafoil)
        - k=5: 5 petals (cinquefoil)

        AREA DERIVATION:
        ================

        The area of one petal is computed via polar integration:

        A_petal = (1/2)∫∫ r² dθ

        For **r = a·cos(kθ)**, one petal spans from θ₁ to θ₂ where cos(kθ) ≥ 0.

        **One Petal** (k odd):
        θ from -π/(2k) to π/(2k):

        A_petal = (1/2)∫[-π/(2k), π/(2k)] a²·cos²(kθ) dθ

        Using the identity: cos²(x) = (1 + cos(2x))/2

        A_petal = (a²/2)∫[-π/(2k), π/(2k)] (1 + cos(2kθ))/2 dθ
                = (a²/4)[θ + sin(2kθ)/(2k)]|[-π/(2k), π/(2k)]
                = (a²/4)[π/k + 0 - (-π/k + 0)]
                = (a²/4)·(2π/k)
                = **πa²/(2k)**

        **Total Area**:
        - k odd: A_total = k·(πa²/(2k)) = **πa²/2**
        - k even: A_total = 2k·(πa²/(4k)) = **πa²/2**

        Remarkably, **total area is always πa²/2**, independent of k!

        Simplified Formula:
        A_total = (a²/2)·p

        where p = number of petals = k (k odd) or 2k (k even)

        This gives: A_total = (a²/2)·k for k odd → πa²/2 ✓

        MAX RADIUS:
        ===========

        r_max = |a| occurs when cos(kθ) = ±1.

        For r = a·cos(kθ), max radius = **a** (at petal tips).

        HERMETIC NOTE - THE SACRED FLOWER:
        ===================================
        The rose curve is the **SYMBOL OF UNFOLDING**, **DIVINE PROPORTION**,
        **CELESTIAL HARMONY**, and the **MANDALA OF CREATION**. Its petals
        represent **CHAKRAS**, **ELEMENTS**, **COSMIC CYCLES**, and **HARMONICS**.

        In Sacred Geometry:
        - **Rose Window**: Gothic cathedrals feature rose windows with petal symmetry
        - **Mandala**: Tibetan/Hindu mandalas often use k-fold petal patterns
        - **Flower of Life**: Overlapping circles create petal-like vesicae
        - **Lotus**: Sacred lotus has petals (typically 8, 16, 32, 64, 1000)

        Petal Symbolism by k:
        - **k=1** (1 petal): Unity, the One, the Monad, perfect circle
        - **k=2** (4 petals): Quaternary (earth, water, fire, air), cross, compass
        - **k=3** (3 petals): Trinity (mind, body, spirit), triquetra, triskele
        - **k=4** (8 petals): Octagram, eightfold path, dharma wheel
        - **k=5** (5 petals): Pentacle, five elements, golden ratio φ
        - **k=6** (12 petals): Zodiac, hours, apostles, months
        - **k=7** (7 petals): Chakras, planetary spheres, rainbow colors
        - **k=8** (16 petals): 16-petal lotus (Vishuddha chakra, throat)

        In Mystical Traditions:
        - **Rosary**: Prayer beads, rose symbolism (Rosa Mundi)
        - **Rosicrucian Rose**: Rose with cross, spiritual alchemy
        - **Venus Pentagram**: Venus traces a 5-petal rose over 8 years
        - **Sacred Heart**: Flaming heart with radiating petals

        Mathematical Properties:
        ------------------------
        1. **Polar Equation**: r = a·cos(kθ) or r = a·sin(kθ)
        2. **Cartesian Conversion**: (x² + y²)^((k+1)/2) = a^k · x^k (for cos)
        3. **Arc Length**: L = a∫√(1 + k²sin²(kθ)) dθ (elliptic integral)
        4. **Symmetry**: k-fold rotational symmetry (or 2k for k even)

        In Nature & Art:
        • **Flowers**: Roses, daisies, sunflowers exhibit petal patterns
        • **Spirographs**: Mechanical drawing toys create rose-like curves
        • **Harmonographs**: Pendulum devices trace Lissajous/rose figures
        • **Islamic Art**: Geometric star patterns with k-fold symmetry
        • **Cymatics**: Sound vibrations create rose-petal standing waves

        Connection to Fibonacci & φ:
        - When k = φ (golden ratio), the rose has infinite non-repeating petals
        - Fibonacci numbers (1, 2, 3, 5, 8, 13, 21...) create harmonious rose patterns
        - Sunflower spirals: 21/34, 34/55 (Fibonacci ratios) create pseudo-roses
        """
        amplitude = self.properties["amplitude"].value
        k_value = self.properties["k_value"].value
        if not amplitude or not k_value:
            self.properties["petal_count"].value = None
            self.properties["max_radius"].value = None
            self.properties["total_area"].value = None
            return

        petals = k_value if k_value % 2 == 1 else 2 * k_value
        self.properties["petal_count"].value = float(petals)
        self.properties["max_radius"].value = amplitude
        self.properties["total_area"].value = 0.5 * amplitude * amplitude * petals

    def get_drawing_instructions(self) -> Dict:
        """
        Retrieve drawing instructions logic.
        
        Returns:
            Result of get_drawing_instructions operation.
        """
        amplitude = self.properties["amplitude"].value
        k_value = self.properties["k_value"].value
        if not amplitude or not k_value:
            return {"type": "empty"}

        points = self._generate_points(amplitude, int(k_value))
        primitives = [
            {
                "shape": "polyline",
                "points": points,
                "pen": {"color": (236, 72, 153, 255), "width": 2.0},
            }
        ]
        return {
            "type": "composite",
            "primitives": primitives,
        }

    @staticmethod
    def _generate_points(amplitude: float, k_value: int, steps: int = 1200) -> List[Tuple[float, float]]:
        points: List[Tuple[float, float]] = []
        total = max(steps, 360)
        for idx in range(total + 1):
            theta = 2 * math.pi * (idx / total)
            radius = amplitude * math.cos(k_value * theta)
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            points.append((x, y))
        return points

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """
        Retrieve label positions logic.
        
        Returns:
            Result of get_label_positions operation.
        """
        labels: List[Tuple[str, float, float]] = []
        amplitude = self.properties["amplitude"].value
        k_value = self.properties["k_value"].value
        if amplitude:
            labels.append((self._fmt("a", amplitude), amplitude * 0.7, 0.2))
        if k_value and amplitude:
            labels.append((self._fmt("k", k_value), -amplitude * 0.7, 0.2))
        petals = self.properties["petal_count"].value
        if petals is not None and amplitude:
            labels.append((self._fmt("petals", petals), 0, amplitude * 0.3))
        area = self.properties["total_area"].value
        if area is not None and amplitude:
            labels.append((self._fmt("A", area), 0, -amplitude * 0.3))
        return labels

    @staticmethod
    def _fmt(symbol: str, value: float) -> str:
        return f"{symbol} = {value:.4f}".rstrip("0").rstrip(".")