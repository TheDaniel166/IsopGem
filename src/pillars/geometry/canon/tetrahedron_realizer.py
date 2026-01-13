"""
Geometry Pillar — Tetrahedron Realizer.

Realizer that converts validated Tetrahedron Declarations into
concrete SolidPayload artifacts by delegating to the existing service.

Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext
from shared.services.geometry.tetrahedron import TetrahedronSolidService

if TYPE_CHECKING:
    from canon_dsl import Form


class TetrahedronRealizer(Realizer):
    """
    Realizer for Tetrahedron forms.
    
    Converts validated Tetrahedron Declarations into SolidPayload artifacts
    by delegating to the existing TetrahedronSolidService.
    
    This realizer:
    - Accepts only Form.kind == "Tetrahedron"
    - Extracts edge_length from form.params
    - Calls TetrahedronSolidService.build(edge_length)
    - Returns artifact with full metrics and provenance
    
    Usage:
        engine = CanonEngine()
        engine.register_realizer("Tetrahedron", TetrahedronRealizer())
        
        decl = Declaration(
            forms=[Form(id="tet", kind="Tetrahedron", params={"edge_length": 5.0})]
        )
        
        result = engine.realize(decl)
        payload = result.get_artifact("tet")
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        """This realizer handles only Tetrahedron forms."""
        return {"Tetrahedron"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize a Tetrahedron form into a SolidPayload.
        
        Args:
            form: The Tetrahedron Form from a validated Declaration
            context: Realization context with epsilon and config
        
        Returns:
            FormRealization with SolidPayload artifact
        """
        # Extract edge_length from params
        edge_length = form.params.get("edge_length")
        if edge_length is None:
            raise ValueError(f"Tetrahedron form '{form.id}' missing required parameter 'edge_length'")
        
        if not isinstance(edge_length, (int, float)) or edge_length <= 0:
            raise ValueError(f"Tetrahedron edge_length must be positive number, got {edge_length}")
        
        # Delegate to service
        result = TetrahedronSolidService.build(float(edge_length))
        
        # Return realization with payload and metrics
        return FormRealization(
            artifact=result.payload,
            metrics={
                "edge_length": result.metrics.edge_length,
                "volume": result.metrics.volume,
                "surface_area": result.metrics.surface_area,
                "height": result.metrics.height,
                "inradius": result.metrics.inradius,
                "circumradius": result.metrics.circumradius,
                "faces": result.metrics.faces,
                "edges": result.metrics.edges,
                "vertices": result.metrics.vertices,
            },
            provenance={
                "form_id": form.id,
                "service": "TetrahedronSolidService",
                "service_version": "1.0",
                "canonical_parameter": "edge_length",
                "canonical_value": float(edge_length),
            },
        )
