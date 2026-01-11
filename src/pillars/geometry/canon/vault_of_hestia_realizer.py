"""
Geometry Pillar — Vault of Hestia Realizer.

Realizer that converts validated VaultOfHestia Declarations into
concrete SolidPayload artifacts by delegating to the existing service.

ARCHITECTURAL PRINCIPLE:
    This realizer WRAPS the existing VaultOfHestiaSolidService.
    It does NOT reimplement the geometry computation.
    It does NOT perform validation (CanonEngine already did that).

Reference: Hermetic Geometry Canon v1.0, Appendix A — Vault of Hestia
Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext
from ..services.vault_of_hestia_solid import (
    VaultOfHestiaSolidService,
    VaultOfHestiaMetrics,
)

if TYPE_CHECKING:
    from canon_dsl import Form


# Service version for provenance tracking
_SERVICE_VERSION = "1.0"


class VaultOfHestiaRealizer(Realizer):
    """
    Realizer for VaultOfHestia forms.
    
    Converts validated VaultOfHestia Declarations into SolidPayload artifacts
    by delegating to the existing VaultOfHestiaSolidService.
    
    This realizer:
    - Accepts only Form.kind == "VaultOfHestia"
    - Extracts side_length from form.params
    - Calls VaultOfHestiaSolidService.build(side_length)
    - Returns artifact with full metrics and provenance
    
    It does NOT:
    - Perform validation (CanonEngine already did that)
    - Reimplement geometry computation (delegates to existing service)
    - Import UI components (stays pure)
    
    Usage:
        engine = CanonEngine()
        engine.register_realizer("VaultOfHestia", VaultOfHestiaRealizer())
        
        decl = Declaration(
            forms=[Form(id="vault", kind="VaultOfHestia", params={"side_length": 10})]
        )
        
        result = engine.realize(decl)  # Validates first, then realizes
        payload = result.get_artifact("vault")
    
    Canon References:
        - Appendix A: Vault of Hestia canonical example
        - III.4: Transcendental constants (φ relationship)
        - VI.1-4: Void computations
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        """This realizer handles only VaultOfHestia forms."""
        return {"VaultOfHestia"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize a VaultOfHestia form into a SolidPayload.
        
        Args:
            form: The VaultOfHestia Form from a validated Declaration
            context: Realization context with epsilon and config
        
        Returns:
            FormRealization containing:
            - artifact: The SolidPayload from VaultOfHestiaSolidService
            - metrics: Key derived metrics (φ resonance, volumes, etc.)
            - provenance: Full traceability data
        
        Raises:
            ValueError: If form.kind is not "VaultOfHestia"
        """
        # Sanity check (should never fail if CanonEngine is routing correctly)
        if form.kind not in self.supported_kinds:
            raise ValueError(
                f"VaultOfHestiaRealizer received unsupported kind: {form.kind}"
            )
        
        # Extract canonical parameter
        side_length = form.params.get("side_length", 10.0)
        
        # Delegate to existing service (no reimplementation!)
        result = VaultOfHestiaSolidService.build(side_length)
        
        # Extract metrics for the realization result
        metrics = self._extract_metrics(result.metrics)
        
        # Build provenance for traceability
        provenance = self._build_provenance(form, result.metrics, context)
        
        return FormRealization(
            artifact=result.payload,
            metrics=metrics,
            provenance=provenance,
        )
    
    def _extract_metrics(self, raw_metrics: VaultOfHestiaMetrics) -> dict:
        """
        Extract key metrics from the service result.
        
        These are the metrics most useful for verification and display.
        """
        return {
            # Canonical parameter
            "side_length": raw_metrics.side_length,
            
            # Core dimensions
            "sphere_radius": raw_metrics.sphere_radius,
            "pyramid_height": raw_metrics.side_length,  # h = s
            
            # Volumes
            "cube_volume": raw_metrics.cube_volume,
            "pyramid_volume": raw_metrics.pyramid_volume,
            "sphere_volume": raw_metrics.sphere_volume,
            
            # Void volumes (Canon VI)
            "void_volume_cube_pyramid": raw_metrics.void_volume_cube_pyramid,
            "void_volume_pyramid_sphere": raw_metrics.void_volume_pyramid_sphere,
            
            # Surface areas
            "cube_surface_area": raw_metrics.cube_surface_area,
            "sphere_surface_area": raw_metrics.sphere_surface_area,
            "pyramid_total_surface_area": raw_metrics.pyramid_total_surface_area,
            
            # Sacred ratios
            "hestia_ratio_3d": raw_metrics.hestia_ratio_3d,
            "inradius_resonance_phi": raw_metrics.inradius_resonance_phi,
            "ratio_sphere_pyramid": raw_metrics.ratio_sphere_pyramid,
            "ratio_pyramid_cube": raw_metrics.ratio_pyramid_cube,
            
            # Efficiency
            "volume_efficiency": raw_metrics.volume_efficiency,
        }
    
    def _build_provenance(
        self,
        form: Form,
        metrics: VaultOfHestiaMetrics,
        context: RealizeContext,
    ) -> dict:
        """
        Build provenance data for full traceability.
        
        Provenance enables:
        - Debugging ("why does this look like this?")
        - Reproducibility ("same declaration → same artifact")
        - Case law storage ("this declaration was valid/invalid")
        """
        return {
            # Declaration source
            "form_id": form.id,
            "form_kind": form.kind,
            "declaration_title": context.declaration.title,
            
            # Service identity
            "service": "VaultOfHestiaSolidService",
            "service_version": _SERVICE_VERSION,
            "realizer": "VaultOfHestiaRealizer",
            
            # Canon references
            "canon_refs": [
                "Appendix A — Vault of Hestia",
                "III.4 — Transcendental Constants (φ relationship)",
                "VI.1-4 — Void Computations",
            ],
            
            # Key invariants verified by this realization
            "invariants": {
                "phi_resonance": metrics.inradius_resonance_phi,
                "trinity_ratio": metrics.ratio_pyramid_cube,  # = 1/3
                "hestia_ratio": metrics.hestia_ratio_3d,      # = π/(6φ³)
            },
            
            # Configuration
            "epsilon": context.epsilon,
        }
