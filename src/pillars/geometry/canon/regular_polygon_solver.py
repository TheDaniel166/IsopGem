"""
Geometry Pillar — Regular Polygon Solver.

Bidirectional Canon solver for regular n-gons. Accepts side length (canonical)
with an integer side count and computes area, radii, and angle metrics.

Reference: ADR-010 — Canon DSL Adoption
Reference: ADR-011 — Unified Geometry Viewer
"""
from __future__ import annotations

import math
from typing import Any, Dict

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition


_DEF_SIDE = 1.0


def compute_regular_polygon_metrics(num_sides: int, side_length: float) -> Dict[str, float | dict[int, float]]:
    """Compute core metrics for a regular n-gon from side length.

    Args:
        num_sides: Number of sides (n >= 3)
        side_length: Edge length (s > 0)

    Returns:
        Mapping of derived metrics including perimeter, area, radii, angles, and diagonals.
    """
    n = max(3, int(num_sides))
    s = max(float(side_length), 1e-9)

    apothem = s / (2 * math.tan(math.pi / n))
    circumradius = s / (2 * math.sin(math.pi / n))
    perimeter = n * s
    area = (perimeter * apothem) / 2

    interior_angle = ((n - 2) * 180.0) / n
    exterior_angle = 360.0 / n
    num_diagonals = n * (n - 3) / 2

    # Diagonal lengths per skip (k edges apart). Skip of 1 is an edge; start at 2.
    diagonal_lengths: dict[int, float] = {}
    max_skip = n // 2
    for skip in range(2, max_skip + 1):
        length = s * math.sin(skip * math.pi / n) / math.sin(math.pi / n)
        diagonal_lengths[skip] = length

    shortest_diag = diagonal_lengths.get(2, 0.0)
    # The longest diagonal for even n is skip = n/2; for odd n it is skip = floor(n/2).
    longest_diag = diagonal_lengths.get(max_skip, shortest_diag)

    return {
        "num_sides": float(n),
        "side_length": s,
        "perimeter": perimeter,
        "area": area,
        "apothem": apothem,
        "circumradius": circumradius,
        "wedge_area": area / n,
        "incircle_circumference": 2 * math.pi * apothem,
        "circumcircle_circumference": 2 * math.pi * circumradius,
        "interior_angle": interior_angle,
        "exterior_angle": exterior_angle,
        "num_diagonals": num_diagonals,
        "diagonal_lengths": diagonal_lengths,
        "shortest_diagonal": shortest_diag,
        "longest_diagonal": longest_diag,
    }


def generate_regular_polygon_points(num_sides: int, radius: float) -> list[tuple[float, float]]:
    """Generate vertex coordinates for a regular n-gon centered at the origin."""
    n = max(3, int(num_sides))
    r = max(float(radius), 1e-6)
    points: list[tuple[float, float]] = []
    for i in range(n):
        angle = (2 * math.pi * i / n) - (math.pi / 2)
        points.append((r * math.cos(angle), r * math.sin(angle)))
    return points


