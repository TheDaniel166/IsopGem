"""Curved shape solvers for annulus, crescent, vesica piscis, and rose curves."""
from __future__ import annotations

import math
from typing import Any, Optional

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition


ANNULUS_DERIVATION = r"""
Annulus (ring) shape calculator.

An annulus is a ring-shaped region bounded by two concentric circles—a "circle with
a hole." It is the 2D analog of a spherical shell or hollow cylinder. The annulus
appears in washer method integration (calculus), planetary ring systems, and mechanical
engineering (pipes, bearings, washers).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Area as Difference (The Subtraction Principle)
═══════════════════════════════════════════════════════════════════════════════════════

Given outer radius R and inner radius r (where $R > r$):

  Area = $\pi R^2 - \pi r^2 = \pi(R^2 - r^2)$

This factors beautifully:

  $A = \pi(R - r)(R + r) = \pi w\cdot d_{avg}$

  where:
    $w = R - r$    (ring width)
    $d_{avg} = R + r$    (average of inner and outer diameters... wait, that's not quite right!)

Actually, let's rewrite more carefully:

  $A = \pi(R + r)(R - r) = 2\pi\left(\frac{R+r}{2}\right)(R-r) = C_{avg} \times w$

  where:
    $C_{avg} = 2\pi(R+r)/2 = \pi(R+r)$    (average circumference)
    $w = R - r$    (width)

So: **Annulus area = average circumference × width**

This is intuitive: imagine "unrolling" the ring into a rectangular strip of height w
and length C_avg!

**Special case** (thin ring, $R \approx r$):
  $A \approx 2\pi R w$    (circumference × width, like a ribbon)

This is the basis for **differential area** in polar coordinates:
  $dA = r\, d\theta\, dr$    (infinitesimal annulus sector)

**Comparison to circle**:
• Circle: $A = \pi R^2$ (all interior space)
• Annulus: $A = \pi(R^2-r^2)$ (exterior minus interior)
• Fraction filled: $f = (R^2-r^2)/R^2 = 1 - (r/R)^2$

As $r \to 0$: Annulus → full circle (100% filled)
As $r \to R$: Annulus → thin ring (area → 0)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Washer Method (Calculus of Volumes of Revolution)
═══════════════════════════════════════════════════════════════════════════════════════

The annulus is the cross-sectional "washer" used in calculus to compute volumes of
solids of revolution with HOLES.

**Disk method** (solid of revolution, no hole):
Rotate y = f(x) around x-axis:
  $V = \int \pi[f(x)]^2\, dx$    (sum of circular disks)

**Washer method** (hollow solid):
Rotate region between y = f(x) (outer) and y = g(x) (inner) around x-axis:

  $V = \int \pi([f(x)]^2 - [g(x)]^2)\, dx = \int \pi(R^2 - r^2)\, dx$

  where $R = f(x)$, $r = g(x)$

Each infinitesimal slice is an ANNULUS of area $\pi(R^2 - r^2)$ and thickness dx!

**Example**: Find volume of a torus (donut) with major radius R and minor radius a:
• Cross-section at distance x from center: annulus with $R_{outer} = R + \sqrt{a^2-x^2}$,
  $R_{inner} = R - \sqrt{a^2-x^2}$
• Integrate from -a to a
• Result: $V = 2\pi^2 R a^2$ (Pappus's theorem!)

**Shell method** (alternative):
Rotate around axis parallel to the curve:
  $V = \int 2\pi x\, h(x)\, dx$    (sum of cylindrical shells)

Both methods use the annulus as fundamental building block—one as area (washer), one
as circumference (shell).

**Physical applications**:
• Hollow cylinder: $V = \pi(R^2-r^2)h$ (annular base × height)
• Pipe wall: thickness t = R - r, volume ≈ $2\pi R t L$ (for thin walls)
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

  $d \approx 2.44 R \left(\frac{M_{planet}}{M_{moon}}\right)^{1/3}$

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
Ring as ensemble of annular streamlines, each with orbital velocity $v = \sqrt{GM/r}$.
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

Compute all annulus (ring) properties.

ANNULUS DERIVATIONS:
====================

Definition:
-----------
An annulus is the region between two concentric circles.

**Ring Width**: $w = R - r$
The radial distance between outer and inner circles.

**Area**: $A = \pi(R^2 - r^2) = \pi(R + r)(R - r)$

Derivation Method 1 (Subtraction):
- Outer circle area: $A_{outer} = \pi R^2$
- Inner circle area: $A_{inner} = \pi r^2$
- Ring area: $A = A_{outer} - A_{inner} = \pi(R^2 - r^2)$ ✓

Derivation Method 2 (Integration):
- Polar coordinates: $A = \iint \rho \, d\rho \, d\theta$
- $A = \int_0^{2\pi} \int_r^R \rho \, d\rho \, d\theta = \int_0^{2\pi} [\rho^2/2]_r^R d\theta$
- $= \int_0^{2\pi} (R^2 - r^2)/2 \, d\theta = 2\pi(R^2 - r^2)/2 = \pi(R^2 - r^2)$ ✓

Derivation Method 3 (Average Circumference):
- Average radius: $r_{avg} = (R + r)/2$
- Average circumference: $C_{avg} = 2\pi\, r_{avg} = \pi(R + r)$
- Ring width: $w = R - r$
- Approximate area: $A \approx C_{avg} \times w = \pi(R + r)(R - r)$ ✓
(This becomes exact in the limit, derived from Pappus's theorem)

**Factored Form**: $A = \pi w(2r + w)$
Where $w = R - r$, so $R = r + w$:
$A = \pi[(r + w)^2 - r^2] = \pi[r^2 + 2rw + w^2 - r^2] = \pi(2rw + w^2) = \pi w(2r + w)$

**Radius Ratio**: $\rho = R/r$
- $\rho > 1$ always (R > r by definition)
- $\rho \to 1$: thin ring (R ≈ r)
- $\rho \to \infty$: ring approaches full disk

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
2. **Moment of Inertia**: $I = (\pi/2)m(R^2 + r^2)$ for uniform disk
3. **Centroid**: Remains at geometric center (0,0)
4. **Polar Second Moment**: $J = (\pi/2)(R^4 - r^4)$

In Physics & Engineering:
• **Washers**: Mechanical spacers and load distributors
• **Bearings**: Ball bearings roll in annular tracks
• **Toroids**: 3D revolution of annulus
• **Accretion Disks**: Matter spiraling into black hole/star
"""
CRESCENT_DERIVATION = r"""
Crescent (lune) shape calculator.

A crescent (or lune) is the region between two intersecting circular arcs. It is formed
by subtracting one circular disk from another, where the circles partially overlap. The
crescent appears in lunar phases, Islamic symbolism, and geometric constructions related
to the ancient problem of "squaring the circle" (Hippocrates' lunes).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Lune as Intersection Geometry (Circle Minus Circle)
═══════════════════════════════════════════════════════════════════════════════════════

A crescent is defined by TWO circles:
• **Outer circle**: radius R, center O₁
• **Inner circle**: radius r, center O₂
• **Offset**: distance d between centers

The crescent area is:

  $A_{crescent} = A_{outer} - A_{intersection}$

where $A_{intersection}$ is the **lens-shaped overlap** (vesica piscis if $R = r$).

**Lens intersection area** (general formula):

For two circles with radii R and r separated by distance d, the intersection area is:

  $A_{\cap} = R^2\arccos\left(\frac{d^2+R^2-r^2}{2dR}\right) + r^2\arccos\left(\frac{d^2+r^2-R^2}{2dr}\right)$ 
        $- \frac{1}{2}\sqrt{(2dR)^2 - (d^2+R^2-r^2)^2}$

This derives from summing two circular segments (one from each circle).

**Special cases**:
• d = 0 (concentric): $A_{\cap} = \pi r^2$ (smaller circle fully inside) → $A_{crescent} = \pi(R^2-r^2)$ (annulus!)
• d = R + r (externally tangent): $A_{\cap} = 0$ → $A_{crescent} = \pi R^2$ (full circle, no subtraction)
• R = r, d = R (vesica piscis): $A_{\cap} = 2R^2(2\pi/3 - \sqrt{3}/2)$ → symmetric lens

**Triangle inequality constraint**:
For the circles to intersect: $|R - r| < d < R + r$
• If d ≥ R + r: circles don't overlap (no crescent, two separate disks)
• If d ≤ |R - r|: one circle fully inside other (annulus or nothing)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Lunar Phases (Illuminated Crescent)
═══════════════════════════════════════════════════════════════════════════════════════

The crescent shape is most famously observed in **lunar phases**:

**New Moon → Waxing Crescent → First Quarter → Waxing Gibbous → Full Moon**
(then reverse: Waning Gibbous → Third Quarter → Waning Crescent → New Moon)

The crescent phase occurs when the Moon is 0-90° from the Sun (as viewed from Earth):
• **Waxing crescent**: 0-45° (thin sliver growing)
• **Waning crescent**: 315-360° (thin sliver shrinking)

**Geometric model** (simplified):
• Sun illuminates hemisphere facing it (outer circle: full disk)
• We see hemisphere facing Earth (inner circle: terminator curve)
• The visible illuminated part is the CRESCENT (or gibbous when > 50%)

More accurately, the terminator (shadow boundary) is an ELLIPSE (not a circle) because
we view the spherical Moon from an angle. But for thin crescents, the approximation
as two circular arcs is good enough.

**Historical significance**:
• Ancient calendars (lunar calendars) tracked months by crescent sightings
• Islamic calendar begins each month with first visible crescent (hilal)
• The crescent moon (with star) is the symbol of Islam (adopted from Byzantine symbolism)

**Earthshine**: During crescent phase, the dark side of the Moon is faintly visible due
to reflected light from Earth ("the old moon in the new moon's arms"). This is sunlight
reflecting off Earth, then bouncing to the Moon's dark side, then back to us!

**Crescents elsewhere**:
• Venus phases (observed by Galileo, proving heliocentric model!)
• Horns of crescent-shaped nebulae (e.g., Crescent Nebula NGC 6888)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Hippocrates' Lunes (Squaring the Crescent)
═══════════════════════════════════════════════════════════════════════════════════════

**Hippocrates of Chios** (~440 BCE) discovered that certain lune shapes have areas equal
to the areas of triangles or other rectilinear figures. This was a major breakthrough
toward "squaring the circle."

**Hippocrates' Lune Theorem**:

Consider a right triangle ABC with right angle at C. Draw semicircles on all three sides:
• Semicircle on hypotenuse AB (radius R)
• Semicircles on legs AC and BC (radii r and s)

The two LUNES formed outside the legs (crescents bounded by the large semicircle and
the small semicircles) have combined area EXACTLY EQUAL to the area of the triangle!

Proof sketch:
• By Pythagorean theorem: $AB^2 = AC^2 + BC^2$
• Areas of semicircles: $(\pi/2)R^2 = (\pi/2)(r^2 + s^2)$ [using $R^2 = r^2 + s^2$]
• Lune areas = (semicircles on legs) - (segments of large semicircle)
• After algebra: $A_{lunes} = A_{triangle}$ (exactly!)

**Significance**: This showed that SOME curvilinear figures can be "squared" (expressed
as equivalent rectilinear areas). Hippocrates hoped to extend this to the full circle,
but that proved impossible (π is transcendental, proven 1882).

**Other squarable lunes**: Five types of lunes are known to be squarable (expressible
as rational multiples of rational areas). No others exist!

**Modern understanding**: Lunes are squarable because they're formed by RATIONAL
relationships between circular arcs. The circle itself is not squarable because its
area involves the transcendental constant π.

═══════════════════════════════════════════════════════════════════════════════════════
🌙 HERMETIC SIGNIFICANCE 🌙
═══════════════════════════════════════════════════════════════════════════════════════

The crescent embodies **Phases, Transformation, and the Feminine Principle**:

• **Lunar Symbolism**: The crescent is the MOON in transition—neither new (dark) nor
  full (complete), but WAXING (growing) or WANING (diminishing). It represents the
  cycles of life, death, and rebirth. The Moon (feminine, reflective, changeable) vs.
  Sun (masculine, radiant, constant).

• **The Horns**: The two points of the crescent are "horns"—associated with:
  - The bull (Taurus, fertility, strength)
  - The cow (Hathor in Egyptian myth, nourisher)
  - The horned goddess (Diana/Artemis, moon goddess)
  The horns point UPWARD (waxing) or DOWNWARD (waning), indicating direction of change.

• **Islamic Symbolism**: The crescent (hilal) marks the beginning of the lunar month
  (especially Ramadan). It represents RENEWAL, the fresh start, the first light after
  darkness. Often paired with a star (Venus or a five-pointed star), symbolizing
  divine guidance in the darkness.

• **Triple Goddess**: Maiden (waxing crescent) → Mother (full moon) → Crone (waning
  crescent). The crescent is youth (maiden) and wisdom (crone), bookending the fullness
  of maturity.

• **Incomplete Circle**: The crescent is a PARTIAL circle—potential not yet realized
  (waxing) or fading away (waning). It's the geometry of *becoming* and *un-becoming*,
  not static being. The crescent teaches that perfection (full circle) is momentary—
  most of existence is in the liminal phases.

• **Cup and Horn**: Upward crescent (☽) = cup (receptive, gathering, holding) like
  the Holy Grail. Downward crescent (☾) = pouring out, releasing, emptying. The
  geometry of *receiving* vs. *giving*.

The crescent teaches: **Fullness is fleeting; the true work is in the waxing and waning.** 🌙

═══════════════════════════════════════════════════════════════════════════════════════

Compute crescent (lune) properties.

CRESCENT (LUNE) DERIVATIONS:
=============================

Definition:
-----------
A crescent (or lune) is the **region between two intersecting circular arcs**,
typically formed when a smaller circle overlaps a larger circle.

Parameters:
- **Outer radius**: R (larger circle)
- **Inner radius**: r (smaller circle)
- **Offset (center distance)**: d

Geometry Constraints:
- R > r (outer is larger)
- d ≥ 0 (centers can coincide or be separated)

CASES:
======

Case 1: **Disjoint** (d ≥ R + r)
- Circles do not overlap
- Overlap area = 0
- Crescent area = πR² (full outer circle)
- Perimeter = 2πR

Case 2: **One Inside Other** (d ≤ R - r)
- Inner circle completely inside outer circle
- Overlap area = πr² (full inner circle)
- Crescent area = π(R² - r²) (annulus)
- Perimeter = 2πR + 2πr (both boundaries)

Case 3: **Intersection** (R - r < d < R + r)
- True crescent/lune shape
- Overlap area = A_∩ (lens between circles)
- Crescent area = πR² - A_∩
- Perimeter = (2π - α)R + βr

OVERLAP AREA (LENS):
====================

For two intersecting circles with radii R, r and center distance d:

Using the **Cosine Rule** in the triangle formed by the two centers
and an intersection point:

**Half-angles at each center**:
- $\\alpha = 2\\arccos\\left(\\frac{d^2 + R^2 - r^2}{2dR}\\right)$  [angle at outer center]
- $\\beta = 2\\arccos\\left(\\frac{d^2 + r^2 - R^2}{2dr}\\right)$  [angle at inner center]

**Circular Segment Areas**:
- $A_1 = (R^2/2)(\\alpha - \\sin \\alpha)$
- $A_2 = (r^2/2)(\\beta - \\sin \\beta)$

**Total Overlap**:
$A_{\\cap} = A_1 + A_2 = (R^2/2)(\\alpha - \\sin \\alpha) + (r^2/2)(\\beta - \\sin \\beta)$

Alternative (Heron-like formula):
$A_{\\cap}$ can also be expressed using:
$A_{\\cap} = R^2\\arccos\\left(\\frac{d^2+R^2-r^2}{2dR}\\right) + r^2\\arccos\\left(\\frac{d^2+r^2-R^2}{2dr}\\right)$
             $- \\frac{1}{2}\\sqrt{(-d+R+r)(d+R-r)(d-R+r)(d+R+r)}$

This form uses Heron's formula for the **kite-shaped quadrilateral**
formed by the two centers and the two intersection points.

CRESCENT AREA:
==============

$A_{crescent} = \pi R^2 - A_{\\cap}$

For symmetric case (d = 0, concentric):
$A_{crescent} = \pi(R^2 - r^2) = \pi w(2r + w)$ where $w = R - r$

PERIMETER:
==========

The crescent boundary consists of:
- **Outer arc**: Major arc on outer circle = $(2\pi - \\alpha)R$
- **Inner arc**: Minor arc on inner circle = $\\beta r$

$P_{crescent} = (2\pi - \\alpha)R + \\beta r$

Where α, β are the full angles (in radians) as derived above.

HERMETIC NOTE - THE LUNAR CRESCENT:
====================================
The crescent is the **SYMBOL OF THE MOON**, **CYCLICAL TIME**, and
**DIVINE FEMININE POWER**. It represents **GROWTH**, **WAXING AND WANING**,
and the **RHYTHM OF NATURE**.

In Symbolism:
- **Waxing Moon**: Growth, increase, fertility, new beginnings
- **Waning Moon**: Decrease, reflection, rest, releasing
- **Horns of the Crescent**: Receptivity, capturing light/energy
- **Islamic Crescent**: Star and crescent, faith, celestial guidance

In Sacred Traditions:
- **Lunar Goddesses**: Diana, Artemis, Selene, Hecate
- **Virgin Mary**: Often depicted on a crescent moon
- **Osiris**: Associated with lunar cycles, death and rebirth
- **Isis**: Horns of the cow goddess form crescent

Mathematical Properties:
------------------------
1. **Lune of Hippocrates**: Special lunes can have area equal to a triangle
   (Famous ancient squaring problem)
2. **Area-angle relation**: Crescent area depends on α, β derived from
   cosine law
3. **Symmetry**: Crescent is symmetric about the line joining centers

In Nature & Culture:
• **Moon Phases**: Waxing/waning crescent, gibbous phases
• **Dune Crescents**: Barchan dunes in desert landscapes
• **Fingernails**: Lunula (white crescent at nail base)
• **Scythes & Sickles**: Tools for harvest, reaping time
• **Horns**: Bull, ram, crescent as strength and power

In Astronomy:
- **Phases of Venus**: Galileo observed crescent Venus (heliocentric proof)
- **Eclipses**: Partial solar eclipses show crescent sun
- **Thin Crescent**: New moon visible just after sunset
"""
VESICA_PISCIS_DERIVATION = r"""
Vesica Piscis shape calculator.

The Vesica Piscis ("bladder of the fish") is the almond-shaped lens formed by the
intersection of two equal circles, each passing through the center of the other. It is
one of the most sacred geometric forms, appearing in Christian iconography (Christ,
Mary, saints within vesica mandorla), the Flower of Life, and as the generative matrix
for many sacred constructions.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: The √3 Ratio (The First Irrational from Two Circles)
═══════════════════════════════════════════════════════════════════════════════════════

Given two circles of radius r, each passing through the other's center:
• **Center separation**: $s = r$ (by construction!)
• **Lens width** (perpendicular distance between intersection points): $w = r$
• **Lens height** (long axis of the almond): $h = r\sqrt{3}$

**Derivation of height**:
The two intersection points lie at distance r from each center. Form an equilateral
triangle with:
• Two centers: O₁, O₂
• One intersection point: P
• All sides = $r$ (equilateral!)

The height of an equilateral triangle with side r is:

  $h = (r\sqrt{3})/2$    (altitude formula)

But the FULL vesica height is TWICE this (from bottom intersection to top):

  $h_{vesica} = 2 \times (r\sqrt{3})/2 = r\sqrt{3}$

**Ratio of height to width**:

  $h/w = (r\sqrt{3})/r = \sqrt{3} \approx 1.732$

This √3 ratio is FUNDAMENTAL:
• It arises from the $60^\circ$ angle in the equilateral triangle ($\sin(60^\circ) = \sqrt{3}/2$)
• It's the aspect ratio of the vesica piscis (elongation factor)
• It appears in hexagonal geometry (hexagon inscribed in circle has side = radius)

**Area of vesica piscis**:

  $A = 2r^2(2\pi/3 - \sqrt{3}/2) = r^2(4\pi/3 - \sqrt{3})$

  $\approx r^2 \times 2.456$    (about 39% of the circle area $\pi r^2$)

This combines:
• Two circular segments (each with central angle $120^\circ = 2\pi/3$ radians)
• Minus the area of the equilateral triangle ($r^2\sqrt{3}/4$, counted twice)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Vesica as Generative Matrix (The Flower of Life)
═══════════════════════════════════════════════════════════════════════════════════════

The vesica piscis is the FIRST STEP in constructing the **Flower of Life**:

1. Start with one circle (unity, the Monad)
2. Draw a second circle through its center → creates vesica piscis (duality, division)
3. Draw circles through each vesica intersection → creates 6 petals (hexagon, Seed of Life)
4. Continue pattern → 19 circles → Flower of Life
5. Connect centers → Fruit of Life (13 circles)
6. Extract straight lines → Metatron's Cube (contains all 5 Platonic solids!)

The vesica is the **birth canal** of sacred geometry—from it emerges:

• **Equilateral triangle**: Connect the two centers and the two intersections → △
• **Square**: Draw perpendicular lines through centers and intersection points
• **Pentagon**: Use vesica width/height ratio to construct golden ratio φ
• **Hexagon**: Six circles around one create 6-petal flower (natural packing)

**Compass-and-straightedge construction**:
The vesica enables many geometric constructions:
• Perpendicular bisector: Line through vesica intersections is ⊥ to line of centers
• Angle trisection: Can trisect 60° angle (but NOT general angles, proven impossible)
• √3 construction: The vesica height is exactly r√3 (constructible!)

**Biological resonance**:
• Cell division: Mitosis creates vesica shape as membrane pinches
• Eye shape: Almond-shaped eyes (mandorla in art)
• Fish symbol: Ichthys (⌘), early Christian symbol (vesica = fish bladder)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Width:Height Ratio and Measure of the Fish
═══════════════════════════════════════════════════════════════════════════════════════

The vesica has a special property:

  **Width : Height = $1 : \sqrt{3}$**

This √3 ratio has deep connections:

1) **Hexagonal close packing**: Bees build honeycombs with hexagons because:
   • Hexagon = 6 equilateral triangles
   • Equilateral triangle has height/side = $\sqrt{3}/2$
   • Vesica appears in the gaps between circles in hexagonal packing

2) **Musical intervals**: $\sqrt{3} \approx 1.732$ is close to the minor sixth interval ($8:5 = 1.6$)
   and relates to the tritone ($\sqrt{2} \approx 1.414$, the "devil's interval"). √3 appears in
   harmonic series relationships.

3) **Measure of the Fish** (ancient): In Pythagorean sacred geometry, the ratio
   1 : √3 was called the "measure of the fish" (vesica piscis dimensions). It was
   used to encode the relationship between unity (1) and the first irrational arising
   from compass-and-straightedge geometry (√3, from 60° angle).

4) **Perimeter of vesica**:
   • Two circular arcs, each subtending $120^\circ$ ($2\pi/3$ radians)
   • Arc length = $r\theta = r(2\pi/3)$ per arc
   • Total: $P = 2 \times r(2\pi/3) = 4\pi r/3 \approx 4.189r$

5) **Diagonal of hexagon**: A regular hexagon with side s has:
   • Long diagonal (vertex to opposite vertex through center) = $2s$
   • Short diagonal (vertex to next-but-one vertex) = $s\sqrt{3}$
   The vesica encodes this short diagonal ratio!

═══════════════════════════════════════════════════════════════════════════════════════
🐟 HERMETIC SIGNIFICANCE 🐟
═══════════════════════════════════════════════════════════════════════════════════════

The vesica piscis embodies **Union, Birth, and the Portal Between Worlds**:

• **Sacred Union**: Two circles (masculine/feminine, spirit/matter, heaven/earth)
  OVERLAP to create the vesica—the womb of creation. It's the geometry of sacred
  marriage (hieros gamos), the union that births new reality.

• **Christ Mandorla**: In medieval Christian art, Christ (and Mary, saints) is often
  depicted within a vesica piscis (called mandorla = almond). This represents:
  - The intersection of heaven and earth (two circles)
  - The womb of Mary (vesica as birth canal for divine incarnation)
  - The portal between worlds (Christ as mediator, the door)

• **Ichthys (Fish Symbol)**: Early Christians used the fish (⌘) as secret symbol.
  Greek: ἸΧΘΥΣ = "Jesus Christ, Son of God, Savior" (acrostic).
  The vesica piscis is literally the "bladder of the fish"—the fish's swim bladder
  or the cross-section of two fish facing each other (yin-yang of the deep).

• **The Vulva and Yoni**: The vesica is the geometric form of the female genitalia
  (vulva/yoni), the literal portal of birth. In sacred sexuality traditions (Tantra,
  Kundalini), the yoni is the gateway through which souls incarnate. The vesica is
  the geometric abstraction of this biological mystery.

• **The Eye of God**: The almond-shaped eye (mandorla-shaped) sees all. The "Eye of
  Providence" is often vesica-shaped. To be within the vesica = to be seen by God,
  to be in the light of divine attention.

• **First Division**: The vesica is what happens when the One (circle) SPLITS to
  create the Two (two circles). But they remain OVERLAPPING—not fully separated.
  The vesica is the shared space, the middle path, the synthesis. It represents:
  "I am You, You are Me, We are One" (even in duality).

The vesica teaches: **Creation happens in the overlap, not in separation.** 🐟

═══════════════════════════════════════════════════════════════════════════════════════

Compute lens (vesica piscis) properties.

VESICA PISCIS DERIVATIONS:
==========================

Definition:
-----------
The vesica piscis is the **lens-shaped region** formed by the intersection
of two congruent circles whose centers are separated by a distance equal
to the circle radius (the "classic" or "sacred" vesica).

Generalizing: for any separation s where $0 < s < 2r$, we get an almond lens.

**Classic Vesica**: $s = r$
Then:
- Each circle passes through the center of the other
- Intersection angle $\theta = 120^\circ$ ($2\pi/3$ radians)
- Lens height $h = r\sqrt{3}$
- Apex angle at each end = $120^\circ$

AREA DERIVATION:
================

The lens area equals the sum of two **circular segments**.

Method 1 (Circular Segment):
- Let $s$ = center separation
- Each segment has chord length $c = 2\sqrt{r^2 - (s/2)^2}$
- Half-angle $\alpha = \arccos(s/(2r))$
- Segment area $A_{seg} = r^2\alpha - (r^2/2)\sin(2\alpha)$
- Lens area $A = 2A_{seg} = 2r^2\alpha - r^2\sin(2\alpha)$

Method 2 (Classic Vesica, s = r):
- $\alpha = \arccos(1/2) = \pi/3$ ($60^\circ$)
- $2\alpha = 2\pi/3$ ($120^\circ$)
- $A = 2r^2(\pi/3) - r^2\sin(2\pi/3)$
- $\sin(2\pi/3) = \sqrt{3}/2$
- $A = 2r^2(\pi/3 - \sqrt{3}/4) = 2r^2\cdot(2\pi/3 - \sqrt{3}/2)/2$
- **$A = r^2(2\pi/3 - \sqrt{3}/2)$** $\approx 0.608r^2$

Method 3 (Integration):
- Parametric circle 1: center at $(-s/2, 0)$
- Parametric circle 2: center at $(+s/2, 0)$
- Intersection at x = 0 (by symmetry), $y = \pm\sqrt{r^2 - s^2/4}$
- Integrate: $A = 2\int_0^h [x_{right} - x_{left}]\, dy$
- Where $x = s/2 \pm \sqrt{r^2 - y^2}$
- Leads to $A = 2r^2\arccos(s/(2r)) - (s/2)\sqrt{4r^2 - s^2}$ ✓

HEIGHT DERIVATION:
==================

By Pythagoras in the right triangle formed by:
- Radius r (hypotenuse)
- Half-separation s/2 (base)
- Half-height h/2 (altitude from base to circle edge)

(h/2)² = r² - (s/2)²
$h = 2\sqrt{r^2 - s^2/4}$

For classic vesica (s = r):
$h = 2\sqrt{r^2 - r^2/4} = 2r\sqrt{3/4} = r\sqrt{3}$ ✓

PERIMETER DERIVATION:
=====================

The lens boundary consists of two **circular arcs**, each subtending
angle 2α at the respective circle center.

- Half-angle: $\alpha = \arccos(s/(2r))$
- Full angle: 2α
- Arc length: $s_{arc} = r(2\alpha) = 2r\arccos(s/(2r))$
- Total perimeter: $P = 2s_{arc} = 4r\arccos(s/(2r))$

For classic vesica (s = r):
- $\alpha = \pi/3 \rightarrow 2\alpha = 2\pi/3$
- $P = 4r(\pi/3) = 4\pi r/3 \approx 4.189r$

HERMETIC NOTE - THE SACRED FISH:
=================================
The vesica piscis is among the **MOST SACRED** geometric figures,
appearing across traditions as the **BIRTH PORTAL**, **DIVINE WOMB**,
and the **INTERSECTION OF HEAVEN AND EARTH**.

In Christianity:
- **Mandorla** (almond): Aureole around Christ, Virgin Mary
- **Ichthys** (fish): Early Christian symbol, Jesus as fish
- Represents the **miracle of loaves and fishes**

In Sacred Geometry:
- **√3 ratio**: The vertical/horizontal proportion ($h/s = \sqrt{3}$ for $s=r$)
- **Vesica width** = $r$ → produces the **√3 rectangle** (holy proportion)
- **Seed of Life**: Six circles around one, all vesica intersections
- **Flower of Life**: Extended pattern of overlapping circles
- **Platonic Lambda**: Musical ratio generator (1, √2, √3)

In Architecture:
- **Gothic Arches**: Pointed arches derive from vesica geometry
- **Rose Windows**: Central vesica surrounded by petals
- **Labyrinth Entrances**: Vesica as threshold between worlds

Symbolic Meanings:
- **Feminine Sacred**: Vulva, birth canal, womb of creation
- **Duality United**: Two circles (spirit + matter) create third (soul)
- **Christ Consciousness**: The lens is the divine made flesh
- **Fish Symbol**: Piscis = fish, age of Pisces, baptism, depth

Mathematical Properties:
------------------------
1. **Aspect Ratio** (classic): $h/s = \sqrt{3} \approx 1.732$
2. **Area Ratio**: $A_{lens}/A_{circle} = (2\pi/3 - \sqrt{3}/2)/\pi \approx 0.193$
3. **√3 Generator**: Produces 30-60-90 triangles
4. **Reuleaux Triangle**: Three vesicae form a curve of constant width

In Nature & Symbolism:
• **Almond**: Sacred nut, mandorla shape, awakening
• **Eye**: Lens shape, vision, third eye, enlightenment
• **Leaf**: Growth, vitality, sprouting
• **Portal**: Gateway between realms, birth, threshold
"""
ROSE_CURVE_DERIVATION = r"""
Rose (Rhodonea) curve calculator.

A rose curve (or rhodonea curve) is a sinusoidal polar curve defined by $r = a\cos(k\theta)$
or $r = a\sin(k\theta)$, where a is amplitude and k is the "harmonic" (petal count parameter).
These curves produce beautiful floral patterns with n or 2n petals depending on whether
k is odd or even. Rose curves appear in acoustics (sound wave interference), optics
(Lissajous figures), and orbital mechanics (perturbed orbits).

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Petal Count Formula (Odd vs. Even k)
═══════════════════════════════════════════════════════════════════════════════════════

Polar equation: **$r = a\cos(k\theta)$**  (or sin, which just rotates the pattern)

Number of petals:

  **$p = k$    if k is odd**
  **$p = 2k$   if k is even**

Why the difference?

**Odd k** (e.g., k=3, 5, 7...):
• As $\theta$ goes from 0 to $2\pi$, the function $\cos(k\theta)$ completes k full cycles
• But when $r < 0$ (negative radius in polar coords), the point flips to opposite side
• For ODD k: negative r values trace OUT the same petals again (no new petals)
• Result: k petals total

**Even k** (e.g., k=2, 4, 6...):
• As $\theta$ goes from 0 to $\pi$, the function $\cos(k\theta)$ completes k/2 cycles (k/2 petals)
• As $\theta$ goes from $\pi$ to $2\pi$, another k/2 petals appear in the GAPS
• For EVEN k: negative r values create NEW petals (interleaved)
• Result: 2k petals total

**Examples**:
• k=1: p=1 (circle! $r = a\cos(\theta)$ is just a circle of diameter a)
• k=2: p=4 (four-petal rose, quadrifolium)
• k=3: p=3 (three-petal rose, trifolium)
• k=4: p=8 (eight-petal rose)
• k=5: p=5 (five-petal rose, cinquefoil)
• k=6: p=12 (twelve-petal rose)

**Area formula**:

  $A = (a^2/2) \times p = (a^2/2) \times k$    (if odd)
       $= (a^2/2) \times 2k$   (if even)

Derivation: Integrate in polar coordinates:
  $A = \int \frac{1}{2} r^2\, d\theta = \int \frac{1}{2} a^2\cos^2(k\theta)\, d\theta$

Using $\cos^2(x) = (1 + \cos(2x))/2$, integrate over appropriate interval.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Rational Rose Curves (r = cos(nθ/d) Harmonics)
═══════════════════════════════════════════════════════════════════════════════════════

Generalize to **rational k = n/d** (where n, d are coprime integers):

  $r = a\cos(n\theta/d)$

Petal count:
• If n and d are both odd: p = n petals
• If one is even, one is odd: p = 2n petals
• Period: The curve repeats every $2\pi d$ radians (must go around d times to complete)

**Example**: $r = \cos(5\theta/2)$
• n=5 (odd), d=2 (even) → p = 2×5 = 10 petals
• But you must trace $\theta$ from 0 to $4\pi$ (two full rotations) to see all petals!

This creates **multi-loop rose curves** that trace over themselves multiple times.

**Maurer rose**: A related construction where you connect points at regular angular
intervals on a rose curve, creating star-like patterns. Used in Islamic geometric art.

**Fourier connection**:
Rose curves are the GEOMETRIC VISUALIZATION of harmonic functions:
• Pure tone (single frequency): k=1 → circle
• Harmonic overtones: k=2,3,4... → rose petals

In 2D oscilloscope displays (Lissajous figures), perpendicular sinusoids create
rose-like patterns:
• $x(t) = A\sin(\omega_1 t)$, $y(t) = B\sin(\omega_2 t)$
• Frequency ratio $\omega_1/\omega_2$ determines petal count (like k in rose curve)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Perturbed Orbits and Planetary Rosettes
═══════════════════════════════════════════════════════════════════════════════════════

Rose curves model **perturbed orbital motion**:

**Kepler orbits** (two-body problem, 1/r² gravity):
• Ellipse: $r = a(1-e^2)/(1 + e\cos(\theta))$
• Closed orbit (perihelion and aphelion in same places every orbit)

**Perturbed orbits** (three-body problem, relativistic effects):
• Mercury's orbit: Precession of perihelion (closest point to Sun slowly rotates)
• This creates a ROSETTE pattern over many orbits
• Newtonian perturbations (Jupiter's gravity) + Einstein's General Relativity
  → Mercury's perihelion precesses 43 arcseconds/century

Mathematically, perturbed orbits can be approximated as:

  $r(\theta) \approx a(1-e^2)/(1 + e\cos(k\theta))$    where $k \ne 1$ (slight deviation)

For k slightly less than 1 (e.g., k=0.99), the orbit:
• Nearly closes after one revolution
• But perihelion shifts slightly each orbit
• Over many orbits → rosette pattern (like $r = \cos(k\theta)$ with k≪1)

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

Compute rose (rhodonea) curve properties.

ROSE CURVE (RHODONEA) DERIVATIONS:
===================================

Definition:
-----------
A rose curve (rhodonea curve) is a **polar sinusoid** defined by:

**$r = a\cos(k\theta)$** or **$r = a\sin(k\theta)$**

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
For **$r = a\cos(k\theta)$**:
- One petal is traced for each period of $\cos(k\theta)$ where $r \ge 0$
- $\cos(k\theta)$ has period $2\pi/k$
- In one full rotation ($0 \le \theta \le 2\pi$), k completes **k cycles**

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

$A_{petal} = (1/2)\int\int r^2\, d\theta$

For **$r = a\cos(k\theta)$**, one petal spans from $\theta_1$ to $\theta_2$ where $\cos(k\theta) \ge 0$.

**One Petal** (k odd):
$\theta$ from $-\pi/(2k)$ to $\pi/(2k)$:

$A_{petal} = (1/2)\int_{-\pi/(2k)}^{\pi/(2k)} a^2\cos^2(k\theta)\, d\theta$

Using the identity: $\cos^2(x) = (1 + \cos(2x))/2$

$A_{petal} = (a^2/2)\int_{-\pi/(2k)}^{\pi/(2k)} (1 + \cos(2k\theta))/2\, d\theta$
        $= (a^2/4)[\theta + \sin(2k\theta)/(2k)]|[-\pi/(2k), \pi/(2k)]$
        $= (a^2/4)[\pi/k + 0 - (-\pi/k + 0)]$
        $= (a^2/4)\cdot(2\pi/k)$
        $= \pi a^2/(2k)$

**Total Area**:
- k odd: $A_{total} = k\cdot(\pi a^2/(2k)) = \pi a^2/2$
- k even: $A_{total} = 2k\cdot(\pi a^2/(4k)) = \pi a^2/2$

Remarkably, **total area is always $\pi a^2/2$**, independent of k!

Simplified Formula:
$A_{total} = (a^2/2)\cdot p$

where p = number of petals = k (k odd) or 2k (k even)

This gives: $A_{total} = (a^2/2)\cdot k$ for k odd → $\pi a^2/2$ ✓

MAX RADIUS:
===========

$r_{max} = |a|$ occurs when $\cos(k\theta) = \pm 1$.

For $r = a\cos(k\theta)$, max radius = **a** (at petal tips).

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
1. **Polar Equation**: $r = a\cos(k\theta)$ or $r = a\sin(k\theta)$
2. **Cartesian Conversion**: $(x^2 + y^2)^{(k+1)/2} = a^k \cdot x^k$ (for cos)
3. **Arc Length**: $L = a\int\sqrt{1 + k^2\sin^2(k\theta)}\, d\theta$ (elliptic integral)
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


def _circle_overlap_area(r1: float, r2: float, d: float) -> float:
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2

    alpha = math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)) * 2
    beta = math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2)) * 2
    area1 = 0.5 * r1 * r1 * (alpha - math.sin(alpha))
    area2 = 0.5 * r2 * r2 * (beta - math.sin(beta))
    return area1 + area2


def _crescent_perimeter(r1: float, r2: float, d: float) -> float:
    if d >= r1 + r2:
        return 2 * math.pi * r1
    if d <= abs(r1 - r2):
        return 2 * math.pi * r1 + 2 * math.pi * r2

    alpha = math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1)) * 2
    beta = math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2)) * 2
    outer_arc = (2 * math.pi - alpha) * r1
    inner_arc = beta * r2
    return outer_arc + inner_arc


def _vesica_overlap_area(radius: float, separation: float) -> float:
    if separation <= 0:
        return math.pi * radius * radius
    if separation >= 2 * radius:
        return 0.0
    part = math.acos(separation / (2 * radius))
    return 2 * radius * radius * part - 0.5 * separation * math.sqrt(4 * radius * radius - separation * separation)


class AnnulusSolver(GeometrySolver):
    """Solver for annulus (ring) geometry."""

    def __init__(self, outer_radius: float = 2.0, inner_radius: float = 1.0) -> None:
        outer = max(float(outer_radius), 1e-9)
        inner = max(float(inner_radius), 1e-9)
        if inner >= outer:
            inner = max(outer * 0.5, 1e-9)
        self._state = {"outer_radius": outer, "inner_radius": inner}

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "Annulus"

    @property
    def canonical_key(self) -> str:
        return "annulus"

    @property
    def supported_keys(self) -> set[str]:
        return {"outer_radius", "inner_radius", "ring_width", "outer_diameter", "inner_diameter"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="outer_radius",
                label="Outer Radius (R)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"R",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inner_radius",
                label="Inner Radius (r)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="ring_width",
                label="Ring Width (R - r)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"w = R - r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="outer_diameter",
                label="Outer Diameter",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"D = 2R",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inner_diameter",
                label="Inner Diameter",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"d = 2r",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="area",
                label="Ring Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \pi(R^2 - r^2)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="outer_circumference",
                label="Outer Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"C_{outer} = 2\pi R",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inner_circumference",
                label="Inner Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"C_{inner} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="radius_ratio",
                label="Radius Ratio (R / r)",
                unit="",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"\rho = \frac{R}{r}",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for annulus")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        outer = canonical["outer_radius"]
        inner = canonical["inner_radius"]
        formula = ""

        if key == "outer_radius":
            if value <= inner:
                return SolveResult.invalid(key, value, "Outer radius must exceed inner radius")
            outer = value
            formula = "R = R"
        elif key == "inner_radius":
            if value >= outer:
                return SolveResult.invalid(key, value, "Inner radius must be less than outer radius")
            inner = value
            formula = "r = r"
        elif key == "ring_width":
            new_inner = outer - value
            if new_inner <= 0 or new_inner >= outer:
                return SolveResult.invalid(key, value, "Ring width invalid for current outer radius")
            inner = new_inner
            formula = "r = R - w"
        elif key == "outer_diameter":
            outer = value / 2
            if outer <= inner:
                return SolveResult.invalid(key, value, "Outer diameter too small")
            formula = "R = D/2"
        elif key == "inner_diameter":
            inner = value / 2
            if inner >= outer:
                return SolveResult.invalid(key, value, "Inner diameter too large")
            formula = "r = d/2"

        canonical["outer_radius"] = outer
        canonical["inner_radius"] = inner
        self._state = canonical

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=formula)
        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        outer = canonical["outer_radius"]
        inner = canonical["inner_radius"]
        if outer <= 0 or inner <= 0 or inner >= outer:
            return {}

        ring_width = outer - inner
        return {
            "outer_radius": outer,
            "inner_radius": inner,
            "ring_width": ring_width,
            "outer_diameter": outer * 2,
            "inner_diameter": inner * 2,
            "area": math.pi * (outer * outer - inner * inner),
            "outer_circumference": 2 * math.pi * outer,
            "inner_circumference": 2 * math.pi * inner,
            "radius_ratio": outer / inner,
        }

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="annulus",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
            )
        ]
        return Declaration(
            title=title
            or f"Annulus (R={canonical['outer_radius']:.4f}, r={canonical['inner_radius']:.4f})",
            forms=forms,
            metadata={"solver": "AnnulusSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("outer_radius") is not None:
                canonical["outer_radius"] = float(canonical_value["outer_radius"])
            if canonical_value.get("inner_radius") is not None:
                canonical["inner_radius"] = float(canonical_value["inner_radius"])
        else:
            try:
                canonical["outer_radius"] = float(canonical_value)
            except (TypeError, ValueError):
                pass
        self._state = canonical
        return canonical

    def get_derivation(self) -> str:
        return ANNULUS_DERIVATION


class CrescentSolver(GeometrySolver):
    """Solver for crescent (lune) geometry."""

    def __init__(self, outer_radius: float = 3.0, inner_radius: float = 1.5, offset: float = 1.0) -> None:
        outer = max(float(outer_radius), 1e-9)
        inner = max(float(inner_radius), 1e-9)
        if inner >= outer:
            inner = max(outer * 0.5, 1e-9)
        self._state = {
            "outer_radius": outer,
            "inner_radius": inner,
            "offset": max(float(offset), 0.0),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "Crescent"

    @property
    def canonical_key(self) -> str:
        return "crescent"

    @property
    def supported_keys(self) -> set[str]:
        return {"outer_radius", "inner_radius", "offset", "outer_diameter", "inner_diameter"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="outer_radius",
                label="Outer Radius (R)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"R",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inner_radius",
                label="Inner Radius (r)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="offset",
                label="Center Offset (d)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"d",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="outer_diameter",
                label="Outer Diameter",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"D_R = 2R",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inner_diameter",
                label="Inner Diameter",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"D_r = 2r",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="intersection_area",
                label="Overlap Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=(
                    r"A_{\cap} = R^2\cos^{-1}\!\frac{d^2+R^2-r^2}{2dR} + r^2\cos^{-1}\!\frac{d^2+r^2-R^2}{2dr} "
                    r"- \tfrac{1}{2}\sqrt{(-d+R+r)(d+R-r)(d-R+r)(d+R+r)}"
                ),
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="crescent_area",
                label="Crescent Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A_{cres} = \pi R^2 - A_{\cap}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Crescent Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = (2\pi-\alpha)R + \beta r",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for crescent")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        outer = canonical["outer_radius"]
        inner = canonical["inner_radius"]
        offset = canonical["offset"]
        formula = ""

        if key == "outer_radius":
            if value <= inner:
                return SolveResult.invalid(key, value, "Outer radius must exceed inner radius")
            outer = value
            formula = "R = R"
        elif key == "inner_radius":
            if value >= outer:
                return SolveResult.invalid(key, value, "Inner radius must be less than outer radius")
            inner = value
            formula = "r = r"
        elif key == "offset":
            if value < 0:
                return SolveResult.invalid(key, value, "Offset must be non-negative")
            offset = value
            formula = "d = d"
        elif key == "outer_diameter":
            outer = value / 2
            if outer <= inner:
                return SolveResult.invalid(key, value, "Outer diameter too small")
            formula = "R = D/2"
        elif key == "inner_diameter":
            inner = value / 2
            if inner >= outer:
                return SolveResult.invalid(key, value, "Inner diameter too large")
            formula = "r = d/2"

        if outer <= inner or inner <= 0 or outer <= 0 or offset < 0:
            return SolveResult.invalid(key, value, "Invalid crescent geometry")

        canonical["outer_radius"] = outer
        canonical["inner_radius"] = inner
        canonical["offset"] = offset
        self._state = canonical

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=formula)
        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        outer = canonical["outer_radius"]
        inner = canonical["inner_radius"]
        offset = canonical["offset"]

        if outer <= inner or inner <= 0 or outer <= 0 or offset < 0:
            return {}

        overlap = _circle_overlap_area(outer, inner, offset)
        crescent_area = math.pi * outer * outer - overlap
        perimeter = _crescent_perimeter(outer, inner, offset)

        return {
            "outer_radius": outer,
            "inner_radius": inner,
            "offset": offset,
            "outer_diameter": outer * 2,
            "inner_diameter": inner * 2,
            "intersection_area": overlap,
            "crescent_area": crescent_area,
            "perimeter": perimeter,
        }

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="crescent",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
            )
        ]
        return Declaration(
            title=title
            or f"Crescent (R={canonical['outer_radius']:.4f}, r={canonical['inner_radius']:.4f})",
            forms=forms,
            metadata={"solver": "CrescentSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("outer_radius") is not None:
                canonical["outer_radius"] = float(canonical_value["outer_radius"])
            if canonical_value.get("inner_radius") is not None:
                canonical["inner_radius"] = float(canonical_value["inner_radius"])
            if canonical_value.get("offset") is not None:
                canonical["offset"] = float(canonical_value["offset"])
        self._state = canonical
        return canonical

    def get_derivation(self) -> str:
        return CRESCENT_DERIVATION


class VesicaPiscisSolver(GeometrySolver):
    """Solver for vesica piscis geometry."""

    def __init__(self, radius: float = 2.0, separation: float | None = None) -> None:
        radius = max(float(radius), 1e-9)
        sep = radius if separation is None else max(float(separation), 1e-9)
        if sep > 2 * radius:
            sep = radius
        self._state = {"radius": radius, "separation": sep}

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "VesicaPiscis"

    @property
    def canonical_key(self) -> str:
        return "vesica_piscis"

    @property
    def supported_keys(self) -> set[str]:
        return {"radius", "diameter", "separation"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="radius",
                label="Circle Radius",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="diameter",
                label="Diameter",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"d = 2r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="separation",
                label="Center Separation",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"s = r",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="lens_height",
                label="Lens Height",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"h = r\sqrt{3}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="lens_area",
                label="Lens Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = 2r^2\left(\frac{2\pi}{3} - \frac{\sqrt{3}}{2}\right)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Lens Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = 4r\arccos\left(\frac{s}{2r}\right)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="apex_angle",
                label="Arc Angle (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\theta = 120^\circ",
                format_spec=".2f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for vesica piscis")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        radius = canonical["radius"]
        separation = canonical["separation"]
        formula = ""

        if key == "radius":
            radius = value
            formula = "r = r"
        elif key == "diameter":
            radius = value / 2
            formula = "r = d/2"
        elif key == "separation":
            separation = value
            formula = "s = s"

        if separation <= 0 or separation > 2 * radius:
            return SolveResult.invalid(key, value, "Separation must satisfy 0 < s <= 2r")

        canonical["radius"] = radius
        canonical["separation"] = separation
        self._state = canonical

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=formula)
        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        radius = canonical["radius"]
        separation = canonical["separation"]

        if radius <= 0 or separation <= 0 or separation > 2 * radius:
            return {}

        half_sep = separation / 2
        lens_height = 2 * math.sqrt(max(radius * radius - half_sep * half_sep, 0.0))
        area = _vesica_overlap_area(radius, separation)
        angle = 2 * math.acos(min(1.0, max(-1.0, separation / (2 * radius))))
        perimeter = 2 * radius * angle

        return {
            "radius": radius,
            "diameter": radius * 2,
            "separation": separation,
            "lens_height": lens_height,
            "lens_area": area,
            "perimeter": perimeter,
            "apex_angle": math.degrees(angle),
        }

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="vesica_piscis",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
            )
        ]
        return Declaration(
            title=title or f"Vesica Piscis (r={canonical['radius']:.4f})",
            forms=forms,
            metadata={"solver": "VesicaPiscisSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("radius") is not None:
                canonical["radius"] = float(canonical_value["radius"])
            if canonical_value.get("separation") is not None:
                canonical["separation"] = float(canonical_value["separation"])
        self._state = canonical
        return canonical

    def get_derivation(self) -> str:
        return VESICA_PISCIS_DERIVATION


class RoseCurveSolver(GeometrySolver):
    """Solver for rose (rhodonea) curves."""

    def __init__(self, amplitude: float = 2.0, k_value: int = 4) -> None:
        self._state = {
            "amplitude": max(float(amplitude), 1e-9),
            "k_value": max(int(k_value), 1),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "RoseCurve"

    @property
    def canonical_key(self) -> str:
        return "rose_curve"

    @property
    def supported_keys(self) -> set[str]:
        return {"amplitude", "k_value"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="amplitude",
                label="Amplitude (a)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"a",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="k_value",
                label="Harmonic (k)",
                unit="",
                editable=True,
                category="Dimensions",
                formula=r"k",
                format_spec=".0f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="petal_count",
                label="Petal Count",
                unit="",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"p = \begin{cases}k,&k\text{ odd}\\2k,&k\text{ even}\end{cases}",
                format_spec=".0f",
            ),
            PropertyDefinition(
                key="max_radius",
                label="Max Radius",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"r_{max} = a",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="total_area",
                label="Total Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{1}{2}a^2 p",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for rose curve")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        if key == "amplitude":
            canonical["amplitude"] = value
            formula = "a = a"
        else:
            canonical["k_value"] = max(1, int(round(value)))
            formula = "k = k"

        self._state = canonical

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=formula)
        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        amplitude = canonical["amplitude"]
        k_value = canonical["k_value"]

        petals = k_value if k_value % 2 == 1 else 2 * k_value
        return {
            "amplitude": amplitude,
            "k_value": float(k_value),
            "petal_count": float(petals),
            "max_radius": amplitude,
            "total_area": 0.5 * amplitude * amplitude * petals,
        }

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="rose_curve",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
            )
        ]
        return Declaration(
            title=title or f"Rose Curve (a={canonical['amplitude']:.4f}, k={canonical['k_value']})",
            forms=forms,
            metadata={"solver": "RoseCurveSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float | int]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("amplitude") is not None:
                canonical["amplitude"] = float(canonical_value["amplitude"])
            if canonical_value.get("k_value") is not None:
                canonical["k_value"] = max(1, int(round(canonical_value["k_value"])))
        self._state = canonical
        return canonical

    def get_derivation(self) -> str:
        return ROSE_CURVE_DERIVATION


__all__ = [
    "AnnulusSolver",
    "CrescentSolver",
    "VesicaPiscisSolver",
    "RoseCurveSolver",
]
