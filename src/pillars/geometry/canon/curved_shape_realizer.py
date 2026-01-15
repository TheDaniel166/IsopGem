"""Curved shape realizers for annulus, crescent, vesica piscis, and rose curve."""
from __future__ import annotations

from typing import Any

from canon_dsl import FormRealization, RealizeContext, Realizer

from ..services.seed_of_life_shape import SeedOfLifeShape
from ..services.curved_shape_service import (
    AnnulusShapeService,
    CrescentShapeService,
    VesicaPiscisShapeService,
    RoseCurveShapeService,
)
from ..ui.scene_adapter import build_scene_payload
from .curved_shape_solvers import (
    AnnulusSolver,
    CrescentSolver,
    VesicaPiscisSolver,
    RoseCurveSolver,
)
from .seed_of_life_solver import SeedOfLifeSolver


_SERVICE_VERSION = "1.0"


class CurvedShapeRealizer(Realizer):
    """Realizer for curved 2D forms (annulus, crescent, vesica piscis, rose)."""

    @property
    def supported_kinds(self) -> set[str]:
        return {"Annulus", "Crescent", "VesicaPiscis", "RoseCurve", "SeedOfLife"}

    def realize_form(self, form: Any, context: RealizeContext) -> FormRealization:  # type: ignore[override]
        kind = getattr(form, "kind", None)
        if kind not in self.supported_kinds:
            raise ValueError(f"CurvedShapeRealizer received unsupported kind: {kind}")

        params = getattr(form, "params", {}) or {}

        if kind == "Annulus":
            solver = AnnulusSolver()
            canonical = params.get("annulus", {}) or {}
            if params.get("outer_radius") is not None:
                canonical["outer_radius"] = params.get("outer_radius")
            if params.get("inner_radius") is not None:
                canonical["inner_radius"] = params.get("inner_radius")
            metrics = solver.get_all_properties(canonical)
            outer = metrics.get("outer_radius", canonical.get("outer_radius", 1.0))
            inner = metrics.get("inner_radius", canonical.get("inner_radius"))
            drawing = AnnulusShapeService.build(outer_radius=outer, inner_radius=inner)
            parameters = {"outer_radius": outer, "inner_radius": inner}

        elif kind == "Crescent":
            solver = CrescentSolver()
            canonical = params.get("crescent", {}) or {}
            if params.get("outer_radius") is not None:
                canonical["outer_radius"] = params.get("outer_radius")
            if params.get("inner_radius") is not None:
                canonical["inner_radius"] = params.get("inner_radius")
            if params.get("offset") is not None:
                canonical["offset"] = params.get("offset")
            metrics = solver.get_all_properties(canonical)
            outer = metrics.get("outer_radius", canonical.get("outer_radius", 1.0))
            inner = metrics.get("inner_radius", canonical.get("inner_radius", 0.5))
            offset = metrics.get("offset", canonical.get("offset", 0.0))
            drawing = CrescentShapeService.build(outer_radius=outer, inner_radius=inner, offset=offset)
            parameters = {"outer_radius": outer, "inner_radius": inner, "offset": offset}

        elif kind == "VesicaPiscis":
            solver = VesicaPiscisSolver()
            canonical = params.get("vesica_piscis", {}) or {}
            if params.get("radius") is not None:
                canonical["radius"] = params.get("radius")
            if params.get("separation") is not None:
                canonical["separation"] = params.get("separation")
            metrics = solver.get_all_properties(canonical)
            radius = metrics.get("radius", canonical.get("radius", 1.0))
            separation = metrics.get("separation", canonical.get("separation", radius))
            drawing = VesicaPiscisShapeService.build(radius=radius, separation=separation)
            parameters = {"radius": radius, "separation": separation}

        elif kind == "RoseCurve":
            solver = RoseCurveSolver()
            canonical = params.get("rose_curve", {}) or {}
            if params.get("amplitude") is not None:
                canonical["amplitude"] = params.get("amplitude")
            if params.get("k_value") is not None:
                canonical["k_value"] = params.get("k_value")
            metrics = solver.get_all_properties(canonical)
            amplitude = metrics.get("amplitude", canonical.get("amplitude", 1.0))
            k_value = int(metrics.get("k_value", canonical.get("k_value", 1)))
            drawing = RoseCurveShapeService.build(amplitude=amplitude, k_value=k_value)
            parameters = {"amplitude": amplitude, "k_value": k_value}

        elif kind == "SeedOfLife":
            solver = SeedOfLifeSolver()
            canonical = params.get("seed_of_life", {}) or {}
            if params.get("radius") is not None:
                canonical["radius"] = params.get("radius")
            metrics = solver.get_all_properties(canonical)
            radius = metrics.get("radius", canonical.get("radius", 1.0))
            # Create a mock object that mimics SeedOfLifeShape properties for get_drawing_instructions
            # Since SeedOfLifeShape is a class instance, we can instantiate it and set properties
            # logic similar to how legacy factories worked, but via service call if possible.
            # However, SeedOfLifeShape is a GeometricShape subclass, not a static service method class.
            # We should probably adapt it or use it as is.
            shape_instance = SeedOfLifeShape()
            shape_instance.properties["radius"].value = radius
            drawing = shape_instance.get_drawing_instructions()
            parameters = {"radius": radius}

        else:
            raise ValueError(f"Unhandled curved shape kind: {kind}")

        scene_payload = build_scene_payload(drawing, labels=[])
        provenance = self._build_provenance(form, parameters, context)

        return FormRealization(
            artifact=scene_payload,
            metrics=metrics,
            provenance=provenance,
        )

    def _build_provenance(self, form: Any, parameters: dict, context: RealizeContext) -> dict:
        declaration_title = getattr(getattr(context, "declaration", None), "title", None)
        return {
            "form_id": getattr(form, "id", None),
            "form_kind": getattr(form, "kind", None),
            "declaration_title": declaration_title,
            "service": "CurvedShapeService",
            "service_version": _SERVICE_VERSION,
            "realizer": "CurvedShapeRealizer",
            "parameters": parameters,
            "epsilon": getattr(context, "epsilon", None),
        }
