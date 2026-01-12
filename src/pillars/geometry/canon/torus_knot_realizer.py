"""
Geometry Pillar — Torus Knot Realizer.

Wraps TorusKnotSolidService to produce Canon-compatible realizations
for (p, q) torus knots.

Reference: ADR-012 — Complete Canon Migration
Reference: ADR-010 — Canon DSL Adoption
Reference: ADR-011 — Unified Geometry Viewer
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from canon_dsl import RealizeContext, Realizer, FormRealization

from ..services.torus_knot_solid import TorusKnotMetrics, TorusKnotSolidService

if TYPE_CHECKING:
    from canon_dsl import Form


_SERVICE_VERSION = "1.0"


class TorusKnotRealizer(Realizer):
    """Realizer for TorusKnot forms."""

    @property
    def supported_kinds(self) -> set[str]:
        return {"TorusKnot"}

    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        if form.kind not in self.supported_kinds:
            raise ValueError(f"TorusKnotRealizer received unsupported kind: {form.kind}")

        params = getattr(form, "params", {}) or {}
        canonical: dict[str, Any] = params.get("torus_knot", {}) or {}

        p = int(params.get("p", canonical.get("p", 2)))
        q = int(params.get("q", canonical.get("q", 3)))
        major = float(params.get("major_radius", canonical.get("major_radius", 3.0)))
        minor = float(params.get("minor_radius", canonical.get("minor_radius", 1.0)))
        tube = float(params.get("tube_radius", canonical.get("tube_radius", 0.4)))

        result = TorusKnotSolidService.build(p=p, q=q, major_radius=major, minor_radius=minor, tube_radius=tube)

        metrics = self._extract_metrics(result.metrics)
        provenance = self._build_provenance(form, metrics, context)

        return FormRealization(
            artifact=result.payload,
            metrics=metrics,
            provenance=provenance,
        )

    def _extract_metrics(self, raw: TorusKnotMetrics) -> dict[str, float]:
        return {
            "p": float(raw.p),
            "q": float(raw.q),
            "major_radius": raw.major_radius,
            "minor_radius": raw.minor_radius,
            "tube_radius": raw.tube_radius,
            "arc_length": raw.arc_length,
            "approx_surface_area": raw.approx_surface_area,
            "approx_volume": raw.approx_volume,
            "gcd": float(math.gcd(int(raw.p), int(raw.q))),
        }

    def _build_provenance(
        self,
        form: Form,
        metrics: dict[str, float],
        context: RealizeContext,
    ) -> dict:
        return {
            "form_id": getattr(form, "id", "torus_knot"),
            "form_kind": form.kind,
            "declaration_title": getattr(context, "declaration", None).title if getattr(context, "declaration", None) else None,
            "service": "TorusKnotSolidService",
            "service_version": _SERVICE_VERSION,
            "realizer": "TorusKnotRealizer",
            "canon_refs": ["ADR-012 — Torus Knot migration"],
            "parameters": {
                "p": metrics.get("p"),
                "q": metrics.get("q"),
                "major_radius": metrics.get("major_radius"),
                "minor_radius": metrics.get("minor_radius"),
                "tube_radius": metrics.get("tube_radius"),
            },
            "invariants": {
                "gcd": metrics.get("gcd"),
            },
            "epsilon": getattr(context, "epsilon", None),
        }
