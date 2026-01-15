"""Triangle Realizer for Canon DSL migration."""
from __future__ import annotations

from typing import Any

from canon_dsl import FormRealization, RealizeContext, Realizer

from ..services.triangle_shape_service import TriangleShapeService
from ..ui.scene_adapter import build_scene_payload
from .triangle_solvers import (
    EquilateralTriangleSolver,
    RightTriangleSolver,
    IsoscelesTriangleSolver,
    ScaleneTriangleSolver,
    AcuteTriangleSolver,
    ObtuseTriangleSolver,
    HeronianTriangleSolver,
    IsoscelesRightTriangleSolver,
    ThirtySixtyNinetyTriangleSolver,
    GoldenTriangleSolver,
    TriangleSolver,
)


_SERVICE_VERSION = "1.0"


class TriangleRealizer(Realizer):
    """Realizer for all triangle form kinds."""

    @property
    def supported_kinds(self) -> set[str]:
        return {
            "EquilateralTriangle",
            "RightTriangle",
            "IsoscelesTriangle",
            "ScaleneTriangle",
            "AcuteTriangle",
            "ObtuseTriangle",
            "HeronianTriangle",
            "IsoscelesRightTriangle",
            "ThirtySixtyNinetyTriangle",
            "GoldenTriangle",
            "TriangleSolver",
        }

    def realize_form(self, form: Any, context: RealizeContext) -> FormRealization:  # type: ignore[override]
        kind = getattr(form, "kind", None)
        if kind not in self.supported_kinds:
            raise ValueError(f"TriangleRealizer received unsupported kind: {kind}")

        params = getattr(form, "params", {}) or {}

        if kind == "EquilateralTriangle":
            side = float(params.get("side", 1.0))
            solver = EquilateralTriangleSolver()
            metrics = solver.get_all_properties(side)
            drawing = TriangleShapeService.build_equilateral(side)
            parameters = {"side": side}

        elif kind == "RightTriangle":
            canonical = params.get("right_triangle", {}) or {}
            base = float(params.get("base", canonical.get("base", 1.0)))
            height = float(params.get("height", canonical.get("height", 1.0)))
            solver = RightTriangleSolver()
            metrics = solver.get_all_properties({"base": base, "height": height})
            drawing = TriangleShapeService.build_right(base, height)
            parameters = {"base": base, "height": height}

        elif kind == "IsoscelesTriangle":
            canonical = params.get("isosceles_triangle", {}) or {}
            base = float(params.get("base", canonical.get("base", 1.0)))
            leg = float(params.get("leg", canonical.get("leg", 1.0)))
            solver = IsoscelesTriangleSolver()
            metrics = solver.get_all_properties({"base": base, "leg": leg})
            drawing = TriangleShapeService.build_from_sides(leg, leg, base)
            parameters = {"base": base, "leg": leg}

        elif kind in {"ScaleneTriangle", "AcuteTriangle", "ObtuseTriangle", "HeronianTriangle"}:
            canonical_key = {
                "ScaleneTriangle": "scalene_triangle",
                "AcuteTriangle": "acute_triangle",
                "ObtuseTriangle": "obtuse_triangle",
                "HeronianTriangle": "heronian_triangle",
            }[kind]
            canonical = params.get(canonical_key, {}) or {}
            side_a = float(params.get("side_a", canonical.get("side_a", 1.0)))
            side_b = float(params.get("side_b", canonical.get("side_b", 1.0)))
            side_c = float(params.get("side_c", canonical.get("side_c", 1.0)))

            solver_cls = {
                "ScaleneTriangle": ScaleneTriangleSolver,
                "AcuteTriangle": AcuteTriangleSolver,
                "ObtuseTriangle": ObtuseTriangleSolver,
                "HeronianTriangle": HeronianTriangleSolver,
            }[kind]
            solver = solver_cls()
            metrics = solver.get_all_properties({"side_a": side_a, "side_b": side_b, "side_c": side_c})
            drawing = TriangleShapeService.build_from_sides(side_a, side_b, side_c)
            parameters = {"side_a": side_a, "side_b": side_b, "side_c": side_c}

        elif kind == "IsoscelesRightTriangle":
            leg = float(params.get("leg", 1.0))
            solver = IsoscelesRightTriangleSolver()
            metrics = solver.get_all_properties(leg)
            drawing = TriangleShapeService.build_right(leg, leg)
            parameters = {"leg": leg}

        elif kind == "ThirtySixtyNinetyTriangle":
            short = float(params.get("short_leg", 1.0))
            solver = ThirtySixtyNinetyTriangleSolver()
            metrics = solver.get_all_properties(short)
            drawing = TriangleShapeService.build_right(short, short * (3 ** 0.5))
            parameters = {"short_leg": short}

        elif kind == "GoldenTriangle":
            leg = float(params.get("equal_leg", 1.0))
            solver = GoldenTriangleSolver()
            metrics = solver.get_all_properties(leg)
            base = metrics.get("base", leg)
            drawing = TriangleShapeService.build_from_sides(leg, leg, base)
            parameters = {"equal_leg": leg}

        elif kind == "TriangleSolver":
            canonical = params.get("triangle_solver", {}) or {}
            side_a = float(params.get("side_a", canonical.get("side_a", 3.0)))
            side_b = float(params.get("side_b", canonical.get("side_b", 4.0)))
            side_c = float(params.get("side_c", canonical.get("side_c", 5.0)))
            solver = TriangleSolver()
            metrics = solver.get_all_properties(
                {
                    "side_a": side_a,
                    "side_b": side_b,
                    "side_c": side_c,
                    "angle_a_deg": canonical.get("angle_a_deg"),
                    "angle_b_deg": canonical.get("angle_b_deg"),
                    "angle_c_deg": canonical.get("angle_c_deg"),
                }
            )
            drawing = TriangleShapeService.build_from_sides(side_a, side_b, side_c)
            parameters = {"side_a": side_a, "side_b": side_b, "side_c": side_c}

        else:
            raise ValueError(f"Unhandled triangle kind: {kind}")

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
            "service": "TriangleShapeService",
            "service_version": _SERVICE_VERSION,
            "realizer": "TriangleRealizer",
            "parameters": parameters,
            "epsilon": getattr(context, "epsilon", None),
        }
