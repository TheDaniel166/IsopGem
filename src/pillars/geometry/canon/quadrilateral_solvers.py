"""Quadrilateral solvers for Canon migration."""
from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition


QUADRILATERAL_DERIVATION = r"""
Quadrilateral shape calculators.

Quadrilaterals are 4-sided polygons—the most general 2D shapes with straight edges.
They range from highly symmetric (square, rectangle) to completely irregular (trapezoid,
kite, general quadrilateral). Special quadrilaterals (parallelogram, rhombus, rectangle,
square, trapezoid, kite) have unique properties that make them fundamental to geometry,
architecture, and tiling.

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #1: Parallelogram Hierarchy (Opposite Sides Parallel)
═══════════════════════════════════════════════════════════════════════════════════════

**Parallelogram**: Both pairs of opposite sides are parallel (and equal)
• Area: $A = b \times h$ (where h is perpendicular height, not slant side!)
• Opposite angles are equal: $\alpha = \gamma$, $\beta = \delta$
• Adjacent angles sum to 180°: $\alpha + \beta = 180^\circ$
• Diagonals bisect each other (but NOT necessarily equal or perpendicular)

The parallelogram FAMILY (increasing constraints):

1. **General parallelogram**: Opposite sides parallel, sides a ≠ b, angles ≠ 90°

2. **Rectangle**: Parallelogram + all angles 90°
   • $A = \text{length} \times \text{width}$
   • Diagonals are EQUAL ($d_1 = d_2$)

3. **Rhombus**: Parallelogram + all sides equal (a = b)
   • $A = a^2\sin(\theta)$ where θ is interior angle
   • Diagonals are PERPENDICULAR ($d_1 \perp d_2$)
   • Area also = $(d_1 d_2)/2$ (half the product of diagonals)

4. **Square**: Rectangle + Rhombus (all sides equal + all angles 90°)
   • $A = s^2$
   • Diagonals are equal AND perpendicular ($d = s\sqrt{2}$)

**Venn diagram logic**:
  Square ⊆ Rectangle ⊆ Parallelogram
  Square ⊆ Rhombus ⊆ Parallelogram
  Square = Rectangle ∩ Rhombus

Every square is a rectangle; not every rectangle is a square!

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #2: Shoelace Formula (Area of Any Polygon from Coordinates)
═══════════════════════════════════════════════════════════════════════════════════════

Given vertices (x₁,y₁), (x₂,y₂), ..., (xₙ,yₙ) in order (counterclockwise or clockwise):

**Shoelace Formula** (also called surveyor's formula):

  $A = \frac{1}{2} \left|\sum(x_i y_{i+1} - x_{i+1} y_i)\right|$

  where indices wrap around ($x_{n+1} = x_1$, $y_{n+1} = y_1$)

Expanded for quadrilateral:

  $A = \frac{1}{2} |x_1y_2 - x_2y_1 + x_2y_3 - x_3y_2 + x_3y_4 - x_4y_3 + x_4y_1 - x_1y_4|$

**Why "shoelace"?** If you write coordinates in two columns and draw diagonal lines:

  x₁  y₁  ↘
  x₂  y₂  ↘
  x₃  y₃  ↘
  x₄  y₄  ↘
  x₁  y₁  (wrap)

You multiply along the diagonals (like lacing a shoe!):
• Rightward diagonals: +x₁y₂, +x₂y₃, +x₃y₄, +x₄y₁
• Leftward diagonals: -x₂y₁, -x₃y₂, -x₄y₃, -x₁y₄
• Sum them, take absolute value, divide by 2 → area!

**Derivation** (via Green's theorem):
The shoelace formula is equivalent to:

  $A = \iint dA = \frac{1}{2} \oint (x\,dy - y\,dx)$

Integrating around the polygon boundary.

**Sign convention**: If vertices are counterclockwise, result is positive; if clockwise,
result is negative. Taking absolute value gives area regardless of orientation.

**Applications**:
• GIS (Geographic Information Systems): Calculate land parcel areas from GPS coordinates
• Computer graphics: Determine if polygon is convex, find area for rendering
• Surveying: Compute field areas from surveyor's measurements

═══════════════════════════════════════════════════════════════════════════════════════
AHA MOMENT #3: Trapezoid and Kite (Non-Parallelogram Quadrilaterals)
═══════════════════════════════════════════════════════════════════════════════════════

Not all quadrilaterals are parallelograms! Two important exceptions:

**Trapezoid** (US) / Trapezium (UK): ONE pair of opposite sides parallel
• Parallel sides called "bases" (b₁, b₂)
• Non-parallel sides called "legs"
• **Area**: $A = \frac{(b_1 + b_2)h}{2}$  (average of bases × height)

**Isosceles trapezoid**: Legs are equal, base angles are equal
• Diagonals are EQUAL (like rectangle)
• Symmetric about perpendicular bisector of bases

**Kite**: TWO pairs of adjacent sides are equal
• Sides: a, a, b, b (adjacent pairs equal, not opposite!)
• One diagonal is the axis of symmetry
• Diagonals are PERPENDICULAR
• **Area**: $A = \frac{d_1 d_2}{2}$ (half the product of diagonals, like rhombus!)

**Rhombus vs. Kite**:
• Rhombus: ALL four sides equal (special parallelogram)
• Kite: Only adjacent sides equal (NOT a parallelogram)
• Both have perpendicular diagonals!

**Cyclic quadrilateral**: All four vertices lie on a circle (inscribed)
• **Brahmagupta's formula** (area from side lengths a,b,c,d):
    $A = \sqrt{(s-a)(s-b)(s-c)(s-d)}$  where $s = (a+b+c+d)/2$
  (This is Heron's formula generalized to quadrilaterals! Only works if cyclic.)
• Opposite angles sum to 180°: $\alpha + \gamma = 180^\circ$, $\beta + \delta = 180^\circ$

**Tangential quadrilateral**: All four sides are tangent to an inscribed circle
• Sum of opposite sides are equal: $a + c = b + d$ (Pitot's theorem)

**Bicentric quadrilateral**: Both inscribed AND circumscribed (cyclic + tangential)
• Very special! Examples: square, isosceles trapezoid with specific ratios

═══════════════════════════════════════════════════════════════════════════════════════
📦 HERMETIC SIGNIFICANCE 📦
═══════════════════════════════════════════════════════════════════════════════════════

Quadrilaterals embody **Balance, Opposition, and the Material World**:

• **Four Elements / Four Directions**: The quadrilateral is the geometry of QUATERNARY
  division—Earth/Air/Fire/Water, NESW, Spring/Summer/Fall/Winter. Four corners = four
  fixed points anchoring reality. The square (most symmetric) is Earth; the kite
  (dynamic, airborne) is Air.

• **Parallelogram as Shearing**: A rectangle sheared into a parallelogram represents
  *stress* and *strain* in materials. The parallelogram is a deformed square—it's
  the geometry of *matter under pressure*. In physics, shear stress creates
  parallelogram deformation (not rotation, not compression, but SKEWING).

• **Rhombus as Diamond**: The rhombus (◆) is the diamond shape—compressed square,
  stretched along one diagonal. In alchemy, the rhombus represents sulfur (🜗, the
  active/masculine principle). The rhombus has TENSION (perpendicular diagonals create
  internal stress, like stretched fabric).

• **Kite as Flight**: The kite shape is asymmetric (unlike rhombus) but still has
  perpendicular diagonals. It's the geometry of DIRECTED MOTION (the kite points
  somewhere). In heraldry, the kite shield is for defense in one direction. The kite
  is the rhombus made purposeful.

• **Trapezoid as Transition**: The trapezoid (one pair parallel) is the IN-BETWEEN
  form—not fully parallelogram (which would have TWO pairs parallel), not fully
  irregular. It's the geometry of *gradual change*, of ramps and pyramids (side view
  of pyramid = trapezoid). Architecturally, trapezoids mediate between different
  levels (staircases, amphitheaters).

Quadrilaterals teach: **Four points create structure; symmetry determines stability.** 📦
"""

