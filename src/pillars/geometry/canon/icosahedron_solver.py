"""
Geometry Pillar — Icosahedron Solver.

Bidirectional solver for regular icosahedron that converts user input
into Canon-compliant Declarations.

Reference: ADR-010: Canon DSL Adoption
Reference: ADR-011: Unified Geometry Viewer
Reference: ADR-012: Complete Canon Migration
"""

from __future__ import annotations

import math
from typing import Optional

from canon_dsl import (
    SolveResult,
    SolveProvenance,
    Declaration,
    Form,
)

from .geometry_solver import GeometrySolver, PropertyDefinition


# Golden ratio
_PHI = (1.0 + math.sqrt(5.0)) / 2.0

# Base constants for icosahedron with edge length = 1
_BASE_EDGE_LENGTH = 1.0
_BASE_FACE_AREA = (math.sqrt(3.0) / 4.0) * _BASE_EDGE_LENGTH ** 2
_BASE_SURFACE_AREA = 20.0 * _BASE_FACE_AREA
_BASE_VOLUME = (5.0 * (3.0 + math.sqrt(5.0)) / 12.0) * _BASE_EDGE_LENGTH ** 3
_BASE_INRADIUS = (_PHI * _PHI * _BASE_EDGE_LENGTH) / (2.0 * math.sqrt(3.0))
_BASE_MIDRADIUS = _BASE_EDGE_LENGTH * _PHI / 2.0
_BASE_CIRCUMRADIUS = _BASE_EDGE_LENGTH * math.sqrt(10.0 + 2.0 * math.sqrt(5.0)) / 4.0
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS

# Face geometry (equilateral triangle)
_BASE_FACE_INRADIUS = _BASE_EDGE_LENGTH * math.sqrt(3.0) / 6.0
_BASE_FACE_CIRCUMRADIUS = _BASE_EDGE_LENGTH / math.sqrt(3.0)

# Sphere metrics
_BASE_INSPHERE_SA = 4.0 * math.pi * _BASE_INRADIUS ** 2
_BASE_MIDSPHERE_SA = 4.0 * math.pi * _BASE_MIDRADIUS ** 2
_BASE_CIRCUMSPHERE_SA = 4.0 * math.pi * _BASE_CIRCUMRADIUS ** 2
_BASE_INSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_INRADIUS ** 3
_BASE_MIDSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_MIDRADIUS ** 3
_BASE_CIRCUMSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_CIRCUMRADIUS ** 3

# Moment of inertia (k coefficients for icosahedron)
_MOI_K_SOLID = 0.4  # Approximate for icosahedron
_MOI_K_SHELL = 0.6
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH


