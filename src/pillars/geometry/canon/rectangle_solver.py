"""Rectangle Solver - Canon-compliant bidirectional solver."""

from __future__ import annotations

import math
from typing import Any, Optional

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition


class RectangleSolver(GeometrySolver):
    """
    Bidirectional solver for rectangles.
    
    Canonical Parameters:
        - width
        - height
    """

    def __init__(self, width: float = 2.0, height: float = 1.0) -> None:
        self._state = {
            "width": max(float(width), 1e-9),
            "height": max(float(height), 1e-9),
        }

    @property
    def form_type(self) -> str:
        return "Rectangle"

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def canonical_key(self) -> str:
        return "rectangle"
    
    @property
    def supported_keys(self) -> set[str]:
        return {"width", "height", "area", "perimeter", "diagonal"}

    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="width",
                label="Width",
                unit="units",
                editable=True,
                category="Dimensions",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="height",
                label="Height",
                unit="units",
                editable=True,
                category="Dimensions",
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
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="diagonal",
                label="Diagonal",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="aspect_ratio",
                label="Aspect Ratio (w/h)",
                unit="",
                editable=False,
                readonly=True,
                category="Measurements",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Solve for width/height.
        Note: Solving from Area/Perimeter is underdetermined without context.
        We return invalid for now, consistent with legacy behavior.
        """
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for rectangle")

        if key in {"area", "perimeter", "diagonal"}:
            return SolveResult.invalid(
                key,
                value,
                "Cannot solve unique rectangle from derived property",
            )

        if value <= 0:
            return SolveResult.invalid(key, value, "Side lengths must be positive")

        canonical = self._state.copy()

        if key == "width":
            canonical["width"] = value
            formula = "w = w"
        elif key == "height":
            canonical["height"] = value
            formula = "h = h"
        else:
            return SolveResult.invalid(key, value, "Unsupported property for rectangle")

        self._state = canonical

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )

        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical: dict | float) -> dict[str, float]:
        canonical_dict = self._normalize_canonical(canonical)
        w = float(canonical_dict.get("width", 0.0))
        h = float(canonical_dict.get("height", 0.0))
        aspect_ratio = (w / h) if h else 0.0

        return {
            "width": w,
            "height": h,
            "area": w * h,
            "perimeter": 2 * (w + h),
            "diagonal": math.sqrt(w * w + h * h),
            "aspect_ratio": aspect_ratio,
        }
    
    def create_declaration(
        self,
        canonical_value: float | dict,
        *,
        title: Optional[str] = None,
    ) -> Declaration:
        """Create a Canon-compliant Declaration for a Rectangle."""
        canonical = self._normalize_canonical(canonical_value)
        w = canonical.get("width", 1.0)
        h = canonical.get("height", 1.0)
        metrics = self.get_all_properties(canonical)

        params = {
            "rectangle": {"width": w, "height": h},
            "width": w,
            "height": h,
            "area": metrics.get("area", w * h),
            "perimeter": metrics.get("perimeter", 2 * (w + h)),
            "diagonal": metrics.get("diagonal", math.sqrt(w * w + h * h)),
            "aspect_ratio": metrics.get("aspect_ratio", (w / h) if h else 0.0),
        }

        return Declaration(
            title=title or f"Rectangle (w={w:.4f}, h={h:.4f})",
            forms=[
                Form(
                    id="rectangle",
                    kind="Rectangle",
                    params=params,
                    dimensional_class=2,
                )
            ],
            epsilon=1e-9,
            metadata={
                "solver": "RectangleSolver",
            },
        )

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("width") is not None:
                canonical["width"] = float(canonical_value["width"])
            if canonical_value.get("height") is not None:
                canonical["height"] = float(canonical_value["height"])
        else:
            try:
                canonical["width"] = float(canonical_value)
            except (TypeError, ValueError):
                pass

        canonical["width"] = max(canonical["width"], 1e-9)
        canonical["height"] = max(canonical["height"], 1e-9)
        self._state = canonical
        return canonical
