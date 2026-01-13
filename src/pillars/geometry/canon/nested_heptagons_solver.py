"""
Geometry Pillar — Nested Heptagons Canon Solver.

Bidirectional Canon solver for N nested regular heptagons (default 7).
Uses the Golden Trisection ratios: Σ, Ρ, and α.

The canonical parameter is the edge length of the middle (layer 4 for N=7) heptagon.
All other layer properties are derived from the Golden Trisection cascade.

Reference: ADR-010 — Canon DSL Adoption
Reference: Golden Trisection ratios in heptagonal geometry
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition
from ..services.nested_heptagons_service import NestedHeptagonsService


_DEF_CANONICAL = 1.0


class NestedHeptagonsSolver(GeometrySolver):
    """Canon solver for nested regular heptagons (2D)."""

    def __init__(self, num_layers: int = 7, canonical_edge: float = _DEF_CANONICAL) -> None:
        """Initialize the solver.
        
        Args:
            num_layers: Number of nested heptagons (default 7)
            canonical_edge: Edge length of the canonical (middle) layer
        """
        self._num_layers = max(3, num_layers)
        self._service = NestedHeptagonsService(num_layers=self._num_layers, canonical_edge_length=canonical_edge)
        self._state: Dict[str, float] = {
            "num_layers": float(self._num_layers),
            "canonical_layer": float(self._service.canonical_layer),
            "canonical_edge": self._service.canonical_edge,
        }
        
        # Populate state with all layer properties
        for layer in range(1, self._num_layers + 1):
            props = self._service.layer_properties(layer)
            prefix = f"layer_{layer}_"
            self._state[f"{prefix}edge"] = props.edge_length
            self._state[f"{prefix}perimeter"] = props.perimeter
            self._state[f"{prefix}area"] = props.area
            self._state[f"{prefix}short_diagonal"] = props.short_diagonal
            self._state[f"{prefix}long_diagonal"] = props.long_diagonal
            self._state[f"{prefix}inradius"] = props.inradius
            self._state[f"{prefix}circumradius"] = props.circumradius

    # ── GeometrySolver properties ──────────────────────────────────────────
    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def form_type(self) -> str:
        return "NestedHeptagons"

    # ── Solver properties ──────────────────────────────────────────────────
    @property
    def canonical_key(self) -> str:
        return "canonical_edge"

    @property
    def supported_keys(self) -> set[str]:
        keys = {"canonical_edge", "num_layers", "canonical_layer"}
        # Add all layer-specific properties
        for layer in range(1, self._num_layers + 1):
            prefix = f"layer_{layer}_"
            keys.update({
                f"{prefix}edge",
                f"{prefix}perimeter",
                f"{prefix}area",
                f"{prefix}short_diagonal",
                f"{prefix}long_diagonal",
                f"{prefix}inradius",
                f"{prefix}circumradius",
            })
        return keys

    def read(self, key: str) -> float:
        if key not in self.supported_keys:
            raise KeyError(f"Unsupported key: {key}")
        return self._state[key]

    # ── Solving ────────────────────────────────────────────────────────────
    def solve_from(self, key: str, value: float) -> SolveResult:
        """Bidirectional solve: set any layer property and propagate."""
        if key not in self.supported_keys:
            return SolveResult(
                ok=False,
                message=f"Key '{key}' not supported",
                canonical_parameter=None,
                provenance=SolveProvenance(method="validation_failure"),
            )

        if key == "canonical_edge":
            new_canonical = value
        elif key == "num_layers" or key == "canonical_layer":
            return SolveResult(
                ok=False,
                message=f"Cannot solve from structural parameter '{key}'",
                canonical_parameter=None,
                provenance=SolveProvenance(method="unsupported_key"),
            )
        else:
            # Parse layer number and property from key: layer_N_property
            parts = key.split("_", 2)
            if len(parts) != 3 or parts[0] != "layer":
                return SolveResult(
                    ok=False,
                    message=f"Invalid layer key format: {key}",
                    canonical_parameter=None,
                    provenance=SolveProvenance(method="parse_error"),
                )
            
            try:
                layer = int(parts[1])
                property_name = parts[2]
            except ValueError:
                return SolveResult(
                    ok=False,
                    message=f"Invalid layer number in key: {key}",
                    canonical_parameter=None,
                    provenance=SolveProvenance(method="parse_error"),
                )
            
            # Map property short names to service names
            property_map = {
                "edge": "edge_length",
                "short_diagonal": "short_diagonal",
                "long_diagonal": "long_diagonal",
                "circumradius": "circumradius",
                "inradius": "inradius",
                "perimeter": "perimeter",
                "area": "area",
            }
            
            service_prop = property_map.get(property_name)
            if not service_prop:
                return SolveResult(
                    ok=False,
                    message=f"Unknown property: {property_name}",
                    canonical_parameter=None,
                    provenance=SolveProvenance(method="unsupported_property"),
                )
            
            # Use service's bidirectional setter
            try:
                self._service.set_layer_property(layer, service_prop, value)
                new_canonical = self._service.canonical_edge
            except ValueError as e:
                return SolveResult(
                    ok=False,
                    message=str(e),
                    canonical_parameter=None,
                    provenance=SolveProvenance(method="constraint_violation"),
                )

        # Update service and recompute all state
        self._service.canonical_edge = new_canonical
        self._state["canonical_edge"] = new_canonical
        
        for layer in range(1, self._num_layers + 1):
            props = self._service.layer_properties(layer)
            prefix = f"layer_{layer}_"
            self._state[f"{prefix}edge"] = props.edge_length
            self._state[f"{prefix}perimeter"] = props.perimeter
            self._state[f"{prefix}area"] = props.area
            self._state[f"{prefix}short_diagonal"] = props.short_diagonal
            self._state[f"{prefix}long_diagonal"] = props.long_diagonal
            self._state[f"{prefix}inradius"] = props.inradius
            self._state[f"{prefix}circumradius"] = props.circumradius

        return SolveResult(
            ok=True,
            message=f"Solved {key} = {value:.6f} → canonical_edge = {new_canonical:.6f}",
            canonical_parameter=new_canonical,
            provenance=SolveProvenance(
                method="golden_trisection_cascade",
                iterations=1,
                final_residual=0.0,
            ),
        )

    # ── Declaration Creation ───────────────────────────────────────────────
    def create_declaration(
        self,
        canonical_value: float,
        *,
        title: Optional[str] = None,
    ) -> Declaration:
        """Create a Canon-compliant Declaration."""
        self._service.canonical_edge = canonical_value
        
        # Collect all layer properties
        layers_data = []
        for layer in range(1, self._num_layers + 1):
            props = self._service.layer_properties(layer)
            layers_data.append({
                "layer": layer,
                "edge_length": props.edge_length,
                "perimeter": props.perimeter,
                "area": props.area,
                "short_diagonal": props.short_diagonal,
                "long_diagonal": props.long_diagonal,
                "inradius": props.inradius,
                "circumradius": props.circumradius,
            })

        form = Form(
            kind="NestedHeptagons",
            dimensional_class=2,
            params={
                "num_layers": self._num_layers,
                "canonical_layer": self._service.canonical_layer,
                "canonical_edge": canonical_value,
                "layers": layers_data,
                "sigma": NestedHeptagonsService.SIGMA,
                "rho": NestedHeptagonsService.RHO,
                "alpha": NestedHeptagonsService.ALPHA,
            },
        )

        return Declaration(
            intent=title or f"Sevenfold Nested Heptagons (canonical edge = {canonical_value:.4f})",
            form=form,
            constraints=[],
            metadata={
                "solver": "NestedHeptagonsSolver",
                "num_layers": self._num_layers,
                "canonical_layer": self._service.canonical_layer,
            },
        )

    # ── Property Definitions ───────────────────────────────────────────────
    def get_editable_properties(self) -> list[PropertyDefinition]:
        """Return canonical edge as the primary input."""
        return [
            PropertyDefinition(
                key="canonical_edge",
                label=f"Canonical Edge (Layer {self._service.canonical_layer})",
                unit="units",
                editable=True,
                category="Primary Input",
                tooltip=f"Edge length of the canonical (middle) heptagon layer {self._service.canonical_layer}",
            )
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        """Return all layer properties as editable (bidirectional) fields."""
        props = []
        
        for layer in range(1, self._num_layers + 1):
            # Get planetary name if available
            planet = ""
            if self._num_layers == 7 and layer <= len(NestedHeptagonsService.PLANETARY_NAMES):
                planet = f" ({NestedHeptagonsService.PLANETARY_NAMES[layer - 1]})"
            
            category = f"Layer {layer}{planet}"
            prefix = f"layer_{layer}_"
            
            props.extend([
                PropertyDefinition(
                    key=f"{prefix}edge",
                    label="Edge Length",
                    unit="units",
                    editable=True,
                    category=category,
                    tooltip=f"Edge length of layer {layer}",
                ),
                PropertyDefinition(
                    key=f"{prefix}short_diagonal",
                    label="Short Diagonal (ρ)",
                    unit="units",
                    editable=True,
                    category=category,
                    tooltip=f"Short diagonal of layer {layer}",
                ),
                PropertyDefinition(
                    key=f"{prefix}long_diagonal",
                    label="Long Diagonal (σ)",
                    unit="units",
                    editable=True,
                    category=category,
                    tooltip=f"Long diagonal of layer {layer}",
                ),
                PropertyDefinition(
                    key=f"{prefix}circumradius",
                    label="Circumradius",
                    unit="units",
                    editable=True,
                    category=category,
                    tooltip=f"Circumradius of layer {layer}",
                ),
                PropertyDefinition(
                    key=f"{prefix}inradius",
                    label="Inradius (Apothem)",
                    unit="units",
                    editable=True,
                    category=category,
                    tooltip=f"Inradius of layer {layer}",
                ),
                PropertyDefinition(
                    key=f"{prefix}perimeter",
                    label="Perimeter",
                    unit="units",
                    editable=True,
                    category=category,
                    tooltip=f"Perimeter of layer {layer}",
                ),
                PropertyDefinition(
                    key=f"{prefix}area",
                    label="Area",
                    unit="units²",
                    editable=True,
                    category=category,
                    tooltip=f"Area of layer {layer}",
                ),
            ])
        
        return props

    def get_derivation(self) -> str:
        """Return the mathematical foundation of the Golden Trisection."""
        return f"""
