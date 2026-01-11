"""
Canon DSL — Canon Engine.

This module implements the CanonEngine, the central validation and
realization coordinator for Canon-compliant geometry.

ARCHITECTURAL PRINCIPLE:
    The CanonEngine is the SOLE execution gateway.
    No realization without passing validation (unless explicitly overridden).
    This is the structural enforcement of Canon law.

Reference: Hermetic Geometry Canon v1.0
Reference: Canon DSL Implementation Spec v0.2, Section 7-8
"""

from __future__ import annotations

import hashlib
import json
import logging
import warnings
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .ast import Declaration
from .findings import Finding, Severity, Verdict
from .rules import CanonRule, get_builtin_rules

if TYPE_CHECKING:
    from .realizers import Realizer, RealizeResult

logger = logging.getLogger(__name__)


def _compute_declaration_signature(decl: Declaration) -> str:
    """
    Compute a stable signature for a declaration.
    
    Used for:
    - Verdict caching
    - Reproducibility verification
    - Case law storage
    """
    # Create a canonical JSON representation
    sig_data = {
        "title": decl.title,
        "forms": [
            {
                "id": f.id,
                "kind": f.kind,
                "params": f.params,
                "orientation": f.orientation,
                "symmetry_class": f.symmetry_class,
                "curvature_class": f.curvature_class,
                "iteration_depth": f.iteration_depth,
                "truncated": f.truncated,
            }
            for f in decl.forms
        ],
        "relations": [
            {"kind": r.kind, "a": r.a, "b": r.b, "params": r.params}
            for r in decl.relations
        ],
        "traces": [
            {
                "id": t.id,
                "kind": t.kind,
                "closure_status": t.closure_status,
                "void_type": t.void_type,
                "params": t.params,
            }
            for t in decl.traces
        ],
        "epsilon": decl.epsilon,
    }
    
    sig_json = json.dumps(sig_data, sort_keys=True, default=str)
    return hashlib.sha256(sig_json.encode()).hexdigest()[:16]


