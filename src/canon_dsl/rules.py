"""
Canon DSL — Validation Rules.

This module defines the CanonRule interface and built-in validation rules
that enforce the Hermetic Geometry Canon v1.0.

Reference: Hermetic Geometry Canon v1.0
Reference: Canon DSL Implementation Spec v0.2, Section 7
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .findings import Finding, Severity
from .canon_refs import (
    Canon,
    ORIENTATION_SENSITIVE_FORMS,
    CURVED_FORMS,
    RECURSIVE_FORMS,
)

if TYPE_CHECKING:
    from .ast import Declaration


class CanonRule(ABC):
    """
    Abstract base class for Canon validation rules.
    
    Each rule:
    - Has a stable ID and human-readable title
    - References specific Canon articles
    - Checks a Declaration and returns findings
    """
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Stable rule identifier (e.g., 'CANON-INTEGRITY-IDS')."""
        ...
    
    @property
    @abstractmethod
    def title(self) -> str:
        """Human-readable rule title."""
        ...
    
    @property
    @abstractmethod
    def articles(self) -> list[str]:
        """Canon article references this rule enforces."""
        ...
    
    @abstractmethod
    def check(self, decl: Declaration) -> list[Finding]:
        """
        Validate the declaration against this rule.
        
        Returns a list of findings (may be empty if no issues).
        """
        ...


# =============================================================================
# RULE 1: DECLARATION INTEGRITY
# =============================================================================

class DeclarationIntegrityRule(CanonRule):
    """
    Validates structural integrity of the declaration.
    
    Checks:
    - Form IDs are unique
    - Relations reference existing forms
    - Traces reference existing forms (if source_form specified)
    - Constraints reference existing forms
    """
    
    @property
    def id(self) -> str:
        return "CANON-INTEGRITY"
    
    @property
    def title(self) -> str:
        return "Declaration Integrity"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.X_CODE_IS_INSTRUMENT]
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        # Check unique form IDs
        seen_ids: set[str] = set()
        for form in decl.forms:
            if form.id in seen_ids:
                findings.append(Finding(
                    severity=Severity.FATAL,
                    rule_id=f"{self.id}-DUPLICATE-ID",
                    message=f"Duplicate form ID: '{form.id}'",
                    articles=self.articles,
                    subject_ids=[form.id],
                    suggested_fix=f"Rename one of the forms with ID '{form.id}' to a unique identifier.",
                ))
            seen_ids.add(form.id)
        
        # Add trace IDs to known IDs
        for trace in decl.traces:
            if trace.id in seen_ids:
                findings.append(Finding(
                    severity=Severity.FATAL,
                    rule_id=f"{self.id}-DUPLICATE-ID",
                    message=f"Duplicate ID (trace conflicts with form): '{trace.id}'",
                    articles=self.articles,
                    subject_ids=[trace.id],
                ))
            seen_ids.add(trace.id)
        
        all_ids = decl.get_all_ids()
        
        # Check relations reference valid forms
        for rel in decl.relations:
            if rel.a not in all_ids:
                findings.append(Finding(
                    severity=Severity.FATAL,
                    rule_id=f"{self.id}-BAD-REF",
                    message=f"Relation references unknown form: '{rel.a}'",
                    articles=self.articles,
                    subject_ids=[rel.a],
                    suggested_fix=f"Ensure form '{rel.a}' is declared before using it in a relation.",
                ))
            if rel.b not in all_ids:
                findings.append(Finding(
                    severity=Severity.FATAL,
                    rule_id=f"{self.id}-BAD-REF",
                    message=f"Relation references unknown form: '{rel.b}'",
                    articles=self.articles,
                    subject_ids=[rel.b],
                    suggested_fix=f"Ensure form '{rel.b}' is declared before using it in a relation.",
                ))
        
        # Check traces reference valid source forms
        for trace in decl.traces:
            if trace.source_form and trace.source_form not in all_ids:
                findings.append(Finding(
                    severity=Severity.FATAL,
                    rule_id=f"{self.id}-BAD-REF",
                    message=f"Trace references unknown source form: '{trace.source_form}'",
                    articles=self.articles,
                    subject_ids=[trace.id, trace.source_form],
                ))
        
        # Check constraints reference valid forms
        for constraint in decl.constraints:
            for scope_id in constraint.scope:
                if scope_id not in all_ids:
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        rule_id=f"{self.id}-BAD-REF",
                        message=f"Constraint '{constraint.name}' references unknown form: '{scope_id}'",
                        articles=self.articles,
                        subject_ids=[scope_id],
                    ))
        
        return findings


