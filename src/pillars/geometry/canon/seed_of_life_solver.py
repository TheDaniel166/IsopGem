"""Seed of Life solver."""
from __future__ import annotations

import math
from typing import Any, Optional

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition


SEED_OF_LIFE_DERIVATION = r"""
The Seed of Life is a sacred geometric pattern consisting of seven circles arranged
with six-fold symmetry—one central circle surrounded by six circles of equal radius,
each passing through the center circle's center. It is the second stage in constructing
the Flower of Life and represents the seven days of creation, the seven chakras, and
the fundamental pattern of natural growth and organization.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Hexagonal Close Packing (The Most Efficient Pattern)
═══════════════════════════════════════════════════════════════════════════════════════

The Seed of Life arises naturally from the question:

  **How do you pack circles as densely as possible in a plane?**

Answer: **Hexagonal close packing** (HCP)—each circle is surrounded by SIX others.

**Construction**:
1. Draw one circle (radius r)
2. Place compass point on circumference, draw circle of same radius → two circles overlap
3. Repeat at each intersection point around the first circle
4. Result: 1 central circle + 6 surrounding circles = 7 total

**Key properties**:
• All 7 circles have the SAME radius r
• Centers of the 6 outer circles form a regular HEXAGON of side r
• Each outer circle passes through the center circle's center
• Adjacent outer circles create vesica piscis (almond-shaped overlap)

**Packing density**:
For infinite HCP tiling: π/√12 ≈ 0.9069 (about 91% of plane covered by circles)

This is OPTIMAL for 2D circle packing (proven by Lagrange 1773, refined by Thue 1890s).
No packing can be denser!

**Natural occurrences**:
• **Bee honeycombs**: Hexagonal cells (HCP of cylinders in 3D)
• **Atomic crystal lattices**: Graphene (carbon atoms in hexagonal lattice), many metals
• **Bubble rafts**: Soap bubbles self-organize into hexagonal patterns (minimal surface energy)
• **Insect compound eyes**: Ommatidia packed in hexagonal arrays

**6-fold rotational symmetry** (C₆):
Rotate by 60° (360°/6) → pattern looks identical.
This is why snowflakes have 6-fold symmetry (ice crystal lattice is hexagonal)!

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: 6 Petals + 1 Center = 7 (The Creation Week)
═══════════════════════════════════════════════════════════════════════════════════════

The number 7 is deeply symbolic:

**Genesis creation narrative** (6 days of work + 1 day of rest):
• Days 1-6: Six outer circles (active creation, manifestation)
• Day 7: Central circle (rest, stillness, completion)

The Seed of Life encodes: **6 (action) + 1 (being) = 7 (completeness)**

**7 in sacred traditions**:
• **7 chakras**: Root, Sacral, Solar Plexus, Heart, Throat, Third Eye, Crown
• **7 classical planets**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
• **7 musical notes**: Do-Re-Mi-Fa-Sol-La-Ti (diatonic scale)
• **7 colors**: ROYGBIV (rainbow spectrum)
• **7 days of week**: Named after the 7 planets (Sunday = Sun, Monday = Moon, etc.)

**Vesica piscis petals**:
The 6 outer circles create SIX VESICA PISCIS shapes (almond-shaped petals) radiating
from the center. Each petal:
• Height = r√3 (vesica ratio)
• Width = r
• Area = r²(4π/3 - √3) per petal

**Total pattern area**:
• 7 full circles: 7πr²
• But with overlaps subtracted, the "rosette" area (just the visible flower) is smaller
• Central hexagon (connecting outer circle centers): Area = (3√3/2)r²

**Geometric progression**:
• Seed of Life: 7 circles (6 + 1)
• Expand outward: 19 circles (Flower of Life)
• Further: 37, 61, 91... circles (hexagonal number sequence: H_n = 3n(n-1) + 1)

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Flower of Life → Metatron's Cube (All Platonic Solids Hidden)
═══════════════════════════════════════════════════════════════════════════════════════

The Seed of Life is the FOUNDATION for extracting all Platonic solids:

**Construction sequence**:

1. **Seed of Life**: 7 circles (hexagonal symmetry)

2. **Flower of Life**: Expand to 19 circles (or more) in hexagonal pattern

3. **Fruit of Life**: Select 13 circles from the Flower (specific subset):
   • 1 center + 12 surrounding (like clock face)
   • Connect ALL centers with straight lines

4. **Metatron's Cube**: The resulting figure contains:
   • 13 vertices (circle centers)
   • 78 lines connecting them
   • Hidden within: ALL FIVE PLATONIC SOLIDS!

**How to extract the Platonic solids** from Metatron's Cube:
• **Tetrahedron** (4 vertices): Select 4 points forming equilateral triangular base + apex
• **Cube** (8 vertices): Select 8 points forming square faces
• **Octahedron** (6 vertices): Dual of cube (6 points, 8 triangular faces)
• **Dodecahedron** (20 vertices): 12 pentagonal faces (hardest to see!)
• **Icosahedron** (12 vertices): 20 triangular faces (dual of dodecahedron)

This means: **The Seed of Life contains the blueprint for ALL regular 3D forms.**

**Cosmological significance**:
• Plato: The 5 Platonic solids correspond to the 5 elements:
  - Tetrahedron = Fire
  - Cube = Earth
  - Octahedron = Air
  - Icosahedron = Water
  - Dodecahedron = Aether (the cosmos itself)
• The Seed/Flower/Metatron sequence shows: *All manifestation arises from one pattern*
  (the hexagonal seed) by unfolding into complexity.

**Physics connection**:
Crystal lattices, molecular geometries (carbon structures, fullerenes), and even
spacetime foam models in quantum gravity use these geometric patterns!

═══════════════════════════════════════════════════════════════════════════════════════
🌺 HERMETIC SIGNIFICANCE 🌺
═══════════════════════════════════════════════════════════════════════════════════════

The Seed of Life embodies **Primordial Pattern, Genesis, and the Template of Creation**:

• **The First Week**: Seven circles = seven days of creation. The Seed of Life is
  the GEOMETRIC EXPRESSION of Genesis 1. God's work unfolds in 6 stages (6 petals)
  around a central point of stillness (day 7, Sabbath). The pattern is the *cosmos
  in embryo*.

• **The Cosmic Egg**: The Seed of Life is the first recognizable STRUCTURE to emerge
  from the undifferentiated unity (single circle). It's the moment when the One
  becomes the Many while remaining unified (all circles touch the center). This is
  the *World Egg hatching*.

• **The Flower of Life**: Found in ancient temples (Temple of Osiris, Abydos, Egypt;
  Masada, Israel; Golden Temple, India; Forbidden City, China). It's been independently
  discovered by every major civilization because IT'S THE NATURAL PATTERN—the way
  reality organizes itself at fundamental levels (atoms, cells, galaxies).

• **Metatron**: In Kabbalah, Metatron is the "Angel of the Presence," the scribe of
  God, the voice of the divine. Metatron's Cube (derived from the Seed/Flower) is
  the BLUEPRINT OF CREATION—it contains all Platonic solids, therefore all possible
  forms. Metatron is the *Logos made geometric*.

• **The Rosette and the Rose**: The 6-petaled flower is the archetypal ROSE (rosa
  mystica). The rose is the flower of Venus (beauty, love, harmony). In alchemy,
  the rose is the philosopher's stone (perfected matter). In Christianity, the rose
  window in cathedrals represents the cosmos unfolding from God's mind. The Seed of
  Life is the *geometric rose*.

• **Cellular Division**: When a fertilized egg divides: 1 → 2 → 4 → 8 cells (morula),
  they naturally arrange in closest packing (hexagonal). The Seed of Life is literally
  the pattern of EMBRYONIC DEVELOPMENT—the geometry of life itself.

The Seed of Life teaches: **All complexity unfolds from one simple pattern, endlessly
repeated.** 🌺

═══════════════════════════════════════════════════════════════════════════════════════

Compute Seed of Life properties.

DERIVATIONS:
============

Definition:
-----------
7 circles of equal radius r
- 1 central circle
- 6 surrounding circles, centers at distance r from main center
- Centers forming a regular hexagon

Properties:
1. **Total Width (Extents)**: $W = 4r$
   (Distance from left edge of leftmost circle to right edge of rightmost circle)
   Leftmost center = (-r, 0), radius r -> edge at -2r
   Rightmost center = (r, 0), radius r -> edge at 2r
   Span = 4r

2. **Vesica (Petal) Area**: $A_v = r^2(2\pi/3 - \sqrt{3}/2)$
   Intersection of two circles of radius r separated by r.

3. **Flower (Rosette) Area**: $A_{flower} = 6 \times A_v$
   The 6-petaled flower visual pattern.

4. **Flower/Outer Perimeter**: $P = 4\pi r = 2 \times (2\pi r)$
   The arc length of the outer boundary flower shape is actually 4πr.
   Also the perimeter of the cloud of 6 circles.

5. **Enclosing Circle Area**: $A_{encl} = \pi(2r)^2 = 4\pi r^2$
   A circle of radius 2r encloses the entire seed.
"""