class IcosahedronSolver(GeometrySolver):
    """
    Bidirectional solver for regular icosahedron.
    
    Converts any valid property input into the canonical parameter (edge_length),
    then returns a SolveResult that can be used to build a Declaration.
    
    Canonical Parameter: edge_length (a)
    
    Relationships:
        - face_area: A_f = (√3/4)a²
        - surface_area: A = 5√3 a²
        - volume: V = (5(3+√5)/12)a³
        - inradius: r = φ²a/(2√3)
        - midradius: ρ = aφ/2
        - circumradius: R = a√(10+2√5)/4
        - All sphere and circumference properties
        - Moment of inertia properties
        
    Where φ = (1+√5)/2 is the golden ratio.
    
    Usage:
        solver = IcosahedronSolver()
        result = solver.solve_from("volume", 2.182)
        
        if result.ok:
            decl = solver.create_declaration(result.canonical_parameter)
            verdict = engine.validate(decl)
    """
    
    @property
    def dimensional_class(self) -> int:
        """Icosahedron is a 3D form."""
        return 3
    
    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "Icosahedron"
    
    @property
    def canonical_key(self) -> str:
        return "edge_length"
    
    @property
    def supported_keys(self) -> set[str]:
        return {
            "edge_length",
            "face_area",
            "surface_area",
            "volume",
            "inradius",
            "midradius",
            "circumradius",
            "incircle_circumference",
            "midsphere_circumference",
            "circumcircle_circumference",
            "face_inradius",
            "face_circumradius",
            "insphere_surface_area",
            "insphere_volume",
            "midsphere_surface_area",
            "midsphere_volume",
            "circumsphere_surface_area",
            "circumsphere_volume",
            "moment_inertia_solid",
            "moment_inertia_shell",
        }
    
    def get_editable_properties(self) -> list[PropertyDefinition]:
        """Return editable property definitions for UI."""
        return [
            PropertyDefinition(
                key="edge_length",
                label="Edge Length (a)",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Length of each edge (canonical parameter)",
                format_spec=".6f",
                formula=r"a = \text{edge length}",
            ),
            PropertyDefinition(
                key="face_area",
                label="Face Area",
                unit="sq units",
                editable=True,
                category="Core",
                tooltip="Area of one triangular face",
                format_spec=".6f",
                formula=r"A_f = \frac{\sqrt{3}}{4}a^2",
            ),
            PropertyDefinition(
                key="surface_area",
                label="Surface Area",
                unit="sq units",
                editable=True,
                category="Core",
                tooltip="Total surface area of 20 faces",
                format_spec=".6f",
                formula=r"A = 5\sqrt{3}a^2",
            ),
            PropertyDefinition(
                key="volume",
                label="Volume",
                unit="cubic units",
                editable=True,
                category="Core",
                tooltip="Total enclosed volume",
                format_spec=".6f",
                formula=r"V = \frac{5(3+\sqrt{5})}{12}a^3",
            ),
        ]
    
    def get_derived_properties(self) -> list[PropertyDefinition]:
        """Return derived property definitions for UI."""
        return [
            PropertyDefinition(
                key="inradius",
                label="Inradius (r)",
                unit="units",
                editable=False,
                category="Radii",
                tooltip="Radius of inscribed sphere",
                format_spec=".6f",
                formula=r"r = \frac{\varphi^2 a}{2\sqrt{3}}",
            ),
            PropertyDefinition(
                key="midradius",
                label="Midradius (ρ)",
                unit="units",
                editable=False,
                category="Radii",
                tooltip="Radius to edge midpoints",
                format_spec=".6f",
                formula=r"\rho = \frac{a\varphi}{2}",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius (R)",
                unit="units",
                editable=False,
                category="Radii",
                tooltip="Radius of circumscribed sphere",
                format_spec=".6f",
                formula=r"R = \frac{a\sqrt{10+2\sqrt{5}}}{4}",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                category="Circumferences",
                tooltip="Circumference of inscribed circle",
                format_spec=".6f",
                formula=r"C_r = 2\pi r",
            ),
            PropertyDefinition(
                key="midsphere_circumference",
                label="Midsphere Circumference",
                unit="units",
                editable=False,
                category="Circumferences",
                tooltip="Circumference at midradius",
                format_spec=".6f",
                formula=r"C_\rho = 2\pi\rho = \pi a\varphi",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                category="Circumferences",
                tooltip="Circumference of circumscribed circle",
                format_spec=".6f",
                formula=r"C_R = 2\pi R",
            ),
            PropertyDefinition(
                key="face_inradius",
                label="Face Inradius",
                unit="units",
                editable=False,
                category="Face Geometry",
                tooltip="Inradius of triangular face",
                format_spec=".6f",
                formula=r"r_f = \frac{a\sqrt{3}}{6}",
            ),
            PropertyDefinition(
                key="face_circumradius",
                label="Face Circumradius",
                unit="units",
                editable=False,
                category="Face Geometry",
                tooltip="Circumradius of triangular face",
                format_spec=".6f",
                formula=r"R_f = \frac{a}{\sqrt{3}}",
            ),
            PropertyDefinition(
                key="insphere_surface_area",
                label="Insphere Surface Area",
                unit="sq units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Surface area of inscribed sphere",
                format_spec=".6f",
                formula=r"A_r = 4\pi r^2",
            ),
            PropertyDefinition(
                key="insphere_volume",
                label="Insphere Volume",
                unit="cubic units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Volume of inscribed sphere",
                format_spec=".6f",
                formula=r"V_r = \frac{4\pi r^3}{3}",
            ),
            PropertyDefinition(
                key="midsphere_surface_area",
                label="Midsphere Surface Area",
                unit="sq units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Surface area at midradius",
                format_spec=".6f",
                formula=r"A_\rho = 4\pi\rho^2",
            ),
            PropertyDefinition(
                key="midsphere_volume",
                label="Midsphere Volume",
                unit="cubic units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Volume at midradius",
                format_spec=".6f",
                formula=r"V_\rho = \frac{4\pi\rho^3}{3}",
            ),
            PropertyDefinition(
                key="circumsphere_surface_area",
                label="Circumsphere Surface Area",
                unit="sq units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Surface area of circumscribed sphere",
                format_spec=".6f",
                formula=r"A_R = 4\pi R^2",
            ),
            PropertyDefinition(
                key="circumsphere_volume",
                label="Circumsphere Volume",
                unit="cubic units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Volume of circumscribed sphere",
                format_spec=".6f",
                formula=r"V_R = \frac{4\pi R^3}{3}",
            ),
            PropertyDefinition(
                key="moment_inertia_solid",
                label="Moment of Inertia (Solid)",
                unit="mass·units²",
                editable=False,
                category="Dynamics",
                tooltip="Rotational inertia for solid icosahedron",
                format_spec=".6f",
                formula=r"I_{solid} \approx 0.4Ma^2",
            ),
            PropertyDefinition(
                key="moment_inertia_shell",
                label="Moment of Inertia (Shell)",
                unit="mass·units²",
                editable=False,
                category="Dynamics",
                tooltip="Rotational inertia for hollow shell",
                format_spec=".6f",
                formula=r"I_{shell} \approx 0.6Ma^2",
            ),
        ]
    
    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Solve for canonical parameter from any supported property.
        
        Args:
            key: Property key (e.g. "volume", "surface_area")
            value: Numeric value for that property
            
        Returns:
            SolveResult with canonical parameter or error
        """
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, f"Unsupported key: {key}")
        
        if value <= 0:
            return SolveResult.invalid(key, value, f"Value must be positive, got {value}")
        
        # Solve for edge_length based on the input property
        edge_length: float
        
        if key == "edge_length":
            edge_length = value
        elif key == "face_area":
            edge_length = math.sqrt(4.0 * value / math.sqrt(3.0))
        elif key == "surface_area":
            edge_length = math.sqrt(value / (5.0 * math.sqrt(3.0)))
        elif key == "volume":
            edge_length = (12.0 * value / (5.0 * (3.0 + math.sqrt(5.0)))) ** (1.0 / 3.0)
        elif key == "inradius":
            edge_length = 2.0 * math.sqrt(3.0) * value / (_PHI * _PHI)
        elif key == "midradius":
            edge_length = 2.0 * value / _PHI
        elif key == "circumradius":
            edge_length = 4.0 * value / math.sqrt(10.0 + 2.0 * math.sqrt(5.0))
        elif key == "incircle_circumference":
            r = value / (2.0 * math.pi)
            edge_length = 2.0 * math.sqrt(3.0) * r / (_PHI * _PHI)
        elif key == "midsphere_circumference":
            rho = value / (2.0 * math.pi)
            edge_length = 2.0 * rho / _PHI
        elif key == "circumcircle_circumference":
            R = value / (2.0 * math.pi)
            edge_length = 4.0 * R / math.sqrt(10.0 + 2.0 * math.sqrt(5.0))
        elif key == "face_inradius":
            edge_length = 6.0 * value / math.sqrt(3.0)
        elif key == "face_circumradius":
            edge_length = value * math.sqrt(3.0)
        elif key == "insphere_surface_area":
            r = math.sqrt(value / (4.0 * math.pi))
            edge_length = 2.0 * math.sqrt(3.0) * r / (_PHI * _PHI)
        elif key == "insphere_volume":
            r = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 2.0 * math.sqrt(3.0) * r / (_PHI * _PHI)
        elif key == "midsphere_surface_area":
            rho = math.sqrt(value / (4.0 * math.pi))
            edge_length = 2.0 * rho / _PHI
        elif key == "midsphere_volume":
            rho = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 2.0 * rho / _PHI
        elif key == "circumsphere_surface_area":
            R = math.sqrt(value / (4.0 * math.pi))
            edge_length = 4.0 * R / math.sqrt(10.0 + 2.0 * math.sqrt(5.0))
        elif key == "circumsphere_volume":
            R = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 4.0 * R / math.sqrt(10.0 + 2.0 * math.sqrt(5.0))
        elif key == "moment_inertia_solid":
            edge_length = math.sqrt(value / (_MOI_K_SOLID * _BASE_VOLUME))
        elif key == "moment_inertia_shell":
            edge_length = math.sqrt(value / (_MOI_K_SHELL * _BASE_SURFACE_AREA))
        else:
            return SolveResult.invalid(key, value, f"Unsupported solve key: {key}")
        
        # Build provenance
        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=f"Icosahedron: {key} → edge_length (algebraic)",
        )
        
        return SolveResult.success(
            canonical_parameter=edge_length,
            canonical_key="edge_length",
            provenance=provenance,
        )
    
    def get_all_properties(self, edge_length: float) -> dict[str, float]:
        """
        Compute all properties from canonical parameter.
        
        Args:
            edge_length: Edge length (a)
            
        Returns:
            Dictionary mapping property keys to values
        """
        a = edge_length
        
        # Scale from base values
        scale = a / _BASE_EDGE_LENGTH
        
        return {
            "edge_length": a,
            "face_area": _BASE_FACE_AREA * scale * scale,
            "surface_area": _BASE_SURFACE_AREA * scale * scale,
            "volume": _BASE_VOLUME * scale * scale * scale,
            "inradius": _BASE_INRADIUS * scale,
            "midradius": _BASE_MIDRADIUS * scale,
            "circumradius": _BASE_CIRCUMRADIUS * scale,
            "incircle_circumference": _BASE_INCIRC_CIRC * scale,
            "midsphere_circumference": _BASE_MID_CIRC * scale,
            "circumcircle_circumference": _BASE_CIRCUM_CIRC * scale,
            "face_inradius": _BASE_FACE_INRADIUS * scale,
            "face_circumradius": _BASE_FACE_CIRCUMRADIUS * scale,
            "insphere_surface_area": _BASE_INSPHERE_SA * scale * scale,
            "insphere_volume": _BASE_INSPHERE_VOL * scale * scale * scale,
            "midsphere_surface_area": _BASE_MIDSPHERE_SA * scale * scale,
            "midsphere_volume": _BASE_MIDSPHERE_VOL * scale * scale * scale,
            "circumsphere_surface_area": _BASE_CIRCUMSPHERE_SA * scale * scale,
            "circumsphere_volume": _BASE_CIRCUMSPHERE_VOL * scale * scale * scale,
            "moment_inertia_solid": _BASE_MOI_SOLID * scale * scale,
            "moment_inertia_shell": _BASE_MOI_SHELL * scale * scale,
        }
    
    def create_declaration(self, edge_length: float) -> Declaration:
        """
        Create a Canon-compliant Declaration for this icosahedron.
        
        Args:
            edge_length: Edge length (a)
            
        Returns:
            Declaration with form type and params
        """
        return Declaration(
            title=f"Icosahedron (a={edge_length:.4f})",
            forms=[
                Form(
                    id="icosahedron",
                    kind="Icosahedron",
                    params={"edge_length": edge_length},
                    dimensional_class=3,
                    symmetry_class="icosahedral",
                )
            ],
            epsilon=1e-9,
            metadata={
                "solver": "IcosahedronSolver",
                "dual": "dodecahedron",
                "golden_ratio": True,
            },
        )
    
    def get_derivation(self) -> Optional[str]:
        """Return mathematical derivations in LaTeX format."""
        return r"""
