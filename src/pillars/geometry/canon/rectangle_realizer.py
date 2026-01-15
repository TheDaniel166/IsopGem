"""Rectangle Realizer - Canon-compliant realization."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from canon_dsl import RealizeContext, Realizer, FormRealization

if TYPE_CHECKING:
    from canon_dsl import Form


_SERVICE_VERSION = "1.0"


class RectangleRealizer(Realizer):
    """Realizer for Rectangle forms."""

    @property
    def supported_kinds(self) -> set[str]:
        return {"Rectangle"}

    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        if form.kind not in self.supported_kinds:
            raise ValueError(f"RectangleRealizer received unsupported kind: {form.kind}")

        params = getattr(form, "params", {}) or {}
        canonical = params.get("rectangle", {}) or {}

        width = float(params.get("width", canonical.get("width", 1.0)))
        height = float(params.get("height", canonical.get("height", 1.0)))

        from ..services.square_shape import RectangleShapeService
        from ..ui.scene_adapter import build_scene_payload

        drawing_dict = RectangleShapeService.build(width=width, height=height)
        scene_payload = build_scene_payload(drawing_dict, labels=[])

        metrics = self._extract_metrics(width, height)
        provenance = self._build_provenance(form, metrics, context)

        return FormRealization(
            artifact=scene_payload,
            metrics=metrics,
            provenance=provenance,
        )

    def _extract_metrics(self, width: float, height: float) -> dict:
        aspect_ratio = (width / height) if height else 0.0
        return {
            "width": width,
            "height": height,
            "area": width * height,
            "perimeter": 2 * (width + height),
            "diagonal": math.sqrt(width * width + height * height),
            "aspect_ratio": aspect_ratio,
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
            "service": "RectangleShapeService",
            "service_version": _SERVICE_VERSION,
            "realizer": "RectangleRealizer",
            "parameters": {
                "width": metrics.get("width"),
                "height": metrics.get("height"),
            },
            "epsilon": context.epsilon,
        }
