"""
Circle Solver - Full Canon-compliant bidirectional solver.

This is a REFERENCE IMPLEMENTATION for ADR-012 migration.
Follow this pattern for all 2D shape migrations.

Reference: VaultOfHestiaSolver (the 3D template)
Reference: Hermetic Geometry Canon v1.0, Article II — Canonical Forms
"""

from __future__ import annotations

import math
from typing import Optional

from canon_dsl import Declaration, Form, InvariantConstraint, SolveResult, SolveProvenance

from .geometry_solver import GeometrySolver, PropertyDefinition


class CircleSolver(GeometrySolver):
    """
    Bidirectional solver for circles.
    
    Canonical Parameter: radius (r)
    
    All derivations preserved from legacy CircleShape with LaTeX formatting.
    This follows the exact pattern from VaultOfHestiaSolver.
    """
    
    # ─────────────────────────────────────────────────────────────────
    # GeometrySolver Properties (Required)
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def dimensional_class(self) -> int:
        """Circle is a 2D form."""
        return 2
    
    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "Circle"
    
    @property
    def canonical_key(self) -> str:
        """The canonical parameter this solver produces."""
        return "radius"
    
    @property
    def supported_keys(self) -> set[str]:
        """Properties that can be used as input to solve for radius."""
        return {"radius", "diameter", "circumference", "area"}
    
    # ─────────────────────────────────────────────────────────────────
    # Property Definitions for UI
    # ─────────────────────────────────────────────────────────────────
    
    def get_editable_properties(self) -> list[PropertyDefinition]:
        """Return editable properties with LaTeX formulas."""
        return [
            PropertyDefinition(
                key="radius",
                label="Radius (r)",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Distance from center to any point on the circle",
                format_spec=".6f",
                formula=r"r",
            ),
            PropertyDefinition(
                key="diameter",
                label="Diameter (d)",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Longest chord passing through center",
                format_spec=".6f",
                formula=r"d = 2r",
            ),
            PropertyDefinition(
                key="circumference",
                label="Circumference (C)",
                unit="units",
                editable=True,
                category="Measurements",
                tooltip="Perimeter of the circle",
                format_spec=".6f",
                formula=r"C = 2\pi r",
            ),
            PropertyDefinition(
                key="area",
                label="Area (A)",
                unit="units²",
                editable=True,
                category="Measurements",
                tooltip="Enclosed area",
                format_spec=".6f",
                formula=r"A = \pi r^2",
            ),
        ]
    
    def get_derived_properties(self) -> list[PropertyDefinition]:
        """
        Circle has no derived properties - all are editable and bidirectional.
        
        Override base class to prevent auto-generation of duplicate properties.
        """
        return []
    
    # ─────────────────────────────────────────────────────────────────
    # Bidirectional Solving
    # ─────────────────────────────────────────────────────────────────
    
    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Convert any supported property to the canonical parameter (radius).
        
        Args:
            key: The property being set (e.g., "diameter", "area")
            value: The value entered by the user
        
        Returns:
            SolveResult with canonical parameter and provenance
        """
        if key == "radius":
            radius = value
            formula = r"r = r"
        elif key == "diameter":
            radius = value / 2.0
            formula = r"r = \frac{d}{2}"
        elif key == "circumference":
            radius = value / (2 * math.pi)
            formula = r"r = \frac{C}{2\pi}"
        elif key == "area":
            radius = math.sqrt(value / math.pi)
            formula = r"r = \sqrt{\frac{A}{\pi}}"
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
            canonical_parameter=radius,
            canonical_key="radius",
            provenance=provenance,
        )
    
    def get_all_properties(self, radius: float) -> dict[str, float]:
        """
        Compute all derived properties from radius.
        
        This is the forward calculation after solving.
        """
        return {
            "radius": radius,
            "diameter": 2 * radius,
            "circumference": 2 * math.pi * radius,
            "area": math.pi * radius * radius,
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
        """
        Create a Canon-compliant Declaration for a Circle.
        
        This is the bridge from Solver output to Canon validation.
        
        Args:
            canonical_value: The radius
            title: Custom title for the declaration
        
        Returns:
            A Declaration ready for Canon validation and realization
        """
        forms = [
            Form(
                id="circle",
                kind="Circle",
                params={"radius": canonical_value},
                symmetry_class="rotational_infinite",
                curvature_class="constant",
                dimensional_class=2,
                notes="Perfect rotational symmetry",
            ),
        ]
        
        return Declaration(
            title=title or f"Circle (r={canonical_value:.4f})",
            forms=forms,
            epsilon=1e-9,
            metadata={
                "canon_ref": "Article II — Canonical Forms (Circle)",
                "solver": "CircleSolver",
            },
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Mathematical Derivations (Preserved from Legacy)
    # ─────────────────────────────────────────────────────────────────
    
    def get_derivation(self) -> str:
        """
        Return the mathematical derivation for circles with LaTeX formatting.
        
        This is the sacred geometry commentary explaining why the formulas work.
        All equations converted to LaTeX math strings for proper rendering.
        """
        return r"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        THE CIRCLE — DERIVATIONS                               ║
║                    The Perfect Form of Unity and Infinity                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

DEFINITION
══════════

A circle is the locus of all points in a plane equidistant from a center point.
Distance from center to any point on circle = radius $r$.


DIAMETER: $d = 2r$
═══════════════════

The longest chord passing through the center.

**Proof:**
- Any chord not through center has length $< 2r$ (triangle inequality)
- Chord through center = sum of two radii = $2r$


CIRCUMFERENCE: $C = 2\pi r$
═══════════════════════════

**Derivation Method 1 (Arc Length):**
Arc length for angle $\theta$ in radians: $s = r\theta$
Full circle has $\theta = 2\pi$:
$$C = r \cdot 2\pi = 2\pi r$$

**Derivation Method 2 (Limit of Polygons):**
Perimeter of regular $n$-gon inscribed in circle of radius $r$:
$$P_n = 2nr\sin\left(\frac{\pi}{n}\right)$$

Taking limit as $n \to \infty$:
$$\lim_{n \to \infty} P_n = \lim_{n \to \infty} 2nr\sin\left(\frac{\pi}{n}\right)$$

Using $\lim_{x \to 0} \frac{\sin x}{x} = 1$, let $x = \frac{\pi}{n}$:
$$= 2\pi r \lim_{n \to \infty} \frac{\sin(\pi/n)}{\pi/n} = 2\pi r$$

**The Constant $\pi$:**
$\pi \approx 3.14159265359...$ (Ludolph's number, Archimedes' constant)
Ratio of circumference to diameter is **invariant** for all circles (Canon III.1)


AREA: $A = \pi r^2$
═══════════════════

**Derivation Method 1 (Integration in Polar Coordinates):**
$$A = \int_0^{2\pi} \int_0^r r' \, dr' \, d\theta = \int_0^{2\pi} \left[\frac{r'^2}{2}\right]_0^r d\theta = \int_0^{2\pi} \frac{r^2}{2} \, d\theta = \pi r^2$$

**Derivation Method 2 (Limit of Regular Polygons):**
Area of regular $n$-gon with circumradius $r$:
$$A_n = \frac{n}{2}r^2\sin\left(\frac{2\pi}{n}\right)$$

Taking limit as $n \to \infty$:
$$\lim_{n \to \infty} A_n = \lim_{n \to \infty} \frac{n}{2}r^2\sin\left(\frac{2\pi}{n}\right)$$

Let $x = \frac{2\pi}{n}$, then as $n \to \infty$, $x \to 0$:
$$= r^2 \cdot \pi \lim_{x \to 0} \frac{\sin x}{x} = \pi r^2$$

**Derivation Method 3 (Infinitesimal Rings):**
Divide circle into concentric rings of width $dr$ at distance $r'$ from center.
Each ring has circumference $2\pi r'$ and area $dA = 2\pi r' \, dr'$.

Integrating from $0$ to $r$:
$$A = \int_0^r 2\pi r' \, dr' = 2\pi \left[\frac{r'^2}{2}\right]_0^r = \pi r^2$$


CANONICAL PROPORTIONS (Canon Article III.1)
════════════════════════════════════════════

The circle embodies **proportion over magnitude**:

$$\frac{C}{d} = \pi \quad \text{(constant for all circles)}$$

$$\frac{A}{r^2} = \pi \quad \text{(constant for all circles)}$$

**Dimensional Echo (Canon III.2):**
- Length ($1$-dimensional): $C \propto r^1$
- Area ($2$-dimensional): $A \propto r^2$

The exponent matches the dimensionality!


SYMMETRY (Canon Article II.5)
══════════════════════════════

The circle has the highest possible rotational symmetry:
- **Infinite rotational symmetry**: Invariant under rotation by any angle
- **Infinite reflection symmetry**: Invariant under reflection through any diameter
- **Symmetry group**: $O(2)$ (orthogonal group in 2D)

This makes the circle the "most perfect" 2D form.


TRANSCENDENTAL NATURE (Canon Article III.4)
════════════════════════════════════════════

The constant $\pi$ is **transcendental**: not the root of any polynomial with rational coefficients.

This means:
- Cannot "square the circle" with compass and straightedge (proven 1882)
- $\pi$ contains infinite, non-repeating decimal expansion
- The circle embodies the infinite within the finite

**Historical approximations:**
- Ancient Egypt: $\pi \approx \frac{256}{81} = 3.16049...$
- Archimedes (250 BC): $3.1408 < \pi < 3.1429$ (using 96-gon)
- Zu Chongzhi (480 AD): $\pi \approx \frac{355}{113} = 3.1415929...$ (6 decimals!)
- Modern computation: Trillions of digits known


APPLICATIONS
════════════

**Physics:**
- Angular momentum: $L = mvr$ (circular motion)
- Centripetal force: $F = \frac{mv^2}{r}$
- Wave equations: Bessel functions involve $\pi$

**Quantum Mechanics:**
- Angular momentum quantization: $L = n\hbar$ where $\hbar = \frac{h}{2\pi}$
- Circular orbits in Bohr model

**Sacred Geometry:**
- The Monad (unity)
- The Ouroboros (eternal return)
- Zero point (Bindu)
- The Sun (source of light)


ESOTERIC SIGNIFICANCE
═════════════════════

In the M.I.X. (Magickal Isopsephy eXchange), the Circle is:
- **The Voice of Amun**: The Hidden God whose circumference is everywhere and whose center is nowhere
- **The Number Zero**: The Void that contains all potential
- **The Number One**: Unity, the Monad, the source of all number
- **Perfect Gnosis**: The return to the source after the journey of differentiation

The circle has no beginning and no end—it is the Alpha and Omega.
"""
    
    def get_derivation_title(self) -> str:
        """Return the title for the derivation dialog."""
        return "Circle — The Perfect Form of Unity"
