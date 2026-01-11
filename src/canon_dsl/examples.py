"""
Canon DSL — Examples.

This module provides runnable examples demonstrating the Canon DSL.
These examples use no UI dependencies and are suitable for testing.

NOTE: The example realizers defined here are for demonstration only.
Production realizers belong in their respective pillars:
    - VaultOfHestiaRealizer → src/pillars/geometry/realizers/
    - OrbitalTraceRealizer → src/pillars/astronomy/realizers/

Reference: Canon DSL Implementation Spec v0.2, Section 9

Run with:
    python3 -m src.canon_dsl.examples
"""

from __future__ import annotations

import math

from .ast import (
    Declaration,
    Form,
    Relation,
    Trace,
    InvariantConstraint,
    CanonTestRequest,
)
from .engine import CanonEngine, CanonValidationError, CanonBypassWarning
from .realizers import Realizer, FormRealization, RealizeContext


# =============================================================================
# EXAMPLE REALIZERS (for demonstration only)
# Production realizers belong in their respective pillars.
# =============================================================================

class CircleRealizer(Realizer):
    """
    Example realizer for Circle forms.
    
    NOTE: This is an example. Production version would live in:
        src/pillars/geometry/realizers/circle.py
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        return {"Circle"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        radius = form.params.get("radius", 1.0)
        center_x = form.params.get("center_x", 0.0)
        center_y = form.params.get("center_y", 0.0)
        
        circumference = 2 * math.pi * radius
        area = math.pi * radius ** 2
        
        metrics = {
            "radius": radius,
            "diameter": 2 * radius,
            "circumference": circumference,
            "area": area,
            "center": (center_x, center_y),
        }
        
        artifact = {
            "type": "circle",
            "center": (center_x, center_y),
            "radius": radius,
            "orientation": form.orientation,
        }
        
        return FormRealization(
            artifact=artifact,
            metrics=metrics,
            provenance={
                "form_id": form.id,
                "form_kind": form.kind,
            },
        )


class SquareRealizer(Realizer):
    """
    Example realizer for Square forms.
    
    NOTE: This is an example. Production version would live in:
        src/pillars/geometry/realizers/square.py
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        return {"Square"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        side = form.params.get("side", 1.0)
        
        metrics = {
            "side": side,
            "diagonal": side * math.sqrt(2),
            "perimeter": 4 * side,
            "area": side ** 2,
            "inradius": side / 2,
            "circumradius": side * math.sqrt(2) / 2,
        }
        
        artifact = {
            "type": "square",
            "side": side,
            "vertices": [
                (0, 0),
                (side, 0),
                (side, side),
                (0, side),
            ],
        }
        
        return FormRealization(
            artifact=artifact,
            metrics=metrics,
            provenance={
                "form_id": form.id,
                "form_kind": form.kind,
            },
        )


# =============================================================================
# EXAMPLES
# =============================================================================

def example_circle_in_square() -> None:
    """
    Example 9.1: Circle inscribed in Square.
    
    Demonstrates:
    - Declaring forms with parameters
    - Declaring a relation (INSCRIBED)
    - Declaring a constraint (circumference ratio)
    - Validating and realizing
    """
    print("=" * 60)
    print("Example 9.1: Circle in Square (Inscription)")
    print("=" * 60)
    
    decl = Declaration(
        title="Circle Inscribed in Square",
        forms=[
            Form(
                id="outer_square",
                kind="Square",
                params={"side": 10.0},
                symmetry_class="rotational_4",
            ),
            Form(
                id="inner_circle",
                kind="Circle",
                params={"radius": 5.0},
                curvature_class="constant",
                symmetry_class="continuous",
            ),
        ],
        relations=[
            Relation(
                kind="INSCRIBED",
                a="inner_circle",
                b="outer_square",
                params={"tangent": True},
            ),
        ],
        constraints=[
            InvariantConstraint(
                name="tangency_radius",
                expr={"equals": "side/2", "tolerance": "epsilon"},
                scope=["inner_circle", "outer_square"],
            ),
        ],
        epsilon=1e-9,
    )
    
    # Create engine and register example realizers
    engine = CanonEngine()
    engine.register_realizer("Circle", CircleRealizer())
    engine.register_realizer("Square", SquareRealizer())
    
    verdict = engine.validate(decl)
    print("\nValidation Result:")
    print(verdict.summary())
    
    if verdict.ok:
        print("\nRealization:")
        result = engine.realize(decl)
        print(result.summary())
        
        # Show declaration signature
        sig = result.get_declaration_signature()
        print(f"\nDeclaration Signature: {sig}")
    
    print()


def example_vault_of_hestia() -> None:
    """
    Example 9.2: Vault of Hestia.
    
    Demonstrates:
    - Complex form with φ-based constraints
    - Symmetry and dimensional class declarations
    - Constraint with phi tolerance
    
    Note: Full realization requires VaultOfHestiaRealizer from geometry pillar.
    """
    print("=" * 60)
    print("Example 9.2: Vault of Hestia")
    print("=" * 60)
    
    decl = Declaration(
        title="Vault of Hestia (2D)",
        forms=[
            Form(
                id="vault",
                kind="VaultOfHestia",
                params={"side_length": 10.0},
                symmetry_class="rotational_4",
                curvature_class="variable",
                dimensional_class=2,
            ),
        ],
        constraints=[
            InvariantConstraint(
                name="phi_resonance",
                expr={"equals": "phi", "tolerance": 1e-6},
                scope=["vault"],
                notes="The inradius resonance should equal φ (golden ratio)",
            ),
        ],
        tests=[
            CanonTestRequest(
                test="DIMENSIONAL_CONSISTENCY",
                scope=["vault"],
                notes="Verify 2D→3D extension preserves φ relationship",
            ),
        ],
        epsilon=1e-9,
        metadata={
            "author": "The Temple",
            "canon_ref": "Appendix A — Vault of Hestia",
        },
    )
    
    engine = CanonEngine()
    verdict = engine.validate(decl)
    
    print("\nValidation Result:")
    print(verdict.summary())
    
    print("\n(Realization requires VaultOfHestiaRealizer from geometry pillar)")
    print()


def example_venus_rose_trace() -> None:
    """
    Example 9.3: Venus Rose (Traced Form).
    
    Demonstrates:
    - Trace declaration for motion-revealed geometry
    - Closure status and period declaration
    - Void type and invariant claims
    
    Canon Reference: XII.7 — The Venus Pentagram
    """
    print("=" * 60)
    print("Example 9.3: Venus Rose (Traced Form)")
    print("=" * 60)
    
    decl = Declaration(
        title="Venus Rose Pentagram",
        forms=[
            Form(
                id="earth",
                kind="Point",
                params={"x": 0, "y": 0},
                notes="Geocentric reference point",
            ),
        ],
        traces=[
            Trace(
                id="venus_trace",
                kind="ORBITAL_TRACE",
                source_form=None,
                frame="earth",
                params={
                    "period": "8y",
                    "synodic_cycles": 5,
                    "orbital_ratio": "13:8",
                    "orientation": "CCW",
                },
                invariants_claimed=[
                    "closure_invariance",
                    "period_ratio_phi",
                    "five_fold_symmetry",
                ],
                void_type="swept",
                closure_status="closed",
            ),
        ],
        constraints=[
            InvariantConstraint(
                name="orbital_phi_ratio",
                expr={"ratio": ["synodic_cycles", "earth_years"], "approx": 0.625, "rel_tol": 0.01},
                scope=["venus_trace"],
                notes="5/8 = 0.625 ≈ 1/φ",
            ),
        ],
        tests=[
            CanonTestRequest(
                test="CLOSURE_INVARIANCE",
                scope=["venus_trace"],
            ),
            CanonTestRequest(
                test="PERIOD_RATIO",
                scope=["venus_trace"],
            ),
            CanonTestRequest(
                test="SYMMETRY_EMERGENCE",
                scope=["venus_trace"],
                params={"expected_symmetry": "rotational_5"},
            ),
        ],
        epsilon=1e-6,
        metadata={
            "canon_ref": "XII.7 — The Venus Pentagram",
        },
    )
    
    engine = CanonEngine()
    verdict = engine.validate(decl)
    
    print("\nValidation Result:")
    print(verdict.summary())
    
    if verdict.findings:
        print("\nAll Findings:")
        for finding in verdict.findings:
            print(f"\n{finding}")
    
    print()


def example_recursive_form() -> None:
    """
    Example: Sierpinski Triangle (Recursive Form with Truncation).
    
    Demonstrates:
    - Recursive form declaration
    - Truncation declaration (Canon XIII.6)
    - Iteration depth specification
    """
    print("=" * 60)
    print("Example: Sierpinski Triangle (Truncated Recursive Form)")
    print("=" * 60)
    
    decl = Declaration(
        title="Sierpinski Triangle (7 iterations)",
        forms=[
            Form(
                id="sierpinski",
                kind="SierpinskiTriangle",
                params={
                    "base_side": 100.0,
                    "generating_rule": "remove_middle_triangle",
                },
                symmetry_class="rotational_3",
                iteration_depth=7,
                truncated=True,
                notes="Finite representation of the infinite Sierpinski Triangle",
            ),
        ],
        tests=[
            CanonTestRequest(
                test="RECURSIVE_STABILITY",
                scope=["sierpinski"],
                params={"check_depth": 7},
            ),
        ],
        epsilon=1e-9,
    )
    
    engine = CanonEngine()
    verdict = engine.validate(decl)
    
    print("\nValidation Result:")
    print(verdict.summary())
    
    # Demonstrate Canon XIII.6 violation
    print("\n--- Testing Canon XIII.6 violation ---")
    
    bad_decl = Declaration(
        title="Sierpinski Triangle (INCORRECT - missing truncation)",
        forms=[
            Form(
                id="bad_sierpinski",
                kind="SierpinskiTriangle",
                params={"base_side": 100.0},
                iteration_depth=7,
                truncated=False,  # VIOLATION
            ),
        ],
    )
    
    bad_verdict = engine.validate(bad_decl)
    print("\nValidation Result (missing truncation):")
    print(bad_verdict.summary())
    
    print()


def example_bypass_protection() -> None:
    """
    Example: Bypass Protection.
    
    Demonstrates:
    - CanonBypassError when attempting skip_validation without allow_bypass
    - Proper way to enable bypass for migration
    """
    print("=" * 60)
    print("Example: Bypass Protection")
    print("=" * 60)
    
    decl = Declaration(
        title="Test Declaration",
        forms=[Form(id="test", kind="Circle", params={"radius": 5})],
    )
    
    # Engine with bypass disabled (default)
    engine = CanonEngine()
    engine.register_realizer("Circle", CircleRealizer())
    
    print("\n1. Attempting skip_validation=True with default engine...")
    try:
        result = engine.realize(decl, skip_validation=True)
        print("   (This should not print)")
    except Exception as e:
        print(f"   CanonBypassError: {e}")
    
    # Engine with bypass enabled (for migration)
    print("\n2. With allow_bypass=True (migration mode)...")
    import warnings
    migration_engine = CanonEngine(allow_bypass=True)
    migration_engine.register_realizer("Circle", CircleRealizer())
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = migration_engine.realize(decl, skip_validation=True)
        
        if w:
            print(f"   Warning emitted: {w[0].category.__name__}")
        print(f"   Result.was_validated(): {result.was_validated()}")
    
    print()


def main() -> None:
    """Run all examples."""
    print("\n" + "=" * 60)
    print("CANON DSL EXAMPLES")
    print("Hermetic Geometry Canon v1.0")
    print("=" * 60 + "\n")
    
    example_circle_in_square()
    example_vault_of_hestia()
    example_venus_rose_trace()
    example_recursive_form()
    example_bypass_protection()
    
    print("=" * 60)
    print("All examples complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