class RegularPolygonSolver(GeometrySolver):
    """Canon solver for regular polygons (2D)."""

    def __init__(self, num_sides: int = 6, side_length: float = _DEF_SIDE) -> None:
        self._state: Dict[str, float] = {
            "num_sides": float(max(3, int(num_sides))),
            "side_length": float(side_length if side_length > 0 else _DEF_SIDE),
        }

    # ── GeometrySolver properties ──────────────────────────────────────────
    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "RegularPolygon"

    @property
    def canonical_key(self) -> str:
        return "polygon"

    @property
    def supported_keys(self) -> set[str]:
        base = {
            "num_sides",
            "side_length",
            "perimeter",
            "area",
            "apothem",
            "circumradius",
            "shortest_diagonal",
            "longest_diagonal",
        }
        n = max(3, int(self._state.get("num_sides", 3)))
        diag_keys = {f"diagonal_skip_{skip}" for skip in range(2, (n // 2) + 1)}
        return base | diag_keys

    # ── Property metadata ──────────────────────────────────────────────────
    def get_editable_properties(self) -> list[PropertyDefinition]:
        props = [
            PropertyDefinition(
                key="num_sides",
                label="Number of Sides (n)",
                unit="sides",
                editable=True,
                tooltip="Integer sides (n ≥ 3)",
                format_spec=".0f",
                category="Core",
            ),
            PropertyDefinition(
                key="side_length",
                label="Side Length (s)",
                unit="units",
                editable=True,
                tooltip="Canonical side length",
                format_spec=".6f",
                category="Core",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter (P)",
                unit="units",
                editable=True,
                tooltip="ns",
                format_spec=".6f",
                category="Perimeter",
            ),
            PropertyDefinition(
                key="area",
                label="Area (A)",
                unit="units²",
                editable=True,
                tooltip="A = (ns²) / (4 tan(π/n))",
                format_spec=".6f",
                category="Area",
            ),
            PropertyDefinition(
                key="apothem",
                label="Apothem (a)",
                unit="units",
                editable=True,
                tooltip="a = s / (2 tan(π/n))",
                format_spec=".6f",
                category="Radii",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius (R)",
                unit="units",
                editable=True,
                tooltip="R = s / (2 sin(π/n))",
                format_spec=".6f",
                category="Radii",
            ),
        ]

        # Add per-skip diagonals as editable properties (first-class)
        n = max(3, int(self._state.get("num_sides", 3)))
        max_skip = n // 2
        for skip in range(2, max_skip + 1):
            props.append(
                PropertyDefinition(
                    key=f"diagonal_skip_{skip}",
                    label=f"Diagonal (skip {skip})",
                    unit="units",
                    editable=True,
                    tooltip=f"Diagonal connecting vertices separated by {skip-1} edges",
                    format_spec=".6f",
                    category="Diagonals",
                )
            )

        return props

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="wedge_area",
                label="Wedge Area",
                unit="units²",
                editable=False,
                readonly=True,
                tooltip="Sector area = A / n",
                format_spec=".6f",
                category="Area",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                tooltip="2πa",
                format_spec=".6f",
                category="Radii",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                readonly=True,
                tooltip="2πR",
                format_spec=".6f",
                category="Radii",
            ),
            PropertyDefinition(
                key="interior_angle",
                label="Interior Angle",
                unit="°",
                editable=False,
                readonly=True,
                tooltip="((n-2)·180°) / n",
                format_spec=".4f",
                category="Angles",
            ),
            PropertyDefinition(
                key="exterior_angle",
                label="Exterior Angle",
                unit="°",
                editable=False,
                readonly=True,
                tooltip="360° / n",
                format_spec=".4f",
                category="Angles",
            ),
            PropertyDefinition(
                key="num_diagonals",
                label="Number of Diagonals",
                unit="",
                editable=False,
                readonly=True,
                tooltip="n(n-3)/2",
                format_spec=".0f",
                category="Combinatorics",
            ),
            PropertyDefinition(
                key="shortest_diagonal",
                label="Shortest Diagonal",
                unit="units",
                editable=False,
                readonly=True,
                tooltip="Diagonal with skip=2 (if n ≥ 4)",
                format_spec=".6f",
                category="Diagonals",
            ),
            PropertyDefinition(
                key="longest_diagonal",
                label="Longest Diagonal",
                unit="units",
                editable=False,
                readonly=True,
                tooltip="Diagonal with skip=⌊n/2⌋",
                format_spec=".6f",
                category="Diagonals",
            ),
        ]

    # ── Public helpers ─────────────────────────────────────────────────────
    def set_num_sides(self, num_sides: int) -> None:
        """Update the working side count (clamped to n ≥ 3)."""
        self._state["num_sides"] = float(max(3, int(num_sides)))

    # ── Solving ────────────────────────────────────────────────────────────
    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            # Allow dynamic diagonal keys (diagonal_skip_k)
            if not key.startswith("diagonal_skip_"):
                return SolveResult.invalid(key, value, "Unsupported property for regular polygon")

        if key == "num_sides":
            if value < 3:
                return SolveResult.invalid(key, value, "n must be at least 3")
            n = int(value)
            canonical = {"num_sides": float(n), "side_length": self._state["side_length"]}
            self._state = canonical
            return SolveResult.success(
                canonical_parameter=canonical,  # type: ignore[arg-type]
                canonical_key=self.canonical_key,
                provenance=SolveProvenance(
                    source_key=key,
                    source_value=value,
                    formula_used="n updated (integer) with existing side length",
                    intermediate_values={},
                    assumptions=["n ≥ 3", "side length unchanged"],
                ),
            )

        if value <= 0:
            return SolveResult.invalid(key, value, "Values must be positive")

        n = max(3, int(self._state.get("num_sides", 3)))

        # Diagonal inversion: d_k => side
        if key.startswith("diagonal_skip_"):
            try:
                skip = int(key.split("diagonal_skip_")[1])
            except Exception:
                return SolveResult.invalid(key, value, "Malformed diagonal key; expected diagonal_skip_k")
            if skip < 2 or skip > n // 2:
                return SolveResult.invalid(key, value, f"Diagonal skip must be between 2 and {n // 2}")
            side = float(value) * math.sin(math.pi / n) / math.sin(skip * math.pi / n)
            formula = f"s = d_{skip} · sin(π/n) / sin({skip}π/n)"
            canonical = {"num_sides": float(n), "side_length": side}
            self._state = canonical
            return SolveResult.success(
                canonical_parameter=canonical,  # type: ignore[arg-type]
                canonical_key=self.canonical_key,
                provenance=SolveProvenance(
                    source_key=key,
                    source_value=value,
                    formula_used=formula,
                    intermediate_values={"skip": skip},
                    assumptions=["n ≥ 3", "diagonal measured accurately"],
                ),
            )

        if key == "side_length":
            side = float(value)
            formula = "canonical side"
        elif key == "perimeter":
            side = float(value) / n
            formula = "s = P / n"
        elif key == "area":
            side = math.sqrt((4 * float(value) * math.tan(math.pi / n)) / n)
            formula = "s = sqrt((4A tan(π/n))/n)"
        elif key == "apothem":
            side = 2 * float(value) * math.tan(math.pi / n)
            formula = "s = 2a tan(π/n)"
        elif key == "circumradius":
            side = 2 * float(value) * math.sin(math.pi / n)
            formula = "s = 2R sin(π/n)"
        elif key == "shortest_diagonal":
            if n < 4:
                return SolveResult.invalid(key, value, "No diagonals when n < 4")
            side = float(value) * math.sin(math.pi / n) / math.sin(2 * math.pi / n)
            formula = "s = d₂ · sin(π/n) / sin(2π/n)"
        elif key == "longest_diagonal":
            skip = n // 2
            if skip < 2:
                return SolveResult.invalid(key, value, "No diagonals when n < 4")
            side = float(value) * math.sin(math.pi / n) / math.sin(skip * math.pi / n)
            formula = f"s = d_{skip} · sin(π/n) / sin({skip}π/n)"
        else:
            return SolveResult.invalid(key, value, "Unhandled property")

        canonical = {"num_sides": float(n), "side_length": side}
        self._state = canonical

        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=SolveProvenance(
                source_key=key,
                source_value=value,
                formula_used=formula,
                intermediate_values={"n": n},
                assumptions=["n ≥ 3", "side > 0"],
            ),
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = compute_regular_polygon_metrics(int(canonical["num_sides"]), canonical["side_length"])
        flat_metrics: dict[str, float] = {k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))}
        # Expose diagonal lengths by skip as separate keys for detailed inspection
        diag_map = metrics.get("diagonal_lengths", {})
        if isinstance(diag_map, dict):
            for skip, length in diag_map.items():
                flat_metrics[f"diagonal_skip_{skip}"] = float(length)
        return flat_metrics

    def create_declaration(self, canonical_value: Any, *, title: str | None = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        n = int(canonical["num_sides"])
        side = canonical["side_length"]
        metrics = compute_regular_polygon_metrics(n, side)

        forms = [
            Form(
                id="regular_polygon",
                kind=self.form_type,
                params={
                    self.canonical_key: canonical,
                    "num_sides": n,
                    "side_length": side,
                    "apothem": metrics["apothem"],
                    "circumradius": metrics["circumradius"],
                    "area": metrics["area"],
                    "perimeter": metrics["perimeter"],
                    "shortest_diagonal": metrics["shortest_diagonal"],
                    "longest_diagonal": metrics["longest_diagonal"],
                    "diagonal_lengths": metrics.get("diagonal_lengths", {}),
                },
                dimensional_class=2,
                symmetry_class="cyclic",
                notes=f"Regular {n}-gon defined by side length",
            )
        ]

        return Declaration(
            title=title or f"Regular {n}-gon • s={side:.4f}",
            forms=forms,
            metadata={
                "solver": "RegularPolygonSolver",
                "version": "1.0.0",
                "num_sides": n,
            },
        )

    def get_derivation(self) -> str:
        return (
            "Regular n-gon relations:\n"
            "  • Perimeter: P = n·s\n"
            "  • Apothem: a = s / (2 tan(π/n))\n"
            "  • Circumradius: R = s / (2 sin(π/n))\n"
            "  • Area: A = (P·a)/2 = (n·s²)/(4 tan(π/n))\n"
            "  • Angles: interior = ((n-2)·180°)/n, exterior = 360°/n\n"
            "  • Diagonals: n(n-3)/2"
        )

    # ── Helpers ───────────────────────────────────────────────────────────
    def _normalize_canonical(self, canonical_value: Any) -> Dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if "num_sides" in canonical_value and canonical_value["num_sides"] is not None:
                self.set_num_sides(int(canonical_value["num_sides"]))
                canonical["num_sides"] = self._state["num_sides"]
            if "side_length" in canonical_value and canonical_value["side_length"] is not None:
                canonical["side_length"] = float(canonical_value["side_length"])
            else:
                # Allow diagonal-based canonical input (diagonal_skip_k)
                for key, val in canonical_value.items():
                    if not isinstance(key, str) or not key.startswith("diagonal_skip_"):
                        continue
                    try:
                        skip = int(key.split("diagonal_skip_")[1])
                    except Exception:
                        continue
                    if skip < 2:
                        continue
                    n = int(self._state.get("num_sides", 3))
                    if skip > n // 2:
                        continue
                    try:
                        diag = float(val)
                    except Exception:
                        continue
                    canonical["side_length"] = diag * math.sin(math.pi / n) / math.sin(skip * math.pi / n)
                    break
        else:
            try:
                canonical["side_length"] = float(canonical_value)
            except Exception:
                pass

        canonical["side_length"] = max(canonical["side_length"], 1e-9)
        canonical["num_sides"] = float(max(3, int(canonical.get("num_sides", 3))))

        # Persist
        self._state = canonical
        return canonical
