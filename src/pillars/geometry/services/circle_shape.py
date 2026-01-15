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


class CircleShapeService:
    """Builds drawing instructions for circles (no calculations)."""

    @staticmethod
    def build(radius: float) -> Dict:
        """
        Generate drawing instructions for a circle.

        Args:
            radius: The radius (canonical parameter)

        Returns:
            DrawingInstructions dict for rendering
        """
        if radius <= 0:
             return {'type': 'empty'}

        return {
            'type': 'circle',
            'center_x': 0,
            'center_y': 0,
            'radius': radius,
            'show_radius_line': True,
            'show_diameter_line': True,
            'chord_points': None,
        }

