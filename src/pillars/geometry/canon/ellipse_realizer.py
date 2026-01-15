"""Ellipse Realizer - Canon-compliant realization."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from canon_dsl import RealizeContext, Realizer, FormRealization

if TYPE_CHECKING:
    from canon_dsl import Form


_SERVICE_VERSION = "1.0"


class EllipseRealizer(Realizer):
    """Realizer for Ellipse forms."""

    @property
    def supported_kinds(self) -> set[str]:
        return {"Ellipse"}

    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        if form.kind not in self.supported_kinds:
            raise ValueError(f"EllipseRealizer received unsupported kind: {form.kind}")

        params = getattr(form, "params", {}) or {}
        canonical = params.get("ellipse", {}) or {}

        a = float(params.get("semi_major_axis", canonical.get("semi_major_axis", 1.0)))
        b = float(params.get("semi_minor_axis", canonical.get("semi_minor_axis", 1.0)))

        from ..services.ellipse_shape import EllipseShapeService
        from ..ui.scene_adapter import build_scene_payload

        drawing_dict = EllipseShapeService.build(a=a, b=b)
        scene_payload = build_scene_payload(drawing_dict, labels=[])

        metrics = self._extract_metrics(a, b)
        provenance = self._build_provenance(form, metrics, context)

        return FormRealization(
            artifact=scene_payload,
            metrics=metrics,
            provenance=provenance,
        )

    def _extract_metrics(self, a: float, b: float) -> dict:
        math_a = max(a, b)
        math_b = min(a, b)

        area = math.pi * math_a * math_b
        ecc = math.sqrt(1 - (math_b * math_b) / (math_a * math_a)) if math_a > 0 else 0.0
        focal_dist = math.sqrt(max(math_a * math_a - math_b * math_b, 0.0))

        perimeter = 0.0
        if (math_a + math_b) > 0:
            h = ((math_a - math_b) ** 2) / ((math_a + math_b) ** 2)
            perimeter = math.pi * (math_a + math_b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))

        return {
            "semi_major_axis": a,
            "semi_minor_axis": b,
            "major_axis": 2 * a,
            "minor_axis": 2 * b,
            "area": area,
            "perimeter": perimeter,
            "eccentricity": ecc,
            "focal_distance": focal_dist,
        }

    def _build_provenance(
        self,
        form: Form,
        metrics: dict,
        context: RealizeContext,
    ) -> dict:
        return {
            "form_id": form.id,
            "form_kind": form.kind,
            "declaration_title": getattr(context.declaration, "title", None),
            "service": "EllipseShapeService",
            "service_version": _SERVICE_VERSION,
            "realizer": "EllipseRealizer",
            "parameters": {
                "semi_major_axis": metrics.get("semi_major_axis"),
                "semi_minor_axis": metrics.get("semi_minor_axis"),
            },
            "epsilon": context.epsilon,
        }