Compute all geometric metrics for a regular icosahedron from edge length.

CORE DIMENSION FORMULAS & DERIVATIONS:
========================================

The Golden Ratio: $\varphi = (1 + \sqrt{5})/2 \approx 1.618$
-----------------------------------------
The icosahedron is fundamentally governed by the golden ratio.
All sphere radii and many geometric relationships involve $\varphi$.

Key golden ratio identities:
- $\varphi^2 = \varphi + 1$
- $1/\varphi = \varphi - 1$
- $\varphi = 2\cdot\cos(36^\circ) = 2\cdot\sin(54^\circ)$

Face Area: $A_{face} = (\sqrt{3}/4)a^2$
-----------------------------
Each face is an equilateral triangle with side length $a$.
Same formula as tetrahedron faces:
$A_{face} = (\sqrt{3}/4)a^2$

Surface Area: $A = 20 \times (\sqrt{3}/4)a^2 = 5\sqrt{3} a^2$
------------------------------------------
Icosahedron has 20 identical equilateral triangle faces.
Total surface area = $20 \times (\sqrt{3}/4)a^2 = 5\sqrt{3} a^2$

Volume: $V = (5/12)(3 + \sqrt{5})a^3 = (5\varphi^2/6)a^3$
------------------------------------------
Derivation via canonical coordinates:
    