# =============================================================================
# RULE 2: ORIENTATION DECLARATION RULE
# =============================================================================

class OrientationDeclarationRule(CanonRule):
    """
    Validates that orientation-sensitive forms declare their orientation.
    
    Canon V.4.5: "When a form admits chirality, its orientation must be declared."
    Canon V.4.6: 2D forms require CW/CCW; 3D forms require L/R or RH/LH.
    """
    
    @property
    def id(self) -> str:
        return "CANON-V-ORIENTATION"
    
    @property
    def title(self) -> str:
        return "Orientation Declaration"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.V_DIRECTION_OF_TRUTH, Canon.V_CHIRALITY_DIMENSIONAL_STATUS]
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        for form in decl.forms:
            if form.kind in ORIENTATION_SENSITIVE_FORMS:
                if form.orientation is None:
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        rule_id=f"{self.id}-REQUIRED",
                        message=f"Orientation-sensitive form '{form.id}' (kind: {form.kind}) "
                                f"must declare orientation.",
                        articles=self.articles,
                        subject_ids=[form.id],
                        suggested_fix="Add orientation='CW' or 'CCW' (2D) or 'L'/'R' (3D) to the form.",
                    ))
        
        # Check traces for orientation
        for trace in decl.traces:
            if trace.kind in {"ORBITAL_TRACE", "SPIRAL_TRACE", "EPICYCLOID_TRACE"}:
                # Check if orientation is in params
                if "orientation" not in trace.params:
                    findings.append(Finding(
                        severity=Severity.WARN,
                        rule_id=f"{self.id}-TRACE",
                        message=f"Trace '{trace.id}' should declare orientation in params.",
                        articles=self.articles,
                        subject_ids=[trace.id],
                        suggested_fix="Add params={'orientation': 'CW'} or similar to the trace.",
                    ))
        
        return findings


# =============================================================================
# RULE 3: MOTION-AS-PARAMETER RULE
# =============================================================================

class MotionAsParameterRule(CanonRule):
    """
    Validates that traces properly declare their temporal scope.
    
    Canon XII.6: "Any geometric claim involving motion must declare:
    1. Generating motion
    2. Duration
    3. Closure status"
    """
    
    @property
    def id(self) -> str:
        return "CANON-XII-MOTION"
    
    @property
    def title(self) -> str:
        return "Motion as Parameter"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.XII_TEMPORAL_SCOPE, Canon.XII_TIME_AS_PARAMETER, Canon.XII_CYCLIC_MOTION]
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        for trace in decl.traces:
            # Check closure status is declared
            if trace.closure_status == "indeterminate":
                findings.append(Finding(
                    severity=Severity.WARN,
                    rule_id=f"{self.id}-CLOSURE",
                    message=f"Trace '{trace.id}' has indeterminate closure status. "
                            f"Consider declaring 'closed', 'asymptotic', or 'open'.",
                    articles=[Canon.XII_TEMPORAL_SCOPE],
                    subject_ids=[trace.id],
                    suggested_fix="Set closure_status='closed' if the trace returns to initial state.",
                ))
            
            # Check for period declaration
            if "period" not in trace.params and "duration" not in trace.params:
                findings.append(Finding(
                    severity=Severity.WARN,
                    rule_id=f"{self.id}-PERIOD",
                    message=f"Trace '{trace.id}' should declare 'period' or 'duration' in params.",
                    articles=[Canon.XII_TEMPORAL_SCOPE],
                    subject_ids=[trace.id],
                    suggested_fix="Add params={'period': '8y'} or similar temporal scope.",
                ))
        
        return findings


# =============================================================================
# RULE 4: NO IMPLICIT REFLECTION RULE
# =============================================================================

