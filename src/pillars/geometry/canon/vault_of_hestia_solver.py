"""
Geometry Pillar — Vault of Hestia Solver.

Bidirectional solver for the Vault of Hestia that converts user input
into Canon-compliant Declarations.

This wraps the bidirectional logic from VaultOfHestiaSolidCalculator
but outputs Declarations instead of calling builders directly.

Reference: Hermetic Geometry Canon v1.0, Appendix A — Vault of Hestia
Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

import math
from typing import Optional

from canon_dsl import (
    Solver,
    SolveResult,
    SolveProvenance,
    Declaration,
    Form,
    InvariantConstraint,
)


# Golden ratio constant
PHI = (1 + math.sqrt(5)) / 2


class VaultOfHestiaSolver(Solver):
    """
    Bidirectional solver for the Vault of Hestia.
    
    Converts any valid property input into the canonical parameter (side_length),
    then returns a SolveResult that can be used to build a Declaration.
    
    Canonical Parameter: side_length (s)
    
    Relationships:
        - sphere_radius: r = s / (2φ)
        - cube_volume: V_c = s³
        - pyramid_volume: V_p = s³/3
        - sphere_volume: V_s = (4/3)πr³ = (4/3)π(s/2φ)³
        - sphere_surface_area: A_s = 4πr²
        - cube_surface_area: A_c = 6s²
    
    Usage:
        solver = VaultOfHestiaSolver()
        result = solver.solve_from("sphere_volume", 523.6)
        
        if result.ok:
            decl = solver.create_declaration(result.canonical_parameter)
            verdict = engine.validate(decl)
    """
    
    @property
    def canonical_key(self) -> str:
        return "side_length"
    
    @property
    def supported_keys(self) -> set[str]:
        return {
            "side_length",
            "sphere_radius",
            "cube_volume",
            "cube_surface_area",
            "pyramid_volume",
            "sphere_volume",
            "sphere_surface_area",
        }
    
    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Solve for side_length given any valid property.
        
        Args:
            key: The property being set
            value: The value entered by the user
        
        Returns:
            SolveResult with the derived side_length and provenance
        """
        if value <= 0:
            return SolveResult.invalid(
                key=key,
                value=value,
                reason="Value must be positive (Canon I.4: Continuity as Ground)"
            )
        
        if key not in self.supported_keys:
            return SolveResult.invalid(
                key=key,
                value=value,
                reason=f"Unknown property: {key}"
            )
        
        s: Optional[float] = None
        formula: str = ""
        intermediates: dict[str, float] = {}
        warnings: list[str] = []
        
        if key == "side_length":
            s = value
            formula = "s = s (identity)"
            
        elif key == "sphere_radius":
            # r = s / (2φ) → s = r × 2φ
            s = value * 2 * PHI
            formula = "s = r × 2φ"
            intermediates["phi"] = PHI
            
        elif key == "cube_volume":
            # V = s³ → s = ∛V
            s = value ** (1/3)
            formula = "s = ∛V_cube"
            
        elif key == "cube_surface_area":
            # A = 6s² → s = √(A/6)
            s = math.sqrt(value / 6)
            formula = "s = √(A_cube / 6)"
            
        elif key == "pyramid_volume":
            # V = s³/3 → s³ = 3V → s = ∛(3V)
            s = (3 * value) ** (1/3)
            formula = "s = ∛(3 × V_pyramid)"
            
        elif key == "sphere_volume":
            # V = (4/3)πr³ → r = ∛(3V / 4π)
            # r = s / (2φ) → s = r × 2φ
            r = (3 * value / (4 * math.pi)) ** (1/3)
            s = r * 2 * PHI
            formula = "r = ∛(3V / 4π); s = r × 2φ"
            intermediates["sphere_radius"] = r
            intermediates["phi"] = PHI
            
        elif key == "sphere_surface_area":
            # A = 4πr² → r = √(A / 4π)
            # r = s / (2φ) → s = r × 2φ
            r = math.sqrt(value / (4 * math.pi))
            s = r * 2 * PHI
            formula = "r = √(A / 4π); s = r × 2φ"
            intermediates["sphere_radius"] = r
            intermediates["phi"] = PHI
        
        if s is None:
            return SolveResult.invalid(key, value, "Solver logic error")
        
        # Compute φ-resonance for validation hint
        r = s / (2 * PHI)
        inradius_resonance = s / (2 * r)  # Should equal φ
        if abs(inradius_resonance - PHI) > 1e-9:
            warnings.append(
                f"Numerical precision: inradius_resonance={inradius_resonance:.10f}, "
                f"expected φ={PHI:.10f}"
            )
        
        return SolveResult.success(
            canonical_parameter=s,
            canonical_key=self.canonical_key,
            provenance=SolveProvenance(
                source_key=key,
                source_value=value,
                formula_used=formula,
                intermediate_values=intermediates,
                assumptions=[
                    "Vault structure: Cube → Pyramid → Sphere",
                    "Sphere inscribed in pyramid, pyramid inscribed in cube",
                    "Pyramid height equals cube side (h = s)",
                ],
            ),
            warnings=warnings,
        )
    
    def get_all_properties(self, side_length: float) -> dict[str, float]:
        """
        Compute all derived properties from side_length.
        
        This is the forward direction, used to populate UI fields.
        """
        s = side_length
        r = s / (2 * PHI)
        
        return {
            "side_length": s,
            "sphere_radius": r,
            "cube_volume": s ** 3,
            "cube_surface_area": 6 * s ** 2,
            "pyramid_volume": s ** 3 / 3,
            "pyramid_height": s,
            "sphere_volume": (4/3) * math.pi * r ** 3,
            "sphere_surface_area": 4 * math.pi * r ** 2,
            "hestia_ratio_3d": math.pi / (6 * PHI ** 3),
            "inradius_resonance_phi": PHI,
            "volume_efficiency": (4/3) * math.pi * r ** 3 / s ** 3,
        }
    
    def create_declaration(
        self,
        side_length: float,
        *,
        validate_phi: bool = True,
        title: Optional[str] = None,
    ) -> Declaration:
        """
        Create a Canon-compliant Declaration for the Vault of Hestia.
        
        This is the bridge from Solver output to Canon validation.
        
        Args:
            side_length: The canonical parameter
            validate_phi: Whether to include φ-resonance constraint
            title: Custom title for the declaration
        
        Returns:
            A Declaration ready for Canon validation
        """
        forms = [
            Form(
                id="vault",
                kind="VaultOfHestia",
                params={"side_length": side_length},
                symmetry_class="rotational_4",
                curvature_class="variable",
                dimensional_class=3,
                notes="Cube → Pyramid → Sphere with φ mediation",
            ),
        ]
        
        constraints = []
        if validate_phi:
            constraints.append(
                InvariantConstraint(
                    name="phi_resonance",
                    expr={"equals": "phi", "tolerance": 1e-6},
                    scope=["vault"],
                    notes="Inradius resonance should equal φ (golden ratio)",
                )
            )
        
        return Declaration(
            title=title or f"Vault of Hestia (s={side_length:.4f})",
            forms=forms,
            constraints=constraints,
            epsilon=1e-9,
            metadata={
                "canon_ref": "Appendix A — Vault of Hestia",
                "solver": "VaultOfHestiaSolver",
            },
        )
