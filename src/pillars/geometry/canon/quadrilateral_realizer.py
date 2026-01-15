"""Quadrilateral Realizer for Canon DSL migration."""
from __future__ import annotations

from typing import Any

from canon_dsl import FormRealization, RealizeContext, Realizer

from ..services.quadrilateral_shape_service import QuadrilateralShapeService
from ..ui.scene_adapter import build_scene_payload
from .quadrilateral_solvers import (
    ParallelogramSolver,
    RhombusSolver,
    TrapezoidSolver,
    IsoscelesTrapezoidSolver,
    KiteSolver,
    DeltoidSolver,
    CyclicQuadrilateralSolver,
    TangentialQuadrilateralSolver,
    BicentricQuadrilateralSolver,
    QuadrilateralSolver,
)


_SERVICE_VERSION = "1.0"


class QuadrilateralRealizer(Realizer):
    """Realizer for quadrilateral form kinds."""

    @property
    def supported_kinds(self) -> set[str]:
        return {
            "Parallelogram",
            "Rhombus",
            "Trapezoid",
            "IsoscelesTrapezoid",
            "Kite",
            "Deltoid",
            "CyclicQuadrilateral",
            "TangentialQuadrilateral",
            "BicentricQuadrilateral",
            "QuadrilateralSolver",
        }

    def realize_form(self, form: Any, context: RealizeContext) -> FormRealization:  # type: ignore[override]
        kind = getattr(form, "kind", None)
        if kind not in self.supported_kinds:
            raise ValueError(f"QuadrilateralRealizer received unsupported kind: {kind}")

        params = getattr(form, "params", {}) or {}

        if kind == "Parallelogram":
            solver = ParallelogramSolver()
            canonical = params.get("parallelogram", {}) or {}
            for key in ("base", "side", "height", "angle_deg"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            base = metrics.get("base", canonical.get("base", 1.0))
            side = metrics.get("side", canonical.get("side", 1.0))
            angle = metrics.get("angle_deg", canonical.get("angle_deg", 60.0))
            drawing = QuadrilateralShapeService.build_parallelogram(base=base, side=side, angle_deg=angle)
            parameters = {"base": base, "side": side, "angle_deg": angle}

        elif kind == "Rhombus":
            solver = RhombusSolver()
            canonical = params.get("rhombus", {}) or {}
            for key in ("side", "height", "angle_deg", "diagonal_long", "diagonal_short"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            side = metrics.get("side", canonical.get("side", 1.0))
            angle = metrics.get("angle_deg", canonical.get("angle_deg", 60.0))
            drawing = QuadrilateralShapeService.build_rhombus(side=side, angle_deg=angle)
            parameters = {"side": side, "angle_deg": angle}

        elif kind == "Trapezoid":
            solver = TrapezoidSolver()
            canonical = params.get("trapezoid", {}) or {}
            for key in ("base_major", "base_minor", "height", "leg_left", "leg_right"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            base_major = metrics.get("base_major", canonical.get("base_major", 1.0))
            base_minor = metrics.get("base_minor", canonical.get("base_minor", 0.5))
            height = metrics.get("height", canonical.get("height", 1.0))
            leg_left = metrics.get("leg_left", canonical.get("leg_left"))
            leg_right = metrics.get("leg_right", canonical.get("leg_right"))
            drawing = QuadrilateralShapeService.build_trapezoid(
                base_major=base_major,
                base_minor=base_minor,
                height=height,
                leg_left=leg_left,
                leg_right=leg_right,
            )
            parameters = {
                "base_major": base_major,
                "base_minor": base_minor,
                "height": height,
                "leg_left": leg_left,
                "leg_right": leg_right,
            }

        elif kind == "IsoscelesTrapezoid":
            solver = IsoscelesTrapezoidSolver()
            canonical = params.get("isosceles_trapezoid", {}) or {}
            for key in ("base_major", "base_minor", "height", "leg"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            base_major = metrics.get("base_major", canonical.get("base_major", 1.0))
            base_minor = metrics.get("base_minor", canonical.get("base_minor", 0.5))
            height = metrics.get("height", canonical.get("height", 1.0))
            drawing = QuadrilateralShapeService.build_isosceles_trapezoid(
                base_major=base_major,
                base_minor=base_minor,
                height=height,
            )
            parameters = {"base_major": base_major, "base_minor": base_minor, "height": height}

        elif kind == "Kite":
            solver = KiteSolver()
            canonical = params.get("kite", {}) or {}
            for key in ("equal_side", "unequal_side", "included_angle_deg"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            equal_side = metrics.get("equal_side", canonical.get("equal_side", 1.0))
            unequal_side = metrics.get("unequal_side", canonical.get("unequal_side", 1.0))
            angle = metrics.get("included_angle_deg", canonical.get("included_angle_deg", 60.0))
            drawing = QuadrilateralShapeService.build_kite(
                equal_side=equal_side,
                unequal_side=unequal_side,
                angle_deg=angle,
                convex=True,
            )
            parameters = {"equal_side": equal_side, "unequal_side": unequal_side, "included_angle_deg": angle}

        elif kind == "Deltoid":
            solver = DeltoidSolver()
            canonical = params.get("deltoid", {}) or {}
            for key in ("equal_side", "unequal_side", "included_angle_deg"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            equal_side = metrics.get("equal_side", canonical.get("equal_side", 1.0))
            unequal_side = metrics.get("unequal_side", canonical.get("unequal_side", 1.0))
            angle = metrics.get("included_angle_deg", canonical.get("included_angle_deg", 240.0))
            drawing = QuadrilateralShapeService.build_kite(
                equal_side=equal_side,
                unequal_side=unequal_side,
                angle_deg=angle,
                convex=False,
            )
            parameters = {"equal_side": equal_side, "unequal_side": unequal_side, "included_angle_deg": angle}

        elif kind == "CyclicQuadrilateral":
            solver = CyclicQuadrilateralSolver()
            canonical = params.get("cyclic_quadrilateral", {}) or {}
            for key in ("side_a", "side_b", "side_c", "side_d"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            side_a = metrics.get("side_a", canonical.get("side_a", 1.0))
            side_b = metrics.get("side_b", canonical.get("side_b", 1.0))
            side_c = metrics.get("side_c", canonical.get("side_c", 1.0))
            side_d = metrics.get("side_d", canonical.get("side_d", 1.0))
            circumradius = metrics.get("circumradius", 1.0)
            drawing = QuadrilateralShapeService.build_cyclic_quadrilateral(
                side_a=side_a,
                side_b=side_b,
                side_c=side_c,
                side_d=side_d,
                circumradius=circumradius,
            )
            parameters = {"side_a": side_a, "side_b": side_b, "side_c": side_c, "side_d": side_d}

        elif kind == "TangentialQuadrilateral":
            solver = TangentialQuadrilateralSolver()
            canonical = params.get("tangential_quadrilateral", {}) or {}
            for key in ("side_a", "side_b", "side_c", "side_d", "inradius"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            side_a = metrics.get("side_a", canonical.get("side_a", 1.0))
            side_b = metrics.get("side_b", canonical.get("side_b", 1.0))
            side_c = metrics.get("side_c", canonical.get("side_c", 1.0))
            side_d = metrics.get("side_d", canonical.get("side_d", 1.0))
            inradius = metrics.get("inradius", canonical.get("inradius", 1.0))
            drawing = QuadrilateralShapeService.build_tangential_quadrilateral(
                side_a=side_a,
                side_b=side_b,
                side_c=side_c,
                side_d=side_d,
                inradius=inradius,
            )
            parameters = {
                "side_a": side_a,
                "side_b": side_b,
                "side_c": side_c,
                "side_d": side_d,
                "inradius": inradius,
            }

        elif kind == "BicentricQuadrilateral":
            solver = BicentricQuadrilateralSolver()
            canonical = params.get("bicentric_quadrilateral", {}) or {}
            for key in ("side_a", "side_b", "side_c", "side_d"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            side_a = metrics.get("side_a", canonical.get("side_a", 1.0))
            side_b = metrics.get("side_b", canonical.get("side_b", 1.0))
            side_c = metrics.get("side_c", canonical.get("side_c", 1.0))
            side_d = metrics.get("side_d", canonical.get("side_d", 1.0))
            circumradius = metrics.get("circumradius", 1.0)
            drawing = QuadrilateralShapeService.build_cyclic_quadrilateral(
                side_a=side_a,
                side_b=side_b,
                side_c=side_c,
                side_d=side_d,
                circumradius=circumradius,
            )
            parameters = {"side_a": side_a, "side_b": side_b, "side_c": side_c, "side_d": side_d}

        elif kind == "QuadrilateralSolver":
            solver = QuadrilateralSolver()
            canonical = params.get("quadrilateral_solver", {}) or {}
            for key in ("side_a", "side_b", "side_c", "side_d", "diagonal_p", "diagonal_q", "diagonal_angle_deg"):
                if params.get(key) is not None:
                    canonical[key] = params.get(key)
            metrics = solver.get_all_properties(canonical)
            p = metrics.get("diagonal_p", canonical.get("diagonal_p", 1.0))
            q = metrics.get("diagonal_q", canonical.get("diagonal_q", 1.0))
            angle = metrics.get("diagonal_angle_deg", canonical.get("diagonal_angle_deg", 60.0))
            drawing = QuadrilateralShapeService.build_quadrilateral_solver(p=p, q=q, angle_deg=angle)
            parameters = {"diagonal_p": p, "diagonal_q": q, "diagonal_angle_deg": angle}

        else:
            raise ValueError(f"Unhandled quadrilateral kind: {kind}")

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
            "service": "QuadrilateralShapeService",
            "service_version": _SERVICE_VERSION,
            "realizer": "QuadrilateralRealizer",
            "parameters": parameters,
            "epsilon": getattr(context, "epsilon", None),
        }