The icosahedron can be constructed with 12 vertices at:
- $(0, \pm 1, \pm \varphi)$   [4 vertices]
- $(\pm 1, \pm \varphi, 0)$   [4 vertices]
- $(\pm \varphi, 0, \pm 1)$   [4 vertices]
    
Edge length for this configuration = 2
Volume = $(5/12)(3 + \sqrt{5}) \times 2^3 = (10/3)(3 + \sqrt{5})$
    
For general edge length $a$:
Scale factor = $a/2$
$V = (10/3)(3 + \sqrt{5}) \times (a/2)^3$
$  = (10/3)(3 + \sqrt{5}) \times a^3/8$
$  = (5/12)(3 + \sqrt{5}) \times a^3$
    
Using $\varphi = (1 + \sqrt{5})/2$:
$3 + \sqrt{5} = 3 + 2\varphi - 1 = 2 + 2\varphi = 2(1 + \varphi) = 2\varphi^2$
    
Therefore:
$V = (5/12) \times 2\varphi^2 \times a^3 = (5\varphi^2/6)a^3$ ✓

AHA MOMENT #1: GOLDEN RATIO IN THE COORDINATES
===============================================
The icosahedron is the ONLY Platonic solid whose canonical vertex
coordinates explicitly contain the golden ratio $\varphi$!
    
