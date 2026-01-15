"""
Circle Realizer - Full Canon-compliant realization.

This is a REFERENCE IMPLEMENTATION for ADR-012 migration.
Follow this pattern for all 2D shape migrations.

Reference: VaultOfHestiaRealizer (the 3D template)
Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext

if TYPE_CHECKING:
    from canon_dsl import Form


# Service version for provenance tracking
_SERVICE_VERSION = "1.0"


class CircleRealizer(Realizer):
    """
    Realizer for Circle forms.
    
    Converts validated Circle Declarations into drawable artifacts
    by delegating to the existing CircleShapeService.
    
    This realizer:
    - Accepts only Form.kind == "Circle"
    - Extracts radius from form.params
    - Calls CircleShapeService.build(radius=...)
    - Returns artifact with full metrics and provenance
    
    It does NOT:
    - Perform validation (CanonEngine already did that)
    - Reimplement geometry computation (delegates to existing service)
    - Import UI components (stays pure)
    
    Usage:
        engine = CanonEngine()
        engine.register_realizer("Circle", CircleRealizer())
        
        decl = Declaration(
            forms=[Form(id="circle", kind="Circle", params={"radius": 5.0})]
        )
        
        result = engine.realize(decl)  # Validates first, then realizes
        payload = result.get_artifact("circle")
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        """This realizer handles only Circle forms."""
        return {"Circle"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize a Circle form into a drawable artifact.
        
        Args:
            form: The Circle Form from a validated Declaration
            context: Realization context with epsilon and config
        
        Returns:
            FormRealization containing:
            - artifact: Drawing instructions from CircleShapeService
            - metrics: Key derived metrics (radius, area, circumference)
            - provenance: Full traceability data
        
        Raises:
            ValueError: If form.kind is not "Circle"
        """
        # Sanity check (should never fail if CanonEngine is routing correctly)
        if form.kind not in self.supported_kinds:
            raise ValueError(
                f"CircleRealizer received unsupported kind: {form.kind}"
            )
        
        # Extract canonical parameter
        radius = form.params.get("radius", 1.0)
        
        # Delegate to existing service (no reimplementation!)
        from ..services.circle_shape import CircleShapeService
        from ..ui.scene_adapter import build_scene_payload
        
        # Get drawing instructions from service (returns a dict)
        drawing_dict = CircleShapeService.build(radius=radius)
        
        # Convert to scene payload with primitives
        # Return scene_payload directly (like VaultOfHestia returns SolidPayload)
        scene_payload = build_scene_payload(drawing_dict, labels=[])
        
        # Extract metrics for the realization result
        metrics = self._extract_metrics(radius)
        
        # Build provenance for traceability
        provenance = self._build_provenance(form, radius, context)
        
        return FormRealization(
            artifact=scene_payload,  # Return scene payload directly
            metrics=metrics,
            provenance=provenance,
        )
    
    def _extract_metrics(self, radius: float) -> dict:
        """
        Extract key metrics from the realization.
        
        These are the metrics most useful for verification and display.
        """
        import math
        
        return {
            # Canonical parameter
            "radius": radius,
            
            # Core measurements
            "diameter": 2 * radius,
            "circumference": 2 * math.pi * radius,
            "area": math.pi * radius * radius,
            
            # Proportions (Canon III.1)
            "circumference_to_diameter": math.pi,  # Always π
            "area_to_radius_squared": math.pi,      # Always π
        }
    
    def _build_provenance(
        self,
        form: Form,
        radius: float,
        context: RealizeContext,
    ) -> dict:
        """
        Build provenance data for full traceability.
        
        Provenance enables:
        - Debugging ("why does this look like this?")
        - Reproducibility ("same declaration → same artifact")
        - Case law storage ("this declaration was valid/invalid")
        """
        import math
        
        return {
            # Declaration source
            "form_id": form.id,
            "form_kind": form.kind,
            "declaration_title": context.declaration.title,
            
            # Service identity
            "service": "CircleShapeService",
            "service_version": _SERVICE_VERSION,
            "realizer": "CircleRealizer",
            
            # Canon references
            "canon_refs": [
                "Article II — Canonical Forms (Circle)",
                "III.1 — Proportion over Magnitude",
                "III.4 — Transcendental Constants (π)",
            ],
            
            # Key invariants verified by this realization
            "invariants": {
                "pi_circumference": 2 * math.pi * radius / (2 * radius),  # = π
                "pi_area": (math.pi * radius * radius) / (radius * radius),  # = π
            },
            
            # Configuration
            "epsilon": context.epsilon,
        }