class CanonEngine:
    """
    The Canon validation and realization engine.
    
    CRITICAL: The CanonEngine is the SOLE execution gateway.
    
    The CanonEngine is the central coordinator that:
    1. Validates declarations against Canon rules
    2. Gates realization on passing validation (ENFORCED BY DEFAULT)
    3. Coordinates with realizers to produce artifacts
    4. Tracks provenance for reproducibility
    
    Architectural Guarantees:
    - realize() ALWAYS validates first unless explicitly overridden
    - Legacy bypass attempts emit warnings
    - All artifacts include provenance with declaration signature
    
    Usage:
        engine = CanonEngine()
        
        # Preferred: validate first, decide what to do
        verdict = engine.validate(declaration)
        if verdict.ok:
            result = engine.realize(declaration)
        
        # Alternative: let realize() handle validation
        try:
            result = engine.realize(declaration)  # Validates internally
        except CanonValidationError as e:
            handle_failure(e.verdict)
    
    Canon References:
        - X.1: Code is an instrument (validation gates realization)
        - IX: Canonical Tests
    """
    
    def __init__(
        self,
        rules: list[CanonRule] | None = None,
        canon_version: str = "1.0",
        strict: bool = True,
        allow_bypass: bool = False,
    ):
        """
        Initialize the Canon Engine.
        
        Args:
            rules: List of validation rules. If None, uses built-in rules.
            canon_version: Version of the Canon being enforced.
            strict: If True, ERROR findings block realization. If False, only FATAL.
            allow_bypass: If True, skip_validation is permitted. If False (default),
                         skip_validation=True raises an error unless allow_bypass
                         is explicitly set. This prevents accidental bypass paths.
        """
        self.rules = rules if rules is not None else get_builtin_rules()
        self.canon_version = canon_version
        self.strict = strict
        self.allow_bypass = allow_bypass
        self._realizer_registry: dict[str, Realizer] = {}
        self._verdict_cache: dict[str, tuple[Verdict, datetime]] = {}
    
    def validate(self, decl: Declaration) -> Verdict:
        """
        Validate a declaration against all Canon rules.
        
        Args:
            decl: The declaration to validate.
        
        Returns:
            A Verdict containing all findings and an ok/fail determination.
        """
        all_findings: list[Finding] = []
        validated_at = datetime.now(timezone.utc)
        
        for rule in self.rules:
            try:
                findings = rule.check(decl)
                all_findings.extend(findings)
            except Exception as e:
                # Rule execution failed—this is a system error, not a Canon violation
                all_findings.append(Finding(
                    severity=Severity.FATAL,
                    rule_id=f"{rule.id}-EXCEPTION",
                    message=f"Rule '{rule.title}' raised an exception: {e}",
                    articles=rule.articles,
                    context={"exception": str(e), "exception_type": type(e).__name__},
                ))
        
        # Determine if validation passes
        has_fatal = any(f.severity == Severity.FATAL for f in all_findings)
        has_error = any(f.severity == Severity.ERROR for f in all_findings)
        
        if self.strict:
            ok = not (has_fatal or has_error)
        else:
            ok = not has_fatal
        
        verdict = Verdict(
            ok=ok,
            findings=all_findings,
            declaration_title=decl.title,
            canon_version=self.canon_version,
        )
        
        # Cache the verdict for reproducibility
        sig = _compute_declaration_signature(decl)
        self._verdict_cache[sig] = (verdict, validated_at)
        
        return verdict
    
    def register_realizer(self, form_kind: str, realizer: Realizer) -> None:
        """
        Register a realizer for a specific form kind.
        
        Args:
            form_kind: The Form.kind this realizer handles (e.g., "Circle", "VaultOfHestia")
            realizer: The Realizer instance
        """
        self._realizer_registry[form_kind] = realizer
    
    def get_realizer(self, form_kind: str) -> Realizer | None:
        """Get the registered realizer for a form kind."""
        return self._realizer_registry.get(form_kind)
    
    def realize(
        self,
        decl: Declaration,
        *,
        skip_validation: bool = False,
        context: dict | None = None,
    ) -> RealizeResult:
        """
        Realize a declaration into concrete artifacts.
        
        CRITICAL: Validation is enforced by default.
        
        This method:
        1. Validates the declaration (ALWAYS, unless bypass is explicitly enabled)
        2. For each form, finds the appropriate realizer
        3. Produces artifacts with provenance including declaration signature
        
        Args:
            decl: The declaration to realize.
            skip_validation: If True AND allow_bypass was set on the engine,
                            skip validation. Otherwise raises CanonBypassError.
                            USE WITH EXTREME CAUTION.
            context: Additional context for realizers.
        
        Returns:
            A RealizeResult containing artifacts and provenance.
        
        Raises:
            CanonValidationError: If validation fails.
            CanonBypassError: If skip_validation=True but allow_bypass=False.
        """
        from .realizers import RealizeResult, RealizeContext
        
        validated_at = datetime.now(timezone.utc)
        declaration_signature = _compute_declaration_signature(decl)
        
        # ENFORCEMENT: No bypass without explicit engine configuration
        if skip_validation:
            if not self.allow_bypass:
                raise CanonBypassError(
                    "skip_validation=True is not permitted unless the engine was "
                    "initialized with allow_bypass=True. This is a safety mechanism "
                    "to prevent accidental Canon violations."
                )
            # Bypass permitted but logged
            logger.warning(
                "Canon validation bypassed for declaration '%s' (signature: %s). "
                "This realization is UNVALIDATED and may violate the Canon.",
                decl.title,
                declaration_signature,
            )
            warnings.warn(
                f"LEGACY/UNVALIDATED: Declaration '{decl.title}' was realized "
                "without Canon validation. This is a migration artifact.",
                CanonBypassWarning,
                stacklevel=2,
            )
            verdict = None
        else:
            # NORMAL PATH: Always validate
            verdict = self.validate(decl)
            validated_at = datetime.now(timezone.utc)
            
            if not verdict.ok:
                raise CanonValidationError(verdict)
        
        # Build realization context
        ctx = RealizeContext(
            declaration=decl,
            epsilon=decl.epsilon or 1e-9,
            config=context or {},
        )
        
        artifacts: dict[str, Any] = {}
        provenance: dict[str, Any] = {
            "_declaration": {
                "title": decl.title,
                "signature": declaration_signature,
                "validated_at": validated_at.isoformat() if verdict else None,
                "validation_bypassed": skip_validation,
                "canon_version": self.canon_version,
            }
        }
        errors: list[str] = []
        
        # Realize each form
        for form in decl.forms:
            realizer = self.get_realizer(form.kind)
            if realizer is None:
                errors.append(f"No realizer registered for form kind '{form.kind}'")
                continue
            
            try:
                result = realizer.realize_form(form, ctx)
                artifacts[form.id] = result.artifact
                # Merge realizer's provenance with engine's provenance
                provenance[form.id] = {
                    # Engine-level provenance
                    "form_kind": form.kind,
                    "realizer": type(realizer).__name__,
                    "declaration_signature": declaration_signature,
                    "validated_at": validated_at.isoformat() if verdict else None,
                    # Realizer-provided provenance (includes metrics, canon_refs, etc.)
                    **result.provenance,
                    # Metrics as a separate key for easy access
                    "metrics": result.metrics,
                }
            except Exception as e:
                errors.append(f"Realization of '{form.id}' failed: {e}")
        
        return RealizeResult(
            artifacts=artifacts,
            provenance=provenance,
            errors=errors,
            declaration_title=decl.title,
        )
    
    def validate_and_summarize(self, decl: Declaration) -> str:
        """
        Validate and return a human-readable summary.
        
        Convenience method for quick validation feedback.
        """
        verdict = self.validate(decl)
        return verdict.summary()
    
    def get_cached_verdict(self, decl: Declaration) -> tuple[Verdict, datetime] | None:
        """
        Retrieve a cached verdict for a declaration if available.
        
        Returns:
            Tuple of (Verdict, validated_at) if cached, else None.
        """
        sig = _compute_declaration_signature(decl)
        return self._verdict_cache.get(sig)


class CanonValidationError(Exception):
    """
    Exception raised when Canon validation fails.
    
    Contains the full Verdict for inspection.
    """
    
    def __init__(self, verdict: Verdict):
        self.verdict = verdict
        super().__init__(
            f"Canon validation failed: {verdict.fatal_count()} fatal, "
            f"{verdict.error_count()} errors"
        )
    
    def __str__(self) -> str:
        return self.verdict.summary()


class CanonBypassError(Exception):
    """
    Exception raised when attempting to bypass Canon validation
    without explicit authorization.
    
    This is a safety mechanism to prevent accidental bypass paths.
    """
    pass


class CanonBypassWarning(UserWarning):
    """
    Warning emitted when Canon validation is bypassed.
    
    This marks legacy/unvalidated realizations during migration.
    """
    pass
