"""
Geometry Pillar — Geometry Solver Base Class.

Extended solver interface for the Unified Geometry Viewer that adds
dimension awareness and Declaration creation helpers.

This extends the canon_dsl Solver ABC with geometry-specific functionality
needed by the unified viewer architecture (ADR-011).

Reference: ADR-010: Canon DSL Adoption
Reference: ADR-011: Unified Geometry Viewer
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from canon_dsl import (
    Declaration,
    Form,
    InvariantConstraint,
    Solver,
    SolveResult,
)

if TYPE_CHECKING:
    from ..ui.unified.payloads.geometry_payload import GeometryPayload

logger = logging.getLogger(__name__)


@dataclass
class PropertyDefinition:
    """
    Definition of a geometry property for UI rendering.
    
    Used by solvers to tell the UI what properties to display
    and how to format them.
    
    Attributes:
        key: Internal property key (e.g., "side_length")
        label: Display label (e.g., "Side Length")
        unit: Unit string (e.g., "units", "units²", "units³")
        editable: Whether the user can edit this property
        readonly: Whether this property is readonly (derived)
        format_spec: Python format spec for display (e.g., ".4f")
        tooltip: Help text for the property
        category: Grouping category (e.g., "Linear", "Area", "Volume")
        formula: LaTeX formula string for display in FormulaDialog
    """
    
    key: str
    label: str
    unit: str = "units"
    editable: bool = True
    readonly: bool = False
    format_spec: str = ".4f"
    tooltip: str = ""
    formula: str = ""  # LaTeX formula for FormulaDialog
    category: str = "General"
    
    @property
    def is_input(self) -> bool:
        """Return True if this is a user-editable input property."""
        return self.editable and not self.readonly


class GeometrySolver(Solver):
    """
    Extended solver base class for the Unified Geometry Viewer.
    
    This adds:
    - dimensional_class property (2 for shapes, 3 for solids)
    - form_type property (Canon form kind)
    - create_declaration() helper (standard pattern)
    - get_property_definitions() for UI rendering
    - get_derived_properties() separated from editable
    
    Concrete solvers (e.g., VaultOfHestiaSolver, CircleSolver) should
    extend this class when supporting the unified viewer.
    
    Example:
        class CircleSolver(GeometrySolver):
            @property
            def dimensional_class(self) -> int:
                return 2
            
            @property
            def form_type(self) -> str:
                return "Circle"
            
            @property
            def canonical_key(self) -> str:
                return "radius"
    """
    
    @property
    @abstractmethod
    def dimensional_class(self) -> int:
        """
        Return the dimensional class: 2 for shapes, 3 for solids.
        
        Per Canon XI: Dimensional Classes.
        """
        ...
    
    @property
    @abstractmethod
    def form_type(self) -> str:
        """
        Return the Canon form kind (e.g., 'Circle', 'VaultOfHestia').
        
        This should match the `kind` field used in Form declarations.
        """
        ...
    
    @property
    def is_2d(self) -> bool:
        """Return True if this is a 2D (shape) solver."""
        return self.dimensional_class == 2
    
    @property
    def is_3d(self) -> bool:
        """Return True if this is a 3D (solid) solver."""
        return self.dimensional_class == 3
    
    def get_derivation(self) -> str:
        """
        Return the mathematical derivation/commentary for this form.
        
        Override in subclasses to provide form-specific derivation text.
        This should include the mathematical foundations, proofs, and
        Hermetic insights that explain why the formulas work.
        
        Returns:
            A multi-line string with the derivation text, suitable for
            display in a scrollable dialog. May include ASCII math notation.
        """
        return ""
    
    def get_derivation_title(self) -> str:
        """
        Return a title for the derivation dialog.
        
        Override in subclasses to customize.
        """
        return f"{self.form_type} — Derivations & Commentary"
    
    def get_editable_properties(self) -> list[PropertyDefinition]:
        """
        Return property definitions for user-editable fields.
        
        Override in subclasses to customize which properties
        appear in the input panel and how they are formatted.
        
        Default: Returns just the canonical parameter.
        """
        return [
            PropertyDefinition(
                key=self.canonical_key,
                label=self._format_label(self.canonical_key),
                unit="units",
                editable=True,
            )
        ]
    
    def get_derived_properties(self) -> list[PropertyDefinition]:
        """
        Return property definitions for readonly derived fields.
        
        Override in subclasses to customize which derived
        properties appear in the UI.
        
        Default: Returns all supported keys except the canonical key.
        """
        result = []
        for key in self.supported_keys:
            if key != self.canonical_key:
                result.append(
                    PropertyDefinition(
                        key=key,
                        label=self._format_label(key),
                        unit=self._guess_unit(key),
                        editable=True,  # Editable but will trigger solve
                        readonly=False,
                    )
                )
        return result
    
    def get_all_property_definitions(self) -> list[PropertyDefinition]:
        """Return all property definitions (editable + derived)."""
        return self.get_editable_properties() + self.get_derived_properties()
    
    @abstractmethod
    def create_declaration(
        self,
        canonical_value: float,
        *,
        title: Optional[str] = None,
    ) -> Declaration:
        """
        Create a Canon-compliant Declaration from the canonical parameter.
        
        This is the bridge from solver output to Canon validation.
        Subclasses must implement this to construct proper Forms,
        Constraints, and metadata.
        
        Args:
            canonical_value: The canonical parameter value
            title: Optional custom title
        
        Returns:
            A Declaration ready for Canon validation
        """
        ...
    
    def create_declaration_from_solve(
        self,
        result: SolveResult,
        *,
        title: Optional[str] = None,
    ) -> Optional[Declaration]:
        """
        Create a Declaration directly from a SolveResult.
        
        Convenience method that extracts the canonical parameter
        from a successful SolveResult and creates a Declaration.
        
        Args:
            result: A SolveResult from solve_from()
            title: Optional custom title
        
        Returns:
            Declaration if result was successful, None otherwise
        """
        if not result.ok or result.canonical_parameter is None:
            logger.warning(f"Cannot create declaration from failed solve: {result.message}")
            return None
        
        return self.create_declaration(
            result.canonical_parameter,
            title=title,
        )
    
    def get_form_defaults(self) -> dict[str, Any]:
        """
        Return default Form field values for this solver.
        
        Override in subclasses to provide form-specific defaults
        like symmetry_class, curvature_class, etc.
        """
        defaults: dict[str, Any] = {
            "dimensional_class": self.dimensional_class,
        }
        
        if self.is_3d:
            defaults["curvature_class"] = "zero"  # Default for polyhedra
        
        return defaults
    
    # ─────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────
    
    def _format_label(self, key: str) -> str:
        """Convert a property key to a display label."""
        # side_length → Side Length
        return key.replace("_", " ").title()
    
    def _guess_unit(self, key: str) -> str:
        """Guess the unit based on property key."""
        key_lower = key.lower()
        if "volume" in key_lower:
            return "units³"
        if "area" in key_lower or "surface" in key_lower:
            return "units²"
        if "angle" in key_lower:
            return "°"
        if "ratio" in key_lower or "phi" in key_lower:
            return ""  # Dimensionless
        return "units"
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}({self.form_type}, dim={self.dimensional_class})"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"{self.__class__.__name__}("
            f"form_type={self.form_type!r}, "
            f"dimensional_class={self.dimensional_class}, "
            f"canonical_key={self.canonical_key!r})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Solver Registry Extension
# ─────────────────────────────────────────────────────────────────────────────

class GeometrySolverRegistry:
    """
    Extended registry that tracks dimensional class.
    
    This allows the unified viewer to query for solvers by dimension
    (e.g., "give me all 3D solvers").
    """
    
    def __init__(self):
        self._solvers: dict[str, GeometrySolver] = {}
    
    def register(self, solver: GeometrySolver) -> None:
        """Register a geometry solver by its form type."""
        self._solvers[solver.form_type] = solver
        logger.info(f"Registered solver: {solver.form_type} ({solver.dimensional_class}D)")
    
    def get(self, form_type: str) -> Optional[GeometrySolver]:
        """Get solver for a form type."""
        return self._solvers.get(form_type)
    
    def get_2d_solvers(self) -> list[GeometrySolver]:
        """Get all 2D (shape) solvers."""
        return [s for s in self._solvers.values() if s.is_2d]
    
    def get_3d_solvers(self) -> list[GeometrySolver]:
        """Get all 3D (solid) solvers."""
        return [s for s in self._solvers.values() if s.is_3d]
    
    def all_form_types(self) -> set[str]:
        """Return all registered form types."""
        return set(self._solvers.keys())
    
    def __len__(self) -> int:
        return len(self._solvers)
    
    def __contains__(self, form_type: str) -> bool:
        return form_type in self._solvers


# Global registry instance
_geometry_solver_registry = GeometrySolverRegistry()


def get_geometry_solver_registry() -> GeometrySolverRegistry:
    """Get the global geometry solver registry."""
    return _geometry_solver_registry


def register_geometry_solver(solver: GeometrySolver) -> None:
    """Register a solver in the global registry."""
    _geometry_solver_registry.register(solver)
