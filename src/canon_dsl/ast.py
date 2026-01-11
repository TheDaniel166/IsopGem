"""
Canon DSL — Abstract Syntax Tree (AST) Dataclasses.

This module defines the immutable data structures that represent
Canon-compliant geometry declarations.

Reference: Hermetic Geometry Canon v1.0
Reference: Canon DSL Implementation Spec v0.2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class Form:
    """
    A declarative geometric form.
    
    Forms are declarations of geometric intent, not computed meshes.
    Every form must declare its properties explicitly per Canon requirements.
    
    Attributes:
        id: Unique identifier within the declaration (e.g., "circle_1")
        kind: Form type (e.g., "Circle", "Cube", "VaultOfHestia", "SierpinskiTriangle")
        params: Numeric/symbolic parameters (e.g., {"radius": 10})
        meaning: Optional symbolic tags (non-binding, for documentation)
        orientation: Chirality/orientation ("CW", "CCW", "L", "R", "RH", "LH")
                     Required for orientation-sensitive forms (Canon V.4.5)
        symmetry_class: Symmetry type ("rotational_3", "reflective", "continuous", "none")
                        Required per Canon II.5
        curvature_class: Curvature type ("zero", "constant", "variable")
                         Required for curved forms per Canon XIV.1
        dimensional_class: Dimensional power (1=length, 2=area, 3=volume)
                           Per Canon XI definitions
        iteration_depth: For recursive forms; None means infinite/limit (Canon XIII)
        truncated: True if this is a finite representation of infinite form (Canon XIII.6)
        notes: Human documentation
    
    Canon References:
        - II.1: Fundamental Forms
        - II.5: Symmetry Classes
        - V.4: Chirality and Orientation
        - XIII: Recursive Forms
        - XIV: Curvature
    """
    
    id: str
    kind: str
    params: dict[str, Any] = field(default_factory=dict)
    meaning: dict[str, Any] = field(default_factory=dict)
    orientation: Optional[str] = None
    symmetry_class: Optional[str] = None
    curvature_class: Optional[str] = None
    dimensional_class: Optional[int] = None
    iteration_depth: Optional[int] = None
    truncated: bool = False
    notes: Optional[str] = None


@dataclass(frozen=True)
class Relation:
    """
    A declared relationship between forms.
    
    Relations describe how forms relate geometrically (containment,
    inscription, intersection, etc.).
    
    Attributes:
        kind: Relation type (e.g., "INSCRIBED", "CONTAINS", "GEODESIC_PATH")
        a: Source form ID
        b: Target form ID
        params: Additional parameters (e.g., {"tangent": True, "reflection": True})
        notes: Human documentation
    
    Canon References:
        - II.2: Boundedness and Containment
        - V.4.3: Reflection must be explicitly declared
        - XIV.4: Geodesics
    """
    
    kind: str
    a: str
    b: str
    params: dict[str, Any] = field(default_factory=dict)
    notes: Optional[str] = None


@dataclass(frozen=True)
class Trace:
    """
    A motion-revealed form declaration (Canon Article XII).
    
    Traces assert that a form is revealed through motion over time.
    The trace does not compute—it declares intent and invariants
    that must be validated.
    
    Attributes:
        id: Unique identifier
        kind: Trace type ("ORBITAL_TRACE", "LISSAJOUS_TRACE", "SPIRAL_TRACE", etc.)
        source_form: ID of moving form (if applicable)
        frame: Reference frame identifier
        params: Motion parameters (period, steps, sampling, etc.)
        invariants_claimed: List of claimed invariants 
                           (e.g., ["closure_invariance", "period_ratio"])
        void_type: Type of void measurement ("swept", "instantaneous", "time_averaged")
                   Required per Canon XII.9
        closure_status: Closure declaration ("closed", "asymptotic", "open", "indeterminate")
                        Required per Canon XII.6
        notes: Human documentation
    
    Canon References:
        - XII.1: Motion reveals, it does not create
        - XII.4: Cyclic motion and closure
        - XII.6: Declaration of temporal scope
        - XII.9: Cyclic motion and void
    """
    
    id: str
    kind: str
    source_form: Optional[str] = None
    frame: Optional[str] = None
    params: dict[str, Any] = field(default_factory=dict)
    invariants_claimed: list[str] = field(default_factory=list)
    void_type: Optional[str] = None
    closure_status: str = "indeterminate"
    notes: Optional[str] = None


@dataclass(frozen=True)
class InvariantConstraint:
    """
    A declared invariant that must hold.
    
    Constraints express proportional or numeric relationships
    that the declaration claims to satisfy.
    
    Attributes:
        name: Constraint identifier (e.g., "phi_resonance")
        expr: Structured expression defining the constraint
              Examples:
                {"equals": "phi", "tolerance": "epsilon"}
                {"approx": 1.618, "rel_tol": 1e-6}
                {"ratio": ["a.radius", "b.radius"], "equals": "sqrt_2"}
        scope: Form IDs involved in this constraint
        notes: Human documentation
    
    Canon References:
        - III.1: Proportion over magnitude
        - III.4: Transcendental constants must arise naturally
        - Appendix C: Epsilon law
    """
    
    name: str
    expr: dict[str, Any]
    scope: list[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass(frozen=True)
class CanonTestRequest:
    """
    A request to run a specific Canon test.
    
    Test requests invoke the validation tests defined in Canon Article IX.
    
    Attributes:
        test: Test identifier (e.g., "VOID_MONOTONICITY", "SCALING_INVARIANCE")
        scope: Form IDs to include in the test
        params: Test-specific parameters
        notes: Human documentation
    
    Canon References:
        - IX.1: Proportional Recovery Test
        - IX.2: Dimensional Consistency Test
        - IX.3: Void Monotonicity Test
        - IX.4: Scaling Invariance Test
        - IX.5: Limit Behavior Test
        - IX.6: Recursive Stability Test
        - IX.7: Curvature Invariance Test
        - XII.8.1: Closure Invariance Test
        - XII.8.2: Period Ratio Test
        - XII.8.3: Symmetry Emergence Test
    """
    
    test: str
    scope: list[str] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    notes: Optional[str] = None


@dataclass(frozen=True)
class Declaration:
    """
    A complete Canon-compliant geometry declaration.
    
    A Declaration bundles forms, relations, traces, constraints,
    and test requests into a single validatable unit.
    
    Attributes:
        title: Human-readable title
        forms: List of declared forms
        relations: List of declared relations between forms
        traces: List of motion-revealed form declarations
        constraints: List of invariant constraints to verify
        tests: List of Canon tests to run
        metadata: Additional metadata (author, version, etc.)
        epsilon: Default numerical tolerance for this declaration
                 (required if any numeric constraints exist per Appendix C.3)
    
    Canon References:
        - All articles; Declaration is the root container
    """
    
    title: str
    forms: list[Form] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    traces: list[Trace] = field(default_factory=list)
    constraints: list[InvariantConstraint] = field(default_factory=list)
    tests: list[CanonTestRequest] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    epsilon: Optional[float] = None
    
    def get_form(self, form_id: str) -> Optional[Form]:
        """Retrieve a form by ID."""
        for form in self.forms:
            if form.id == form_id:
                return form
        return None
    
    def get_all_ids(self) -> set[str]:
        """Get all declared form and trace IDs."""
        ids = {f.id for f in self.forms}
        ids.update(t.id for t in self.traces)
        return ids
