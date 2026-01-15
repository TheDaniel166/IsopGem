"""
Geometry Pillar — Icosahedron Realizer.

Forward-only computation for icosahedron that wraps the existing service.

Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext

if TYPE_CHECKING:
    from canon_dsl import Form


class IcosahedronRealizer(Realizer):
    """
    Realizer for Icosahedron forms.
    
    Converts validated Icosahedron Declarations into 3D artifacts
    by delegating to the existing PlatonicSolidsService.
    
    Usage:
        engine = CanonEngine()
        engine.register_realizer("Icosahedron", IcosahedronRealizer())
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        """This realizer handles only Icosahedron forms."""
        return {"Icosahedron"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize an Icosahedron form into a drawable artifact.
        
        Args:
            form: The Icosahedron Form from a validated Declaration
            context: Realization context with epsilon and config
        
        Returns:
            FormRealization containing artifact, metrics, and provenance
        
        Raises:
            ValueError: If form.kind is not "Icosahedron"
        """
        if form.kind not in self.supported_kinds:
            raise ValueError(
                f"IcosahedronRealizer received unsupported kind: {form.kind}"
            )
        
        # Extract canonical parameter
        edge_length = form.params.get("edge_length", 1.0)
        
        # Delegate to existing service
        from shared.services.geometry.icosahedron import IcosahedronSolidService
        
        # Get 3D drawing instructions
        service = IcosahedronSolidService()
        result = service.build(edge_length=edge_length)
        solid_payload = result.payload
        
        # Extract key metrics from metadata
        metrics = {
            "edge_length": edge_length,
            "volume": solid_payload.metadata.get("volume", 0.0),
            "surface_area": solid_payload.metadata.get("surface_area", 0.0),
            "faces": 20,
            "vertices": 12,
            "edges": 30,
        }
        
        # Build provenance
        provenance = {
            "realizer": "IcosahedronRealizer",
            "service": "IcosahedronSolidService",
            "method": "build",
            "face_shape": "triangle",
            "dual": "dodecahedron",
        }
        
        return FormRealization(
            artifact=solid_payload,
            metrics=metrics,
            provenance=provenance,
        )
