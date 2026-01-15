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

IMPORTANT: This module uses LAZY IMPORTS to prevent pulling UI/DB layers at import time.
           Classes are imported on-demand when accessed via __getattr__ or when
           explicitly loaded by the application.
"""

from .geometry_solver import (
    GeometrySolver,
    GeometrySolverRegistry,
    PropertyDefinition,
    get_geometry_solver_registry,
    register_geometry_solver,
)

# Lazy import map - modules are imported only when their classes are requested
_LAZY_IMPORTS = {
    "VaultOfHestiaSolver": ".vault_of_hestia_solver",
    "VaultOfHestiaRealizer": ".vault_of_hestia_realizer",
    "TorusKnotSolver": ".torus_knot_solver",
    "TorusKnotRealizer": ".torus_knot_realizer",
    "RegularPolygonSolver": ".regular_polygon_solver",
    "RegularPolygonRealizer": ".regular_polygon_realizer",
    "TetrahedronSolver": ".tetrahedron_solver",
    "TetrahedronRealizer": ".tetrahedron_realizer",
    "CubeSolver": ".cube_solver",
    "CubeRealizer": ".cube_realizer",
    "OctahedronSolver": ".octahedron_solver",
    "OctahedronRealizer": ".octahedron_realizer",
    "DodecahedronSolver": ".dodecahedron_solver",
    "DodecahedronRealizer": ".dodecahedron_realizer",
    "IcosahedronSolver": ".icosahedron_solver",
    "IcosahedronRealizer": ".icosahedron_realizer",
    "CircleSolver": ".circle_solver",
    "CircleRealizer": ".circle_realizer",
    "SquareSolver": ".square_solver",
    "SquareRealizer": ".square_realizer",
    "EllipseSolver": ".ellipse_solver",
    "EllipseRealizer": ".ellipse_realizer",
    "RectangleSolver": ".rectangle_solver",
    "RectangleRealizer": ".rectangle_realizer",
    "EquilateralTriangleSolver": ".triangle_solvers",
    "RightTriangleSolver": ".triangle_solvers",
    "IsoscelesTriangleSolver": ".triangle_solvers",
    "ScaleneTriangleSolver": ".triangle_solvers",
    "AcuteTriangleSolver": ".triangle_solvers",
    "ObtuseTriangleSolver": ".triangle_solvers",
    "HeronianTriangleSolver": ".triangle_solvers",
    "IsoscelesRightTriangleSolver": ".triangle_solvers",
    "ThirtySixtyNinetyTriangleSolver": ".triangle_solvers",
    "GoldenTriangleSolver": ".triangle_solvers",
    "TriangleSolver": ".triangle_solvers",
    "TriangleRealizer": ".triangle_realizer",
    "QuadrilateralRealizer": ".quadrilateral_realizer",
    "ParallelogramSolver": ".quadrilateral_solvers",
    "RhombusSolver": ".quadrilateral_solvers",
    "TrapezoidSolver": ".quadrilateral_solvers",
    "IsoscelesTrapezoidSolver": ".quadrilateral_solvers",
    "KiteSolver": ".quadrilateral_solvers",
    "DeltoidSolver": ".quadrilateral_solvers",
    "CyclicQuadrilateralSolver": ".quadrilateral_solvers",
    "TangentialQuadrilateralSolver": ".quadrilateral_solvers",
    "BicentricQuadrilateralSolver": ".quadrilateral_solvers",
    "QuadrilateralSolver": ".quadrilateral_solvers",
    "CurvedShapeRealizer": ".curved_shape_realizer",
    "AnnulusSolver": ".curved_shape_solvers",
    "CrescentSolver": ".curved_shape_solvers",
    "VesicaPiscisSolver": ".curved_shape_solvers",
    "RoseCurveSolver": ".curved_shape_solvers",
    "SeedOfLifeSolver": ".seed_of_life_solver",
}

def __getattr__(name: str):
    """Lazy import mechanism - import classes only when accessed."""
    if name in _LAZY_IMPORTS:
        from importlib import import_module
        module = import_module(_LAZY_IMPORTS[name], package=__package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Base classes (eagerly imported)
    "GeometrySolver",
    "GeometrySolverRegistry",
    "PropertyDefinition",
    "get_geometry_solver_registry",
    "register_geometry_solver",
    # Lazy-loaded classes
    "VaultOfHestiaSolver",
    "VaultOfHestiaRealizer",
    "TorusKnotSolver",
    "TorusKnotRealizer",
    "RegularPolygonSolver",
    "RegularPolygonRealizer",
    "TetrahedronSolver",
    "TetrahedronRealizer",
    "CubeSolver",
    "CubeRealizer",
    "OctahedronSolver",
    "OctahedronRealizer",
    "DodecahedronSolver",
    "DodecahedronRealizer",
    "IcosahedronSolver",
    "IcosahedronRealizer",
    "CircleSolver",
    "CircleRealizer",
    "SquareSolver",
    "SquareRealizer",
    "EllipseSolver",
    "EllipseRealizer",
    "RectangleSolver",
    "RectangleRealizer",
    "EquilateralTriangleSolver",
    "RightTriangleSolver",
    "IsoscelesTriangleSolver",
    "ScaleneTriangleSolver",
    "AcuteTriangleSolver",
    "ObtuseTriangleSolver",
    "HeronianTriangleSolver",
    "IsoscelesRightTriangleSolver",
    "ThirtySixtyNinetyTriangleSolver",
    "GoldenTriangleSolver",
    "TriangleSolver",
    "TriangleRealizer",
    "QuadrilateralRealizer",
    "ParallelogramSolver",
    "RhombusSolver",
    "TrapezoidSolver",
    "IsoscelesTrapezoidSolver",
    "KiteSolver",
    "DeltoidSolver",
    "CyclicQuadrilateralSolver",
    "TangentialQuadrilateralSolver",
    "BicentricQuadrilateralSolver",
    "QuadrilateralSolver",
    "CurvedShapeRealizer",
    "AnnulusSolver",
    "CrescentSolver",
    "VesicaPiscisSolver",
    "RoseCurveSolver",
    "SeedOfLifeSolver",
]
