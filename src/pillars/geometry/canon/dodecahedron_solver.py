"""
Geometry Pillar — Dodecahedron Solver.

Bidirectional solver for regular dodecahedron that converts user input
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

# Base constants for dodecahedron with edge length = 1
_BASE_EDGE_LENGTH = 1.0
_BASE_FACE_AREA = (math.sqrt(25.0 + 10.0 * math.sqrt(5.0)) / 4.0) * _BASE_EDGE_LENGTH ** 2
_BASE_SURFACE_AREA = 12.0 * _BASE_FACE_AREA
_BASE_VOLUME = ((15.0 + 7.0 * math.sqrt(5.0)) / 4.0) * _BASE_EDGE_LENGTH ** 3
_BASE_INRADIUS = _BASE_EDGE_LENGTH * math.sqrt(250.0 + 110.0 * math.sqrt(5.0)) / 20.0
_BASE_MIDRADIUS = _BASE_EDGE_LENGTH * _PHI * math.sqrt(3.0) / 2.0
_BASE_CIRCUMRADIUS = _BASE_EDGE_LENGTH * math.sqrt(3.0) * _PHI / 2.0
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS

# Face geometry (regular pentagon)
_BASE_FACE_INRADIUS = _BASE_EDGE_LENGTH * math.sqrt(25.0 + 10.0 * math.sqrt(5.0)) / 10.0
_BASE_FACE_CIRCUMRADIUS = _BASE_EDGE_LENGTH * _PHI / math.sqrt(3.0 - _PHI)

# Sphere metrics
_BASE_INSPHERE_SA = 4.0 * math.pi * _BASE_INRADIUS ** 2
_BASE_MIDSPHERE_SA = 4.0 * math.pi * _BASE_MIDRADIUS ** 2
_BASE_CIRCUMSPHERE_SA = 4.0 * math.pi * _BASE_CIRCUMRADIUS ** 2
_BASE_INSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_INRADIUS ** 3
_BASE_MIDSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_MIDRADIUS ** 3
_BASE_CIRCUMSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_CIRCUMRADIUS ** 3

# Moment of inertia (k coefficients for dodecahedron)
_MOI_K_SOLID = 0.29  # Approximate for dodecahedron
_MOI_K_SHELL = 0.43
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH


class DodecahedronSolver(GeometrySolver):
    """
    Bidirectional solver for regular dodecahedron.
    
    Converts any valid property input into the canonical parameter (edge_length),
    then returns a SolveResult that can be used to build a Declaration.
    
    Canonical Parameter: edge_length (a)
    
    Relationships:
        - face_area: A_f = (√(25+10√5)/4)a²
        - surface_area: A = 3√(25+10√5)a²
        - volume: V = ((15+7√5)/4)a³
        - inradius: r = a√(250+110√5)/20
        - midradius: ρ = aφ√3/2
        - circumradius: R = a√3φ/2
        - All sphere and circumference properties
        - Moment of inertia properties
        
    Where φ = (1+√5)/2 is the golden ratio.
    
    Usage:
        solver = DodecahedronSolver()
        result = solver.solve_from("volume", 7.663)
        
        if result.ok:
            decl = solver.create_declaration(result.canonical_parameter)
            verdict = engine.validate(decl)
    """
    
    @property
    def dimensional_class(self) -> int:
        """Dodecahedron is a 3D form."""
        return 3
    
    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "Dodecahedron"
    
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
                tooltip="Area of one pentagonal face",
                format_spec=".6f",
                formula=r"A_f = \frac{\sqrt{25+10\sqrt{5}}}{4}a^2",
            ),
            PropertyDefinition(
                key="surface_area",
                label="Surface Area",
                unit="sq units",
                editable=True,
                category="Core",
                tooltip="Total surface area of 12 faces",
                format_spec=".6f",
                formula=r"A = 3\sqrt{25+10\sqrt{5}}a^2",
            ),
            PropertyDefinition(
                key="volume",
                label="Volume",
                unit="cubic units",
                editable=True,
                category="Core",
                tooltip="Total enclosed volume",
                format_spec=".6f",
                formula=r"V = \frac{15+7\sqrt{5}}{4}a^3",
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
                formula=r"r = \frac{a\sqrt{250+110\sqrt{5}}}{20}",
            ),
            PropertyDefinition(
                key="midradius",
                label="Midradius (ρ)",
                unit="units",
                editable=False,
                category="Radii",
                tooltip="Radius to edge midpoints",
                format_spec=".6f",
                formula=r"\rho = \frac{a\varphi\sqrt{3}}{2}",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius (R)",
                unit="units",
                editable=False,
                category="Radii",
                tooltip="Radius of circumscribed sphere",
                format_spec=".6f",
                formula=r"R = \frac{a\sqrt{3}\varphi}{2}",
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
                formula=r"C_\rho = 2\pi\rho",
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
                tooltip="Inradius of pentagonal face",
                format_spec=".6f",
                formula=r"r_f = \frac{a\sqrt{25+10\sqrt{5}}}{10}",
            ),
            PropertyDefinition(
                key="face_circumradius",
                label="Face Circumradius",
                unit="units",
                editable=False,
                category="Face Geometry",
                tooltip="Circumradius of pentagonal face",
                format_spec=".6f",
                formula=r"R_f = \frac{a\varphi}{\sqrt{3-\varphi}}",
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
                tooltip="Rotational inertia for solid dodecahedron",
                format_spec=".6f",
                formula=r"I_{solid} \approx 0.29Ma^2",
            ),
            PropertyDefinition(
                key="moment_inertia_shell",
                label="Moment of Inertia (Shell)",
                unit="mass·units²",
                editable=False,
                category="Dynamics",
                tooltip="Rotational inertia for hollow shell",
                format_spec=".6f",
                formula=r"I_{shell} \approx 0.43Ma^2",
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
            edge_length = math.sqrt(4.0 * value / math.sqrt(25.0 + 10.0 * math.sqrt(5.0)))
        elif key == "surface_area":
            edge_length = math.sqrt(value / (3.0 * math.sqrt(25.0 + 10.0 * math.sqrt(5.0))))
        elif key == "volume":
            edge_length = (4.0 * value / (15.0 + 7.0 * math.sqrt(5.0))) ** (1.0 / 3.0)
        elif key == "inradius":
            edge_length = 20.0 * value / math.sqrt(250.0 + 110.0 * math.sqrt(5.0))
        elif key == "midradius":
            edge_length = 2.0 * value / (_PHI * math.sqrt(3.0))
        elif key == "circumradius":
            edge_length = 2.0 * value / (math.sqrt(3.0) * _PHI)
        elif key == "incircle_circumference":
            r = value / (2.0 * math.pi)
            edge_length = 20.0 * r / math.sqrt(250.0 + 110.0 * math.sqrt(5.0))
        elif key == "midsphere_circumference":
            rho = value / (2.0 * math.pi)
            edge_length = 2.0 * rho / (_PHI * math.sqrt(3.0))
        elif key == "circumcircle_circumference":
            R = value / (2.0 * math.pi)
            edge_length = 2.0 * R / (math.sqrt(3.0) * _PHI)
        elif key == "face_inradius":
            edge_length = 10.0 * value / math.sqrt(25.0 + 10.0 * math.sqrt(5.0))
        elif key == "face_circumradius":
            edge_length = value * math.sqrt(3.0 - _PHI) / _PHI
        elif key == "insphere_surface_area":
            r = math.sqrt(value / (4.0 * math.pi))
            edge_length = 20.0 * r / math.sqrt(250.0 + 110.0 * math.sqrt(5.0))
        elif key == "insphere_volume":
            r = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 20.0 * r / math.sqrt(250.0 + 110.0 * math.sqrt(5.0))
        elif key == "midsphere_surface_area":
            rho = math.sqrt(value / (4.0 * math.pi))
            edge_length = 2.0 * rho / (_PHI * math.sqrt(3.0))
        elif key == "midsphere_volume":
            rho = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 2.0 * rho / (_PHI * math.sqrt(3.0))
        elif key == "circumsphere_surface_area":
            R = math.sqrt(value / (4.0 * math.pi))
            edge_length = 2.0 * R / (math.sqrt(3.0) * _PHI)
        elif key == "circumsphere_volume":
            R = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 2.0 * R / (math.sqrt(3.0) * _PHI)
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
            formula_used=f"Dodecahedron: {key} → edge_length (algebraic)",
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
        Create a Canon-compliant Declaration for this dodecahedron.
        
        Args:
            edge_length: Edge length (a)
            
        Returns:
            Declaration with form type and params
        """
        return Declaration(
            title=f"Dodecahedron (a={edge_length:.4f})",
            forms=[
                Form(
                    id="dodecahedron",
                    kind="Dodecahedron",
                    params={"edge_length": edge_length},
                    dimensional_class=3,
                    symmetry_class="icosahedral",
                )
            ],
            epsilon=1e-9,
            metadata={
                "solver": "DodecahedronSolver",
                "dual": "icosahedron",
                "golden_ratio": True,
            },
        )
    
    def get_derivation(self) -> Optional[str]:
        """Return mathematical derivations in LaTeX format."""
        return r"""
Compute all geometric metrics for a regular dodecahedron from edge length.

CORE DIMENSION FORMULAS & DERIVATIONS:
========================================

The Golden Ratio: $\varphi = (1 + \sqrt{5})/2 \approx 1.618$
-----------------------------------------
Like the icosahedron, the dodecahedron is governed by the golden ratio.
Pentagon geometry inherently involves $\varphi$:
- Pentagon diagonal/side = $\varphi$
- Pentagon appears in all 12 pentagonal faces

Key golden ratio identities:
- $\varphi^2 = \varphi + 1 = (3 + \sqrt{5})/2$
- $1/\varphi = \varphi - 1 = (\sqrt{5} - 1)/2$
- $\varphi^3 = 2\varphi + 1$

Face Area: $A_{face} = (\sqrt{25 + 10\sqrt{5}}/4)a^2 = [(\sqrt{3})\varphi^2/2]a^2$
---------------------------------------------------
Each face is a regular pentagon with side length $a$.

Pentagon area formula:
$A_{pentagon} = (1/4)\sqrt{25 + 10\sqrt{5}} \times a^2$

Using $\varphi = (1 + \sqrt{5})/2$:
$25 + 10\sqrt{5} = 25 + 20\varphi - 10 = 15 + 20\varphi$
    
Alternative derivation via apothem:
Pentagon apothem (inradius): $r_p = (a/2)\sqrt{1 + 2/\sqrt{5}}$
Pentagon area = $(1/2) \times perimeter \times apothem$
              = $(1/2) \times 5a \times (a/2)\sqrt{1 + 2/\sqrt{5}}$
              = $(5a^2/4)\sqrt{1 + 2/\sqrt{5}}$
    
Simplified using golden ratio:
$A_{face} \approx 1.7204774a^2$ ✓

Surface Area: $A = 12 \times A_{face} = 3\sqrt{25 + 10\sqrt{5}} a^2$
------------------------------------------------
Dodecahedron has 12 identical pentagonal faces.
$A = 12 \times (1/4)\sqrt{25 + 10\sqrt{5}} \times a^2$
$= 3\sqrt{25 + 10\sqrt{5}} \times a^2$
$\approx 20.6457728a^2$

Volume: $V = [(15 + 7\sqrt{5})/4]a^3 = [(\varphi/2)(15 + 7\sqrt{5})]a^3$
----------------------------------------------------
Derivation via dual relationship with icosahedron:
    
The dodecahedron is the dual of the icosahedron.
Given an icosahedron, its face centers form a dodecahedron.
    
Using the duality formulas and edge-length relationships:
$V = (1/4)(15 + 7\sqrt{5})a^3$
    
Using $\varphi^2 = (3 + \sqrt{5})/2$:
$15 + 7\sqrt{5} = 15 + 14\varphi - 7 = 8 + 14\varphi = 2(4 + 7\varphi)$
    
Numerical value:
$V \approx 7.6631189606a^3$ ✓
    
Alternative derivation via canonical coordinates:
The dodecahedron vertices can be placed at:
- $(\pm 1, \pm 1, \pm 1)$                    [8 cube vertices]
- $(0, \pm \varphi, \pm 1/\varphi)$                  [4 vertices]
- $(\pm 1/\varphi, 0, \pm \varphi)$                  [4 vertices]
- $(\pm \varphi, \pm 1/\varphi, 0)$                  [4 vertices]
    
Total: 20 vertices (as expected)
Edge length for this configuration $\approx 2/\varphi$
Volume can be computed via convex hull integration.

AHA MOMENT #1: PHI GOVERNS EVERYTHING
=======================================
The dodecahedron is the ULTIMATE embodiment of the golden ratio $\varphi$ in 3D.
    
Every critical measurement involves $\varphi$:
- Vertex coordinates: $(\pm 1,\pm 1,\pm 1)$, $(0,\pm \varphi,\pm 1/\varphi)$, $(\pm 1/\varphi,0,\pm \varphi)$, $(\pm \varphi,\pm 1/\varphi,0)$
- Pentagon diagonal/side ratio = $\varphi$
- Volume formula includes $(15 + 7\sqrt{5})$ = function of $\varphi$
- All three sphere radii are $\varphi$-dependent
- Face area involves $\sqrt{25 + 10\sqrt{5}}$ = function of $\varphi$
    
The golden ratio $\varphi = (1+\sqrt{5})/2$ has the unique property: $\varphi^2 = \varphi + 1$
This recursive self-similarity (the whole is to the part as the part is
to the remainder) makes $\varphi$ the "most irrational" number—it cannot be
approximated well by rational fractions.
    
The dodecahedron crystallizes this transcendent irrationality into
geometric form. It is the Platonic solid of DIVINE PROPORTION.

SPHERE RADII FORMULAS & DERIVATIONS:
=====================================

Inradius (Inscribed Sphere): $r = [\varphi^2/2]\cdot a/\sqrt{3-\varphi} \approx 1.1135163645a$
------------------------------------------------------------------
The inscribed sphere touches the center of each pentagonal face.

Derivation using volume-to-surface-area ratio:
For any polyhedron: $r = 3V/A$

$r = 3 \times [(15 + 7\sqrt{5})/4]a^3 / [3\sqrt{25 + 10\sqrt{5}}a^2]$
$= [(15 + 7\sqrt{5})/4] \times a / \sqrt{25 + 10\sqrt{5}}$
    
Simplified using golden ratio algebra:
$r = (a/2)\sqrt{(3 + \varphi)} = (a/2)\sqrt{\varphi^2} \cdot \sqrt{3}$
$\approx 1.1135163645a$ ✓

Alternative geometric derivation:
Distance from center to pentagon face center.
Using canonical coordinates, the face normal points radially,
and the inradius is the perpendicular distance.

Midradius (Midsphere): $\rho = (a\varphi/2)\sqrt{\varphi + 2/\varphi} \approx 1.3090169944a$
--------------------------------------------------------------
The midsphere touches the midpoint of each edge.

Derivation via edge midpoint calculation:
Using canonical dodecahedron coordinates,
edge midpoints lie at distance:
$\rho = (a/2)\varphi\sqrt{1 + 1/\varphi^2}$
    
Using $\varphi^2 = \varphi + 1$:
$1 + 1/\varphi^2 = 1 + 1/(\varphi+1) = (\varphi+2)/(\varphi+1)$
    
Simplified:
$\rho \approx 1.3090169944a$ ✓

Circumradius (Circumscribed Sphere): $R = [\sqrt{3}/2]\varphi a \approx 1.4012585384a$
--------------------------------------------------------------------
The circumscribed sphere passes through all 20 vertices.

Derivation via canonical coordinates:
Vertex at $(1, 1, 1)$ for cube-embedded dodecahedron.
Distance from origin = $\sqrt{3}$
    
For canonical edge $\approx 2/\varphi$:
$R = \sqrt{3}$
    
For general edge $a$:
$R = \sqrt{3} \times (a\cdot \varphi/2) = (\sqrt{3}/2)\varphi a$ ✓

Alternative derivation:
Using vertex $(0, \varphi, 1/\varphi)$:
$R = \sqrt{0^2 + \varphi^2 + 1/\varphi^2}$
$= \sqrt{\varphi^2 + (\varphi-1)^2}$  [since $1/\varphi = \varphi-1$]
$= \sqrt{\varphi^2 + \varphi^2 - 2\varphi + 1}$
$= \sqrt{2\varphi^2 - 2\varphi + 1}$
    
Using $\varphi^2 = \varphi + 1$:
$= \sqrt{2(\varphi+1) - 2\varphi + 1} = \sqrt{3}$
    
Scaled for edge $a$: $R = (\sqrt{3}/2)\varphi a$ ✓

AHA MOMENT #2: THE COSMOS IN MINIATURE
========================================
The dodecahedron has 12 pentagonal faces—the same number as:
- 12 zodiac constellations
- 12 months of the year
- 12 Olympian gods
- 12 tribes of Israel
- 12 apostles
    
This is NOT coincidence. The number 12 represents COSMIC COMPLETENESS—
the division of the circle ($360^\circ$) into 12 equal $30^\circ$ sectors, the
duodecimal completion of the annual solar cycle.
    
The pentagon's 5-fold symmetry (5 vertices, 5 sides) multiplied by
12 faces gives 60 vertices of relationship (edges), encoding the
sexagesimal (base-60) system of ancient Babylonian astronomy.
    
The dodecahedron is the geometric mandala of the heavens—a 3D zodiac,
a crystallized celestial sphere. Plato's Timaeus calls it "the god's
design for the universe."

AHA MOMENT #3: MOST SPHERICAL PLATONIC SOLID
==============================================
The dodecahedron has the HIGHEST sphericity of all five Platonic solids!
    
Sphericity measures how closely a shape approximates a perfect sphere:
$\Psi = (\pi^{1/3} \times (6V)^{2/3}) / A$
    
Platonic solid sphericity ranking:
1. Dodecahedron: $\Psi \approx 0.910$ (closest to sphere)
2. Icosahedron: $\Psi \approx 0.939$ (second closest)
3. Cube: $\Psi \approx 0.806$
4. Octahedron: $\Psi \approx 0.846$
5. Tetrahedron: $\Psi \approx 0.671$ (least spherical)
    
With 12 faces, the dodecahedron achieves a smoother, more uniform
curvature than any other Platonic solid. It is the Platonic form
that most closely approximates the PERFECT SPHERE—the shape of
the cosmos, the sun, the planets.
    
This is why it represents the fifth element (Aether/Quintessence)—
it transcends the four terrestrial elements and approaches the
perfection of the celestial realm.

HERMETIC NOTE - THE AETHER/QUINTESSENCE:
==========================================
The dodecahedron represents the FIFTH ELEMENT (Aether/Quintessence):

Symbolism:
- 12 pentagonal faces = cosmic completeness (12 zodiac signs)
- Pentagon = 5-fold symmetry = human form (5 fingers, 5 senses)
- $\varphi$ governs all proportions = divine proportion, cosmic harmony
- Dual to icosahedron (water) = spirit transcending matter
- Highest sphericity among Platonic solids (most sphere-like)

Aristotelian Correspondence:
- Fifth element beyond Earth/Air/Fire/Water
- "Quinta Essentia" = quintessence
- Material of celestial spheres and heavenly bodies
- Represents the cosmos, the heavens, the divine order

Golden Ratio as Cosmic Principle:
- $\varphi$ appears throughout nature (spirals, growth patterns)
- Divine proportion in art, architecture, anatomy
- Self-similarity: $\varphi^2 = \varphi + 1$ (part equals whole plus part)
- Dodecahedron embodies this principle in 3D form

Spiritual Correspondences:
- Insphere ($r \approx 1.113a$): The inner sanctum, core of being
- Midsphere ($\rho \approx 1.309a$): The boundary of manifestation
- Circumsphere ($R \approx 1.401a$): The sphere of infinite potential

Ratios: $r : \rho : R \approx 1.113 : 1.309 : 1.401$

All three radii exceed the edge length, making the dodecahedron
"expansive" compared to tetrahedron/cube/octahedron.
This reflects Aether's transcendent, all-encompassing nature.

Dihedral Angle:
- Exactly $\arctan(2) \approx 116.57^\circ$
- Obtuse enough for smooth, sphere-like appearance
- Creates gentle, flowing surface

Packing Density:
- Cannot fill space (like icosahedron)
- Represents Aether's non-materiality
- Exists "between" ordinary matter

Pythagorean/Platonic Philosophy:
- Plato assigned dodecahedron to the cosmos in Timaeus
- "God used it for embroidering the constellations on the whole heaven"
- Symbol of the universe as ordered whole
- Pentagon = $\varphi$ = ratio that governs beauty and harmony
"""
