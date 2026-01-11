"""
Geometry Pillar — Canon Integration.

This package contains Canon DSL integration for the Geometry pillar:
- Solvers: Bidirectional calculators that produce Declarations
- Realizers: Forward computation that wraps existing services
- Factories: Declaration factories for common geometry

Architectural Ownership:
    These components belong to the Geometry pillar, not to canon_dsl.
    They import from canon_dsl (substrate) but are owned by geometry (pillar).
"""