class NoImplicitReflectionRule(CanonRule):
    """
    Validates that relations requiring reflection declare it explicitly.
    
    Canon V.4.3: "A transformation that requires reflection... must be explicitly declared.
    Any transformation pipeline that implicitly reflects a form violates Canonical clarity."
    """
    
    @property
    def id(self) -> str:
        return "CANON-V-REFLECTION"
    
    @property
    def title(self) -> str:
        return "No Implicit Reflection"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.V_REFLECTION_NOT_NEUTRAL]
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        # Relations that may involve reflection
        reflection_relations = {"MIRROR", "REFLECT", "FLIP"}
        
        for rel in decl.relations:
            if rel.kind.upper() in reflection_relations:
                if not rel.params.get("reflection", False):
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        rule_id=f"{self.id}-REQUIRED",
                        message=f"Relation '{rel.kind}' between '{rel.a}' and '{rel.b}' "
                                f"involves reflection but does not explicitly declare it.",
                        articles=self.articles,
                        subject_ids=[rel.a, rel.b],
                        suggested_fix="Add params={'reflection': True} to explicitly declare the reflection.",
                    ))
        
        return findings


# =============================================================================
# RULE 5: EPSILON DECLARATION RULE
# =============================================================================

class EpsilonDeclarationRule(CanonRule):
    """
    Validates that numeric constraints have declared tolerance.
    
    Canon Appendix C.3: "All numerical comparisons must use a declared tolerance ε."
    """
    
    @property
    def id(self) -> str:
        return "CANON-C-EPSILON"
    
    @property
    def title(self) -> str:
        return "Epsilon Declaration"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.C_EPSILON_LAW]
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        # Check if declaration has numeric constraints but no epsilon
        has_numeric_constraints = False
        
        for constraint in decl.constraints:
            expr = constraint.expr
            if "approx" in expr or "equals" in expr or "ratio" in expr:
                has_numeric_constraints = True
                # Check if constraint has its own tolerance
                if "tolerance" not in expr and "rel_tol" not in expr and "abs_tol" not in expr:
                    if decl.epsilon is None:
                        findings.append(Finding(
                            severity=Severity.ERROR,
                            rule_id=f"{self.id}-REQUIRED",
                            message=f"Constraint '{constraint.name}' requires numeric comparison "
                                    f"but no tolerance is declared.",
                            articles=self.articles,
                            subject_ids=constraint.scope,
                            suggested_fix="Either add 'tolerance' to the constraint expr, "
                                         "or set epsilon on the Declaration.",
                        ))
        
        # Check tests that require epsilon
        for test in decl.tests:
            if test.test in {"PROPORTIONAL_RECOVERY", "SCALING_INVARIANCE"}:
                if decl.epsilon is None and "epsilon" not in test.params:
                    findings.append(Finding(
                        severity=Severity.WARN,
                        rule_id=f"{self.id}-TEST",
                        message=f"Test '{test.test}' may require epsilon for numeric comparison.",
                        articles=self.articles,
                        subject_ids=test.scope,
                        suggested_fix="Set epsilon on the Declaration or in the test params.",
                    ))
        
        return findings


# =============================================================================
# RULE 6: TRUNCATION DECLARATION RULE
# =============================================================================

class TruncationDeclarationRule(CanonRule):
    """
    Validates that recursive forms with finite depth declare truncation.
    
    Canon XIII.6: "Truncation must be declared, and no truncated instance
    may be treated as the full form."
    """
    
    @property
    def id(self) -> str:
        return "CANON-XIII-TRUNCATION"
    
    @property
    def title(self) -> str:
        return "Truncation Declaration"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.XIII_TRUNCATION]
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        for form in decl.forms:
            if form.kind in RECURSIVE_FORMS:
                # If iteration_depth is specified, truncated should be True
                if form.iteration_depth is not None and not form.truncated:
                    findings.append(Finding(
                        severity=Severity.ERROR,
                        rule_id=f"{self.id}-REQUIRED",
                        message=f"Recursive form '{form.id}' has finite iteration_depth={form.iteration_depth} "
                                f"but truncated=False. Finite iterations must declare truncation.",
                        articles=self.articles,
                        subject_ids=[form.id],
                        suggested_fix="Set truncated=True to acknowledge this is a finite representation.",
                    ))
        
        return findings


# =============================================================================
# RULE 7: SYMMETRY DECLARATION RULE
# =============================================================================

