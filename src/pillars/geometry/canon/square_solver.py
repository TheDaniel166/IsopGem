"""Square Solver - Canon-compliant bidirectional solver.

Reference implementation following CircleSolver pattern.
All mathematical derivations preserved from legacy SquareShape with LaTeX formatting.
"""

from __future__ import annotations

import math
from typing import Optional

from canon_dsl import Declaration, Form, SolveResult, SolveProvenance

from .geometry_solver import GeometrySolver, PropertyDefinition


class SquareSolver(GeometrySolver):
    """
    Bidirectional solver for squares.
    
    Canonical Parameter: side (s)
    
    All derivations preserved from legacy SquareShape with LaTeX formatting.
    This follows the exact pattern from CircleSolver.
    """

    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "Square"

    @property
    def dimensional_class(self) -> int:
        """Square is a 2D form."""
        return 2
    
    @property
    def canonical_key(self) -> str:
        """The canonical parameter this solver produces."""
        return "side"
    
    @property
    def supported_keys(self) -> set[str]:
        """Properties that can be used as input to solve for side."""
        return {"side", "perimeter", "area", "diagonal"}
    
    # ─────────────────────────────────────────────────────────────────
    # Property Definitions for UI
    # ─────────────────────────────────────────────────────────────────
    
    def get_editable_properties(self) -> list[PropertyDefinition]:
        """Return editable properties with LaTeX formulas."""
        return [
            PropertyDefinition(
                key="side",
                label="Side (s)",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Side length of the square",
                format_spec=".6f",
                formula=r"s",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter (P)",
                unit="units",
                editable=True,
                category="Measurements",
                tooltip="Total perimeter of the square",
                format_spec=".6f",
                formula=r"P = 4s",
            ),
            PropertyDefinition(
                key="area",
                label="Area (A)",
                unit="units²",
                editable=True,
                category="Measurements",
                tooltip="Enclosed area",
                format_spec=".6f",
                formula=r"A = s^2",
            ),
            PropertyDefinition(
                key="diagonal",
                label="Diagonal (d)",
                unit="units",
                editable=True,
                category="Measurements",
                tooltip="Diagonal length",
                format_spec=".6f",
                formula=r"d = s\sqrt{2}",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        """
        Square has no derived properties - all are editable and bidirectional.
        
        Override base class to prevent auto-generation of duplicate properties.
        """
        return []

    def solve_from(self, key: str, value: float) -> SolveResult:
        """Convert any supported property to the canonical parameter (side)."""
        
        if key == "side":
            side = value
            formula = r"s = s"
        elif key == "perimeter":
            side = value / 4.0
            formula = r"s = \frac{P}{4}"
        elif key == "area":
            side = math.sqrt(value)
            formula = r"s = \sqrt{A}"
        elif key == "diagonal":
            side = value / math.sqrt(2)
            formula = r"s = \frac{d}{\sqrt{2}}"
        else:
            return SolveResult.invalid(
                key,
                value,
                f"Unknown property: {key}. Supported: {self.supported_keys}"
            )
        
        # Build provenance for traceability
        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )
        
        return SolveResult.success(
            canonical_parameter=side,
            canonical_key="side",
            provenance=provenance,
        )
    
    def get_all_properties(self, side: float) -> dict[str, float]:
        """Compute all derived properties from side length."""
        return {
            "side": side,
            "perimeter": 4 * side,
            "area": side * side,
            "diagonal": side * math.sqrt(2),
        }
    
    # ─────────────────────────────────────────────────────────────────
    # Declaration Creation (Canon DSL Integration)
    # ─────────────────────────────────────────────────────────────────
    
    def create_declaration(
        self,
        canonical_value: float,
        *,
        title: Optional[str] = None,
    ) -> Declaration:
        """Create a Canon-compliant Declaration for a Square."""
        forms = [
            Form(
                id="square",
                kind="Square",
                params={"side": canonical_value},
                symmetry_class="dihedral_d4",
                curvature_class="piecewise_constant",
                dimensional_class=2,
                notes="Four-fold rotational and reflection symmetry",
            ),
        ]
        
        return Declaration(
            title=title or f"Square (s={canonical_value:.4f})",
            forms=forms,
            epsilon=1e-9,
            metadata={
                "canon_ref": "Article II — Canonical Forms (Square)",
                "solver": "SquareSolver",
            },
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Mathematical Derivations (Preserved from Legacy)
    # ─────────────────────────────────────────────────────────────────
    
    def get_derivation(self) -> str:
        """Return the mathematical derivation for squares with LaTeX formatting."""
        return r"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        THE SQUARE — DERIVATIONS                               ║
║                  The Four-Fold Form of Manifest Stability                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

DEFINITION
══════════

A square is a regular quadrilateral with four equal sides and four right angles.
All sides = $s$, all angles = $90°$.


PERIMETER: $P = 4s$
═════════════════════

Sum of all four sides:
$$P = s + s + s + s = 4s$$


AREA: $A = s^2$
═════════════════════

**Derivation (Grid Decomposition):**
A square with side $s$ contains $s \times s$ unit squares:
$$A = s \cdot s = s^2$$

**Derivation (Integration):**
For a square centered at origin with side $s$:
$$A = \int_{-s/2}^{s/2} \int_{-s/2}^{s/2} dx \, dy = s \cdot s = s^2$$


DIAGONAL: $d = s\sqrt{2}$
═════════════════════════════

**Derivation (Pythagorean Theorem):**
The diagonal forms the hypotenuse of a right triangle with legs $s$:
$$d^2 = s^2 + s^2 = 2s^2$$
$$d = \sqrt{2s^2} = s\sqrt{2}$$

**The First Irrational:** $\sqrt{2} \approx 1.414213...$

This was the first irrational number discovered (~500 BCE, Pythagorean school).

**Proof of Irrationality** (by contradiction):
Assume $\sqrt{2} = \frac{p}{q}$ (rational, in lowest terms).

Then: $2 = \frac{p^2}{q^2}$, so $p^2 = 2q^2$

Therefore $p^2$ is even, so $p$ is even. Let $p = 2k$.

Then: $(2k)^2 = 2q^2$, so $4k^2 = 2q^2$, so $q^2 = 2k^2$

Therefore $q^2$ is even, so $q$ is even.

**Contradiction!** Both $p$ and $q$ are even, but we assumed lowest terms.

Hence $\sqrt{2}$ is irrational (cannot be expressed as a ratio of integers).


AHA MOMENT #1: Four-Fold Symmetry (The Cardinal Cross)
═══════════════════════════════════════════════════════════════════════════════════════

The square has **dihedral symmetry group $D_4$**, order 8:

• **4 rotational symmetries**: Identity, 90°, 180°, 270° (4-fold axis)
• **4 reflection symmetries**: 2 through opposite edge midpoints (horizontal/vertical),
  2 through opposite vertices (diagonal axes)
• Total: 8 symmetry operations

Compare to other quadrilaterals:
• Rectangle: $D_2$ (order 4) → 2 rotations + 2 reflections (no diagonal symmetry)
• Rhombus: $D_2$ (order 4) → 2 rotations + 2 reflections (diagonal axes only)
• Square: $D_4$ (order 8) → combines both edge AND diagonal reflection symmetry!

**The Cardinal Directions**:
• Square orientation defines NSEW (North/South/East/West) in Cartesian geometry
• Four corners = four elements (🜂 Earth, 🜁 Air, 🜄 Water, 🜃 Fire)
• Four seasons, four phases of moon, four gospels, four noble truths

**Tessellation**: Squares tile the plane perfectly (no gaps, no overlaps):
• Each vertex has 4 squares meeting (vertex angle sum: $4 \times 90° = 360°)$
• This is the SIMPLEST monohedral tiling (one shape type)
• Grid/lattice structure: foundation of Cartesian coordinates, graph paper, pixels


AHA MOMENT #2: The $\sqrt{2}$ Diagonal (The First Irrational)
═══════════════════════════════════════════════════════════════════════════════════════

**A4 paper ratio**: International paper sizes (A0, A1, A2...) use $1:\sqrt{2}$ ratio!
• When you fold A4 in half → A5 (aspect ratio preserved: $1/\sqrt{2} : 1 = 1 : \sqrt{2})$
• This self-similar scaling property makes photocopying/resizing lossless

**Silver ratio**: $\delta_s = 1 + \sqrt{2} \approx 2.414$ (related to octagon)


AHA MOMENT #3: Square as Fundamental Unit (The Measure of All)
═══════════════════════════════════════════════════════════════════════════════════════

**Area measurement**: We measure area in "square units" (cm², m², km²) because:
• The square is the UNIT CELL of Cartesian space
• Rectangles are stretched squares: $A = \text{length} \times \text{width}$
• Any polygon can be decomposed into squares (approximately) via grid overlay

**Pythagorean theorem visualization**:
For a right triangle with legs $a$ and $b$, hypotenuse $c$:
$$a^2 + b^2 = c^2$$

This is literally about SQUARES:
• $a^2$: area of square built on side $a$
• $b^2$: area of square built on side $b$
• $c^2$: area of square built on hypotenuse $c$
• The theorem states: area(square on $a$) + area(square on $b$) = area(square on $c$)

Euclid's visual proof (Elements, Book I, Proposition 47) uses actual squares drawn
on each side of a right triangle!

**Square numbers**: $1, 4, 9, 16, 25, 36, 49, 64, 81, 100...$
• $n^2 = n \times n$ ($n$ rows, $n$ columns, dots arranged in square)
• Sum of first $n$ odd numbers = $n^2$:
$$\begin{aligned}
1 &= 1^2 \\
1+3 &= 4 = 2^2 \\
1+3+5 &= 9 = 3^2 \\
1+3+5+7 &= 16 = 4^2
\end{aligned}$$

(Visual: each odd number forms an L-shaped border around the previous square)

**Manhattan distance**: In grid cities (NYC), distance is measured by square grid:
$$d_{\text{Manhattan}} = |\Delta x| + |\Delta y|$$
vs. Euclidean distance:
$$d_{\text{Euclidean}} = \sqrt{\Delta x^2 + \Delta y^2}$$

Squares define the **digital world**: pixels, voxels, chess boards, Minecraft blocks.
The square is the atomic unit of discrete space.


ESOTERIC SIGNIFICANCE
═════════════════════

In the M.I.X. (Magickal Isopsephy eXchange), the Square is:

• **Earth Element (🜃)**: The square represents solidity, foundation, the four corners
  of the world. In alchemy, square = material realm (vs. circle = spiritual realm).
  The alchemical symbol for salt (🜔) is a square bisected by a horizontal line—
  matter crystallized.

• **Squaring the Circle**: The impossible compass-and-straightedge construction
  symbolizes the philosopher's quest to EMBODY spirit (circle, $\pi$) in matter (square).
  Not mathematically possible, but spiritually necessary—the incarnation paradox.

• **Tetragrammaton (יהוה)**: The four-letter name of God (YHWH). Four = manifestation
  into the world (three = divine trinity in heaven, four = embodied in creation).
  The square is the *extension* of the triangle into materiality.

• **Temple Foundation**: Sacred architecture uses square bases:
  - Ka'aba (Mecca): cube (6 squares)
  - New Jerusalem (Revelation): perfect square city, 12,000 stadia per side
  - Roman castrum (military camp): square with cross roads (cardo/decumanus)
  The square provides STABLE FOUNDATION for vertical ascent (axis mundi).

• **Checker/Chess Board**: $8 \times 8 = 64$ squares $(2^6)$ represents the cosmic game board,
  alternating black/white (yin/yang, good/evil, light/dark dualities). Life as
  strategic movement across the grid of fate.

• **The Four Worlds (Kabbalah)**: Atziluth, Briah, Yetzirah, Assiah—emanation,
  creation, formation, action. The square as descent through four planes from
  divine unity to physical multiplicity.

The square teaches: **To manifest is to LIMIT the infinite into definite form.** 🝆
"""
    
    def get_derivation_title(self) -> str:
        """Return the title for the derivation dialog."""
        return "Square — The Four-Fold Form of Manifest Stability"
