# ADR-012: Complete Canon Migration for All Geometry Shapes

<!-- Last Verified: 2026-01-11 -->

**Status: Proposed**

**Depends On:**
- ADR-010: Canon DSL Adoption
- ADR-011: Unified Geometry Viewer

**Supersedes:** Individual shape Calculator classes (to be removed)

**Critical Requirement:**
🚨 **Mathematical derivation comments MUST be preserved during migration** 🚨
- 34 files contain 100-300 lines of derivation comments each
- These are the mathematical foundation of the geometry pillar
- See "Preserving Mathematical Derivations" section below for details

---

## Table of Contents

1. [Context](#context)
2. [Decision](#decision)
3. [Migration Phases](#migration-phases)
   - [Phase 1: Foundation & Simple Shapes](#phase-1-foundation--simple-shapes-week-1)
   - [Phase 2: Regular Polygons & Triangles](#phase-2-regular-polygons--triangles-week-2)
   - [Phase 3: Quadrilaterals & Complex 2D](#phase-3-quadrilaterals--complex-2d-week-3)
   - [Phase 4: Pyramids & Prisms](#phase-4-pyramids--prisms-week-4)
   - [Phase 5: Antiprisms, Archimedean & Frustums](#phase-5-antiprisms-archimedean--frustums-week-5)
   - [Phase 6: Curves, Surfaces & Special Solids](#phase-6-curves-surfaces--special-solids-week-6)
4. [Implementation Checklist](#implementation-checklist)
   - [Pre-Migration Setup](#pre-migration-setup)
   - [Per-Shape Migration Steps](#per-shape-migration-steps)
5. [**Preserving Mathematical Derivations**](#preserving-mathematical-derivations) ⚠️ CRITICAL
6. [File Organization](#file-organization)
7. [Rollout Strategy](#rollout-strategy)
8. [Testing Strategy](#testing-strategy)
9. [Risk Mitigation](#risk-mitigation)
10. [Success Criteria](#success-criteria)
11. [Timeline Summary](#timeline-summary)
12. [Critical Path](#critical-path)
13. [Open Questions](#open-questions)
14. [References](#references)
15. [Approval](#approval)

---

## Context

With the Unified Geometry Viewer now operational (ADR-011) and the Vault of Hestia successfully migrated to the Canon DSL architecture, we have **proven the pattern** for Canon-compliant geometry.

### Current State

**Architecture Pattern Established:**
```
User Input → Solver (bidirectional) → Realizer (wraps Service) → Service (mesh only) → UnifiedGeometryViewer
```

**Vault of Hestia Migration Complete:**
- ✅ `VaultOfHestiaSolver` — Bidirectional calculations, creates Declarations
- ✅ `VaultOfHestiaRealizer` — Wraps Service, produces GeometryPayload
- ✅ `VaultOfHestiaSolidService` — Builds 3D mesh (vertices, faces, edges)
- ❌ `VaultOfHestiaSolidCalculator` — **REMOVED** (duplicate calculation logic)

**Remaining Work:**
- **99+ shapes** still use the old architecture (Shape/Calculator classes)
- Code duplication between old and new systems
- Inconsistent user experience across shapes
- No Canon validation for 99+ shapes
- No history system for legacy shapes

### The Problem

Every existing geometry shape follows this **legacy pattern**:

```python
# OLD ARCHITECTURE (to be removed)
class CircleShape(GeometricShape):
    """Contains calculation logic AND drawing instructions."""

    def calculate(self, **kwargs):
        # Bidirectional solving
        ...

    def get_drawing_instructions(self):
        # Returns DrawingInstructions dict
        ...
```

This violates separation of concerns:
1. **Calculation and rendering are mixed**
2. **No Canon validation**
3. **No declarative output**
4. **No history support**
5. **Duplicates logic across 99+ files**

### The Solution

Migrate all shapes to the Canon-compliant pattern:

```python
# NEW ARCHITECTURE (target state)

# 1. Solver: Calculations only, outputs Declarations
class CircleSolver(GeometrySolver):
    def solve_from(self, key: str, value: float) -> SolveResult:
        """Bidirectional solving."""
        ...

    def create_declaration(self, radius: float) -> Declaration:
        """Create Canon Declaration."""
        ...

# 2. Realizer: Wraps service, produces GeometryPayload
class CircleRealizer(GeometryRealizer):
    def realize(self, declaration: Declaration, verdict: Verdict) -> GeometryPayload:
        """Convert Declaration to geometry."""
        service = CircleShapeService()
        drawing = service.build(radius=radius)
        return GeometryPayload(
            dimensional_class=2,
            drawing_instructions=drawing,
            ...
        )

# 3. Service: Drawing/mesh generation only (renamed from Shape)
class CircleShapeService:
    """Builds drawing instructions for circle."""

    @staticmethod
    def build(radius: float) -> DrawingInstructions:
        """Pure rendering logic, no calculations."""
        ...
```

---

## Decision

We will migrate all 99+ geometry shapes to the Canon DSL architecture over **6 phases**, following the proven Vault of Hestia pattern.

### Core Principles

1. **Solvers are Pure Functions** — No side effects, only calculations
2. **Services Build Geometry** — No calculations, only rendering
3. **Realizers Bridge the Gap** — Wrap services, produce payloads
4. **Declarations are Truth** — Single source of truth for history
5. **Backward Compatible** — Old and new coexist during migration
6. **Delete, Don't Deprecate** — Remove old code when replaced

---

## Migration Phases

### Phase 1: Foundation & Simple Shapes (Week 1)
**Goal:** Establish 2D and 3D patterns with simplest shapes

**Time Estimate:** 80 hours

#### 2D Shapes (4 shapes)

| Shape | Canonical Parameter | Complexity | Hours | Priority |
|-------|-------------------|------------|-------|----------|
| Circle | `radius` | Simple | 8 | 🔥 Critical (establishes 2D pattern) |
| Square | `side_length` | Simple | 6 | 🔥 Critical |
| Rectangle | `length, width` (compound) | Medium | 10 | High (compound param example) |
| Ellipse | `semi_major_axis, semi_minor_axis` | Medium | 10 | Medium |

#### 3D Solids (5 Platonic solids)

| Solid | Canonical Parameter | Complexity | Hours | Priority |
|-------|-------------------|------------|-------|----------|
| Tetrahedron | `edge_length` | Simple | 8 | 🔥 Critical (establishes 3D pattern) |
| Cube | `edge_length` | Simple | 6 | 🔥 Critical |
| Octahedron | `edge_length` | Simple | 8 | High |
| Dodecahedron | `edge_length` | Medium | 10 | High |
| Icosahedron | `edge_length` | Medium | 10 | High |

**Deliverables:**
- ✅ Generic `GeometrySolver` ABC (already exists)
- ✅ Generic `GeometryRealizer` ABC (may need enhancement)
- New: `CircleSolver`, `CircleRealizer`, `CircleShapeService`
- New: `SquareSolver`, `SquareRealizer`, `SquareShapeService`
- New: `RectangleSolver`, `RectangleRealizer`, `RectangleShapeService`
- New: `EllipseSolver`, `EllipseRealizer`, `EllipseShapeService`
- New: `TetrahedronSolver`, `TetrahedronRealizer`, `TetrahedronSolidService`
- New: `CubeSolver`, `CubeRealizer`, `CubeSolidService`
- New: `OctahedronSolver`, `OctahedronRealizer`, `OctahedronSolidService`
- New: `DodecahedronSolver`, `DodecahedronRealizer`, `DodecahedronSolidService`
- New: `IcosahedronSolver`, `IcosahedronRealizer`, `IcosahedronSolidService`
- Delete: `CircleShape`, `SquareShape`, `RectangleShape`, `EllipseShape`
- Delete: `TetrahedronSolidCalculator`, `CubeSolidCalculator`, `OctahedronSolidCalculator`, `DodecahedronSolidCalculator`, `IcosahedronSolidCalculator`

---

### Phase 2: Regular Polygons & Triangles (Week 2)
**Goal:** Implement generic n-gon solver and triangle family

**Time Estimate:** 64 hours

#### Generic Pattern (1 solver handles all regular n-gons)

| Shape Family | Canonical Parameters | Complexity | Hours | Priority |
|--------------|---------------------|------------|-------|----------|
| RegularPolygon | `n_sides, circumradius` | Medium | 12 | 🔥 Critical (generic pattern) |

**Implementation:**
```python
class RegularPolygonSolver(GeometrySolver):
    """Generic solver for any regular n-sided polygon."""

    def __init__(self, n_sides: int):
        self.n_sides = n_sides

    def solve_from(self, key: str, value: float) -> SolveResult:
        # Handles: circumradius, inradius, side_length, area, perimeter
        ...

    def create_declaration(self, circumradius: float) -> Declaration:
        return Declaration(
            form_type=f"RegularPolygon_{self.n_sides}",
            dimensional_class=2,
            canonical={"n_sides": self.n_sides, "circumradius": circumradius},
            ...
        )
```

**Replaces:** Pentagon, Hexagon, Heptagon, Octagon individual solvers

#### Triangle Family (9 shapes)

| Triangle Type | Canonical Parameters | Complexity | Hours |
|---------------|---------------------|------------|-------|
| EquilateralTriangle | `side_length` | Simple | 4 |
| RightTriangle | `leg_a, leg_b` | Simple | 5 |
| IsoscelesTriangle | `base, leg` | Simple | 5 |
| ScaleneTriangle | `side_a, side_b, side_c` | Medium | 6 |
| AcuteTriangle | `side_a, side_b, side_c` + validation | Medium | 6 |
| ObtuseTriangle | `side_a, side_b, side_c` + validation | Medium | 6 |
| HeronianTriangle | `side_a, side_b, side_c` + integer area | Medium | 7 |
| IsoscelesRightTriangle | `leg_length` | Simple | 4 |
| ThirtySixtyNinetyTriangle | `hypotenuse` | Simple | 4 |
| GoldenTriangle | `base` (φ-mediated) | Medium | 7 |

**Deliverables:**
- New: `RegularPolygonSolver` (generic)
- New: `EquilateralTriangleSolver`, `RightTriangleSolver`, etc. (9 solvers)
- New: Corresponding 9 Realizers
- New: Corresponding 9 ShapeServices
- Delete: `RegularPolygonShape` (if it exists as monolithic)
- Delete: 9 triangle `*Shape` classes
- Delete: `TriangleSolverShape` (old bidirectional solver)

---

### Phase 3: Quadrilaterals & Complex 2D (Week 3)
**Goal:** Migrate all quadrilateral types and specialized 2D shapes

**Time Estimate:** 78 hours

#### Quadrilaterals (11 shapes)

| Shape | Canonical Parameters | Complexity | Hours |
|-------|---------------------|------------|-------|
| Parallelogram | `base, side, angle` | Medium | 6 |
| Rhombus | `side_length, angle` | Medium | 6 |
| Trapezoid | `base_a, base_b, height` | Medium | 7 |
| IsoscelesTrapezoid | `base_a, base_b, leg` | Medium | 7 |
| Kite | `diagonal_a, diagonal_b` | Medium | 6 |
| Deltoid | Similar to Kite | Medium | 6 |
| CyclicQuadrilateral | `side_a, side_b, side_c, side_d` | Complex | 8 |
| TangentialQuadrilateral | `side_a, side_b, side_c, side_d` | Complex | 8 |
| BicentricQuadrilateral | Both cyclic & tangential | Complex | 10 |
| QuadrilateralSolver | Generic bidirectional | Complex | 10 |

#### Specialized 2D (4 shapes)

| Shape | Canonical Parameters | Complexity | Hours |
|-------|---------------------|------------|-------|
| Annulus | `outer_radius, inner_radius` | Simple | 4 |
| Crescent | `radius_a, radius_b, offset` | Medium | 6 |
| VesicaPiscis | `radius` (two circles) | Medium | 6 |
| RoseCurve | `amplitude, n_petals, k` | Medium | 8 |

**Deliverables:**
- New: 11 quadrilateral solvers + realizers + services
- New: 4 specialized shape solvers + realizers + services
- Delete: 15 corresponding `*Shape` classes

---

### Phase 4: Pyramids & Prisms (Week 4)
**Goal:** Migrate pyramid and prism families

**Time Estimate:** 82 hours

#### Pyramids (8 types)

| Pyramid | Canonical Parameters | Complexity | Hours |
|---------|---------------------|------------|-------|
| SquarePyramid | `base_edge, height` | Simple | 6 |
| RectangularPyramid | `base_length, base_width, height` | Medium | 7 |
| TriangularPyramid | `base_edge, height` | Simple | 6 |
| PentagonalPyramid | `base_edge, height` | Medium | 7 |
| HexagonalPyramid | `base_edge, height` | Medium | 7 |
| HeptagonalPyramid | `base_edge, height` | Medium | 7 |
| GoldenPyramid | `base_edge` (φ-mediated height) | Medium | 8 |
| StepPyramid | `base_edge, steps, step_height` | Complex | 10 |

**Generic Pyramid Pattern:**
```python
class RegularPyramidSolver(GeometrySolver):
    """Generic solver for regular n-gon base pyramids."""

    def __init__(self, n_sides: int):
        self.n_sides = n_sides
```

#### Prisms (7 types)

| Prism | Canonical Parameters | Complexity | Hours |
|-------|---------------------|------------|-------|
| RectangularPrism | `length, width, height` | Simple | 6 |
| TriangularPrism | `base_edge, height, length` | Medium | 7 |
| PentagonalPrism | `base_edge, length` | Medium | 7 |
| HexagonalPrism | `base_edge, length` | Medium | 7 |
| HeptagonalPrism | `base_edge, length` | Medium | 7 |
| OctagonalPrism | `base_edge, length` | Medium | 7 |
| ObliquePrism | `base_edge, length, angle` | Complex | 8 |

**Deliverables:**
- New: `RegularPyramidSolver` (generic, handles n-gon base)
- New: 8 pyramid-specific solvers + realizers + services
- New: `RegularPrismSolver` (generic)
- New: 7 prism-specific solvers + realizers + services
- Delete: 8 pyramid `*SolidCalculator` classes
- Delete: 7 prism `*SolidCalculator` classes

---

### Phase 5: Antiprisms, Archimedean & Frustums (Week 5)
**Goal:** Migrate antiprisms, Archimedean solids, and frustums

**Time Estimate:** 86 hours

#### Antiprisms (6 types)

| Antiprism | Canonical Parameters | Complexity | Hours |
|-----------|---------------------|------------|-------|
| TriangularAntiprism | `base_edge, height` | Medium | 7 |
| SquareAntiprism | `base_edge, height` | Medium | 7 |
| PentagonalAntiprism | `base_edge, height` | Medium | 7 |
| HexagonalAntiprism | `base_edge, height` | Medium | 7 |
| HeptagonalAntiprism | `base_edge, height` | Medium | 7 |
| OctagonalAntiprism | `base_edge, height` | Medium | 7 |

**Generic Antiprism Pattern:**
```python
class RegularAntiprismSolver(GeometrySolver):
    def __init__(self, n_sides: int):
        self.n_sides = n_sides
```

#### Archimedean Solids (13 types)

| Solid | Canonical Parameters | Complexity | Hours |
|-------|---------------------|------------|-------|
| Cuboctahedron | `edge_length` | Medium | 6 |
| TruncatedTetrahedron | `edge_length` | Medium | 6 |
| TruncatedCube | `edge_length` | Medium | 6 |
| TruncatedOctahedron | `edge_length` | Medium | 6 |
| Rhombicuboctahedron | `edge_length` | Medium | 6 |
| TruncatedCuboctahedron | `edge_length` | Complex | 7 |
| SnubCube | `edge_length` | Complex | 7 |
| Icosidodecahedron | `edge_length` | Medium | 6 |
| TruncatedDodecahedron | `edge_length` | Medium | 6 |
| TruncatedIcosahedron | `edge_length` | Medium | 6 |
| Rhombicosidodecahedron | `edge_length` | Medium | 6 |
| TruncatedIcosidodecahedron | `edge_length` | Complex | 7 |
| SnubDodecahedron | `edge_length` | Complex | 7 |

#### Frustums (3 types)

| Frustum | Canonical Parameters | Complexity | Hours |
|---------|---------------------|------------|-------|
| SquarePyramidFrustum | `base_edge, top_edge, height` | Medium | 7 |
| PentagonalPyramidFrustum | `base_edge, top_edge, height` | Medium | 7 |
| HexagonalPyramidFrustum | `base_edge, top_edge, height` | Medium | 7 |
| PrismaticFrustum | `base_edge, top_edge, height, n_sides` | Complex | 8 |

**Deliverables:**
- New: `RegularAntiprismSolver` (generic)
- New: 6 antiprism solvers + realizers + services
- New: 13 Archimedean solvers + realizers + services
- New: 4 frustum solvers + realizers + services
- Delete: 23 corresponding `*SolidCalculator` classes

---

### Phase 6: Curves, Surfaces & Special Solids (Week 6)
**Goal:** Migrate remaining complex geometries

**Time Estimate:** 70 hours

#### Revolution Surfaces (4 shapes)

| Shape | Canonical Parameters | Complexity | Hours |
|-------|---------------------|------------|-------|
| Sphere | `radius` | Simple | 6 |
| Cylinder | `radius, height` | Simple | 6 |
| Cone | `radius, height` | Simple | 6 |
| Torus | `major_radius, minor_radius` | Medium | 8 |
| TorusKnot | `major_radius, minor_radius, p, q` | Complex | 10 |

#### 4D Projection (1 shape)

| Shape | Canonical Parameters | Complexity | Hours |
|-------|---------------------|------------|-------|
| Tesseract | `edge_length` | Complex | 12 |

#### General Solids (3 types)

| Shape | Canonical Parameters | Complexity | Hours |
|-------|---------------------|------------|-------|
| GeneralPrism | `base_vertices, height` | Complex | 8 |
| GeneralAntiprism | `base_vertices, height` | Complex | 8 |
| GeneralPyramid | `base_vertices, apex` | Complex | 8 |

#### Complex Prismatic (2 types)

| Shape | Canonical Parameters | Complexity | Hours |
|-------|---------------------|------------|-------|
| SnubAntiprism | `base_edge, height, n_sides` | Complex | 8 |
| GyroelongatedSquarePrism | `base_edge, height` | Complex | 8 |

**Deliverables:**
- New: 5 revolution surface solvers + realizers + services
- New: 1 Tesseract solver + realizer + service
- New: 3 general solid solvers + realizers + services
- New: 2 complex prismatic solvers + realizers + services
- Delete: 11 corresponding `*SolidCalculator` or `*Shape` classes

---

## Implementation Checklist

### Pre-Migration Setup

- [ ] **Create Migration Tracking Document** — Spreadsheet with all 99+ shapes
- [ ] **Feature Flag System** — `use_canon_solver: bool` in geometry_definitions.py
- [ ] **Solver ABC Finalization** — Ensure `GeometrySolver` supports all patterns
- [ ] **Realizer ABC Creation** — Define `GeometryRealizer` base class
- [ ] **Service Naming Convention** — Rename `*Shape` → `*ShapeService`, `*SolidCalculator` → `*SolidService`
- [ ] **Test Infrastructure** — Generic test suite for solvers/realizers
- [ ] **Documentation Template** — Standard docstring format for Canon components
- [ ] **Derivation Comments Audit** — Catalog all mathematical derivations to preserve (34 files identified)
- [ ] **Create Derivation Verification Script** — `scripts/verify_derivations.py` for automated checking
- [ ] **Generate Derivation Baseline** — Run `verify_derivations.py --baseline > derivations_baseline.json`

### Per-Shape Migration Steps

For each shape (e.g., Circle):

#### Step 1: Create Solver
```bash
# File: src/pillars/geometry/canon/circle_solver.py
```

**Contents:**
```python
"""Circle Solver - Canon-compliant bidirectional solver."""

from canon_dsl import Declaration, Article, Finding
from .geometry_solver import GeometrySolver, SolveResult
import math

class CircleSolver(GeometrySolver):
    """
    Bidirectional solver for circles.

    IMPORTANT: Derivation comments migrated from old CircleShape class.
    See _compute_all_properties() for full mathematical derivations.
    """

    @property
    def form_type(self) -> str:
        return "Circle"

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def canonical_parameter(self) -> str:
        return "radius"

    def solve_from(self, key: str, value: float) -> SolveResult:
        """Convert any property to radius."""

        if key == "radius":
            radius = value
        elif key == "diameter":
            radius = value / 2.0
        elif key == "circumference":
            radius = value / (2 * math.pi)
        elif key == "area":
            radius = math.sqrt(value / math.pi)
        else:
            return SolveResult(
                success=False,
                error=f"Unknown property: {key}"
            )

        return SolveResult(
            success=True,
            canonical_value=radius,
            canonical_parameter="radius"
        )

    def get_all_properties(self, radius: float) -> dict[str, float]:
        """
        Compute all derived properties.

        Delegates to _compute_all_properties() which contains full derivations.
        """
        return self._compute_all_properties(radius)

    @staticmethod
    def _compute_all_properties(radius: float) -> dict[str, float]:
        """
        Compute all geometric properties from radius.

        CIRCLE DERIVATIONS:
        ===================

        Definition:
        -----------
        A circle is the set of all points in a plane equidistant from a center point.
        Distance from center to any point on circle = radius r.

        **Diameter**: d = 2r
        The longest chord passing through the center.

        **Circumference**: C = 2πr = πd

        Derivation:
        - Arc length for full circle (θ = 2π): s = rθ = r(2π) = 2πr
        - Alternatively: limit of perimeter of inscribed regular n-gons as n→∞
        - π ≈ 3.14159265359... (Ludolph's number, Archimedes' constant)

        **Area**: A = πr²

        Derivation Method 1 (Integration):
        - Polar coordinates: A = ∫∫ r dr dθ
        - A = ∫₀²π ∫₀ʳ r' dr' dθ = ∫₀²π [r'²/2]₀ʳ dθ = ∫₀²π r²/2 dθ = πr²

        Derivation Method 2 (Limit of Polygons):
        - Regular n-gon with circumradius r: A_n = (n/2)r²sin(2π/n)
        - lim(n→∞) A_n = lim(n→∞) (n/2)r²sin(2π/n)
        - Using lim(x→0) sin(x)/x = 1: = πr²

        Derivation Method 3 (Infinitesimal Rings):
        - Divide circle into concentric rings of width dr
        - Ring at radius r' has circumference 2πr', area dA = 2πr'·dr
        - A = ∫₀ʳ 2πr' dr' = 2π[r'²/2]₀ʳ = πr²

        HERMETIC NOTE - THE PERFECT FORM:
        ==================================
        The circle represents **UNITY**, **ETERNITY**, **THE DIVINE**:

        - **No beginning, no end**: Infinite rotational symmetry
        - **All points equal**: Perfect democracy of form
        - **π transcendental**: Cannot be expressed as ratio (divine irrationality)
        - **Sphere in 2D**: Projection of celestial perfection

        In Sacred Traditions:
        - **Sun/Moon**: Circle as symbol of celestial bodies
        - **Wheel of Dharma**: Eternal cycle, no attachment to form
        - **Ouroboros**: Serpent eating tail, unity of beginning/end
        - **Mandala**: Circle as container of sacred space
        - **Halo**: Divine radiance, perfection of saints

        NOTE: Full derivation comments preserved from original CircleShape._compute_properties()
        Additional circle segment formulas (arc length, chord, sagitta, sector, segment)
        are available in the original service file comments.
        """
        return {
            "radius": radius,
            "diameter": 2 * radius,
            "circumference": 2 * math.pi * radius,
            "area": math.pi * radius * radius,
        }

    def create_declaration(self, radius: float) -> Declaration:
        """Create Canon Declaration for this circle."""

        props = self.get_all_properties(radius)

        return Declaration(
            form_type="Circle",
            dimensional_class=2,
            canonical={"radius": radius},
            derived=props,
            metadata={
                "solver": "CircleSolver",
                "version": "1.0.0",
            },
            # Optional: Add Canon articles
            articles=[
                Article(
                    id="CIRCLE_BASIC",
                    title="Circle Fundamentals",
                    content="The circle is the locus of points equidistant from a center.",
                )
            ],
        )
```

**NOTE:** The old `CircleShape` class contains extensive derivation comments (100+ lines) explaining:
- Diameter, circumference, area formulas with multiple derivation methods
- Circle segment formulas (arc length, chord, sagitta, sector area, segment area)
- Hermetic/sacred geometry notes
- Historical context and mathematical insights

**Migration Requirement:** These derivation comments MUST be preserved in the Solver's `_compute_all_properties()` method.

#### Step 2: Create Realizer
```bash
# File: src/pillars/geometry/canon/circle_realizer.py
```

**Contents:**
```python
"""Circle Realizer - Converts Declarations to GeometryPayload."""

from canon_dsl import Declaration, Verdict, RealizeResult
from ..ui.unified.payloads import GeometryPayload
from ..services.circle_shape import CircleShapeService
from .geometry_realizer import GeometryRealizer

class CircleRealizer(GeometryRealizer):
    """Realizes Circle declarations."""

    def realize(self, declaration: Declaration, verdict: Verdict) -> GeometryPayload:
        """Convert Declaration to drawable geometry."""

        # Extract canonical parameter
        radius = declaration.canonical["radius"]

        # Use service to build drawing instructions
        service = CircleShapeService()
        drawing = service.build(radius=radius)

        # Create payload
        return GeometryPayload(
            dimensional_class=2,
            drawing_instructions=drawing,
            solid_payload=None,
            metadata={
                "form_type": "Circle",
                "radius": radius,
            },
            provenance={
                "solver": "CircleSolver",
                "realizer": "CircleRealizer",
                "declaration_signature": declaration.signature,
            },
        )
```

#### Step 3: Create/Rename Service
```bash
# File: src/pillars/geometry/services/circle_shape.py
```

**Refactor old `CircleShape` class:**

**Before (OLD):**
```python
class CircleShape(GeometricShape):
    """Circle with calculations AND drawing."""

    def calculate(self, radius=None, diameter=None, ...):
        # Bidirectional solving
        if radius:
            self.radius = radius
        elif diameter:
            self.radius = diameter / 2
        # ...
        self._compute_properties()

    def get_drawing_instructions(self):
        # Returns drawing dict
        ...
```

**After (NEW):**
```python
class CircleShapeService:
    """Builds drawing instructions for circles (no calculations)."""

    @staticmethod
    def build(radius: float) -> DrawingInstructions:
        """
        Generate drawing instructions for a circle.

        Args:
            radius: The radius (canonical parameter)

        Returns:
            DrawingInstructions dict for rendering
        """

        # Pure rendering logic, no calculations
        return {
            "type": "circle",
            "shapes": [
                {
                    "type": "circle",
                    "center": (0, 0),
                    "radius": radius,
                    "stroke": True,
                    "fill": False,
                }
            ],
            "labels": [
                {"text": f"r = {radius:.2f}", "position": (radius, 0)},
            ],
            "measurements": [
                {"type": "radius", "value": radius, "positions": [(0, 0), (radius, 0)]},
            ],
        }
```

#### Step 4: Update Exports
```python
# File: src/pillars/geometry/canon/__init__.py

from .circle_solver import CircleSolver
from .circle_realizer import CircleRealizer

__all__ = [
    ...
    'CircleSolver',
    'CircleRealizer',
]
```

```python
# File: src/pillars/geometry/services/__init__.py

from .circle_shape import CircleShapeService  # Renamed from CircleShape

__all__ = [
    ...
    'CircleShapeService',  # Updated name
    # Remove: 'CircleShape'
]
```

#### Step 5: Update geometry_definitions.py
```python
# File: src/pillars/geometry/ui/geometry_definitions.py

from ..canon import CircleSolver, CircleRealizer

GEOMETRY_DEFINITIONS = {
    'circle': {
        'title': 'Circle',
        'summary': 'The locus of points equidistant from a center.',

        # NEW: Canon components
        'solver': CircleSolver,
        'realizer': CircleRealizer,
        'use_canon_solver': True,

        # OLD: Legacy components (removed)
        # 'builder': CircleShape.build,  # REMOVE
        # 'calculator': CircleShape,     # REMOVE
    },
    ...
}
```

#### Step 6: Delete Old Class
```bash
# Remove old CircleShape class entirely
git rm src/pillars/geometry/services/circle_shape.py  # If fully replaced

# OR edit file to only keep Service, remove old Shape class
```

#### Step 7: Test Migration
```bash
# Run unified viewer with Circle
python -m pillars.geometry.ui.unified.unified_viewer --shape circle --radius 10

# Verify:
# - [ ] Solver computes properties correctly
# - [ ] Realizer produces valid GeometryPayload
# - [ ] Viewport renders circle
# - [ ] History records declaration
# - [ ] Canon tab shows validation
# - [ ] Export works (PNG, JSON)
```

---

## Preserving Mathematical Derivations

### Critical Requirement: Derivation Comments MUST Be Preserved

**34 geometry files** contain extensive mathematical derivation comments (identified via `CORE FORMULAS`, `DERIVATIONS`, `AHA MOMENT`, `HERMETIC NOTE` markers). These are **not optional documentation** — they are the **mathematical foundation** of the geometry pillar.

### Derivation Comment Structure

Old service files contain multi-level documentation:

```python
@staticmethod
def _compute_properties(canonical_param: float) -> dict:
    """
    Compute all geometric properties.

    [SHAPE NAME] DERIVATIONS:
    ========================

    Definition:
    -----------
    [Geometric definition]

    **Property 1**: formula

    Derivation:
    - Step-by-step mathematical proof
    - Alternative derivation methods
    - Limiting cases and special forms

    **Property 2**: formula

    Derivation Method 1 (Technique):
    - Detailed proof using technique 1

    Derivation Method 2 (Alternative):
    - Detailed proof using technique 2

    HERMETIC NOTE - [SYMBOLIC MEANING]:
    ===================================
    [Sacred geometry significance]

    - **Symbol 1**: Meaning
    - **Symbol 2**: Meaning

    In Sacred Traditions:
    - **Tradition 1**: Application
    - **Tradition 2**: Application

    AHA MOMENT #N: [KEY INSIGHT]
    =============================
    [Deep mathematical or philosophical revelation]
    """
    return {...}
```

### Examples of Derivation Comments

#### Example 1: Circle (Simple)
- **Diameter, Circumference, Area**: 3 derivation methods each
- **Circle Segments**: Arc length, chord, sagitta, sector, segment formulas
- **Hermetic Notes**: Unity, eternity, π transcendence, sacred traditions
- **Length**: ~150 lines of comments

#### Example 2: Vault of Hestia (Complex) ✅ ALREADY MIGRATED
- **Sphere Radius**: 50+ line derivation showing r = s/(2φ)
- **AHA Moments**: 3D structure preserves 2D golden relationship
- **Hermetic Notes**: Cube-Pyramid-Sphere nesting, φ-mediation
- **Cross-references**: Links to 2D Vault of Hestia derivations
- **Length**: ~300 lines of comments
- **Status**: ✅ Successfully preserved in `VaultOfHestiaSolver._compute_metrics()`
- **Reference Implementation**: [vault_of_hestia_solver.py](../../../src/pillars/geometry/canon/vault_of_hestia_solver.py:93-415) shows correct pattern

### Migration Pattern for Derivations

**OLD LOCATION** (Services):
```python
# File: src/pillars/geometry/services/circle_shape.py

class CircleShape(GeometricShape):
    @staticmethod
    def _compute_properties(radius: float) -> dict:
        """
        CIRCLE DERIVATIONS:
        ===================
        [150 lines of mathematical derivations]
        """
        return {...}
```

**NEW LOCATION** (Solvers):
```python
# File: src/pillars/geometry/canon/circle_solver.py

class CircleSolver(GeometrySolver):
    @staticmethod
    def _compute_all_properties(radius: float) -> dict[str, float]:
        """
        Compute all geometric properties from radius.

        CIRCLE DERIVATIONS:
        ===================
        [SAME 150 lines of mathematical derivations - FULLY PRESERVED]
        """
        return {...}
```

### Derivation Preservation Checklist (Per Shape)

For each shape migration:

1. [ ] **Locate derivation comments** in old `_compute_properties()` or `_compute_metrics()`
2. [ ] **Copy verbatim** to new Solver's `_compute_all_properties()`
3. [ ] **Verify formatting** (indentation, symbols, equations preserved)
4. [ ] **Check markers** (`DERIVATIONS:`, `AHA MOMENT`, `HERMETIC NOTE`)
5. [ ] **Test rendering** (ensure docstrings display correctly in IDE)
6. [ ] **Add migration note** referencing original source file

### Files with Extensive Derivations (Priority Audit)

Based on grep for derivation markers, these 34 files require special attention:

**2D Shapes (11 files):**
- `circle_shape.py` — Circle fundamentals, segment formulas
- `square_shape.py` — Square, diagonal, perimeter
- `ellipse_shape.py` — Ellipse, eccentricity, focal properties
- `polygon_shape.py` — Regular polygons, n-gon formulas
- `triangle_shape.py` — Triangle family, Heron's formula
- `quadrilateral_shape.py` — Quadrilateral types, Bretschneider's formula
- `annulus_shape.py` — Annulus, ring area
- `crescent_shape.py` — Crescent, lens area
- `vesica_piscis_shape.py` — Vesica Piscis, sacred fish
- `rose_curve_shape.py` — Rose curves, polar equations
- `vault_of_hestia_shape.py` — 2D Vault, φ relationships

**3D Solids (23 files):**
- `vault_of_hestia_solid.py` — 3D Vault, r = s/(2φ) proof (LARGEST) ✅ DONE
- `sphere_solid.py` — Sphere, 4πr²/3, surface tension
- `cylinder_solid.py` — Cylinder, lateral area
- `cone_solid.py` — Cone, frustum formulas
- `torus_solid.py` — Torus, major/minor radii
- `torus_knot_solid.py` — Torus knots, (p,q) parameters
- `tesseract_solid.py` — 4D hypercube, projection to 3D
- `square_pyramid_solid.py` — Square pyramid, slant height
- `rectangular_pyramid_solid.py` — Rectangular pyramid
- `golden_pyramid_solid.py` — Golden pyramid, φ-mediated
- `step_pyramid_solid.py` — Step pyramid, layer formulas
- `rectangular_prism_solid.py` — Box, diagonal
- `oblique_prism_solid.py` — Oblique prism, shear
- `prismatic_frustum_solid.py` — Frustum, trapezoidal volumes
- `regular_pyramid_solids.py` — Generic pyramid formulas
- `regular_prism_solids.py` — Generic prism formulas
- `regular_antiprism_solids.py` — Antiprism twist angles
- `regular_pyramid_frustum_solids.py` — Pyramid frustums
- `general_pyramid_solids.py` — Arbitrary base pyramids
- `general_prismatic_solids.py` — Arbitrary prisms
- `complex_prismatic_solids.py` — Snub antiprism, gyroelongated

### Derivation Complexity Ranking (Top 10 Priority)

For migration planning, these shapes have the most extensive derivations:

| Rank | Shape | File | Est. Lines | Complexity | Phase |
|------|-------|------|------------|------------|-------|
| 1 | Vault of Hestia 3D | `vault_of_hestia_solid.py` | ~300 | Very High | ✅ Done |
| 2 | Vault of Hestia 2D | `vault_of_hestia_shape.py` | ~250 | Very High | Phase 2/3 |
| 3 | Circle | `circle_shape.py` | ~200 | Medium | Phase 1 🔥 |
| 4 | Tesseract | `tesseract_solid.py` | ~180 | Very High | Phase 6 |
| 5 | Torus Knot | `torus_knot_solid.py` | ~160 | High | Phase 6 |
| 6 | Quadrilaterals | `quadrilateral_shape.py` | ~150 | High | Phase 3 |
| 7 | Triangles | `triangle_shape.py` | ~140 | Medium | Phase 2 |
| 8 | Golden Pyramid | `golden_pyramid_solid.py` | ~130 | High | Phase 4 |
| 9 | Ellipse | `ellipse_shape.py` | ~120 | Medium | Phase 1 |
| 10 | Regular Polygon | `polygon_shape.py` | ~110 | Medium | Phase 2 🔥 |

🔥 = Critical path shapes (establish patterns for others)

### Why Derivation Comments Are Critical

1. **Educational Value** — Users learn *why* formulas work, not just *what* they are
2. **Verification** — Derivations allow independent verification of implementations
3. **Sacred Geometry** — Hermetic notes connect math to philosophy/spirituality
4. **Mathematical Rigor** — Multiple derivation methods prove correctness
5. **Historical Context** — References to Euclid, Archimedes, golden ratio traditions
6. **Institutional Memory** — Prevent loss of hard-won mathematical insights

### Failure Mode: Lost Derivations

**DO NOT** do this:

```python
# BAD: Derivations lost during migration
class CircleSolver(GeometrySolver):
    @staticmethod
    def _compute_all_properties(radius: float) -> dict[str, float]:
        """Compute circle properties."""  # ❌ NO DERIVATIONS!
        return {
            "radius": radius,
            "diameter": 2 * radius,
            "area": math.pi * radius * radius,
        }
```

**This is a MIGRATION FAILURE** even if the code works correctly. The mathematical knowledge is lost.

### Success Criteria for Derivation Preservation

A shape migration is **only complete** when:

1. ✅ All formulas in old `_compute_properties()` are in new `_compute_all_properties()`
2. ✅ All derivation steps preserved verbatim
3. ✅ All `AHA MOMENT` insights preserved
4. ✅ All `HERMETIC NOTE` sections preserved
5. ✅ Formatting is readable (equations, symbols, indentation)
6. ✅ Comments reference original source file for traceability

### Automated Derivation Verification Script

Create a pre/post migration verification script:

```bash
# File: scripts/verify_derivations.py
```

```python
"""
Verify that mathematical derivation comments are preserved during migration.

Usage:
    # Before migration - create baseline
    python scripts/verify_derivations.py --baseline > derivations_baseline.json

    # After migration - verify preservation
    python scripts/verify_derivations.py --verify derivations_baseline.json
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List

DERIVATION_MARKERS = [
    "DERIVATIONS:",
    "CORE FORMULAS",
    "AHA MOMENT",
    "HERMETIC NOTE",
]

def extract_derivations(file_path: Path) -> Dict[str, List[str]]:
    """Extract all derivation comments from a Python file."""

    derivations = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if docstring:
                    for marker in DERIVATION_MARKERS:
                        if marker in docstring:
                            derivations[f"{node.name}"] = {
                                "markers": [m for m in DERIVATION_MARKERS if m in docstring],
                                "length": len(docstring),
                                "preview": docstring[:200] + "..." if len(docstring) > 200 else docstring,
                            }
                            break

    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)

    return derivations


def create_baseline(services_dir: Path) -> Dict:
    """Create baseline of all derivation comments in services."""

    baseline = {}

    for py_file in services_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue

        derivations = extract_derivations(py_file)
        if derivations:
            baseline[py_file.name] = derivations

    return baseline


def verify_migration(baseline: Dict, canon_dir: Path) -> bool:
    """Verify that all derivations from baseline exist in canon solvers."""

    all_ok = True

    for service_file, old_derivations in baseline.items():
        # Convert service filename to expected solver filename
        # e.g., circle_shape.py -> circle_solver.py
        solver_name = service_file.replace("_shape.py", "_solver.py").replace("_solid.py", "_solver.py")
        solver_path = canon_dir / solver_name

        if not solver_path.exists():
            print(f"⚠️  Solver not found: {solver_path}")
            all_ok = False
            continue

        new_derivations = extract_derivations(solver_path)

        # Check that each old derivation exists in new solver
        for func_name, old_deriv in old_derivations.items():
            found = False
            for new_func, new_deriv in new_derivations.items():
                # Check markers are preserved
                if set(old_deriv["markers"]).issubset(set(new_deriv["markers"])):
                    found = True
                    # Check length is similar (allow 10% variance for minor edits)
                    old_len = old_deriv["length"]
                    new_len = new_deriv["length"]
                    if abs(new_len - old_len) / old_len > 0.1:
                        print(f"⚠️  {solver_name}::{new_func}: Derivation length changed significantly ({old_len} -> {new_len})")
                    else:
                        print(f"✅ {solver_name}::{new_func}: Derivations preserved")
                    break

            if not found:
                print(f"❌ {solver_name}: Derivations MISSING (was in {service_file}::{func_name})")
                all_ok = False

    return all_ok


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify derivation comment preservation")
    parser.add_argument("--baseline", action="store_true", help="Create baseline from services")
    parser.add_argument("--verify", type=str, help="Verify against baseline JSON file")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    services_dir = project_root / "src" / "pillars" / "geometry" / "services"
    canon_dir = project_root / "src" / "pillars" / "geometry" / "canon"

    if args.baseline:
        baseline = create_baseline(services_dir)
        print(json.dumps(baseline, indent=2))

    elif args.verify:
        with open(args.verify, 'r') as f:
            baseline = json.load(f)

        ok = verify_migration(baseline, canon_dir)
        sys.exit(0 if ok else 1)

    else:
        parser.print_help()
        sys.exit(1)
```

**Usage in Migration Workflow:**

```bash
# Step 1: Before starting Phase 1, create baseline
python scripts/verify_derivations.py --baseline > wiki/01_blueprints/derivations_baseline.json

# Step 2: After each shape migration, verify
python scripts/verify_derivations.py --verify wiki/01_blueprints/derivations_baseline.json

# Step 3: At end of each phase, full verification
python scripts/verify_derivations.py --verify wiki/01_blueprints/derivations_baseline.json || exit 1
```

This script ensures no derivations are accidentally lost during migration.

---

## File Organization

### New Directory Structure

```
src/pillars/geometry/
├── canon/                          # All Solvers and Realizers
│   ├── __init__.py
│   ├── geometry_solver.py          # ABC (already exists)
│   ├── geometry_realizer.py        # ABC (NEW)
│   │
│   ├── vault_of_hestia_solver.py   # ✅ Already migrated
│   ├── vault_of_hestia_realizer.py # ✅ Already migrated
│   │
│   ├── circle_solver.py            # Phase 1
│   ├── circle_realizer.py
│   ├── square_solver.py
│   ├── square_realizer.py
│   ├── rectangle_solver.py
│   ├── rectangle_realizer.py
│   ├── ellipse_solver.py
│   ├── ellipse_realizer.py
│   │
│   ├── tetrahedron_solver.py       # Phase 1
│   ├── tetrahedron_realizer.py
│   ├── cube_solver.py
│   ├── cube_realizer.py
│   ├── octahedron_solver.py
│   ├── octahedron_realizer.py
│   ├── dodecahedron_solver.py
│   ├── dodecahedron_realizer.py
│   ├── icosahedron_solver.py
│   ├── icosahedron_realizer.py
│   │
│   ├── regular_polygon_solver.py   # Phase 2 (generic)
│   ├── regular_polygon_realizer.py
│   ├── equilateral_triangle_solver.py
│   ├── equilateral_triangle_realizer.py
│   ├── right_triangle_solver.py
│   ├── right_triangle_realizer.py
│   └── ...                         # (90+ more solver/realizer pairs)
│
├── services/                       # Renamed classes (rendering only)
│   ├── __init__.py
│   │
│   ├── circle_shape.py             # CircleShapeService (renamed from CircleShape)
│   ├── square_shape.py             # SquareShapeService
│   ├── rectangle_shape.py          # RectangleShapeService
│   │
│   ├── tetrahedron_solid.py        # TetrahedronSolidService (Calculator removed)
│   ├── cube_solid.py               # CubeSolidService (Calculator removed)
│   ├── vault_of_hestia_solid.py    # ✅ VaultOfHestiaSolidService (Calculator already removed)
│   └── ...
│
├── ui/
│   ├── unified/                    # ✅ Unified viewer (already built)
│   │   ├── unified_viewer.py
│   │   ├── adaptive_viewport.py
│   │   └── ...
│   │
│   ├── geometry_definitions.py     # Central registry (update each phase)
│   │
│   ├── calculator/                 # DEPRECATED (remove after Phase 6)
│   │   └── calculator_window.py
│   └── geometry3d/                 # DEPRECATED (remove after Phase 6)
│       └── window3d.py
│
└── tests/
    ├── canon/                      # New test directory
    │   ├── test_circle_solver.py
    │   ├── test_circle_realizer.py
    │   └── ...
    └── services/
        ├── test_circle_service.py
        └── ...
```

### Files to DELETE (After Migration Complete)

**Phase 1:**
```
src/pillars/geometry/services/circle_shape.py           (old CircleShape class)
src/pillars/geometry/services/square_shape.py           (old SquareShape class)
src/pillars/geometry/services/rectangle_shape.py        (old RectangleShape class)
src/pillars/geometry/services/ellipse_shape.py          (old EllipseShape class)
```

**Phase 2:**
```
src/pillars/geometry/services/triangle_shape.py         (all old triangle classes)
```

**Phase 3:**
```
src/pillars/geometry/services/quadrilateral_shape.py    (all old quadrilateral classes)
src/pillars/geometry/services/annulus_shape.py
src/pillars/geometry/services/crescent_shape.py
src/pillars/geometry/services/vesica_piscis_shape.py
src/pillars/geometry/services/rose_curve_shape.py
```

**Phases 4-6:**
```
(All remaining *_shape.py and *_solid.py files with Calculator classes)
```

**Post-Migration Cleanup (Phase 6):**
```
src/pillars/geometry/ui/calculator/calculator_window.py  (entire old 2D viewer)
src/pillars/geometry/ui/geometry3d/window3d.py           (entire old 3D viewer)
src/pillars/geometry/ui/geometry_hub.py                  (if only launched old viewers)
```

---

## Rollout Strategy

### Feature Flags

Each entry in `geometry_definitions.py` gets a flag:

```python
GEOMETRY_DEFINITIONS = {
    'circle': {
        'use_canon_solver': True,   # ✅ Migrated
        'solver': CircleSolver,
        'realizer': CircleRealizer,
    },
    'pentagon': {
        'use_canon_solver': False,  # ❌ Not yet migrated
        'builder': PentagonShape.build,
        'calculator': PentagonShape,
    },
}
```

### Launcher Logic

```python
# In geometry_hub.py or launcher

def launch_geometry_viewer(shape_key: str):
    """Launch appropriate viewer based on migration status."""

    definition = GEOMETRY_DEFINITIONS[shape_key]

    if definition.get('use_canon_solver', False):
        # NEW: Use unified viewer
        viewer = UnifiedGeometryViewer()
        solver = definition['solver']()
        realizer = definition['realizer']()
        viewer.set_solver_and_realizer(solver, realizer)
        viewer.show()
    else:
        # OLD: Use legacy viewer
        if definition.get('dimensional_class') == 2:
            viewer = GeometryCalculatorWindow(shape_key)
        else:
            viewer = Geometry3DWindow(shape_key)
        viewer.show()
```

### Deprecation Warnings

After each phase completes, add warnings to old code:

```python
# In calculator_window.py (old 2D viewer)

import warnings

class GeometryCalculatorWindow(QMainWindow):
    def __init__(self, shape_key: str):
        warnings.warn(
            f"GeometryCalculatorWindow is deprecated for '{shape_key}'. "
            f"Use UnifiedGeometryViewer instead. "
            f"This viewer will be removed in v2.0.0.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__()
        ...
```

### Final Removal (After Phase 6)

Once all 99+ shapes are migrated:

1. **Remove feature flags** — All shapes use Canon
2. **Delete legacy viewers** — Remove calculator_window.py and window3d.py
3. **Update launcher** — Only launch UnifiedGeometryViewer
4. **Update documentation** — Archive old viewer docs
5. **Bump version** — v2.0.0 (breaking change)

---

## Testing Strategy

### Unit Tests (Per Shape)

```python
# test_circle_solver.py

def test_circle_solver_from_radius():
    solver = CircleSolver()
    result = solver.solve_from("radius", 10.0)
    assert result.success
    assert result.canonical_value == 10.0

def test_circle_solver_from_diameter():
    solver = CircleSolver()
    result = solver.solve_from("diameter", 20.0)
    assert result.success
    assert result.canonical_value == 10.0

def test_circle_solver_from_circumference():
    solver = CircleSolver()
    result = solver.solve_from("circumference", 2 * math.pi * 10)
    assert result.success
    assert abs(result.canonical_value - 10.0) < 1e-6

def test_circle_declaration():
    solver = CircleSolver()
    decl = solver.create_declaration(10.0)
    assert decl.form_type == "Circle"
    assert decl.dimensional_class == 2
    assert decl.canonical["radius"] == 10.0
```

### Integration Tests

```python
# test_circle_integration.py

def test_circle_end_to_end(qtbot):
    """Test full workflow: Solver → Realizer → Viewer."""

    # Create components
    solver = CircleSolver()
    realizer = CircleRealizer()
    viewer = UnifiedGeometryViewer()

    # Set up viewer
    viewer.set_solver_and_realizer(solver, realizer)
    qtbot.addWidget(viewer)
    viewer.show()

    # Realize from radius
    payload = viewer.realize_from_canonical(10.0)

    # Verify payload
    assert payload.is_2d
    assert payload.drawing_instructions is not None

    # Verify history
    assert len(viewer._history) == 1
    entry = viewer._history.get_entry(0)
    assert entry.declaration.form_type == "Circle"
```

### Regression Tests

Before and after migration, verify:

```python
def test_circle_properties_unchanged():
    """Ensure new solver produces same results as old shape."""

    # Old way (if still available for comparison)
    old_shape = CircleShape()
    old_shape.calculate(radius=10.0)
    old_area = old_shape.area
    old_circumference = old_shape.circumference

    # New way
    solver = CircleSolver()
    props = solver.get_all_properties(10.0)
    new_area = props["area"]
    new_circumference = props["circumference"]

    # Must match
    assert abs(new_area - old_area) < 1e-6
    assert abs(new_circumference - old_circumference) < 1e-6
```

---

## Risk Mitigation

### Risk 1: Breaking Existing Workflows

**Mitigation:**
- Feature flags keep old code working during migration
- Deprecation warnings give users time to adapt
- Old and new viewers coexist until Phase 6 complete

### Risk 2: Calculation Errors in New Solvers

**Mitigation:**
- Regression tests compare old vs new results
- Unit tests for each bidirectional path
- Manual verification with known test cases

### Risk 3: Migration Fatigue

**Mitigation:**
- Phased approach spreads work over 6 weeks
- Generic solvers (RegularPolygon, RegularPyramid) reduce repetition
- Template files for quick solver creation

### Risk 4: Performance Regression

**Mitigation:**
- Benchmark tests for rendering speed
- Profiling of solver overhead
- History manager uses efficient data structures

### Risk 5: Incomplete Documentation

**Mitigation:**
- ADR documents architecture decisions
- Per-solver docstrings with examples
- Migration guide for contributors

---

## Success Criteria

### Phase Completion Criteria

Each phase is complete when:

1. ✅ All shapes in phase have Solver + Realizer + Service
2. ✅ Old Shape/Calculator classes deleted
3. ✅ **Derivation comments preserved** in Solver `_compute_all_properties()` methods
4. ✅ Unit tests pass (>95% coverage)
5. ✅ Integration tests pass in UnifiedGeometryViewer
6. ✅ Regression tests show <0.01% numerical difference
7. ✅ Visual Liturgy compliance verified
8. ✅ Documentation updated
9. ✅ **Derivation verification test passes** (checks for `DERIVATIONS:` markers)

### Overall Success (Post-Phase 6)

Migration is successful when:

1. ✅ All 99+ shapes work in UnifiedGeometryViewer
2. ✅ No legacy Shape/Calculator classes remain
3. ✅ Old viewers (calculator_window.py, window3d.py) deleted
4. ✅ **All 34 files' derivation comments preserved** in new Solvers
5. ✅ All tests pass (unit, integration, regression, derivation verification)
6. ✅ Performance is equal or better than before
7. ✅ User documentation updated
8. ✅ Contributor migration guide complete
9. ✅ No open migration-related bugs
10. ✅ **Mathematical knowledge audit confirms zero derivation loss**

---

## Timeline Summary

| Phase | Duration | Shapes | Hours | Cumulative |
|-------|----------|--------|-------|------------|
| Phase 1: Foundation | Week 1 | 9 | 80 | 80 |
| Phase 2: Polygons & Triangles | Week 2 | 10 | 64 | 144 |
| Phase 3: Quadrilaterals & 2D | Week 3 | 15 | 78 | 222 |
| Phase 4: Pyramids & Prisms | Week 4 | 15 | 82 | 304 |
| Phase 5: Antiprisms & Archimedean | Week 5 | 23 | 86 | 390 |
| Phase 6: Curves & Special | Week 6 | 11 | 70 | 460 |
| **TOTAL** | **6 weeks** | **83+** | **460** | - |

**Note:** Total shape count exceeds 99 due to generic solvers handling multiple variants.

---

## Critical Path

The following shapes **must** be completed first (they establish patterns):

1. **Circle** (Week 1) — Establishes 2D solver pattern
2. **Tetrahedron** (Week 1) — Establishes 3D solver pattern
3. **Rectangle** (Week 1) — Establishes compound canonical parameters
4. **RegularPolygon** (Week 2) — Establishes generic n-gon pattern
5. **RegularPyramid** (Week 4) — Establishes generic pyramid pattern
6. **RegularPrism** (Week 4) — Establishes generic prism pattern
7. **RegularAntiprism** (Week 5) — Establishes generic antiprism pattern

Once these are complete, remaining shapes follow established patterns.

---

## Open Questions

1. **Compound Canonical Parameters** — How to handle shapes requiring multiple canonical values (e.g., Rectangle needs `length` AND `width`)?
   - **Proposed:** `canonical: dict` supports multiple keys

2. **Generic Solver Registration** — Should `RegularPolygonSolver(n=5)` auto-register as "Pentagon"?
   - **Proposed:** Yes, geometry_definitions.py maps names to solver instances

3. **Backwards Compatibility Export** — Should old JSON/session files be importable?
   - **Proposed:** No, clean break. Provide migration script if needed.

4. **Service Reuse** — Can multiple solvers share one service?
   - **Proposed:** Yes (e.g., `EquilateralTriangleSolver` and `IsoscelesTriangleSolver` both use `TriangleShapeService`)

5. **Derivation Comment Location** — Should derivations stay in Solvers, or move to separate documentation?
   - **Proposed:** Keep in Solvers' `_compute_all_properties()` methods. Derivations are tightly coupled to calculation logic and belong in docstrings for IDE visibility.

6. **Derivation Comment Verification** — How to ensure derivations aren't accidentally lost during migration?
   - **Proposed:** Pre-migration audit extracts all derivation blocks. Post-migration diff ensures all preserved. Add automated test checking for `DERIVATIONS:` marker presence in new Solvers.

---

## References

- [ADR-010: Canon DSL Adoption](./ADR-010_canon_dsl_adoption.md)
- [ADR-011: Unified Geometry Viewer](./ADR-011_unified_geometry_viewer.md)
- [Hermetic Geometry Canon v1.0](../HERMETIC_GEOMETRY_CANON.md)
- [Visual Liturgy Reference](../../00_foundations/VISUAL_LITURGY_REFERENCE.md)
- [Vault of Hestia Migration Example](../../../src/pillars/geometry/canon/vault_of_hestia_solver.py)

---

## Approval

- [ ] **Magus Approval** — Architecture and phasing approved
- [ ] **Technical Lead Review** — Implementation details verified
- [ ] **Timeline Acceptance** — 6-week schedule realistic

---

## Summary: The Three Pillars of Migration

This migration has three equally critical success requirements:

### 1. Functional Architecture ⚙️
- All 99+ shapes work in UnifiedGeometryViewer
- Canon DSL integration complete
- Bidirectional solving preserved
- Performance maintained or improved

### 2. Code Quality 🏗️
- Clean separation: Solver (calculations) → Realizer → Service (rendering)
- Type safety and test coverage
- Visual Liturgy compliance
- Backward compatibility during transition

### 3. Mathematical Knowledge Preservation 📚
- **All 34 files' derivation comments preserved**
- Mathematical proofs intact
- Sacred geometry insights maintained
- Historical context retained
- Hermetic wisdom transmitted

**Failure in ANY of these three areas constitutes a failed migration.**

Code without derivations is a calculator without understanding.
A migration that loses the "why" while preserving the "what" has failed its educational mission.

---

*"From the Many, One Viewer. From the One, Many Forms."*

*"From the Formulas, Understanding. From the Understanding, Wisdom."*

*This ADR proposes the complete migration of all geometry shapes to the Canon DSL architecture, establishing a unified, declarative, and historically-aware system for geometric computation — while preserving the mathematical knowledge that makes it meaningful.*