12 vertices at:
- $(0, \pm 1, \pm \varphi)$   [4 vertices forming a golden rectangle in yz-plane]
- $(\pm 1, \pm \varphi, 0)$   [4 vertices forming a golden rectangle in xy-plane]
- $(\pm \varphi, 0, \pm 1)$   [4 vertices forming a golden rectangle in xz-plane]
    
These are THREE mutually orthogonal golden rectangles (rectangles with
aspect ratio $\varphi:1$), interlocking at right angles. The icosahedron is
literally BUILT from golden rectangles.
    
No other Platonic solid exhibits this property:
- Tetrahedron: vertices at alternating cube corners (integers)
- Cube: vertices at $(\pm 1, \pm 1, \pm 1)$ (integers)
- Octahedron: vertices at $(\pm 1, 0, 0)$, $(0, \pm 1, 0)$, $(0, 0, \pm 1)$ (integers)
- Dodecahedron: vertices include $\varphi$ and $1/\varphi$, but not as cleanly
    
The icosahedron is the purest 3D expression of the golden mean.

SPHERE RADII FORMULAS & DERIVATIONS:
=====================================

Inradius (Inscribed Sphere): $r = (\varphi^2/2\sqrt{3})a = [(3 + \sqrt{5})/(4\sqrt{3})]a$
-----------------------------------------------------------------
The inscribed sphere touches the center of each triangular face.

