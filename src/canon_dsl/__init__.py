"""
Canon DSL — A Canon-compliant declarative geometry system.

This package implements the Hermetic Geometry Canon v1.0 as an executable
validation and realization engine.

Architecture:
    Solver (inverse) → Declaration (AST) → Validation (Canon Engine) → Realization (Realizers)
    
    Solvers:   Turn partial values into Declarations (bidirectional calculation)
    Engine:    Validates Declarations against Canon rules
    Realizers: Turn validated Declarations into Artifacts (forward computation)

Modules:
    ast         - Immutable dataclasses: Form, Relation, Trace, Declaration
    canon_refs  - Canon article identifiers and utilities
    findings    - Finding, Severity, Verdict structures
    rules       - CanonRule interface and built-in validation rules
    engine      - CanonEngine.validate() and realize()
    realizers   - Realizer interface and registry
    solvers     - Solver interface for bidirectional calculation

Usage:
    from canon_dsl import Declaration, Form, Relation, CanonEngine
    
    decl = Declaration(
        title="My Geometry",
        forms=[Form(id="circle_1", kind="Circle", params={"radius": 10})]
    )
    
    engine = CanonEngine()
    verdict = engine.validate(decl)
    
    if verdict.ok:
        result = engine.realize(decl)

Reference:
    Hermetic Geometry Canon v1.0 (Consecrated 2026-01-10)
    ADR-010: Canon DSL Adoption (Accepted 2026-01-10)

"I am the Form; You are the Will. Together, we weave the Reality."
"""

__version__ = "0.2.0"
__canon_version__ = "1.0"

from .ast import (
    Form,
    Relation,
    Trace,
    InvariantConstraint,
    CanonTestRequest,
    Declaration,
)
from .findings import Finding, Severity, Verdict
from .engine import CanonEngine, CanonValidationError, CanonBypassError, CanonBypassWarning
from .realizers import Realizer, RealizerRegistry, RealizeContext, FormRealization, RealizeResult
from .solvers import Solver, SolverRegistry, SolveResult, SolveProvenance, SolveStatus

__all__ = [
    # AST
    "Form",
    "Relation",
    "Trace",
    "InvariantConstraint",
    "CanonTestRequest",
    "Declaration",
    # Findings
    "Finding",
    "Severity",
    "Verdict",
    # Engine
    "CanonEngine",
    "CanonValidationError",
    "CanonBypassError",
    "CanonBypassWarning",
    # Realizers
    "Realizer",
    "RealizerRegistry",
    "RealizeContext",
    "FormRealization",
    "RealizeResult",
    # Solvers
    "Solver",
    "SolverRegistry",
    "SolveResult",
    "SolveProvenance",
    "SolveStatus",
]
