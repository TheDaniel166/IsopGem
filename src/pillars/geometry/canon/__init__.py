"""
Geometry Pillar — Canon Integration.

This package contains Canon DSL integration for the Geometry pillar:
- Solvers: Bidirectional calculators that produce Declarations
- Realizers: Forward computation that wraps existing services
- Factories: Declaration factories for common geometry

Architectural Ownership:
    These components belong to the Geometry pillar, not to canon_dsl.
    They import from canon_dsl (substrate) but are owned by geometry (pillar).

Reference: ADR-010: Canon DSL Adoption
Reference: ADR-011: Unified Geometry Viewer
"""

from .geometry_solver import (
    GeometrySolver,
    GeometrySolverRegistry,
    PropertyDefinition,
    get_geometry_solver_registry,
    register_geometry_solver,
)
from .vault_of_hestia_solver import VaultOfHestiaSolver
from .vault_of_hestia_realizer import VaultOfHestiaRealizer
from .torus_knot_solver import TorusKnotSolver
from .torus_knot_realizer import TorusKnotRealizer
from .regular_polygon_solver import RegularPolygonSolver
from .regular_polygon_realizer import RegularPolygonRealizer

__all__ = [
    # Base classes
    "GeometrySolver",
    "GeometrySolverRegistry",
    "PropertyDefinition",
    "get_geometry_solver_registry",
    "register_geometry_solver",
    # Vault of Hestia
    "VaultOfHestiaSolver",
    "VaultOfHestiaRealizer",
    # Torus Knot
    "TorusKnotSolver",
    "TorusKnotRealizer",
    # Regular Polygon
    "RegularPolygonSolver",
    "RegularPolygonRealizer",
]
