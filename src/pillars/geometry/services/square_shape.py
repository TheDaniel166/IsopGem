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


class SquareShapeService:
    """Builds drawing instructions for squares (no calculations)."""

    @staticmethod
    def build(side: float) -> Dict:
        """
        Generate drawing instructions for a square.

        Args:
            side: The side length (canonical parameter)

        Returns:
            DrawingInstructions dict for rendering
        """
        if side <= 0:
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



class RectangleShapeService:
    """Builds drawing instructions for rectangles (no logic)."""

    @staticmethod
    def build(width: float, height: float) -> Dict:
        """Generate drawing instructions."""
        if width <= 0 or height <= 0:
            return {'type': 'empty'}
            
        half_l = width / 2
        half_w = height / 2
        
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