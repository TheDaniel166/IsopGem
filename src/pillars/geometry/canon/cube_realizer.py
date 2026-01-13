"""
Geometry Pillar — Cube Realizer.

Realizer that converts validated Cube Declarations into
concrete SolidPayload artifacts by delegating to the existing service.

Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext
from shared.services.geometry.cube import CubeSolidService

if TYPE_CHECKING:
    from canon_dsl import Form


class CubeRealizer(Realizer):
    """
    Realizer for Cube forms.
    
    Converts validated Cube Declarations into SolidPayload artifacts
    by delegating to the existing CubeSolidService.
    
    This realizer:
    - Accepts only Form.kind == "Cube"
    - Extracts edge_length from form.params
    - Calls CubeSolidService.build(edge_length)
    - Returns artifact with full metrics and provenance
    
    Usage:
        engine = CanonEngine()
        engine.register_realizer("Cube", CubeRealizer())
        
        decl = Declaration(
            forms=[Form(id="cube", kind="Cube", params={"edge_length": 2.0})]
        )
        
        result = engine.realize(decl)
        payload = result.get_artifact("cube")
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        """This realizer handles only Cube forms."""
        return {"Cube"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize a Cube form into a SolidPayload.
        
        Args:
            form: The Cube Form from a validated Declaration
            context: Realization context with epsilon and config
        
        Returns:
            FormRealization with SolidPayload artifact
        """
        # Extract edge_length from params
        edge_length = form.params.get("edge_length")
        if edge_length is None:
            raise ValueError(f"Cube form '{form.id}' missing required parameter 'edge_length'")
        
        if not isinstance(edge_length, (int, float)) or edge_length <= 0:
            raise ValueError(f"Cube edge_length must be positive number, got {edge_length}")
        
        # Delegate to service
        result = CubeSolidService.build(float(edge_length))
        
        # Return realization with payload and metrics
        return FormRealization(
            artifact=result.payload,
            metrics={
                "edge_length": result.metrics.edge_length,
                "volume": result.metrics.volume,
                "surface_area": result.metrics.surface_area,
                "face_area": result.metrics.face_area,
                "face_diagonal": result.metrics.face_diagonal,
                "space_diagonal": result.metrics.space_diagonal,
                "inradius": result.metrics.inradius,
                "midradius": result.metrics.midradius,
                "circumradius": result.metrics.circumradius,
            },
            provenance={
                "solver": "CubeSolver",
                "realizer": "CubeRealizer",
                "service": "CubeSolidService",
                "method": "build",
            },
        )