class SymmetryDeclarationRule(CanonRule):
    """
    Validates that forms with inherent symmetry declare their symmetry class.
    
    Canon II.5: "Symmetry must be declared, not inferred.
    A form without declared symmetry is treated as asymmetric."
    """
    
    @property
    def id(self) -> str:
        return "CANON-II-SYMMETRY"
    
    @property
    def title(self) -> str:
        return "Symmetry Declaration"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.II_SYMMETRY_CLASSES]
    
    # Forms that inherently have symmetry
    SYMMETRIC_FORMS: set[str] = {
        "Circle", "Sphere", "Square", "Cube", "Triangle", 
        "Pentagon", "Hexagon", "Tetrahedron", "Octahedron",
        "Dodecahedron", "Icosahedron", "VaultOfHestia",
    }
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        for form in decl.forms:
            if form.kind in self.SYMMETRIC_FORMS:
                if form.symmetry_class is None:
                    findings.append(Finding(
                        severity=Severity.WARN,
                        rule_id=f"{self.id}-RECOMMENDED",
                        message=f"Form '{form.id}' (kind: {form.kind}) has inherent symmetry "
                                f"but symmetry_class is not declared.",
                        articles=self.articles,
                        subject_ids=[form.id],
                        suggested_fix=f"Add symmetry_class='rotational_n' or 'continuous' to the form.",
                    ))
        
        return findings


# =============================================================================
# RULE 8: CURVATURE CLASS RULE
# =============================================================================

class CurvatureClassRule(CanonRule):
    """
    Validates that curved forms declare their curvature class.
    
    Canon XIV.1: "Curvature is the measure of deviation from flatness."
    Canon XIV.3: Variable curvature forms must include curvature law.
    """
    
    @property
    def id(self) -> str:
        return "CANON-XIV-CURVATURE"
    
    @property
    def title(self) -> str:
        return "Curvature Class Declaration"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.XIV_CURVATURE_DEFINITION, Canon.XIV_CANONICAL_CURVED_FORMS]
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        for form in decl.forms:
            if form.kind in CURVED_FORMS:
                if form.curvature_class is None:
                    findings.append(Finding(
                        severity=Severity.WARN,
                        rule_id=f"{self.id}-RECOMMENDED",
                        message=f"Curved form '{form.id}' (kind: {form.kind}) should declare curvature_class.",
                        articles=self.articles,
                        subject_ids=[form.id],
                        suggested_fix="Add curvature_class='constant' (for circles/spheres) or 'variable'.",
                    ))
                elif form.curvature_class == "variable":
                    # Variable curvature should have curvature law in params
                    if "curvature_law" not in form.params:
                        findings.append(Finding(
                            severity=Severity.WARN,
                            rule_id=f"{self.id}-LAW",
                            message=f"Form '{form.id}' declares variable curvature but no curvature_law in params.",
                            articles=[Canon.XIV_CANONICAL_CURVED_FORMS],
                            subject_ids=[form.id],
                            suggested_fix="Add params={'curvature_law': ...} describing the curvature function.",
                        ))
        
        return findings


# =============================================================================
# RULE 9: VOID TYPE RULE
# =============================================================================

class VoidTypeRule(CanonRule):
    """
    Validates that traces making void claims declare void type.
    
    Canon XII.9: "A claim about void in the context of motion must declare:
    1. Whether it refers to swept, instantaneous, or time-averaged void"
    """
    
    @property
    def id(self) -> str:
        return "CANON-XII-VOID"
    
    @property
    def title(self) -> str:
        return "Void Type Declaration"
    
    @property
    def articles(self) -> list[str]:
        return [Canon.XII_CYCLIC_VOID]
    
    def check(self, decl: Declaration) -> list[Finding]:
        findings: list[Finding] = []
        
        for trace in decl.traces:
            # Check if any invariants mention "void"
            makes_void_claim = any("void" in inv.lower() for inv in trace.invariants_claimed)
            
            if makes_void_claim and trace.void_type is None:
                findings.append(Finding(
                    severity=Severity.ERROR,
                    rule_id=f"{self.id}-REQUIRED",
                    message=f"Trace '{trace.id}' claims void invariants but does not declare void_type.",
                    articles=self.articles,
                    subject_ids=[trace.id],
                    suggested_fix="Set void_type='swept', 'instantaneous', or 'time_averaged'.",
                ))
        
        return findings


# =============================================================================
# BUILT-IN RULES REGISTRY
# =============================================================================

def get_builtin_rules() -> list[CanonRule]:
    """Return all built-in Canon validation rules."""
    return [
        DeclarationIntegrityRule(),
        OrientationDeclarationRule(),
        MotionAsParameterRule(),
        NoImplicitReflectionRule(),
        EpsilonDeclarationRule(),
        TruncationDeclarationRule(),
        SymmetryDeclarationRule(),
        CurvatureClassRule(),
        VoidTypeRule(),
    ]
