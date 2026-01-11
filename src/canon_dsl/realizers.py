"""
Canon DSL — Realizers.

This module defines the Realizer interface and supporting structures
for converting validated declarations into concrete artifacts.

ARCHITECTURAL PRINCIPLE:
    This module provides ONLY the abstract interface and registry.
    Concrete realizers belong in their respective pillars to maintain
    sovereignty and prevent import tangles.
    
    Example:
        - VaultOfHestiaRealizer → src/pillars/geometry/realizers/
        - OrbitalTraceRealizer → src/pillars/astronomy/realizers/

Reference: Hermetic Geometry Canon v1.0
Reference: Canon DSL Implementation Spec v0.2, Section 8
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .ast import Declaration, Form


@dataclass
class RealizeContext:
    """
    Context provided to realizers during realization.
    
    Contains the full declaration, numeric configuration,
    and access to external services.
    
    Attributes:
        declaration: The full Declaration being realized
        epsilon: Numeric tolerance for this realization
        config: Additional configuration (feature flags, service access, etc.)
    """
    
    declaration: Declaration
    epsilon: float = 1e-9
    config: dict[str, Any] = field(default_factory=dict)
    
    def get_form(self, form_id: str) -> Form | None:
        """Retrieve a form from the declaration by ID."""
        return self.declaration.get_form(form_id)


@dataclass
class FormRealization:
    """
    The result of realizing a single form.
    
    Attributes:
        artifact: The realized artifact (mesh, metrics, drawing instructions, etc.)
        metrics: Computed metrics for the form
        provenance: Traceable mapping from declaration to computation
    """
    
    artifact: Any
    metrics: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass
class RealizeResult:
    """
    The result of realizing a complete declaration.
    
    Attributes:
        artifacts: Map of form_id -> realized artifact
        provenance: Map of form_id -> provenance data
        errors: List of non-fatal errors encountered
        declaration_title: Title of the source declaration
    """
    
    artifacts: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    declaration_title: str = ""
    
    @property
    def ok(self) -> bool:
        """True if realization completed without errors."""
        return len(self.errors) == 0
    
    def get_artifact(self, form_id: str) -> Any | None:
        """Retrieve an artifact by form ID."""
        return self.artifacts.get(form_id)
    
    def get_declaration_signature(self) -> str | None:
        """Retrieve the declaration signature from provenance."""
        decl_meta = self.provenance.get("_declaration", {})
        return decl_meta.get("signature")
    
    def was_validated(self) -> bool:
        """Check if this realization was Canon-validated."""
        decl_meta = self.provenance.get("_declaration", {})
        return not decl_meta.get("validation_bypassed", True)
    
    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"Realization Result: {self.declaration_title or '(untitled)'}",
            f"Artifacts: {len(self.artifacts)}",
            f"Errors: {len(self.errors)}",
        ]
        
        # Show validation status
        if self.was_validated():
            sig = self.get_declaration_signature()
            lines.append(f"Canon Validated: ✓ (signature: {sig})")
        else:
            lines.append("Canon Validated: ✗ BYPASSED (legacy path)")
        
        if self.artifacts:
            lines.append("\nArtifacts:")
            for form_id in self.artifacts:
                if form_id.startswith("_"):
                    continue  # Skip metadata entries
                artifact = self.artifacts[form_id]
                artifact_type = type(artifact).__name__
                lines.append(f"  - {form_id}: {artifact_type}")
        
        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  - {error}")
        
        return "\n".join(lines)


class Realizer(ABC):
    """
    Abstract base class for form realizers.
    
    Realizers convert validated form declarations into concrete artifacts
    such as computed metrics, meshes, or drawing instructions.
    
    ARCHITECTURAL PRINCIPLE:
        Concrete realizers belong in their respective pillars, not in canon_dsl.
        This keeps canon_dsl a pure substrate without pillar dependencies.
    
    Each realizer:
    - Handles one or more form kinds
    - Produces artifacts with provenance
    - May access external services through the context
    - Wraps existing services (no reimplementation)
    
    Example location for VaultOfHestiaRealizer:
        src/pillars/geometry/realizers/vault_of_hestia.py
    
    Canon References:
        - X.1: Code is an instrument (realizers are subordinate to declarations)
    """
    
    @property
    @abstractmethod
    def supported_kinds(self) -> set[str]:
        """Return the set of Form.kind values this realizer supports."""
        ...
    
    @abstractmethod
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize a single form.
        
        Args:
            form: The Form to realize
            context: Realization context with config and access to full declaration
        
        Returns:
            FormRealization containing the artifact and metrics
        """
        ...


class RealizerRegistry:
    """
    Registry for form realizers.
    
    Provides a centralized place to register and look up realizers
    by form kind.
    
    Usage:
        # At app startup (e.g., in main.py or geometry pillar init)
        from pillars.geometry.realizers import VaultOfHestiaRealizer
        
        registry = RealizerRegistry()
        registry.register(VaultOfHestiaRealizer())
        
        engine = CanonEngine()
        for kind, realizer in registry.items():
            engine.register_realizer(kind, realizer)
    """
    
    def __init__(self):
        self._registry: dict[str, Realizer] = {}
    
    def register(self, realizer: Realizer) -> None:
        """Register a realizer for all its supported kinds."""
        for kind in realizer.supported_kinds:
            self._registry[kind] = realizer
    
    def get(self, kind: str) -> Realizer | None:
        """Get the realizer for a form kind."""
        return self._registry.get(kind)
    
    def supported_kinds(self) -> set[str]:
        """Return all registered form kinds."""
        return set(self._registry.keys())
    
    def items(self) -> list[tuple[str, Realizer]]:
        """Return all registered (kind, realizer) pairs."""
        return list(self._registry.items())


# NOTE: Example realizers (CircleRealizer, SquareRealizer) have been moved
# to the examples module. Concrete realizers for geometry should live in:
#     src/pillars/geometry/realizers/
# 
# This maintains pillar sovereignty and prevents canon_dsl from importing
# pillar-specific services.