═══════════════════════════════════════════════════════════════════════════════
THE SEVENFOLD NESTED HEPTAGON: GOLDEN TRISECTION CASCADE
═══════════════════════════════════════════════════════════════════════════════

The {self._num_layers} nested regular heptagons form a sacred geometric cascade based on the 
Golden Trisection ratios discovered in heptagonal geometry.

─── The Three Sacred Ratios ───

In a regular heptagon with unit edge length (s = 1):

  Σ (SIGMA) = {NestedHeptagonsService.SIGMA:.15f}
    • The ratio of the LONG DIAGONAL to the edge
    • Long diagonal connects vertices 3 steps apart (skipping 2)

  Ρ (RHO) = {NestedHeptagonsService.RHO:.15f}
    • The ratio of the SHORT DIAGONAL to the edge
    • Short diagonal connects vertices 2 steps apart (skipping 1)

  α (ALPHA) = {NestedHeptagonsService.ALPHA:.15f}
    • The NESTING RATIO (inner/middle edge ratio)
    • Derived from the geometric cascade relationship

─── The Sevenfold Cascade ───

The canonical reference is layer {self._service.canonical_layer} (the middle layer, representing the Sun).
All other layers scale from this using the Golden Trisection ratios:

  Moving OUTWARD (toward Saturn):
    Each successive layer's edge = previous × (Ρ × Σ)
    Scale factor = (Ρ × Σ)^n ≈ {(NestedHeptagonsService.RHO * NestedHeptagonsService.SIGMA):.6f}^n

  Moving INWARD (toward the Moon):
    Each successive layer's edge = previous × α
    Scale factor = α^n ≈ {NestedHeptagonsService.ALPHA:.6f}^n

