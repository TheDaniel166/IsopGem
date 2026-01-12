"""
Geometry Pillar — Regular Polygon Realizer.

Produces GeometryScenePayload artifacts for regular n-gons using Canon forms.

Reference: ADR-010 — Canon DSL Adoption
Reference: ADR-011 — Unified Geometry Viewer
"""
from __future__ import annotations

from typing import Any

from canon_dsl import RealizeContext, Realizer, FormRealization

from ..ui.primitives import (
    Bounds,
    BrushStyle,
    CirclePrimitive,
    GeometryScenePayload,
    LabelPrimitive,
    LinePrimitive,
    PenStyle,
    PolygonPrimitive,
)
from ..services.polygon_shape import DIAGONAL_COLOR_PALETTE
from .regular_polygon_solver import compute_regular_polygon_metrics, generate_regular_polygon_points

_SERVICE_VERSION = "1.0"


class RegularPolygonRealizer(Realizer):
    """Canon realizer for regular polygons (2D)."""

    @property
    def supported_kinds(self) -> set[str]:
        return {"RegularPolygon"}

    def realize_form(self, form: Any, context: RealizeContext) -> FormRealization:  # type: ignore[override]
        if getattr(form, "kind", None) not in self.supported_kinds:
            raise ValueError(f"RegularPolygonRealizer received unsupported kind: {getattr(form, 'kind', None)}")

        params = getattr(form, "params", {}) or {}
        canonical = params.get("polygon", {}) or {}

        n = int(params.get("num_sides", canonical.get("num_sides", 6)))
        side = float(params.get("side_length", canonical.get("side_length", 1.0)))

        metrics = compute_regular_polygon_metrics(n, side)
        points = generate_regular_polygon_points(int(metrics["num_sides"]), metrics["circumradius"])
        payload = self._build_scene_payload(points, metrics)
        provenance = self._build_provenance(form, metrics, context)

        return FormRealization(
            artifact=payload,
            metrics=metrics,
            provenance=provenance,
        )

    # ── Internals ──────────────────────────────────────────────────────────
    def _build_scene_payload(self, points: list[tuple[float, float]], metrics: dict[str, float]) -> GeometryScenePayload:
        radius = metrics.get("circumradius", 1.0)
        apothem = metrics.get("apothem", max(radius * 0.5, 1e-6))

        polygon_pen = PenStyle(color=(37, 99, 235, 255), width=2.0)
        polygon_brush = BrushStyle(color=(59, 130, 246, 80), enabled=True)

        primitives = [
            CirclePrimitive(
                center=(0.0, 0.0),
                radius=radius,
                pen=PenStyle(color=(148, 163, 184, 200), width=1.2, dashed=True),
                brush=BrushStyle(enabled=False),
                metadata={"role": "circumcircle"},
            ),
            CirclePrimitive(
                center=(0.0, 0.0),
                radius=apothem,
                pen=PenStyle(color=(16, 185, 129, 220), width=1.2, dashed=True),
                brush=BrushStyle(enabled=False),
                metadata={"role": "incircle"},
            ),
            PolygonPrimitive(points=points, pen=polygon_pen, brush=polygon_brush, closed=True),
        ]

        primitives.extend(self._build_diagonals(points))

        label_side = f"s = {metrics['side_length']:.4f}".rstrip("0").rstrip(".")
        labels = [
            LabelPrimitive(text=f"n = {int(metrics['num_sides'])}", position=(0.0, -radius - 0.3)),
            LabelPrimitive(text=label_side, position=(0.0, radius + 0.3)),
        ]

        bounds = Bounds(min_x=-radius, max_x=radius, min_y=-radius, max_y=radius).padded(radius * 0.25 + 0.5)

        return GeometryScenePayload(
            primitives=primitives,
            labels=labels,
            bounds=bounds,
            suggest_grid_span=radius * 0.5 if radius > 0 else None,
        )

    def _build_diagonals(self, points: list[tuple[float, float]]) -> list[LinePrimitive]:
        """Create color-coded diagonal primitives grouped by skip length."""
        n = len(points)
        if n < 4:
            return []

        diagonals: list[LinePrimitive] = []
        palette_len = len(DIAGONAL_COLOR_PALETTE)
        seen: set[tuple[int, int]] = set()

        for skip in range(2, (n // 2) + 1):
            color = DIAGONAL_COLOR_PALETTE[(skip - 2) % palette_len]
            pen = PenStyle(color=color, width=1.2, dashed=False)
            for i in range(n):
                j = (i + skip) % n
                a, b = sorted((i, j))
                if b - a == 1 or (a == 0 and b == n - 1):
                    continue  # skip edges
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                p1 = points[i]
                p2 = points[j]
                diagonals.append(
                    LinePrimitive(
                        start=p1,
                        end=p2,
                        pen=pen,
                        metadata={"role": "diagonal", "skip": skip},
                    )
                )
        return diagonals

    def _build_provenance(self, form: Any, metrics: dict[str, float], context: RealizeContext) -> dict:
        declaration_title = getattr(getattr(context, "declaration", None), "title", None)
        return {
            "form_id": getattr(form, "id", "regular_polygon"),
            "form_kind": getattr(form, "kind", "RegularPolygon"),
            "declaration_title": declaration_title,
            "service": "RegularPolygonShape",
            "service_version": _SERVICE_VERSION,
            "realizer": "RegularPolygonRealizer",
            "canon_refs": ["ADR-011 — Unified Geometry Viewer"],
            "parameters": {
                "num_sides": metrics.get("num_sides"),
                "side_length": metrics.get("side_length"),
                "apothem": metrics.get("apothem"),
                "circumradius": metrics.get("circumradius"),
            },
            "invariants": {
                "interior_angle": metrics.get("interior_angle"),
                "exterior_angle": metrics.get("exterior_angle"),
                "num_diagonals": metrics.get("num_diagonals"),
            },
            "epsilon": getattr(context, "epsilon", None),
        }