Derivation using volume-to-surface-area ratio:
For any polyhedron: $r = 3V/A$

$r = 3 \times [(5\varphi^2/6)a^3] / [5\sqrt{3} a^2]$
$  = 3 \times (5\varphi^2/6) \times a^3 / (5\sqrt{3} a^2)$
$  = (3 \times 5\varphi^2/6) \times a / (5\sqrt{3})$
$  = (5\varphi^2/2) \times a / (5\sqrt{3})$
$  = \varphi^2 a / (2\sqrt{3})$
$  = [(3 + \sqrt{5})/(4\sqrt{3})]a$ ✓

Numerical value: $r \approx 0.7557613141a$

Midradius (Midsphere): $\rho = \varphi a/2 = [(1 + \sqrt{5})/4]a$
-------------------------------------------------
The midsphere touches the midpoint of each edge.

Derivation via canonical coordinates:
Using vertices at $(0, \pm 1, \pm \varphi)$, $(\pm 1, \pm \varphi, 0)$, $(\pm \varphi, 0, \pm 1)$:
- Edge from $(0, 1, \varphi)$ to $(1, \varphi, 0)$
- Midpoint: $(1/2, (1+\varphi)/2, \varphi/2)$
- Distance from origin = $\sqrt{(1/2)^2 + ((1+\varphi)/2)^2 + (\varphi/2)^2}$
    
For this configuration, edge = 2, midradius = $\varphi$
For general edge $a$: $\rho = \varphi \times (a/2) = \varphi a/2$ ✓
    
Using $\varphi = (1 + \sqrt{5})/2$:
$\rho = [(1 + \sqrt{5})/4]a$
    
Numerical value: $\rho \approx 0.8090169944a$

Circumradius (Circumscribed Sphere): $R = (\varphi/\sqrt{3})a\cdot\sqrt{\varphi + 2/\varphi} \approx 0.9510565163a$
-------------------------------------------------------------------------------
The circumscribed sphere passes through all 12 vertices.

Derivation via canonical coordinates:
Vertex at $(0, 1, \varphi)$ has distance from origin:
$R_0 = \sqrt{0^2 + 1^2 + \varphi^2} = \sqrt{1 + \varphi^2}$
    
Using $\varphi^2 = \varphi + 1$:
$R_0 = \sqrt{1 + \varphi + 1} = \sqrt{\varphi + 2}$
    
For canonical edge = 2, $R = \sqrt{\varphi + 2}$
For general edge $a$: $R = \sqrt{\varphi + 2} \times (a/2)$ ✓
    
Alternative form using $\varphi$ properties:
$R = (a/2)\sqrt{\varphi + 2} = (a/2)\sqrt{\varphi + 2(\varphi-1)} = (a/2)\sqrt{3\varphi}$
$R = (a/2)\sqrt{3}\cdot\sqrt{\varphi} = (a\sqrt{3}/2)\cdot\sqrt{\varphi}$
    
Since $\varphi = (1 + \sqrt{5})/2$:
$R = (a/2)\sqrt{(1 + \sqrt{5})/2 + 2}$
$  = (a/2)\sqrt{(5 + \sqrt{5})/2}$
$  \approx 0.9510565163a$ ✓