─── Planetary Correspondence (for 7 layers) ───

  Layer 7 (Outermost): SATURN — Boundary, Structure, Time
  Layer 6: JUPITER — Expansion, Abundance, Wisdom
  Layer 5: MARS — Force, Will, Action
  Layer 4 (Middle): SUN — Center, Source, Canonical Reference
  Layer 3: VENUS — Harmony, Beauty, Proportion
  Layer 2: MERCURY — Communication, Intellect, Speed
  Layer 1 (Innermost): MOON — Reflection, Mystery, Foundation

─── Bidirectional Solving ───

Any property of any layer can be set, and all other layers will recalculate:
• Set layer 3's long diagonal to X → all layers adjust proportionally
• Set layer 7's area to Y → the entire cascade recomputes
• Set layer 1's circumradius to Z → the system maintains golden ratios

This bidirectional capability reveals the INTERCONNECTED NATURE of the 
heptagonal cascade: touch one layer, and all others respond in harmonic resonance.

─── Why the Heptagon? ───

The heptagon (7-sided polygon) is special:
• Cannot be constructed with compass and straightedge (like π, it transcends)
• 7 is the number of classical planets, days of the week, chakras
• The heptagon ratios (Σ, Ρ, α) encode golden proportion relationships
• Nested heptagons create a FRACTAL pattern of sacred sevens

The sevenfold nested heptagon is thus a GEOMETRIC MANDALA of the classical 
cosmos: seven heavens, seven spheres, seven levels of being, all nested within 
each other in perfect harmonic proportion.

═══════════════════════════════════════════════════════════════════════════════
"""
