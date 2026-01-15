"""
Geometry Pillar — Dodecahedron Realizer.

Forward-only computation for dodecahedron that wraps the existing service.

Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext

if TYPE_CHECKING:
    from canon_dsl import Form


class DodecahedronRealizer(Realizer):
    """
    Realizer for Dodecahedron forms.
    
    Converts validated Dodecahedron Declarations into 3D artifacts
    by delegating to the existing PlatonicSolidsService.
    
    Usage:
        engine = CanonEngine()
        engine.register_realizer("Dodecahedron", DodecahedronRealizer())
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        """This realizer handles only Dodecahedron forms."""
        return {"Dodecahedron"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize a Dodecahedron form into a drawable artifact.
        
        Args:
            form: The Dodecahedron Form from a validated Declaration
            context: Realization context with epsilon and config
        
        Returns:
            FormRealization containing artifact, metrics, and provenance
        
        Raises:
            ValueError: If form.kind is not "Dodecahedron"
        """
        if form.kind not in self.supported_kinds:
            raise ValueError(
                f"DodecahedronRealizer received unsupported kind: {form.kind}"
            )
        
        # Extract canonical parameter
        edge_length = form.params.get("edge_length", 1.0)
        
        # Delegate to existing service
        from shared.services.geometry.dodecahedron import DodecahedronSolidService
        
        # Get 3D drawing instructions
        service = DodecahedronSolidService()
        result = service.build(edge_length=edge_length)
        solid_payload = result.payload
        
        # Extract key metrics from metadata
        metrics = {
            "edge_length": edge_length,
            "volume": solid_payload.metadata.get("volume", 0.0),
            "surface_area": solid_payload.metadata.get("surface_area", 0.0),
            "faces": 12,
            "vertices": 20,
            "edges": 30,
        }
        
        # Build provenance
        provenance = {
            "realizer": "DodecahedronRealizer",
            "service": "DodecahedronSolidService",
            "method": "build",
            "face_shape": "pentagon",
            "dual": "icosahedron",
        }
        
        return FormRealization(
            artifact=solid_payload,
            metrics=metrics,
            provenance=provenance,
        )
