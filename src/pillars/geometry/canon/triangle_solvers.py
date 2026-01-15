"""Triangle solvers for Canon DSL migration (Phase 2)."""
from __future__ import annotations

import math
from typing import Any, Optional

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition
from ..services.triangle_math import TriangleMetrics, triangle_metrics_from_sides, valid_triangle_sides


_PHI = (1 + math.sqrt(5)) / 2


def _circumference_from_radius(radius: float) -> float:
    return 2 * math.pi * radius


def _clamp(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


TRIANGLE_DERIVATION = r"""
Triangle shape calculators.

The triangle is the simplest polygon—three sides, three angles, three vertices. It is
the fundamental building block of geometry: every polygon can be decomposed into
triangles (triangulation), and every surface can be approximated by triangular meshes.
The triangle possesses unique rigidity—it is the only polygon that cannot be deformed
without changing side lengths.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Triangle Inequality and Existence (The Fundamental Constraint)
═══════════════════════════════════════════════════════════════════════════════════════

For a triangle with sides a, b, c to EXIST, the **triangle inequality** must hold:

  $a + b > c$    AND    $a + c > b$    AND    $b + c > a$

Intuitively: **The sum of any two sides must exceed the third side.**

Why? Imagine trying to connect three sticks of lengths a, b, c into a triangle:
• If $a + b \le c$, then sticks a and b laid end-to-end cannot reach past stick c
  → they cannot close the triangle ("degenerate" case: collinear points)
• If $a + b = c$ exactly, you get a "flat" triangle (zero area, $180^\circ$ angle)

Equivalently, for sides $a \le b \le c$ (sorted), the single inequality suffices:

  $a + b > c$    (the smallest two must exceed the largest)

**Implications**:
• Given two sides a and b, the third side c must satisfy: $|a - b| < c < a + b$
• This constraint gives triangles RIGIDITY: once you fix three side lengths (and they
  satisfy the inequality), the triangle's shape is UNIQUE (SSS congruence)
• Squares/rectangles can be "parallelogram-ed" (sheared), but triangles CANNOT be
  deformed without changing side lengths → this is why truss bridges use triangles!

**Extension to metrics**: In metric spaces, the triangle inequality generalizes:
  $d(x,z) \le d(x,y) + d(y,z)$    ("direct path $\le$ detour via intermediate point")

This is the FUNDAMENTAL AXIOM of distance—it defines what we mean by "distance."

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Heron's Formula (Area from Sides Alone)
═══════════════════════════════════════════════════════════════════════════════════════

Given three sides a, b, c, the area A can be computed WITHOUT knowing angles or heights:

  **Heron's Formula**:
    $s = \frac{a + b + c}{2}$    (semi-perimeter)
    $A = \sqrt{s(s-a)(s-b)(s-c)}$

This is remarkable because:
• Standard area formula: $A = (\text{base} \times \text{height})/2$  requires altitude computation
• Heron bypasses this—just three sides suffice!

**Proof sketch** (via Law of Cosines):
Law of Cosines: $c^2 = a^2 + b^2 - 2ab\cdot\cos(C)$
⇒ $\cos(C) = \frac{a^2 + b^2 - c^2}{2ab}$
⇒ $\sin^2(C) = 1 - \cos^2(C)$  [after algebra, factor into s terms]

Area: $A = \frac{1}{2}ab\cdot\sin(C)$, then substitute sin(C) from above ⇒ Heron's formula!

**Alternative form** (Brahmagupta's generalization for quadrilaterals):
For cyclic quadrilateral with sides a,b,c,d:
  $A = \sqrt{(s-a)(s-b)(s-c)(s-d)}$    (where $s = \frac{a+b+c+d}{2}$)

Heron's formula is the special case where one side shrinks to zero (quadrilateral
collapses to triangle).

**Computational note**: Direct computation can suffer from floating-point cancellation
when triangle is nearly degenerate. Stable formula (Kahan 2000):

Sort sides: $a \ge b \ge c$
  $A = \frac{1}{4}\sqrt{(a+(b+c))\cdot(c-(a-b))\cdot(c+(a-b))\cdot(a+(b-c))}$

**Special cases**:
• Equilateral (a=b=c): $A = \frac{a^2\sqrt{3}}{4}$    [Heron reduces to this!]
• Right triangle ($c^2=a^2+b^2$): $A = \frac{ab}{2}$    [standard formula]

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Angle Sum Theorem and Degrees of Freedom
═══════════════════════════════════════════════════════════════════════════════════════

For ANY triangle (flat Euclidean plane), the interior angles sum to $180^\circ$:

  $\alpha + \beta + \gamma = 180^\circ$    (or $\pi$ radians)

**Proof** (parallel postulate):
• Draw a line through one vertex parallel to the opposite side
• Alternate interior angles show that the three angles "add up" to a straight line ($180^\circ$)

This is equivalent to Euclid's **Fifth Postulate** (parallel postulate):
  "Through a point not on a line, exactly one line can be drawn parallel to the given line."

**Non-Euclidean geometry**:
• **Spherical** (positive curvature): angle sum > $180^\circ$
  - Example: Triangle on Earth's surface with three $90^\circ$ angles (equator + two meridians)
    → $90^\circ + 90^\circ + 90^\circ = 270^\circ > 180^\circ$
  - Excess: $E = (\alpha+\beta+\gamma) - 180^\circ$ relates to triangle area: $A = R^2\cdot E$ (in radians)

• **Hyperbolic** (negative curvature): angle sum < $180^\circ$
  - Example: Triangles in Poincaré disk get "thinner" as they approach boundary
  - Defect: $D = 180^\circ - (\alpha+\beta+\gamma) > 0$, also proportional to area

**Degrees of freedom**: A triangle in 2D has 6 coordinates (3 vertices × 2 coords)
BUT:
• -2 for translation (x,y position)
• -1 for rotation (θ orientation)
• -1 for scaling (overall size)
• = **2 intrinsic degrees of freedom**

These 2 DOF can be chosen as:
• Two angles (the third is constrained by sum = $180^\circ$)
• Two side ratios (the third ratio is then determined)
• Shape space of triangles is 2-dimensional!

**Rigidity**: Once you specify:
• SSS (3 sides) → triangle fully determined (0 DOF left)
• SAS (2 sides + included angle) → triangle fully determined
• ASA (2 angles + included side) → triangle fully determined
• But AAA (3 angles) → similar triangles (1 DOF: scale)

This is the foundation of **trigonometry** and **surveying** (triangulation).

═══════════════════════════════════════════════════════════════════════════════════════
🔺 HERMETIC SIGNIFICANCE 🔺
═══════════════════════════════════════════════════════════════════════════════════════

The triangle embodies **Trinity, Stability, and the Bridge Between Unity and Plurality**:

• **Holy Trinity**: Father/Son/Spirit, Brahma/Vishnu/Shiva, Maiden/Mother/Crone.
  Three is the first number that creates STRUCTURE (two points = line, three = plane).
  The triangle is the geometric manifestation of the sacred triad.

• **Alchemical Delta (△/▽)**: Upward triangle = Fire/Spirit/Masculine (🜃),
  Downward triangle = Water/Matter/Feminine (🜄). Their union forms the hexagram
  (Star of David, Seal of Solomon)—*As Above, So Below*.

• **Pythagorean Tetraktys**:
      •
     • •
    • • •
   • • • •
  The triangular array of 10 dots ($1+2+3+4 = 10$) representing the sum of all creation.
  Pythagoras swore oaths by the Tetraktys—"the fount of ever-flowing nature."

• **Structural Integrity**: The triangle is RIGID—used in trusses, pyramids, geodesic
  domes. Buckminster Fuller: "Triangles are the strongest shape." This is geometric
  truth: three points define a plane UNIQUELY, no wobble. Spiritually: the trinity
  is STABLE (thesis/antithesis/synthesis, no unresolved duality).

• **The All-Seeing Eye**: In Egyptian/Masonic symbolism, the eye within a triangle
  represents divine omniscience. The triangle as the "eye of God" watching over
  creation (on the US dollar bill: Annuit Cœptis, "He approves our undertakings").

• **Past/Present/Future**: The three vertices of time's flow. Vertex 1 (base left) =
  Past, Vertex 2 (base right) = Future, Vertex 3 (apex) = Present (the synthesis,
  the NOW where past and future meet).

The triangle teaches: **Two creates tension; Three creates resolution.** 🔺

═══════════════════════════════════════════════════════════════════════════════════════
"""


class _SSSTriangleSolver(GeometrySolver):
    """Base solver for triangles defined by three sides."""

    def __init__(self, side_a: float = 1.0, side_b: float = 1.0, side_c: float = 1.0) -> None:
        self._state = {
            "side_a": max(float(side_a), 1e-9),
            "side_b": max(float(side_b), 1e-9),
            "side_c": max(float(side_c), 1e-9),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def supported_keys(self) -> set[str]:
        return {"side_a", "side_b", "side_c"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="side_a",
                label="Side a (BC)",
                unit="units",
                editable=True,
                category="Sides",
                formula=r"a",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="side_b",
                label="Side b (AC)",
                unit="units",
                editable=True,
                category="Sides",
                formula=r"b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="side_c",
                label="Side c (AB)",
                unit="units",
                editable=True,
                category="Sides",
                formula=r"c",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        props = [
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = a + b + c",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \sqrt{s(s-a)(s-b)(s-c)},\ s=\tfrac{a+b+c}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="angle_a_deg",
                label="∠A (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\angle A = \cos^{-1}\!\left(\frac{b^2 + c^2 - a^2}{2bc}\right)",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="angle_b_deg",
                label="∠B (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\angle B = \cos^{-1}\!\left(\frac{a^2 + c^2 - b^2}{2ac}\right)",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="angle_c_deg",
                label="∠C (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\angle C = \cos^{-1}\!\left(\frac{a^2 + b^2 - c^2}{2ab}\right)",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="height_a",
                label="Height to a",
                unit="units",
                editable=False,
                readonly=True,
                category="Heights",
                formula=r"h_a = \frac{2A}{a}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height_b",
                label="Height to b",
                unit="units",
                editable=False,
                readonly=True,
                category="Heights",
                formula=r"h_b = \frac{2A}{b}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height_c",
                label="Height to c",
                unit="units",
                editable=False,
                readonly=True,
                category="Heights",
                formula=r"h_c = \frac{2A}{c}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"r = \frac{A}{s}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"R = \frac{abc}{4A}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]
        return props + self._extra_derived_properties()

    def _extra_derived_properties(self) -> list[PropertyDefinition]:
        return []

    def _validation_error(self, metrics: TriangleMetrics) -> Optional[str]:
        return None

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for triangle")
        if value <= 0:
            return SolveResult.invalid(key, value, "Side lengths must be positive")

        canonical = self._state.copy()
        canonical[key] = value

        if not valid_triangle_sides(canonical["side_a"], canonical["side_b"], canonical["side_c"]):
            return SolveResult.invalid(key, value, "Triangle inequality violated")

        try:
            metrics = triangle_metrics_from_sides(
                canonical["side_a"],
                canonical["side_b"],
                canonical["side_c"],
            )
        except ValueError as exc:
            return SolveResult.invalid(key, value, str(exc))

        error = self._validation_error(metrics)
        if error:
            return SolveResult.invalid(key, value, error)

        self._state = canonical

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=f"{key} = input",
        )

        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = triangle_metrics_from_sides(
            canonical["side_a"],
            canonical["side_b"],
            canonical["side_c"],
        )

        props = {
            "side_a": metrics.side_a,
            "side_b": metrics.side_b,
            "side_c": metrics.side_c,
            "perimeter": metrics.perimeter,
            "area": metrics.area,
            "angle_a_deg": metrics.angle_a,
            "angle_b_deg": metrics.angle_b,
            "angle_c_deg": metrics.angle_c,
            "height_a": metrics.height_a,
            "height_b": metrics.height_b,
            "height_c": metrics.height_c,
            "inradius": metrics.inradius,
            "circumradius": metrics.circumradius,
            "incircle_circumference": _circumference_from_radius(metrics.inradius),
            "circumcircle_circumference": _circumference_from_radius(metrics.circumradius),
        }

        props.update(self._extra_properties(metrics))
        return props

    def _extra_properties(self, metrics: TriangleMetrics) -> dict[str, float]:
        return {}

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            for key in ("side_a", "side_b", "side_c"):
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state = canonical
        return canonical

    def get_derivation(self) -> str:
        return TRIANGLE_DERIVATION


class EquilateralTriangleSolver(GeometrySolver):
    """Equilateral triangle solver (single-parameter)."""

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "EquilateralTriangle"

    @property
    def canonical_key(self) -> str:
        return "side"

    @property
    def supported_keys(self) -> set[str]:
        return {"side", "height", "perimeter", "area", "inradius", "circumradius"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="side",
                label="Side Length",
                unit="units",
                editable=True,
                category="Core",
                formula=r"s",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Height",
                unit="units",
                editable=True,
                category="Core",
                formula=r"h = \tfrac{\sqrt{3}}{2}s",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=True,
                category="Measurements",
                formula=r"P = 3s",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=True,
                category="Measurements",
                formula=r"A = \tfrac{\sqrt{3}}{4}s^2",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=True,
                category="Radii",
                formula=r"r = \tfrac{s}{2\sqrt{3}}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=True,
                category="Radii",
                formula=r"R = \tfrac{s}{\sqrt{3}}",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for equilateral triangle")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        if key == "side":
            side = value
            formula = "s = s"
        elif key == "height":
            side = (2 * value) / math.sqrt(3)
            formula = r"s = \frac{2h}{\sqrt{3}}"
        elif key == "perimeter":
            side = value / 3.0
            formula = r"s = \frac{P}{3}"
        elif key == "area":
            side = math.sqrt((4 * value) / math.sqrt(3))
            formula = r"s = \sqrt{\frac{4A}{\sqrt{3}}}"
        elif key == "inradius":
            side = value * 2 * math.sqrt(3)
            formula = r"s = 2\sqrt{3}\,r"
        elif key == "circumradius":
            side = value * math.sqrt(3)
            formula = r"s = \sqrt{3}\,R"
        else:
            return SolveResult.invalid(key, value, "Unsupported property")

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )

        return SolveResult.success(
            canonical_parameter=side,
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, side: float) -> dict[str, float]:
        height = (side * math.sqrt(3)) / 2
        perimeter = 3 * side
        area = (math.sqrt(3) / 4) * side * side
        inradius = side / (2 * math.sqrt(3))
        circumradius = side / math.sqrt(3)

        return {
            "side": side,
            "height": height,
            "perimeter": perimeter,
            "area": area,
            "inradius": inradius,
            "circumradius": circumradius,
            "incircle_circumference": _circumference_from_radius(inradius),
            "circumcircle_circumference": _circumference_from_radius(circumradius),
        }

    def create_declaration(self, canonical_value: float, *, title: Optional[str] = None) -> Declaration:
        metrics = self.get_all_properties(canonical_value)
        forms = [
            Form(
                id="equilateral_triangle",
                kind=self.form_type,
                params=metrics,
                dimensional_class=2,
                symmetry_class="dihedral_d3",
                notes="Three equal sides and angles",
            )
        ]
        return Declaration(
            title=title or f"Equilateral Triangle (s={canonical_value:.4f})",
            forms=forms,
            metadata={"solver": "EquilateralTriangleSolver"},
        )

    def get_derivation(self) -> str:
        return TRIANGLE_DERIVATION


class RightTriangleSolver(GeometrySolver):
    """Right triangle solver defined by legs (base, height)."""

    def __init__(self, base: float = 1.0, height: float = 1.0) -> None:
        self._state = {
            "base": max(float(base), 1e-9),
            "height": max(float(height), 1e-9),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "RightTriangle"

    @property
    def canonical_key(self) -> str:
        return "right_triangle"

    @property
    def supported_keys(self) -> set[str]:
        return {"base", "height", "hypotenuse", "perimeter", "area"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="base",
                label="Base (a)",
                unit="units",
                editable=True,
                category="Core",
                formula=r"a",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Height (b)",
                unit="units",
                editable=True,
                category="Core",
                formula=r"b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="hypotenuse",
                label="Hypotenuse (c)",
                unit="units",
                editable=True,
                category="Core",
                formula=r"c = \sqrt{a^2 + b^2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=True,
                category="Measurements",
                formula=r"P = a + b + c",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=True,
                category="Measurements",
                formula=r"A = \tfrac{ab}{2}",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"r = \tfrac{a + b - c}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"R = \tfrac{c}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for right triangle")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        base = self._state["base"]
        height = self._state["height"]
        formula = ""

        if key == "base":
            base = value
            formula = "a = a"
        elif key == "height":
            height = value
            formula = "b = b"
        elif key == "hypotenuse":
            hyp = value
            if hyp <= base:
                return SolveResult.invalid(key, value, "Hypotenuse must exceed base")
            height = math.sqrt(hyp * hyp - base * base)
            formula = r"b = \sqrt{c^2 - a^2}"
        elif key == "area":
            area = value
            if base > 0:
                height = (2 * area) / base
                formula = r"b = \frac{2A}{a}"
            else:
                return SolveResult.invalid(key, value, "Base must be positive")
        elif key == "perimeter":
            perimeter = value
            k = perimeter - base
            if k <= 0 or k * k <= base * base:
                return SolveResult.invalid(key, value, "Perimeter too small")
            height = (k * k - base * base) / (2 * k)
            formula = r"b = \frac{K^2 - a^2}{2K},\ K = P - a"

        if base <= 0 or height <= 0:
            return SolveResult.invalid(key, value, "Legs must be positive")

        self._state = {"base": base, "height": height}

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )

        return SolveResult.success(
            canonical_parameter={"base": base, "height": height},  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        base = canonical["base"]
        height = canonical["height"]
        hyp = math.sqrt(base * base + height * height)
        area = 0.5 * base * height
        perimeter = base + height + hyp

        metrics = triangle_metrics_from_sides(base, height, hyp)

        return {
            "base": base,
            "height": height,
            "hypotenuse": hyp,
            "perimeter": perimeter,
            "area": area,
            "inradius": metrics.inradius,
            "circumradius": metrics.circumradius,
            "incircle_circumference": _circumference_from_radius(metrics.inradius),
            "circumcircle_circumference": _circumference_from_radius(metrics.circumradius),
        }

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {
            self.canonical_key: canonical,
            **metrics,
        }
        forms = [
            Form(
                id="right_triangle",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
                notes="Right triangle with perpendicular legs",
            )
        ]
        return Declaration(
            title=title or f"Right Triangle (a={canonical['base']:.4f}, b={canonical['height']:.4f})",
            forms=forms,
            metadata={"solver": "RightTriangleSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("base") is not None:
                canonical["base"] = float(canonical_value["base"])
            if canonical_value.get("height") is not None:
                canonical["height"] = float(canonical_value["height"])
        self._state = canonical
        return canonical

    def get_derivation(self) -> str:
        return TRIANGLE_DERIVATION


class IsoscelesTriangleSolver(GeometrySolver):
    """Isosceles triangle solver defined by base and equal legs."""

    def __init__(self, base: float = 1.0, leg: float = 1.0) -> None:
        self._state = {
            "base": max(float(base), 1e-9),
            "leg": max(float(leg), 1e-9),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "IsoscelesTriangle"

    @property
    def canonical_key(self) -> str:
        return "isosceles_triangle"

    @property
    def supported_keys(self) -> set[str]:
        return {"base", "leg", "height"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="base",
                label="Base (b)",
                unit="units",
                editable=True,
                category="Core",
                formula=r"b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="leg",
                label="Equal Leg (ℓ)",
                unit="units",
                editable=True,
                category="Core",
                formula=r"\ell",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Height",
                unit="units",
                editable=True,
                category="Core",
                formula=r"h = \sqrt{\ell^2 - \left(\tfrac{b}{2}\right)^2}",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = 2\ell + b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{b}{2}\sqrt{\ell^2 - \left(\tfrac{b}{2}\right)^2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="apex_angle_deg",
                label="Apex Angle (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\theta_{apex} = 2\sin^{-1}\!\left(\tfrac{b}{2\ell}\right)",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="base_angle_deg",
                label="Base Angle (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\theta_{base} = \tfrac{180^\circ - \theta_{apex}}{2}",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"r = \tfrac{A}{s},\ s = \ell + \tfrac{b}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"R = \tfrac{\ell^2}{\sqrt{4\ell^2 - b^2}}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for isosceles triangle")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        base = self._state["base"]
        leg = self._state["leg"]
        height = 0.0
        formula = ""

        if key == "base":
            base = value
            formula = "b = b"
        elif key == "leg":
            leg = value
            formula = "ℓ = ℓ"
        elif key == "height":
            height = value
            formula = "h = h"

        if key in {"base", "leg"}:
            if base >= 2 * leg:
                return SolveResult.invalid(key, value, "Base too large for given legs")
            height = math.sqrt(max(leg * leg - (base / 2) ** 2, 0.0))
        elif key == "height":
            if base > 0:
                leg = math.sqrt((base / 2) ** 2 + height * height)
            elif leg > 0:
                base = 2 * math.sqrt(max(leg * leg - height * height, 0.0))

        if base <= 0 or leg <= 0:
            return SolveResult.invalid(key, value, "Invalid base/leg")
        if base >= 2 * leg:
            return SolveResult.invalid(key, value, "Triangle inequality violated")

        self._state = {"base": base, "leg": leg}

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )

        return SolveResult.success(
            canonical_parameter={"base": base, "leg": leg},  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        base = canonical["base"]
        leg = canonical["leg"]

        metrics = triangle_metrics_from_sides(leg, leg, base)

        return {
            "base": base,
            "leg": leg,
            "height": metrics.height_c,
            "perimeter": metrics.perimeter,
            "area": metrics.area,
            "apex_angle_deg": metrics.angle_c,
            "base_angle_deg": metrics.angle_a,
            "inradius": metrics.inradius,
            "circumradius": metrics.circumradius,
            "incircle_circumference": _circumference_from_radius(metrics.inradius),
            "circumcircle_circumference": _circumference_from_radius(metrics.circumradius),
        }

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {
            self.canonical_key: canonical,
            **metrics,
        }
        forms = [
            Form(
                id="isosceles_triangle",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
                notes="Two equal legs with symmetric base",
            )
        ]
        return Declaration(
            title=title or f"Isosceles Triangle (b={canonical['base']:.4f}, ℓ={canonical['leg']:.4f})",
            forms=forms,
            metadata={"solver": "IsoscelesTriangleSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("base") is not None:
                canonical["base"] = float(canonical_value["base"])
            if canonical_value.get("leg") is not None:
                canonical["leg"] = float(canonical_value["leg"])
        self._state = canonical
        return canonical

    def get_derivation(self) -> str:
        return TRIANGLE_DERIVATION


class ScaleneTriangleSolver(_SSSTriangleSolver):
    """Scalene triangle solver (all sides unequal)."""

    def __init__(self) -> None:
        super().__init__(side_a=3.0, side_b=4.0, side_c=5.0)

    @property
    def form_type(self) -> str:
        return "ScaleneTriangle"

    @property
    def canonical_key(self) -> str:
        return "scalene_triangle"

    def _validation_error(self, metrics: TriangleMetrics) -> Optional[str]:
        sides = (metrics.side_a, metrics.side_b, metrics.side_c)
        min_diff = min(abs(sides[i] - sides[j]) for i in range(3) for j in range(i + 1, 3))
        if min_diff <= 1e-4:
            return "Scalene triangle requires all sides to differ"
        return None

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="scalene_triangle",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
                notes="All sides unequal",
            )
        ]
        return Declaration(
            title=title or "Scalene Triangle",
            forms=forms,
            metadata={"solver": "ScaleneTriangleSolver"},
        )


class AcuteTriangleSolver(_SSSTriangleSolver):
    """Acute triangle solver (all angles < 90°)."""

    def __init__(self) -> None:
        super().__init__(side_a=4.0, side_b=5.0, side_c=6.0)

    @property
    def form_type(self) -> str:
        return "AcuteTriangle"

    @property
    def canonical_key(self) -> str:
        return "acute_triangle"

    def _validation_error(self, metrics: TriangleMetrics) -> Optional[str]:
        if any(angle >= 90.0 - 1e-3 for angle in (metrics.angle_a, metrics.angle_b, metrics.angle_c)):
            return "Acute triangle requires all angles < 90°"
        return None

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="acute_triangle",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
                notes="All angles acute",
            )
        ]
        return Declaration(
            title=title or "Acute Triangle",
            forms=forms,
            metadata={"solver": "AcuteTriangleSolver"},
        )


class ObtuseTriangleSolver(_SSSTriangleSolver):
    """Obtuse triangle solver (one angle > 90°)."""

    def __init__(self) -> None:
        super().__init__(side_a=2.0, side_b=3.0, side_c=4.0)

    @property
    def form_type(self) -> str:
        return "ObtuseTriangle"

    @property
    def canonical_key(self) -> str:
        return "obtuse_triangle"

    def _validation_error(self, metrics: TriangleMetrics) -> Optional[str]:
        if max(metrics.angle_a, metrics.angle_b, metrics.angle_c) <= 90.0 + 1e-3:
            return "Obtuse triangle requires an angle > 90°"
        return None

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="obtuse_triangle",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
                notes="One angle obtuse",
            )
        ]
        return Declaration(
            title=title or "Obtuse Triangle",
            forms=forms,
            metadata={"solver": "ObtuseTriangleSolver"},
        )


class HeronianTriangleSolver(_SSSTriangleSolver):
    """Heronian triangle solver (integer sides/area indicator)."""

    def __init__(self) -> None:
        super().__init__(side_a=3.0, side_b=4.0, side_c=5.0)

    @property
    def form_type(self) -> str:
        return "HeronianTriangle"

    @property
    def canonical_key(self) -> str:
        return "heronian_triangle"

    def _extra_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="heronian_flag",
                label="Heronian (1=True)",
                unit="",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"H = 1 \text{ if } a,b,c,A \in \mathbb{Z}",
                format_spec=".0f",
            )
        ]

    def _extra_properties(self, metrics: TriangleMetrics) -> dict[str, float]:
        is_int_area = math.isclose(metrics.area, round(metrics.area), abs_tol=1e-6)
        is_int_sides = all(math.isclose(side, round(side), abs_tol=1e-6) for side in (metrics.side_a, metrics.side_b, metrics.side_c))
        return {"heronian_flag": 1.0 if (is_int_area and is_int_sides) else 0.0}

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [
            Form(
                id="heronian_triangle",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
                notes="Integer-sided triangle with integer area flag",
            )
        ]
        return Declaration(
            title=title or "Heronian Triangle",
            forms=forms,
            metadata={"solver": "HeronianTriangleSolver"},
        )


class IsoscelesRightTriangleSolver(GeometrySolver):
    """45°-45°-90° triangle solver."""

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "IsoscelesRightTriangle"

    @property
    def canonical_key(self) -> str:
        return "leg"

    @property
    def supported_keys(self) -> set[str]:
        return {"leg", "hypotenuse"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="leg",
                label="Leg (ℓ)",
                unit="units",
                editable=True,
                category="Core",
                formula=r"\ell",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="hypotenuse",
                label="Hypotenuse",
                unit="units",
                editable=True,
                category="Core",
                formula=r"c = \ell\sqrt{2}",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = 2\ell + c",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{\ell^2}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Altitude",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"h = \ell",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"r = \tfrac{\ell}{2}\left(2 - \sqrt{2}\right)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"R = \tfrac{c}{2} = \tfrac{\ell}{\sqrt{2}}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for isosceles right triangle")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        if key == "leg":
            leg = value
            formula = "ℓ = ℓ"
        else:
            leg = value / math.sqrt(2)
            formula = r"\ell = \frac{c}{\sqrt{2}}"

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )

        return SolveResult.success(
            canonical_parameter=leg,
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, leg: float) -> dict[str, float]:
        hyp = leg * math.sqrt(2)
        perimeter = 2 * leg + hyp
        area = (leg * leg) / 2
        inradius = (leg / 2) * (2 - math.sqrt(2))
        circumradius = leg / math.sqrt(2)

        return {
            "leg": leg,
            "hypotenuse": hyp,
            "perimeter": perimeter,
            "area": area,
            "height": leg,
            "inradius": inradius,
            "circumradius": circumradius,
            "incircle_circumference": _circumference_from_radius(inradius),
            "circumcircle_circumference": _circumference_from_radius(circumradius),
        }

    def create_declaration(self, canonical_value: float, *, title: Optional[str] = None) -> Declaration:
        metrics = self.get_all_properties(canonical_value)
        forms = [
            Form(
                id="isosceles_right_triangle",
                kind=self.form_type,
                params=metrics,
                dimensional_class=2,
                notes="45-45-90 right triangle",
            )
        ]
        return Declaration(
            title=title or f"Isosceles Right Triangle (ℓ={canonical_value:.4f})",
            forms=forms,
            metadata={"solver": "IsoscelesRightTriangleSolver"},
        )

    def get_derivation(self) -> str:
        return TRIANGLE_DERIVATION


class ThirtySixtyNinetyTriangleSolver(GeometrySolver):
    """30°-60°-90° triangle solver."""

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "ThirtySixtyNinetyTriangle"

    @property
    def canonical_key(self) -> str:
        return "short_leg"

    @property
    def supported_keys(self) -> set[str]:
        return {"short_leg", "long_leg", "hypotenuse"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="short_leg",
                label="Short Leg (opposite 30°)",
                unit="units",
                editable=True,
                category="Core",
                formula=r"s",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="long_leg",
                label="Long Leg (opposite 60°)",
                unit="units",
                editable=True,
                category="Core",
                formula=r"\ell = s\sqrt{3}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="hypotenuse",
                label="Hypotenuse",
                unit="units",
                editable=True,
                category="Core",
                formula=r"c = 2s",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = s + s\sqrt{3} + 2s",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{s^2\sqrt{3}}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"r = \tfrac{s(\sqrt{3}-1)}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"R = s",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for 30-60-90 triangle")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        if key == "short_leg":
            short = value
            formula = "s = s"
        elif key == "long_leg":
            short = value / math.sqrt(3)
            formula = r"s = \frac{\ell}{\sqrt{3}}"
        else:
            short = value / 2
            formula = r"s = \frac{c}{2}"

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )

        return SolveResult.success(
            canonical_parameter=short,
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, short: float) -> dict[str, float]:
        long = short * math.sqrt(3)
        hyp = short * 2
        perimeter = short + long + hyp
        area = (short * long) / 2
        inradius = short * (math.sqrt(3) - 1) / 2
        circumradius = short

        return {
            "short_leg": short,
            "long_leg": long,
            "hypotenuse": hyp,
            "perimeter": perimeter,
            "area": area,
            "inradius": inradius,
            "circumradius": circumradius,
            "incircle_circumference": _circumference_from_radius(inradius),
            "circumcircle_circumference": _circumference_from_radius(circumradius),
        }

    def create_declaration(self, canonical_value: float, *, title: Optional[str] = None) -> Declaration:
        metrics = self.get_all_properties(canonical_value)
        forms = [
            Form(
                id="thirty_sixty_ninety_triangle",
                kind=self.form_type,
                params=metrics,
                dimensional_class=2,
                notes="30-60-90 right triangle",
            )
        ]
        return Declaration(
            title=title or f"30-60-90 Triangle (s={canonical_value:.4f})",
            forms=forms,
            metadata={"solver": "ThirtySixtyNinetyTriangleSolver"},
        )

    def get_derivation(self) -> str:
        return TRIANGLE_DERIVATION


class GoldenTriangleSolver(GeometrySolver):
    """Golden triangle solver (phi-based isosceles)."""

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "GoldenTriangle"

    @property
    def canonical_key(self) -> str:
        return "equal_leg"

    @property
    def supported_keys(self) -> set[str]:
        return {"equal_leg", "base"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="equal_leg",
                label="Equal Leg",
                unit="units",
                editable=True,
                category="Core",
                formula=r"\ell",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="base",
                label="Base",
                unit="units",
                editable=True,
                category="Core",
                formula=r"b = \tfrac{\ell}{\phi}",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="height",
                label="Height",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"h = \sqrt{\ell^2 - \left(\tfrac{b}{2}\right)^2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = 2\ell + b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{b}{2}\sqrt{\ell^2 - \left(\tfrac{b}{2}\right)^2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="apex_angle_deg",
                label="Apex Angle (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\theta_{apex} = 36^\circ",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"r = \tfrac{A}{s},\ s = \ell + \tfrac{b}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"R = \tfrac{\ell^2 b}{4A}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for golden triangle")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        if key == "equal_leg":
            leg = value
            formula = "ℓ = ℓ"
        else:
            leg = value * _PHI
            formula = r"\ell = \phi b"

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )

        return SolveResult.success(
            canonical_parameter=leg,
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, leg: float) -> dict[str, float]:
        base = leg / _PHI
        metrics = triangle_metrics_from_sides(leg, leg, base)

        return {
            "equal_leg": leg,
            "base": base,
            "height": metrics.height_c,
            "perimeter": metrics.perimeter,
            "area": metrics.area,
            "apex_angle_deg": metrics.angle_c,
            "inradius": metrics.inradius,
            "circumradius": metrics.circumradius,
            "incircle_circumference": _circumference_from_radius(metrics.inradius),
            "circumcircle_circumference": _circumference_from_radius(metrics.circumradius),
        }

    def create_declaration(self, canonical_value: float, *, title: Optional[str] = None) -> Declaration:
        metrics = self.get_all_properties(canonical_value)
        forms = [
            Form(
                id="golden_triangle",
                kind=self.form_type,
                params=metrics,
                dimensional_class=2,
                notes="Isosceles triangle with golden ratio proportions",
            )
        ]
        return Declaration(
            title=title or f"Golden Triangle (ℓ={canonical_value:.4f})",
            forms=forms,
            metadata={"solver": "GoldenTriangleSolver"},
        )

    def get_derivation(self) -> str:
        return TRIANGLE_DERIVATION


class TriangleSolver(GeometrySolver):
    """General triangle solver supporting SSS, SAS, ASA/AAS, and SSA inputs."""

    def __init__(self) -> None:
        base_metrics = triangle_metrics_from_sides(3.0, 4.0, 5.0)
        self._state: dict[str, float | None] = {
            "side_a": base_metrics.side_a,
            "side_b": base_metrics.side_b,
            "side_c": base_metrics.side_c,
            "angle_a_deg": base_metrics.angle_a,
            "angle_b_deg": base_metrics.angle_b,
            "angle_c_deg": base_metrics.angle_c,
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "TriangleSolver"

    @property
    def canonical_key(self) -> str:
        return "triangle_solver"

    @property
    def supported_keys(self) -> set[str]:
        return {
            "side_a",
            "side_b",
            "side_c",
            "angle_a_deg",
            "angle_b_deg",
            "angle_c_deg",
        }

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="side_a",
                label="Side a (BC)",
                unit="units",
                editable=True,
                category="Sides",
                formula=r"a",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="side_b",
                label="Side b (AC)",
                unit="units",
                editable=True,
                category="Sides",
                formula=r"b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="side_c",
                label="Side c (AB)",
                unit="units",
                editable=True,
                category="Sides",
                formula=r"c",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="angle_a_deg",
                label="Angle A (°)",
                unit="°",
                editable=True,
                category="Angles",
                formula=r"\angle A = \cos^{-1}\!\left(\frac{b^2 + c^2 - a^2}{2bc}\right)",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="angle_b_deg",
                label="Angle B (°)",
                unit="°",
                editable=True,
                category="Angles",
                formula=r"\angle B = \cos^{-1}\!\left(\frac{a^2 + c^2 - b^2}{2ac}\right)",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="angle_c_deg",
                label="Angle C (°)",
                unit="°",
                editable=True,
                category="Angles",
                formula=r"\angle C = 180^\circ - \angle A - \angle B",
                format_spec=".2f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = a + b + c",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{1}{2}bc\sin A = \sqrt{s(s-a)(s-b)(s-c)}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"r = \tfrac{A}{s}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"R = \tfrac{abc}{4A}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Radii",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for triangle solver")

        if key.startswith("side"):
            if value <= 0:
                return SolveResult.invalid(key, value, "Side lengths must be positive")
        else:
            if not (0 < value < 180):
                return SolveResult.invalid(key, value, "Angles must be between 0 and 180 degrees")

        self._state[key] = value

        solution = self._solve_general(
            self._state.get("side_a"),
            self._state.get("side_b"),
            self._state.get("side_c"),
            self._state.get("angle_a_deg"),
            self._state.get("angle_b_deg"),
            self._state.get("angle_c_deg"),
        )

        if solution is None:
            return SolveResult.invalid(key, value, "Insufficient or conflicting inputs")

        self._state.update(
            {
                "side_a": solution.side_a,
                "side_b": solution.side_b,
                "side_c": solution.side_c,
                "angle_a_deg": solution.angle_a,
                "angle_b_deg": solution.angle_b,
                "angle_c_deg": solution.angle_c,
            }
        )

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=f"{key} = input",
        )

        canonical = {
            "side_a": solution.side_a,
            "side_b": solution.side_b,
            "side_c": solution.side_c,
            "angle_a_deg": solution.angle_a,
            "angle_b_deg": solution.angle_b,
            "angle_c_deg": solution.angle_c,
        }

        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        solution = self._solve_general(
            canonical.get("side_a"),
            canonical.get("side_b"),
            canonical.get("side_c"),
            canonical.get("angle_a_deg"),
            canonical.get("angle_b_deg"),
            canonical.get("angle_c_deg"),
        )

        if solution is None:
            return {}

        return {
            "side_a": solution.side_a,
            "side_b": solution.side_b,
            "side_c": solution.side_c,
            "angle_a_deg": solution.angle_a,
            "angle_b_deg": solution.angle_b,
            "angle_c_deg": solution.angle_c,
            "perimeter": solution.perimeter,
            "area": solution.area,
            "inradius": solution.inradius,
            "circumradius": solution.circumradius,
            "incircle_circumference": _circumference_from_radius(solution.inradius),
            "circumcircle_circumference": _circumference_from_radius(solution.circumradius),
        }

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {
            self.canonical_key: canonical,
            **metrics,
        }
        forms = [
            Form(
                id="triangle_solver",
                kind=self.form_type,
                params=params,
                dimensional_class=2,
                notes="General triangle solver (SSS/SAS/ASA/SSA)",
            )
        ]
        return Declaration(
            title=title or "Triangle Solver",
            forms=forms,
            metadata={"solver": "TriangleSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float | None]:
        canonical = {
            "side_a": self._state.get("side_a"),
            "side_b": self._state.get("side_b"),
            "side_c": self._state.get("side_c"),
            "angle_a_deg": self._state.get("angle_a_deg"),
            "angle_b_deg": self._state.get("angle_b_deg"),
            "angle_c_deg": self._state.get("angle_c_deg"),
        }
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        return canonical

    @staticmethod
    def _solve_general(
        a: float | None,
        b: float | None,
        c: float | None,
        A: float | None,
        B: float | None,
        C: float | None,
    ) -> Optional[TriangleMetrics]:
        if a and b and c:
            try:
                return triangle_metrics_from_sides(a, b, c)
            except ValueError:
                return None

        sas_cases = [
            (a, b, C, "c"),
            (a, c, B, "b"),
            (b, c, A, "a"),
        ]
        for s1, s2, angle, missing_key in sas_cases:
            if s1 and s2 and angle:
                if angle <= 0 or angle >= 180:
                    continue
                rad = math.radians(angle)
                missing = math.sqrt(max(s1 * s1 + s2 * s2 - 2 * s1 * s2 * math.cos(rad), 0.0))
                sides = {"a": a, "b": b, "c": c}
                sides[missing_key] = missing
                try:
                    return triangle_metrics_from_sides(sides["a"], sides["b"], sides["c"])
                except ValueError:
                    return None

        angles = {"A": A, "B": B, "C": C}
        known_angles = [ang for ang in angles.values() if ang is not None]
        if len(known_angles) >= 2:
            total_known = sum(known_angles)
            missing_angle_key = None
            for key, value in angles.items():
                if value is None:
                    missing_angle_key = key
                    break
            missing_value = 180 - total_known if missing_angle_key else 180 - total_known
            if missing_angle_key and missing_value > 0:
                angles[missing_angle_key] = missing_value
            if all(value and value > 0 for value in angles.values()) and abs(sum(angles.values()) - 180) < 1e-4:
                sides = {"a": a, "b": b, "c": c}
                for key, side in sides.items():
                    if side:
                        reference_angle = angles[key.upper()]
                        scale = side / math.sin(math.radians(reference_angle))
                        for target_key in sides.keys():
                            sides[target_key] = scale * math.sin(math.radians(angles[target_key.upper()]))
                        try:
                            return triangle_metrics_from_sides(sides["a"], sides["b"], sides["c"])
                        except ValueError:
                            return None

        ssa_cases = [
            ("a", a, b, B, "b", "B"),
            ("a", a, c, C, "c", "C"),
            ("b", b, a, A, "a", "A"),
            ("b", b, c, C, "c", "C"),
            ("c", c, a, A, "a", "A"),
            ("c", c, b, B, "b", "B"),
        ]
        for base_key, base_side, other_side, _other_angle, _other_key, other_angle_key in ssa_cases:
            base_angle = {"a": A, "b": B, "c": C}[base_key]
            if not (base_side and other_side and base_angle and base_angle > 0):
                continue
            sin_value = math.sin(math.radians(base_angle)) * other_side / base_side
            if sin_value < -1 or sin_value > 1:
                continue
            angle_candidate = math.degrees(math.asin(_clamp(sin_value)))
            alt_candidate = 180 - angle_candidate
            for candidate in (angle_candidate, alt_candidate):
                third_angle = 180 - base_angle - candidate
                if candidate <= 0 or third_angle <= 0:
                    continue
                angles_full = {"A": A, "B": B, "C": C}
                angles_full[base_key.upper()] = base_angle
                angles_full[other_angle_key] = candidate
                missing_key = next(k for k in ("A", "B", "C") if angles_full.get(k) is None)
                angles_full[missing_key] = third_angle
                sides = {"a": a, "b": b, "c": c}
                ref_side = base_side
                ref_angle = angles_full[base_key.upper()]
                scale = ref_side / math.sin(math.radians(ref_angle))
                for label in ("A", "B", "C"):
                    sides[label.lower()] = scale * math.sin(math.radians(angles_full[label]))
                try:
                    return triangle_metrics_from_sides(sides["a"], sides["b"], sides["c"])
                except ValueError:
                    return None

        return None

    def get_derivation(self) -> str:
        return TRIANGLE_DERIVATION
