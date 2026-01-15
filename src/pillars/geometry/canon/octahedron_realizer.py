"""
Geometry Pillar — Octahedron Realizer.

Forward-only computation for octahedron that wraps the existing service.

Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext

if TYPE_CHECKING:
    from canon_dsl import Form


class OctahedronRealizer(Realizer):
    """
    Realizer for Octahedron forms.
    
    Converts validated Octahedron Declarations into 3D artifacts
    by delegating to the existing PlatonicSolidsService.
    
    Usage:
        engine = CanonEngine()
        engine.register_realizer("Octahedron", OctahedronRealizer())
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        """This realizer handles only Octahedron forms."""
        return {"Octahedron"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize an Octahedron form into a drawable artifact.
        
        Args:
            form: The Octahedron Form from a validated Declaration
            context: Realization context with epsilon and config
        
        Returns:
            FormRealization containing artifact, metrics, and provenance
        
        Raises:
            ValueError: If form.kind is not "Octahedron"
        """
        if form.kind not in self.supported_kinds:
            raise ValueError(
                f"OctahedronRealizer received unsupported kind: {form.kind}"
            )
        
        # Extract canonical parameter
        edge_length = form.params.get("edge_length", 1.0)
        
        # Delegate to existing service
        from shared.services.geometry.octahedron import OctahedronSolidService
        
        # Get 3D drawing instructions
        service = OctahedronSolidService()
        result = service.build(edge_length=edge_length)
        solid_payload = result.payload
        
        # Extract key metrics from metadata
        metrics = {
            "edge_length": edge_length,
            "volume": solid_payload.metadata.get("volume", 0.0),
            "surface_area": solid_payload.metadata.get("surface_area", 0.0),
            "faces": 8,
            "vertices": 6,
            "edges": 12,
        }
        
        # Build provenance
        provenance = {
            "realizer": "OctahedronRealizer",
            "service": "OctahedronSolidService",
            "method": "build",
            "dual": "cube",
        }
        
        return FormRealization(
            artifact=solid_payload,
            metrics=metrics,
            provenance=provenance,
        )