AHA MOMENT #2: MOST FACES, MOST FLUID
=======================================
The icosahedron has 20 triangular faces—MORE faces than any other
Platonic solid!
    
Face count ranking:
1. Icosahedron: 20 faces (most faceted)
2. Dodecahedron: 12 faces
3. Octahedron: 8 faces
4. Cube: 6 faces
5. Tetrahedron: 4 faces (least faceted)
    
More faces = smoother surface = more sphere-like = more FLUID.
    
With 20 tiny triangular facets, the icosahedron achieves a finely
subdivided surface that flows smoothly around its volume. This is
why it represents WATER—the element of adaptability, flow, and
infinite subdivision.
    
Water has no fixed shape; it conforms to its container. The icosahedron's
20 faces allow it to approximate ANY curved surface more closely than
the other Platonic solids (except the even-more-faceted dodecahedron).
    
The icosahedron is the Platonic solid of MULTIPLICITY and VARIATION.

AHA MOMENT #3: PENTAGONAL SYMMETRY AND LIFE
=============================================
The icosahedron has 5-fold rotational symmetry—the symmetry of LIFE!
    
Each of the 12 vertices is surrounded by exactly 5 triangular faces,
forming a pentagonal "cap" at every vertex. This 5-fold symmetry is
rare in crystallography (forbidden in classical crystal lattices) but
UBIQUITOUS in biology:
- Starfish: 5 arms
- Flowers: often 5 petals (roses, buttercups, apple blossoms)
- Human hand: 5 fingers
- Sand dollars: 5-fold symmetry
- Many viruses: icosahedral protein shells (T-number symmetry)
    
The golden ratio $\varphi$ governs spiral growth in nature (sunflower seeds,
nautilus shells, galaxy arms). The icosahedron, built from $\varphi$-based
coordinates and pentagonal symmetry, is the GEOMETRIC ARCHETYPE of
biological form.
    
Life is fluid (Water), adaptive (20 faces), and golden-ratio-based
($\varphi$ in DNA spiral pitch, leaf arrangements, etc.). The icosahedron
embodies all three principles.

HERMETIC NOTE - THE WATER ELEMENT:
===================================
The icosahedron represents WATER in Platonic solid cosmology:

Symbolism:
- 20 triangular faces = fluidity, many facets of flow
- Most faces of all Platonic solids
- Closest to spherical (highest sphericity after dodecahedron)
- 5-fold rotational symmetry (pentagonal patterns)
- Dual to dodecahedron (ether/quintessence)

Golden Ratio Correspondences:
- Every key dimension involves $\varphi$
- $\varphi$ appears in pentagon geometry (5-fold symmetry)
- $\varphi^2 = \varphi + 1$ reflects self-similarity and recursive growth
- Water's ability to take any shape → flexibility of $\varphi$-based geometry

Spiritual Correspondences:
- Insphere ($r \approx 0.756a$): The deep waters, hidden currents
- Midsphere ($\rho = \varphi a/2$): The surface tension, mediating boundary
- Circumsphere ($R \approx 0.951a$): The sphere of all possibilities

Ratios: $r : \rho : R \approx 0.756 : 0.809 : 0.951$
       $= \varphi^2/(2\sqrt{3}) : \varphi/2 : \sqrt{(\varphi+2)}/2$

The ratios are all $\varphi$-dependent, reflecting Water's connection
to the golden mean of balance and harmony.

Dihedral Angle:
- Exactly $\arccos(\sqrt{5}/3) \approx 138.19^\circ$
- Very obtuse, allowing smooth, flowing curvature
- Nearly spherical appearance

Packing Density:
- Cannot fill space perfectly
- Represents Water's need for containment
- Flows to fill voids, but cannot create rigid lattice

Connection to Pentagon:
- Each vertex has 5 edges (pentagonal symmetry)
- Pentagon has $\varphi$ in diagonal-to-side ratio
- 5-fold rotational axes through opposite vertices
"""
