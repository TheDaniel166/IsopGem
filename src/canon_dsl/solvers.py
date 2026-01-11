"""
Canon DSL — Solvers.

This module defines the Solver interface for bidirectional calculation
that produces Canon-compliant Declarations.

ARCHITECTURAL PRINCIPLE:
    Solvers turn partial values into Declarations (inverse direction).
    Realizers turn Declarations into Artifacts (forward direction).
    
    Solver → Declaration → CanonEngine.validate() → Realizer
    
    The Solver is NOT part of the realization path.
    It is a parameter discovery tool that outputs lawful declarations.

Reference: Hermetic Geometry Canon v1.0
Reference: ADR-010: Canon DSL Adoption

Example usage:
    # User edits "sphere_volume" in the UI
    solver = VaultOfHestiaSolver()
    result = solver.solve_from("sphere_volume", 523.6)
    
    if result.ok:
        # Create declaration from solved parameters
        decl = create_vault_of_hestia_declaration(
            side_length=result.canonical_parameter,
        )
        
        # Validate and realize
        verdict = engine.validate(decl)
        if verdict.ok:
            artifacts = engine.realize(decl)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SolveStatus(Enum):
    """Status of a solve operation."""
    
    OK = "ok"                       # Single valid solution found
    AMBIGUOUS = "ambiguous"         # Multiple valid solutions
    INVALID_DOMAIN = "invalid"      # Input outside valid domain
    UNDERDETERMINED = "under"       # Not enough information
    OVERDETERMINED = "over"         # Conflicting constraints


@dataclass
class SolveProvenance:
    """
    Provenance of how a canonical parameter was derived.
    
    This enables:
    - UI feedback ("derived from sphere_volume")
    - Educational features ("using formula r = s / 2φ")
    - Debugging bidirectional logic
    
    Attributes:
        source_key: The property that was edited
        source_value: The value that was entered
        formula_used: Human-readable description of the formula
        intermediate_values: Any intermediate computed values
        assumptions: Any assumptions made during solving
    """
    
    source_key: str
    source_value: float
    formula_used: str = ""
    intermediate_values: dict[str, float] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)


@dataclass
class SolveResult:
    """
    The result of a solve operation.
    
    Attributes:
        status: Whether the solve succeeded
        canonical_parameter: The derived canonical parameter value (e.g., side_length)
        canonical_key: Name of the canonical parameter (e.g., "side_length")
        provenance: How the value was derived
        all_solutions: If ambiguous, all valid solutions
        message: Human-readable explanation
        warnings: Non-blocking issues discovered during solve
    """
    
    status: SolveStatus
    canonical_parameter: Optional[float] = None
    canonical_key: str = ""
    provenance: Optional[SolveProvenance] = None
    all_solutions: list[float] = field(default_factory=list)
    message: str = ""
    warnings: list[str] = field(default_factory=list)
    
    @property
    def ok(self) -> bool:
        """True if solve found a valid solution."""
        return self.status == SolveStatus.OK
    
    @classmethod
    def success(
        cls,
        canonical_parameter: float,
        canonical_key: str,
        provenance: SolveProvenance,
        warnings: list[str] | None = None,
    ) -> SolveResult:
        """Create a successful solve result."""
        return cls(
            status=SolveStatus.OK,
            canonical_parameter=canonical_parameter,
            canonical_key=canonical_key,
            provenance=provenance,
            warnings=warnings or [],
        )
    
    @classmethod
    def invalid(cls, key: str, value: float, reason: str) -> SolveResult:
        """Create an invalid domain result."""
        return cls(
            status=SolveStatus.INVALID_DOMAIN,
            message=f"Cannot solve from {key}={value}: {reason}",
            provenance=SolveProvenance(source_key=key, source_value=value),
        )
    
    @classmethod
    def ambiguous(
        cls,
        canonical_key: str,
        solutions: list[float],
        provenance: SolveProvenance,
    ) -> SolveResult:
        """Create an ambiguous result with multiple solutions."""
        return cls(
            status=SolveStatus.AMBIGUOUS,
            canonical_key=canonical_key,
            all_solutions=solutions,
            provenance=provenance,
            message=f"Multiple solutions found: {solutions}. User must select one.",
        )


class Solver(ABC):
    """
    Abstract base class for bidirectional solvers.
    
    Solvers convert partial/user-entered values into canonical parameters
    that can be used to construct Declarations.
    
    ARCHITECTURAL PRINCIPLE:
        Solvers discover parameters. They do NOT realize geometry.
        The output of a Solver is used to build a Declaration,
        which is then validated and realized through the Canon path.
    
    Example:
        class VaultOfHestiaSolver(Solver):
            def solve_from(self, key, value):
                # User entered sphere_radius
                if key == "sphere_radius":
                    s = value * 2 * phi
                    return SolveResult.success(
                        canonical_parameter=s,
                        canonical_key="side_length",
                        provenance=SolveProvenance(
                            source_key="sphere_radius",
                            source_value=value,
                            formula_used="s = r × 2φ",
                        ),
                    )
    """
    
    @property
    @abstractmethod
    def canonical_key(self) -> str:
        """
        The name of the canonical parameter this solver produces.
        
        For VaultOfHestia: "side_length"
        For Circle: "radius"
        For Cube: "edge_length"
        """
        ...
    
    @property
    @abstractmethod
    def supported_keys(self) -> set[str]:
        """Return the set of property keys that can be solved from."""
        ...
    
    @abstractmethod
    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Solve for the canonical parameter given an input property.
        
        Args:
            key: The property being set (e.g., "sphere_volume")
            value: The value entered by the user
        
        Returns:
            SolveResult containing the derived canonical parameter
            and provenance information.
        """
        ...
    
    def can_solve_from(self, key: str) -> bool:
        """Check if this solver can solve from a given key."""
        return key in self.supported_keys
    
    def get_all_properties(self, canonical_value: float) -> dict[str, float]:
        """
        Given the canonical parameter, compute all derived properties.
        
        This is the "forward" direction used to populate UI fields
        after a solve.
        
        Args:
            canonical_value: The canonical parameter value
        
        Returns:
            Dict of all property values
        """
        # Default implementation: solve from the canonical key
        # and return all properties. Subclasses should override
        # for efficiency.
        return {self.canonical_key: canonical_value}


class SolverRegistry:
    """
    Registry for bidirectional solvers.
    
    Associates form kinds with their solvers.
    """
    
    def __init__(self):
        self._registry: dict[str, Solver] = {}
    
    def register(self, form_kind: str, solver: Solver) -> None:
        """Register a solver for a form kind."""
        self._registry[form_kind] = solver
    
    def get(self, form_kind: str) -> Solver | None:
        """Get the solver for a form kind."""
        return self._registry.get(form_kind)
    
    def supported_kinds(self) -> set[str]:
        """Return all registered form kinds."""
        return set(self._registry.keys())
