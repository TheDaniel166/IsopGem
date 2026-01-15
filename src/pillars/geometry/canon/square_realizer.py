"""Square Realizer - Canon-compliant realization.

Reference implementation following CircleRealizer pattern.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext

if TYPE_CHECKING:
    from canon_dsl import Form


_SERVICE_VERSION = "1.0"


class SquareRealizer(Realizer):
    """Realizer for Square forms."""
    
    @property
    def supported_kinds(self) -> set[str]:
        return {"Square"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """Realize a Square form into a drawable artifact."""
        if form.kind not in self.supported_kinds:
            raise ValueError(
                f"SquareRealizer received unsupported kind: {form.kind}"
            )
        
        # Extract canonical parameter
        side = form.params.get("side", 1.0)
        
        # Delegate to existing service (no reimplementation!)
        from ..services.square_shape import SquareShapeService
        from ..ui.scene_adapter import build_scene_payload
        
        # Get drawing instructions from service
        drawing_dict = SquareShapeService.build(side=side)
        
        # Convert to scene payload with primitives
        # Return scene_payload directly (like VaultOfHestia returns SolidPayload)
        scene_payload = build_scene_payload(drawing_dict, labels=[])
        
        # Extract metrics
        metrics = self._extract_metrics(side)
        
        # Build provenance
        provenance = self._build_provenance(form, side, context)
        
        return FormRealization(
            artifact=scene_payload,  # Return scene payload directly
            metrics=metrics,
            provenance=provenance,
        )
    
    def _extract_metrics(self, side: float) -> dict:
        """Extract key metrics from the realization."""
        return {
            "side": side,
            "perimeter": 4 * side,
            "area": side * side,
            "diagonal": side * math.sqrt(2),
            "perimeter_to_side": 4.0,
            "area_to_side_squared": 1.0,
            "diagonal_to_side": math.sqrt(2),
        }
    
    def _build_provenance(self, form: Form, side: float, context: RealizeContext) -> dict:
        """Build provenance data for full traceability."""
        return {
            "form_id": form.id,
            "form_kind": form.kind,
            "declaration_title": context.declaration.title,
            "service": "SquareShapeService",
            "service_version": _SERVICE_VERSION,
            "realizer": "SquareRealizer",
            "canon_refs": [
                "Article II — Canonical Forms (Square)",
                "D₄ Symmetry Group",
            ],
            "invariants": {
                "sqrt_2_diagonal": (side * math.sqrt(2)) / side,  # = √2
            },
            "epsilon": context.epsilon,
        }