class SeedOfLifeSolver(GeometrySolver):
    """Solver for Seed of Life geometry."""

    def __init__(self, radius: float = 10.0) -> None:
        self._state = {"radius": max(float(radius), 1e-9)}

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "SeedOfLife"

    @property
    def canonical_key(self) -> str:
        return "seed_of_life"

    @property
    def supported_keys(self) -> set[str]:
        return {
            "radius",
            "diameter",
            "total_width",
            "circle_area",
            "circle_circumference",
            "vesica_area",
            "flower_area",
        }

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="radius",
                label="Circle Radius (r)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"r",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="diameter",
                label="Circle Diameter (d)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"d = 2r",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="total_width",
                label="Total Width (Extents)",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"W = 4r",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="circle_area",
                label="Single Circle Area",
                unit="units²",
                editable=True,
                category="Dimensions",
                formula=r"A_{\circ} = \pi r^2",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="circle_circumference",
                label="Circle Circumference",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"C_{\circ} = 2\pi r",
                format_spec=".4f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="vesica_height",
                label="Vesica Height",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"h_v = r\sqrt{3}",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="vesica_area",
                label="Vesica (Petal) Area",
                unit="units²",
                editable=True,
                readonly=False,
                category="Measurements",
                formula=r"A_v = r^2(2\pi/3 - \sqrt{3}/2)",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="flower_area",
                label="Flower (Rosette) Area",
                unit="units²",
                editable=True,
                readonly=False,
                category="Measurements",
                formula=r"A_{flower} = 6A_v",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="flower_perimeter",
                label="Flower Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P_{flower} = 4\pi r",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="outer_perimeter",
                label="Outer Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P_{outer} = 4\pi r",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="enclosing_circle_area",
                label="Enclosing Circle Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A_{encl} = \pi(2r)^2",
                format_spec=".4f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for Seed of Life")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        r = canonical["radius"]
        formula = ""

        if key == "radius":
            r = value
            formula = "r = r"
        elif key == "diameter":
            r = value / 2.0
            formula = "r = d/2"
        elif key == "total_width":
            r = value / 4.0
            formula = "r = W/4"
        elif key == "circle_area":
            r = math.sqrt(value / math.pi)
            formula = "r = sqrt(A/pi)"
        elif key == "circle_circumference":
            r = value / (2 * math.pi)
            formula = "r = C/(2pi)"
        elif key == "vesica_area":
            factor = (2 * math.pi / 3) - (math.sqrt(3) / 2)
            r = math.sqrt(value / factor)
            formula = "r = sqrt(A_v / factor)"
        elif key == "flower_area":
            factor = (2 * math.pi / 3) - (math.sqrt(3) / 2)
            # A_flower = 6 * A_v = 6 * r^2 * factor
            r = math.sqrt(value / (6 * factor))
            formula = "r = sqrt(A_flower / (6*factor))"

        canonical["radius"] = r
        self._state = canonical

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=formula)
        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        r = canonical["radius"]
        if r <= 0:
            return {}

        vesica_factor = (2 * math.pi / 3) - (math.sqrt(3) / 2)
        v_area = r * r * vesica_factor
        p_val = 4 * math.pi * r

        return {
            "radius": r,
            "diameter": 2 * r,
            "total_width": 4 * r,
            "circle_area": math.pi * r * r,
            "circle_circumference": 2 * math.pi * r,
            "vesica_height": r * math.sqrt(3),
            "vesica_area": v_area,
            "flower_area": 6 * v_area,
            "flower_perimeter": p_val,
            "outer_perimeter": p_val,
            "enclosing_circle_area": math.pi * (2 * r) ** 2,
        }

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="seed_of_life",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
            )
        ]
        return Declaration(
            title=title or f"Seed of Life (r={canonical['radius']:.4f})",
            forms=forms,
            metadata={"solver": "SeedOfLifeSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("radius") is not None:
                canonical["radius"] = float(canonical_value["radius"])
        else:
            try:
                canonical["radius"] = float(canonical_value)
            except (TypeError, ValueError):
                pass
        self._state = canonical
        return canonical

    def get_derivation(self) -> str:
        return SEED_OF_LIFE_DERIVATION