EPSILON = 1e-7


def _clamp(value: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def _shoelace_area(points: Tuple[Tuple[float, float], ...]) -> float:
    area = 0.0
    n = len(points)
    for idx in range(n):
        x1, y1 = points[idx]
        x2, y2 = points[(idx + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def _circle_intersections(
    c1: Tuple[float, float],
    r1: float,
    c2: Tuple[float, float],
    r2: float,
) -> List[Tuple[float, float]]:
    x1, y1 = c1
    x2, y2 = c2
    dx = x2 - x1
    dy = y2 - y1
    d = math.hypot(dx, dy)
    if d < EPSILON:
        return []
    if d > r1 + r2 + EPSILON:
        return []
    if d < abs(r1 - r2) - EPSILON:
        return []

    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h_sq = r1 * r1 - a * a
    if h_sq < -EPSILON:
        return []
    h_sq = max(h_sq, 0.0)
    h = math.sqrt(h_sq)
    xm = x1 + a * dx / d
    ym = y1 + a * dy / d

    rx = -dy * (h / d)
    ry = dx * (h / d)
    p1 = (xm + rx, ym + ry)
    p2 = (xm - rx, ym - ry)
    if _distance(p1, p2) < EPSILON:
        return [p1]
    return [p1, p2]


class ParallelogramSolver(GeometrySolver):
    """Solver for parallelogram geometry."""

    def __init__(self, base: float = 4.0, side: float = 3.0, angle_deg: float = 60.0) -> None:
        angle_deg = angle_deg if 0 < angle_deg < 180 else 60.0
        height = side * math.sin(math.radians(angle_deg))
        self._state = {
            "base": max(float(base), 1e-9),
            "side": max(float(side), 1e-9),
            "height": height,
            "angle_deg": angle_deg,
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "Parallelogram"

    @property
    def canonical_key(self) -> str:
        return "parallelogram"

    @property
    def supported_keys(self) -> set[str]:
        return {"base", "side", "height", "angle_deg"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="base",
                label="Base",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="side",
                label="Side",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"s",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Height",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"h = s\sin\theta",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="angle_deg",
                label="Included Angle (°)",
                unit="°",
                editable=True,
                category="Angles",
                formula=r"\theta",
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
                formula=r"P = 2(b + s)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = b h = bs\sin\theta",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="diagonal_short",
                label="Short Diagonal",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"d_{short} = \sqrt{b^2 + s^2 - 2bs\cos\theta}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="diagonal_long",
                label="Long Diagonal",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"d_{long} = \sqrt{b^2 + s^2 + 2bs\cos\theta}",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for parallelogram")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value

        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid parallelogram geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="parallelogram", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title
            or f"Parallelogram (b={canonical['base']:.4f}, s={canonical['side']:.4f})",
            forms=forms,
            metadata={"solver": "ParallelogramSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float | None]:
        canonical = {
            "base": self._state.get("base"),
            "side": self._state.get("side"),
            "height": self._state.get("height"),
            "angle_deg": self._state.get("angle_deg"),
        }
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state.update({k: v for k, v in canonical.items() if v is not None})
        return canonical

    def _compute_metrics(self, canonical: dict[str, float | None]) -> Optional[dict[str, dict[str, float]]]:
        base = canonical.get("base")
        side = canonical.get("side")
        height = canonical.get("height")
        angle = canonical.get("angle_deg")

        if angle is not None and not (0 < angle < 180):
            return None

        changed = True
        while changed:
            changed = False
            if side and angle and height is None:
                height = side * math.sin(math.radians(angle))
                changed = True
            if height and side and angle is None:
                ratio = _clamp(height / side, -1.0, 1.0)
                angle = math.degrees(math.asin(ratio))
                changed = True
            if height and angle and side is None:
                sin_val = math.sin(math.radians(angle))
                if sin_val <= EPSILON:
                    return None
                side = height / sin_val
                changed = True

        if side and height and side < height - EPSILON:
            return None

        area = None
        if base and height:
            area = base * height
        elif base and side and angle:
            area = base * side * math.sin(math.radians(angle))

        perimeter = 2 * (base + side) if base and side else None
        diagonal_short = None
        diagonal_long = None
        if base and side and angle:
            rad = math.radians(angle)
            cos_val = math.cos(rad)
            d1 = math.sqrt(max(base * base + side * side - 2 * base * side * cos_val, 0.0))
            d2 = math.sqrt(max(base * base + side * side + 2 * base * side * cos_val, 0.0))
            diagonal_short = min(d1, d2)
            diagonal_long = max(d1, d2)

        canonical_out = {
            "base": base or 0.0,
            "side": side or 0.0,
            "height": height or 0.0,
            "angle_deg": angle or 0.0,
        }
        properties = {
            "base": canonical_out["base"],
            "side": canonical_out["side"],
            "height": canonical_out["height"],
            "angle_deg": canonical_out["angle_deg"],
        }
        if area is not None:
            properties["area"] = area
        if perimeter is not None:
            properties["perimeter"] = perimeter
        if diagonal_short is not None:
            properties["diagonal_short"] = diagonal_short
        if diagonal_long is not None:
            properties["diagonal_long"] = diagonal_long

        return {"canonical": canonical_out, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


class RhombusSolver(GeometrySolver):
    """Solver for rhombus geometry."""

    def __init__(self, side: float = 3.0, angle_deg: float = 60.0) -> None:
        angle_deg = angle_deg if 0 < angle_deg < 180 else 60.0
        height = side * math.sin(math.radians(angle_deg))
        d1 = side * math.sqrt(2 + 2 * math.cos(math.radians(angle_deg)))
        d2 = side * math.sqrt(2 - 2 * math.cos(math.radians(angle_deg)))
        self._state = {
            "side": max(float(side), 1e-9),
            "height": height,
            "angle_deg": angle_deg,
            "diagonal_long": max(d1, d2),
            "diagonal_short": min(d1, d2),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "Rhombus"

    @property
    def canonical_key(self) -> str:
        return "rhombus"

    @property
    def supported_keys(self) -> set[str]:
        return {"side", "height", "angle_deg", "diagonal_long", "diagonal_short"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="side",
                label="Side Length",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"a",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Height",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"h = a\sin\theta",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="angle_deg",
                label="Interior Angle (°)",
                unit="°",
                editable=True,
                category="Angles",
                formula=r"\theta",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="diagonal_long",
                label="Long Diagonal",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"d_1 = a\sqrt{2 + 2\cos\theta}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="diagonal_short",
                label="Short Diagonal",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"d_2 = a\sqrt{2 - 2\cos\theta}",
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
                formula=r"P = 4a",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = a^2\sin\theta = \tfrac{d_1 d_2}{2}",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for rhombus")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid rhombus geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="rhombus", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title or f"Rhombus (a={canonical['side']:.4f})",
            forms=forms,
            metadata={"solver": "RhombusSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float | None]:
        canonical = {
            "side": self._state.get("side"),
            "height": self._state.get("height"),
            "angle_deg": self._state.get("angle_deg"),
            "diagonal_long": self._state.get("diagonal_long"),
            "diagonal_short": self._state.get("diagonal_short"),
        }
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state.update({k: v for k, v in canonical.items() if v is not None})
        return canonical

    def _compute_metrics(self, canonical: dict[str, float | None]) -> Optional[dict[str, dict[str, float]]]:
        angle = canonical.get("angle_deg")
        if angle is not None and not (0 < angle < 180):
            return None

        d_long = canonical.get("diagonal_long")
        d_short = canonical.get("diagonal_short")
        if d_long and d_short and d_long < d_short:
            d_long, d_short = d_short, d_long

        side = canonical.get("side")
        height = canonical.get("height")

        if d_long and d_short:
            side = 0.5 * math.sqrt(d_long * d_long + d_short * d_short)
            cos_val = (d_long * d_long - d_short * d_short) / (d_long * d_long + d_short * d_short)
            angle = math.degrees(math.acos(_clamp(cos_val, -1.0, 1.0)))
            height = side * math.sin(math.radians(angle))

        if side and angle and (d_long is None or d_short is None):
            rad = math.radians(angle)
            d1 = side * math.sqrt(2 + 2 * math.cos(rad))
            d2 = side * math.sqrt(2 - 2 * math.cos(rad))
            d_long = max(d1, d2)
            d_short = min(d1, d2)

        if side and height and angle is None:
            ratio = _clamp(height / side, -1.0, 1.0)
            angle = math.degrees(math.asin(ratio))

        if side and height and side < height - EPSILON:
            return None

        area = None
        if side and height:
            area = side * height
        elif d_long and d_short:
            area = 0.5 * d_long * d_short

        canonical_out = {
            "side": side or 0.0,
            "height": height or 0.0,
            "angle_deg": angle or 0.0,
            "diagonal_long": d_long or 0.0,
            "diagonal_short": d_short or 0.0,
        }
        properties = {
            "side": canonical_out["side"],
            "height": canonical_out["height"],
            "angle_deg": canonical_out["angle_deg"],
            "diagonal_long": canonical_out["diagonal_long"],
            "diagonal_short": canonical_out["diagonal_short"],
        }
        if area is not None:
            properties["area"] = area
        if side:
            properties["perimeter"] = 4 * side

        return {"canonical": canonical_out, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


class TrapezoidSolver(GeometrySolver):
    """Solver for trapezoid geometry."""

    def __init__(self, base_major: float = 6.0, base_minor: float = 4.0, height: float = 2.0) -> None:
        if base_major < base_minor:
            base_major, base_minor = base_minor, base_major
        diff = base_major - base_minor
        leg = math.sqrt(height * height + (diff / 2) * (diff / 2))
        self._state = {
            "base_major": max(float(base_major), 1e-9),
            "base_minor": max(float(base_minor), 1e-9),
            "height": max(float(height), 1e-9),
            "leg_left": leg,
            "leg_right": leg,
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "Trapezoid"

    @property
    def canonical_key(self) -> str:
        return "trapezoid"

    @property
    def supported_keys(self) -> set[str]:
        return {"base_major", "base_minor", "height", "leg_left", "leg_right"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="base_major",
                label="Major Base",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"B",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="base_minor",
                label="Minor Base",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Height",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"h",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="leg_left",
                label="Left Leg",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"\ell_L",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="leg_right",
                label="Right Leg",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"\ell_R",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{(B + b)h}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = B + b + \ell_L + \ell_R",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="midsegment",
                label="Mid-segment",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"m = \tfrac{B + b}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="angle_left_deg",
                label="Left Base Angle (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\alpha_L = \arctan\!\left(\tfrac{h}{\sqrt{\ell_L^2 - h^2}}\right)",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="angle_right_deg",
                label="Right Base Angle (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\alpha_R = \arctan\!\left(\tfrac{h}{\sqrt{\ell_R^2 - h^2}}\right)",
                format_spec=".2f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for trapezoid")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid trapezoid geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="trapezoid", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title
            or f"Trapezoid (B={canonical['base_major']:.4f}, b={canonical['base_minor']:.4f})",
            forms=forms,
            metadata={"solver": "TrapezoidSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float | None]:
        canonical = {
            "base_major": self._state.get("base_major"),
            "base_minor": self._state.get("base_minor"),
            "height": self._state.get("height"),
            "leg_left": self._state.get("leg_left"),
            "leg_right": self._state.get("leg_right"),
        }
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state.update({k: v for k, v in canonical.items() if v is not None})
        return canonical

    def _compute_metrics(self, canonical: dict[str, float | None]) -> Optional[dict[str, dict[str, float]]]:
        base_major = canonical.get("base_major")
        base_minor = canonical.get("base_minor")
        if base_major and base_minor and base_major < base_minor:
            base_major, base_minor = base_minor, base_major

        height = canonical.get("height")
        leg_left = canonical.get("leg_left")
        leg_right = canonical.get("leg_right")

        midsegment = None
        diff = None
        if base_major and base_minor:
            diff = base_major - base_minor
            midsegment = (base_major + base_minor) / 2

        if height and diff is not None:
            if leg_left and leg_left < height - EPSILON:
                return None
            if leg_right and leg_right < height - EPSILON:
                return None

            offset_left = math.sqrt(max(leg_left * leg_left - height * height, 0.0)) if leg_left else None
            offset_right = math.sqrt(max(leg_right * leg_right - height * height, 0.0)) if leg_right else None

            if offset_left is not None and offset_right is not None:
                if abs((offset_left + offset_right) - diff) > 1e-4:
                    return None
            elif offset_left is not None and diff is not None:
                offset_right = diff - offset_left
                if offset_right < -EPSILON:
                    return None
                offset_right = max(offset_right, 0.0)
                leg_right = math.sqrt(height * height + offset_right * offset_right)
            elif offset_right is not None and diff is not None:
                offset_left = diff - offset_right
                if offset_left < -EPSILON:
                    return None
                offset_left = max(offset_left, 0.0)
                leg_left = math.sqrt(height * height + offset_left * offset_left)

        angle_left = None
        angle_right = None
        if height and diff is not None:
            if leg_left:
                offset_left = math.sqrt(max(leg_left * leg_left - height * height, 0.0))
                angle_left = math.degrees(math.atan2(height, offset_left if offset_left > EPSILON else EPSILON))
            if leg_right:
                offset_right = math.sqrt(max(leg_right * leg_right - height * height, 0.0))
                angle_right = math.degrees(math.atan2(height, offset_right if offset_right > EPSILON else EPSILON))

        area = None
        if base_major and base_minor and height:
            area = (base_major + base_minor) * height / 2

        perimeter = None
        if base_major and base_minor and leg_left and leg_right:
            perimeter = base_major + base_minor + leg_left + leg_right

        canonical_out = {
            "base_major": base_major or 0.0,
            "base_minor": base_minor or 0.0,
            "height": height or 0.0,
            "leg_left": leg_left or 0.0,
            "leg_right": leg_right or 0.0,
        }
        properties = {
            "base_major": canonical_out["base_major"],
            "base_minor": canonical_out["base_minor"],
            "height": canonical_out["height"],
            "leg_left": canonical_out["leg_left"],
            "leg_right": canonical_out["leg_right"],
        }
        if midsegment is not None:
            properties["midsegment"] = midsegment
        if angle_left is not None:
            properties["angle_left_deg"] = angle_left
        if angle_right is not None:
            properties["angle_right_deg"] = angle_right
        if area is not None:
            properties["area"] = area
        if perimeter is not None:
            properties["perimeter"] = perimeter

        return {"canonical": canonical_out, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


class IsoscelesTrapezoidSolver(GeometrySolver):
    """Solver for isosceles trapezoid geometry."""

    def __init__(self, base_major: float = 6.0, base_minor: float = 4.0, height: float = 2.0) -> None:
        if base_major < base_minor:
            base_major, base_minor = base_minor, base_major
        delta = (base_major - base_minor) / 2
        leg = math.sqrt(height * height + delta * delta)
        self._state = {
            "base_major": max(float(base_major), 1e-9),
            "base_minor": max(float(base_minor), 1e-9),
            "height": max(float(height), 1e-9),
            "leg": leg,
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "IsoscelesTrapezoid"

    @property
    def canonical_key(self) -> str:
        return "isosceles_trapezoid"

    @property
    def supported_keys(self) -> set[str]:
        return {"base_major", "base_minor", "height", "leg"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="base_major",
                label="Major Base",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"B",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="base_minor",
                label="Minor Base",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Height",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"h",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="leg",
                label="Leg",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"\ell = \sqrt{h^2 + \left(\tfrac{B-b}{2}\right)^2}",
                format_spec=".6f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{(B + b)h}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = B + b + 2\ell",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="midsegment",
                label="Mid-segment",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"m = \tfrac{B + b}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="base_angle_deg",
                label="Base Angle (°)",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                formula=r"\alpha = \arctan\!\left(\tfrac{2h}{B - b}\right)",
                format_spec=".2f",
            ),
            PropertyDefinition(
                key="diagonal",
                label="Diagonal Length",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"d = \sqrt{\ell^2 + B b}",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for isosceles trapezoid")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid isosceles trapezoid geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="isosceles_trapezoid", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title
            or f"Isosceles Trapezoid (B={canonical['base_major']:.4f}, b={canonical['base_minor']:.4f})",
            forms=forms,
            metadata={"solver": "IsoscelesTrapezoidSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float | None]:
        canonical = {
            "base_major": self._state.get("base_major"),
            "base_minor": self._state.get("base_minor"),
            "height": self._state.get("height"),
            "leg": self._state.get("leg"),
        }
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state.update({k: v for k, v in canonical.items() if v is not None})
        return canonical

    def _compute_metrics(self, canonical: dict[str, float | None]) -> Optional[dict[str, dict[str, float]]]:
        base_major = canonical.get("base_major")
        base_minor = canonical.get("base_minor")
        if base_major and base_minor and base_major < base_minor:
            base_major, base_minor = base_minor, base_major

        height = canonical.get("height")
        leg = canonical.get("leg")

        midsegment = None
        delta = None
        if base_major and base_minor:
            delta = (base_major - base_minor) / 2
            midsegment = (base_major + base_minor) / 2

        if delta is not None:
            if height and leg is None:
                leg = math.sqrt(height * height + delta * delta)
            elif leg and height is None:
                if leg <= delta - EPSILON:
                    return None
                height = math.sqrt(max(leg * leg - delta * delta, 0.0))

        base_angle = None
        if height and delta is not None:
            base_angle = math.degrees(math.atan2(height, delta if delta > EPSILON else EPSILON))

        area = None
        if base_major and base_minor and height:
            area = (base_major + base_minor) * height / 2

        perimeter = None
        diagonal = None
        if base_major and base_minor and leg:
            perimeter = base_major + base_minor + 2 * leg
            diagonal = math.sqrt(leg * leg + base_major * base_minor)

        canonical_out = {
            "base_major": base_major or 0.0,
            "base_minor": base_minor or 0.0,
            "height": height or 0.0,
            "leg": leg or 0.0,
        }
        properties = {
            "base_major": canonical_out["base_major"],
            "base_minor": canonical_out["base_minor"],
            "height": canonical_out["height"],
            "leg": canonical_out["leg"],
        }
        if midsegment is not None:
            properties["midsegment"] = midsegment
        if base_angle is not None:
            properties["base_angle_deg"] = base_angle
        if area is not None:
            properties["area"] = area
        if perimeter is not None:
            properties["perimeter"] = perimeter
        if diagonal is not None:
            properties["diagonal"] = diagonal

        return {"canonical": canonical_out, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


class _BaseAdjacentEqualSolver(GeometrySolver):
    convex: bool = True

    def __init__(self, equal_side: float = 3.0, unequal_side: float = 2.0, angle_deg: float = 60.0) -> None:
        if self.convex and not (0 < angle_deg < 180):
            angle_deg = 60.0
        if not self.convex and not (180 < angle_deg < 360):
            angle_deg = 240.0
        self._state = {
            "equal_side": max(float(equal_side), 1e-9),
            "unequal_side": max(float(unequal_side), 1e-9),
            "included_angle_deg": angle_deg,
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def canonical_key(self) -> str:
        return "adjacent_equal"

    @property
    def supported_keys(self) -> set[str]:
        return {"equal_side", "unequal_side", "included_angle_deg"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="equal_side",
                label="Equal Side Length",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"a",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="unequal_side",
                label="Other Side Length",
                unit="units",
                editable=True,
                category="Dimensions",
                formula=r"b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="included_angle_deg",
                label="Angle Between Equal Sides (°)",
                unit="°",
                editable=True,
                category="Angles",
                formula=r"\theta",
                format_spec=".2f",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{d_1 d_2}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = 2(a + b)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="diagonal_long",
                label="Long Diagonal",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"d_1 = \max(AC, BD)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="diagonal_short",
                label="Short Diagonal",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"d_2 = \min(AC, BD)",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for kite/deltoid")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid kite/deltoid geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float | None]:
        canonical = {
            "equal_side": self._state.get("equal_side"),
            "unequal_side": self._state.get("unequal_side"),
            "included_angle_deg": self._state.get("included_angle_deg"),
        }
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state.update({k: v for k, v in canonical.items() if v is not None})
        return canonical

    def _compute_metrics(self, canonical: dict[str, float | None]) -> Optional[dict[str, dict[str, float]]]:
        a = canonical.get("equal_side")
        b = canonical.get("unequal_side")
        angle = canonical.get("included_angle_deg")

        if a is None or b is None or angle is None:
            return None

        if self.convex:
            if not (0 < angle < 180):
                return None
        else:
            if not (180 < angle < 360):
                return None

        theta = math.radians(angle)
        A = (0.0, 0.0)
        B = (a, 0.0)
        D = (a * math.cos(theta), a * math.sin(theta))

        intersections = _circle_intersections(B, b, D, b)
        if not intersections:
            return None

        if self.convex:
            chosen = max(intersections, key=lambda p: p[1])
        else:
            chosen = max(intersections, key=lambda p: -abs(p[1]))

        C = chosen
        points = (A, B, C, D)
        area = _shoelace_area(points)
        diag_ac = _distance(A, C)
        diag_bd = _distance(B, D)
        diagonal_long = max(diag_ac, diag_bd)
        diagonal_short = min(diag_ac, diag_bd)

        canonical_out = {
            "equal_side": a,
            "unequal_side": b,
            "included_angle_deg": angle,
        }
        properties = {
            "equal_side": a,
            "unequal_side": b,
            "included_angle_deg": angle,
            "area": area,
            "perimeter": 2 * (a + b),
            "diagonal_long": diagonal_long,
            "diagonal_short": diagonal_short,
        }
        return {"canonical": canonical_out, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


class KiteSolver(_BaseAdjacentEqualSolver):
    """Solver for convex kite geometry."""

    convex = True

    @property
    def form_type(self) -> str:
        return "Kite"

    @property
    def canonical_key(self) -> str:
        return "kite"

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="kite", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title or "Kite",
            forms=forms,
            metadata={"solver": "KiteSolver"},
        )


class DeltoidSolver(_BaseAdjacentEqualSolver):
    """Solver for concave deltoid (dart) geometry."""

    convex = False

    @property
    def form_type(self) -> str:
        return "Deltoid"

    @property
    def canonical_key(self) -> str:
        return "deltoid"

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="deltoid", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title or "Deltoid",
            forms=forms,
            metadata={"solver": "DeltoidSolver"},
        )


class CyclicQuadrilateralSolver(GeometrySolver):
    """Solver for cyclic quadrilaterals."""

    def __init__(self, side_a: float = 3.0, side_b: float = 4.0, side_c: float = 5.0, side_d: float = 4.0) -> None:
        self._state = {
            "side_a": max(float(side_a), 1e-9),
            "side_b": max(float(side_b), 1e-9),
            "side_c": max(float(side_c), 1e-9),
            "side_d": max(float(side_d), 1e-9),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "CyclicQuadrilateral"

    @property
    def canonical_key(self) -> str:
        return "cyclic_quadrilateral"

    @property
    def supported_keys(self) -> set[str]:
        return {"side_a", "side_b", "side_c", "side_d"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(key="side_a", label="Side a", unit="units", editable=True, category="Dimensions", formula=r"a", format_spec=".6f"),
            PropertyDefinition(key="side_b", label="Side b", unit="units", editable=True, category="Dimensions", formula=r"b", format_spec=".6f"),
            PropertyDefinition(key="side_c", label="Side c", unit="units", editable=True, category="Dimensions", formula=r"c", format_spec=".6f"),
            PropertyDefinition(key="side_d", label="Side d", unit="units", editable=True, category="Dimensions", formula=r"d", format_spec=".6f"),
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
                formula=r"P = a + b + c + d",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="semiperimeter",
                label="Semiperimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"s = \tfrac{a + b + c + d}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \sqrt{(s-a)(s-b)(s-c)(s-d)}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"R = \sqrt{\tfrac{(ab+cd)(ac+bd)(ad+bc)}{16A^2}}",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for cyclic quadrilateral")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid cyclic quadrilateral geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="cyclic_quadrilateral", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title or "Cyclic Quadrilateral",
            forms=forms,
            metadata={"solver": "CyclicQuadrilateralSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state = canonical
        return canonical

    def _compute_metrics(self, canonical: dict[str, float]) -> Optional[dict[str, dict[str, float]]]:
        a = canonical.get("side_a")
        b = canonical.get("side_b")
        c = canonical.get("side_c")
        d = canonical.get("side_d")

        if None in (a, b, c, d):
            return None

        s = 0.5 * (a + b + c + d)
        area_sq = (s - a) * (s - b) * (s - c) * (s - d)
        if area_sq <= 0:
            return None
        area = math.sqrt(area_sq)

        numerator = (a * b + c * d) * (a * c + b * d) * (a * d + b * c)
        denominator = 16 * area_sq
        circumradius = math.sqrt(max(numerator / denominator, 0.0)) if denominator > EPSILON else 0.0

        properties = {
            "side_a": a,
            "side_b": b,
            "side_c": c,
            "side_d": d,
            "perimeter": 2 * s,
            "semiperimeter": s,
            "area": area,
            "circumradius": circumradius,
        }
        return {"canonical": canonical, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


class TangentialQuadrilateralSolver(GeometrySolver):
    """Solver for tangential quadrilaterals."""

    def __init__(self, side_a: float = 4.0, side_b: float = 3.0, side_c: float = 5.0, side_d: float = 6.0, inradius: float = 1.5) -> None:
        self._state = {
            "side_a": max(float(side_a), 1e-9),
            "side_b": max(float(side_b), 1e-9),
            "side_c": max(float(side_c), 1e-9),
            "side_d": max(float(side_d), 1e-9),
            "inradius": max(float(inradius), 1e-9),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "TangentialQuadrilateral"

    @property
    def canonical_key(self) -> str:
        return "tangential_quadrilateral"

    @property
    def supported_keys(self) -> set[str]:
        return {"side_a", "side_b", "side_c", "side_d", "inradius"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(key="side_a", label="Side a", unit="units", editable=True, category="Dimensions", formula=r"a", format_spec=".6f"),
            PropertyDefinition(key="side_b", label="Side b", unit="units", editable=True, category="Dimensions", formula=r"b", format_spec=".6f"),
            PropertyDefinition(key="side_c", label="Side c", unit="units", editable=True, category="Dimensions", formula=r"c", format_spec=".6f"),
            PropertyDefinition(key="side_d", label="Side d", unit="units", editable=True, category="Dimensions", formula=r"d", format_spec=".6f"),
            PropertyDefinition(key="inradius", label="Inradius", unit="units", editable=True, category="Dimensions", formula=r"r", format_spec=".6f"),
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
                formula=r"P = a + b + c + d",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="semiperimeter",
                label="Semiperimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"s = \tfrac{a + b + c + d}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = r\,s \quad (a+c=b+d)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for tangential quadrilateral")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid tangential quadrilateral geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="tangential_quadrilateral", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title or "Tangential Quadrilateral",
            forms=forms,
            metadata={"solver": "TangentialQuadrilateralSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state = canonical
        return canonical

    def _compute_metrics(self, canonical: dict[str, float]) -> Optional[dict[str, dict[str, float]]]:
        a = canonical.get("side_a")
        b = canonical.get("side_b")
        c = canonical.get("side_c")
        d = canonical.get("side_d")
        r = canonical.get("inradius")

        if None in (a, b, c, d, r):
            return None

        if abs((a + c) - (b + d)) > 1e-4:
            return None

        s = 0.5 * (a + b + c + d)
        area = r * s

        properties = {
            "side_a": a,
            "side_b": b,
            "side_c": c,
            "side_d": d,
            "inradius": r,
            "perimeter": 2 * s,
            "semiperimeter": s,
            "area": area,
            "incircle_circumference": 2 * math.pi * r,
        }
        return {"canonical": canonical, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


class BicentricQuadrilateralSolver(GeometrySolver):
    """Solver for bicentric quadrilaterals."""

    def __init__(self, side_a: float = 4.0, side_b: float = 5.0, side_c: float = 6.0, side_d: float = 5.0) -> None:
        self._state = {
            "side_a": max(float(side_a), 1e-9),
            "side_b": max(float(side_b), 1e-9),
            "side_c": max(float(side_c), 1e-9),
            "side_d": max(float(side_d), 1e-9),
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "BicentricQuadrilateral"

    @property
    def canonical_key(self) -> str:
        return "bicentric_quadrilateral"

    @property
    def supported_keys(self) -> set[str]:
        return {"side_a", "side_b", "side_c", "side_d"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(key="side_a", label="Side a", unit="units", editable=True, category="Dimensions", formula=r"a", format_spec=".6f"),
            PropertyDefinition(key="side_b", label="Side b", unit="units", editable=True, category="Dimensions", formula=r"b", format_spec=".6f"),
            PropertyDefinition(key="side_c", label="Side c", unit="units", editable=True, category="Dimensions", formula=r"c", format_spec=".6f"),
            PropertyDefinition(key="side_d", label="Side d", unit="units", editable=True, category="Dimensions", formula=r"d", format_spec=".6f"),
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
                formula=r"P = a + b + c + d",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="semiperimeter",
                label="Semiperimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"s = \tfrac{a + b + c + d}{2}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \sqrt{(s-a)(s-b)(s-c)(s-d)}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"r = \tfrac{A}{s}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"R = \sqrt{\tfrac{(ab+cd)(ac+bd)(ad+bc)}{16A^2}}",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"C_{in} = 2\pi r",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"C_{circ} = 2\pi R",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for bicentric quadrilateral")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid bicentric quadrilateral geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="bicentric_quadrilateral", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title or "Bicentric Quadrilateral",
            forms=forms,
            metadata={"solver": "BicentricQuadrilateralSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state = canonical
        return canonical

    def _compute_metrics(self, canonical: dict[str, float]) -> Optional[dict[str, dict[str, float]]]:
        a = canonical.get("side_a")
        b = canonical.get("side_b")
        c = canonical.get("side_c")
        d = canonical.get("side_d")

        if None in (a, b, c, d):
            return None

        if abs((a + c) - (b + d)) > 1e-4:
            return None

        s = 0.5 * (a + b + c + d)
        area_sq = (s - a) * (s - b) * (s - c) * (s - d)
        if area_sq <= 0:
            return None
        area = math.sqrt(area_sq)
        inradius = area / s

        numerator = (a * b + c * d) * (a * c + b * d) * (a * d + b * c)
        denominator = 16 * area_sq
        circumradius = math.sqrt(max(numerator / denominator, 0.0)) if denominator > EPSILON else 0.0

        properties = {
            "side_a": a,
            "side_b": b,
            "side_c": c,
            "side_d": d,
            "perimeter": 2 * s,
            "semiperimeter": s,
            "area": area,
            "inradius": inradius,
            "circumradius": circumradius,
            "incircle_circumference": 2 * math.pi * inradius,
            "circumcircle_circumference": 2 * math.pi * circumradius,
        }
        return {"canonical": canonical, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


class QuadrilateralSolver(GeometrySolver):
    """General quadrilateral solver using diagonals and included angle."""

    def __init__(self, diagonal_p: float = 5.0, diagonal_q: float = 4.0, diagonal_angle_deg: float = 60.0) -> None:
        self._state = {
            "side_a": 3.0,
            "side_b": 4.0,
            "side_c": 5.0,
            "side_d": 4.0,
            "diagonal_p": max(float(diagonal_p), 1e-9),
            "diagonal_q": max(float(diagonal_q), 1e-9),
            "diagonal_angle_deg": diagonal_angle_deg if 0 < diagonal_angle_deg < 180 else 60.0,
        }

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "QuadrilateralSolver"

    @property
    def canonical_key(self) -> str:
        return "quadrilateral_solver"

    @property
    def supported_keys(self) -> set[str]:
        return {
            "side_a",
            "side_b",
            "side_c",
            "side_d",
            "diagonal_p",
            "diagonal_q",
            "diagonal_angle_deg",
        }

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(key="side_a", label="Side a", unit="units", editable=True, category="Dimensions", formula=r"a", format_spec=".6f"),
            PropertyDefinition(key="side_b", label="Side b", unit="units", editable=True, category="Dimensions", formula=r"b", format_spec=".6f"),
            PropertyDefinition(key="side_c", label="Side c", unit="units", editable=True, category="Dimensions", formula=r"c", format_spec=".6f"),
            PropertyDefinition(key="side_d", label="Side d", unit="units", editable=True, category="Dimensions", formula=r"d", format_spec=".6f"),
            PropertyDefinition(key="diagonal_p", label="Diagonal p", unit="units", editable=True, category="Dimensions", formula=r"p", format_spec=".6f"),
            PropertyDefinition(key="diagonal_q", label="Diagonal q", unit="units", editable=True, category="Dimensions", formula=r"q", format_spec=".6f"),
            PropertyDefinition(key="diagonal_angle_deg", label="Angle Between Diagonals (°)", unit="°", editable=True, category="Angles", formula=r"\phi", format_spec=".2f"),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"A = \tfrac{1}{2}pq\sin\phi",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                formula=r"P = a + b + c + d",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for quadrilateral solver")
        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        canonical = self._state.copy()
        canonical[key] = value
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return SolveResult.invalid(key, value, "Invalid quadrilateral solver geometry")

        self._state.update(metrics["canonical"])

        provenance = SolveProvenance(source_key=key, source_value=value, formula_used=f"{key} = input")
        return SolveResult.success(
            canonical_parameter=self._state.copy(),  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(canonical)
        if metrics is None:
            return {}
        return metrics["properties"]

    def create_declaration(self, canonical_value: Any, *, title: Optional[str] = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self.get_all_properties(canonical)
        params = {self.canonical_key: canonical, **metrics}
        forms = [Form(id="quadrilateral_solver", kind=self.form_type, params=params, dimensional_class=2)]
        return Declaration(
            title=title or "Quadrilateral Solver",
            forms=forms,
            metadata={"solver": "QuadrilateralSolver"},
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            for key in canonical.keys():
                if canonical_value.get(key) is not None:
                    canonical[key] = float(canonical_value[key])
        self._state = canonical
        return canonical

    def _compute_metrics(self, canonical: dict[str, float]) -> Optional[dict[str, dict[str, float]]]:
        p = canonical.get("diagonal_p")
        q = canonical.get("diagonal_q")
        angle = canonical.get("diagonal_angle_deg")

        if p and q and angle and not (0 < angle < 180):
            return None

        area = None
        if p and q and angle:
            area = 0.5 * p * q * math.sin(math.radians(angle))

        perim = 0.0
        missing = False
        for key in ("side_a", "side_b", "side_c", "side_d"):
            val = canonical.get(key)
            if val is None:
                missing = True
                break
            perim += val
        perimeter = None if missing else perim

        properties = {
            "side_a": canonical.get("side_a", 0.0),
            "side_b": canonical.get("side_b", 0.0),
            "side_c": canonical.get("side_c", 0.0),
            "side_d": canonical.get("side_d", 0.0),
            "diagonal_p": canonical.get("diagonal_p", 0.0),
            "diagonal_q": canonical.get("diagonal_q", 0.0),
            "diagonal_angle_deg": canonical.get("diagonal_angle_deg", 0.0),
        }
        if area is not None:
            properties["area"] = area
        if perimeter is not None:
            properties["perimeter"] = perimeter

        return {"canonical": canonical, "properties": properties}

    def get_derivation(self) -> str:
        return QUADRILATERAL_DERIVATION


__all__ = [
    "ParallelogramSolver",
    "RhombusSolver",
    "TrapezoidSolver",
    "IsoscelesTrapezoidSolver",
    "KiteSolver",
    "DeltoidSolver",
    "CyclicQuadrilateralSolver",
    "TangentialQuadrilateralSolver",
    "BicentricQuadrilateralSolver",
    "QuadrilateralSolver",
]
