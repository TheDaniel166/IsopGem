"""
Geometry Pillar — Octahedron Solver.

Bidirectional solver for regular octahedron that converts user input
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


# Base constants for octahedron with edge length = √2
_BASE_EDGE_LENGTH = math.sqrt(2.0)
_BASE_FACE_AREA = (math.sqrt(3.0) / 4.0) * _BASE_EDGE_LENGTH ** 2
_BASE_SURFACE_AREA = 8.0 * _BASE_FACE_AREA
_BASE_VOLUME = (math.sqrt(2.0) / 3.0) * _BASE_EDGE_LENGTH ** 3
_BASE_INRADIUS = _BASE_EDGE_LENGTH * math.sqrt(6.0) / 6.0
_BASE_MIDRADIUS = _BASE_EDGE_LENGTH / 2.0
_BASE_CIRCUMRADIUS = _BASE_EDGE_LENGTH * math.sqrt(2.0) / 2.0
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

# Moment of inertia (k coefficients for octahedron)
_MOI_K_SOLID = 1.0 / 10.0
_MOI_K_SHELL = 1.0 / 6.0
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH


class OctahedronSolver(GeometrySolver):
    """
    Bidirectional solver for regular octahedron.
    
    Converts any valid property input into the canonical parameter (edge_length),
    then returns a SolveResult that can be used to build a Declaration.
    
    Canonical Parameter: edge_length (a)
    
    Relationships:
        - face_area: A_f = (√3/4)a²
        - surface_area: A = 2√3 a²
        - volume: V = (√2/3)a³
        - inradius: r = a√6/6
        - midradius: ρ = a/2
        - circumradius: R = a√2/2
        - All sphere and circumference properties
        - Moment of inertia properties
    
    Usage:
        solver = OctahedronSolver()
        result = solver.solve_from("volume", 0.471)
        
        if result.ok:
            decl = solver.create_declaration(result.canonical_parameter)
            verdict = engine.validate(decl)
    """
    
    @property
    def dimensional_class(self) -> int:
        """Octahedron is a 3D form."""
        return 3
    
    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "Octahedron"
    
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
                tooltip="Total surface area of 8 faces",
                format_spec=".6f",
                formula=r"A = 2\sqrt{3}a^2",
            ),
            PropertyDefinition(
                key="volume",
                label="Volume",
                unit="cubic units",
                editable=True,
                category="Core",
                tooltip="Total enclosed volume",
                format_spec=".6f",
                formula=r"V = \frac{\sqrt{2}}{3}a^3",
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
                formula=r"r = \frac{a\sqrt{6}}{6}",
            ),
            PropertyDefinition(
                key="midradius",
                label="Midradius (ρ)",
                unit="units",
                editable=False,
                category="Radii",
                tooltip="Radius to edge midpoints",
                format_spec=".6f",
                formula=r"\rho = \frac{a}{2}",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius (R)",
                unit="units",
                editable=False,
                category="Radii",
                tooltip="Radius of circumscribed sphere",
                format_spec=".6f",
                formula=r"R = \frac{a\sqrt{2}}{2}",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Incircle Circumference",
                unit="units",
                editable=False,
                category="Circumferences",
                tooltip="Circumference of inscribed circle",
                format_spec=".6f",
                formula=r"C_r = 2\pi r = \frac{\pi a\sqrt{6}}{3}",
            ),
            PropertyDefinition(
                key="midsphere_circumference",
                label="Midsphere Circumference",
                unit="units",
                editable=False,
                category="Circumferences",
                tooltip="Circumference at midradius",
                format_spec=".6f",
                formula=r"C_\rho = 2\pi\rho = \pi a",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumcircle Circumference",
                unit="units",
                editable=False,
                category="Circumferences",
                tooltip="Circumference of circumscribed circle",
                format_spec=".6f",
                formula=r"C_R = 2\pi R = \pi a\sqrt{2}",
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
                formula=r"A_r = 4\pi r^2 = \frac{2\pi a^2}{3}",
            ),
            PropertyDefinition(
                key="insphere_volume",
                label="Insphere Volume",
                unit="cubic units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Volume of inscribed sphere",
                format_spec=".6f",
                formula=r"V_r = \frac{4\pi r^3}{3} = \frac{\pi a^3\sqrt{6}}{27}",
            ),
            PropertyDefinition(
                key="midsphere_surface_area",
                label="Midsphere Surface Area",
                unit="sq units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Surface area at midradius",
                format_spec=".6f",
                formula=r"A_\rho = 4\pi\rho^2 = \pi a^2",
            ),
            PropertyDefinition(
                key="midsphere_volume",
                label="Midsphere Volume",
                unit="cubic units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Volume at midradius",
                format_spec=".6f",
                formula=r"V_\rho = \frac{4\pi\rho^3}{3} = \frac{\pi a^3}{6}",
            ),
            PropertyDefinition(
                key="circumsphere_surface_area",
                label="Circumsphere Surface Area",
                unit="sq units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Surface area of circumscribed sphere",
                format_spec=".6f",
                formula=r"A_R = 4\pi R^2 = 2\pi a^2",
            ),
            PropertyDefinition(
                key="circumsphere_volume",
                label="Circumsphere Volume",
                unit="cubic units",
                editable=False,
                category="Sphere Metrics",
                tooltip="Volume of circumscribed sphere",
                format_spec=".6f",
                formula=r"V_R = \frac{4\pi R^3}{3} = \frac{\pi a^3\sqrt{2}}{3}",
            ),
            PropertyDefinition(
                key="moment_inertia_solid",
                label="Moment of Inertia (Solid)",
                unit="mass·units²",
                editable=False,
                category="Dynamics",
                tooltip="Rotational inertia for solid octahedron",
                format_spec=".6f",
                formula=r"I_{solid} = \frac{1}{10}Ma^2",
            ),
            PropertyDefinition(
                key="moment_inertia_shell",
                label="Moment of Inertia (Shell)",
                unit="mass·units²",
                editable=False,
                category="Dynamics",
                tooltip="Rotational inertia for hollow shell",
                format_spec=".6f",
                formula=r"I_{shell} = \frac{1}{6}Ma^2",
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
            edge_length = math.sqrt(value / (2.0 * math.sqrt(3.0)))
        elif key == "volume":
            edge_length = (3.0 * value / math.sqrt(2.0)) ** (1.0 / 3.0)
        elif key == "inradius":
            edge_length = 6.0 * value / math.sqrt(6.0)
        elif key == "midradius":
            edge_length = 2.0 * value
        elif key == "circumradius":
            edge_length = 2.0 * value / math.sqrt(2.0)
        elif key == "incircle_circumference":
            edge_length = 3.0 * value / (math.pi * math.sqrt(6.0))
        elif key == "midsphere_circumference":
            edge_length = value / math.pi
        elif key == "circumcircle_circumference":
            edge_length = value / (math.pi * math.sqrt(2.0))
        elif key == "face_inradius":
            edge_length = 6.0 * value / math.sqrt(3.0)
        elif key == "face_circumradius":
            edge_length = value * math.sqrt(3.0)
        elif key == "insphere_surface_area":
            edge_length = math.sqrt(3.0 * value / (2.0 * math.pi)) * math.sqrt(6.0) / 3.0
        elif key == "insphere_volume":
            r = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 6.0 * r / math.sqrt(6.0)
        elif key == "midsphere_surface_area":
            edge_length = math.sqrt(value / math.pi)
        elif key == "midsphere_volume":
            rho = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 2.0 * rho
        elif key == "circumsphere_surface_area":
            edge_length = math.sqrt(value / (2.0 * math.pi)) * math.sqrt(2.0)
        elif key == "circumsphere_volume":
            R = ((3.0 * value) / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = 2.0 * R / math.sqrt(2.0)
        elif key == "moment_inertia_solid":
            edge_length = math.sqrt(10.0 * value / _BASE_VOLUME)
        elif key == "moment_inertia_shell":
            edge_length = math.sqrt(6.0 * value / _BASE_SURFACE_AREA)
        else:
            return SolveResult.invalid(key, value, f"Unsupported solve key: {key}")
        
        # Build provenance
        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=f"Octahedron: {key} → edge_length (algebraic)",
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
        Create a Canon-compliant Declaration for this octahedron.
        
        Args:
            edge_length: Edge length (a)
            
        Returns:
            Declaration with form type and params
        """
        return Declaration(
            title=f"Octahedron (a={edge_length:.4f})",
            forms=[
                Form(
                    id="octahedron",
                    kind="Octahedron",
                    params={"edge_length": edge_length},
                    dimensional_class=3,
                    symmetry_class="octahedral",
                )
            ],
            epsilon=1e-9,
            metadata={
                "solver": "OctahedronSolver",
                "dual": "cube",
            },
        )
    
    def get_derivation(self) -> Optional[str]:
        """Return mathematical derivations in LaTeX format."""
        return r"""
Compute all geometric metrics for a regular octahedron from edge length.

CORE DIMENSION FORMULAS & DERIVATIONS:
========================================

Face Area: $A_{face} = (\sqrt{3}/4)a^2$
----------------------------
Each face is an equilateral triangle with side length $a$.
For equilateral triangle:
- Height = $(\sqrt{3}/2)a$
- Area = $(1/2) \times base \times height$
       = $(1/2) \times a \times (\sqrt{3}/2)a$
       = $(\sqrt{3}/4)a^2$ ✓

Surface Area: $A = 8 \times (\sqrt{3}/4)a^2 = 2\sqrt{3} a^2$
----------------------------------------
Octahedron has 8 identical equilateral triangle faces.
Total surface area = $8 \times (\sqrt{3}/4)a^2 = 2\sqrt{3} a^2$

Volume: $V = (\sqrt{2}/3)a^3$
--------------------
View the octahedron as two congruent square pyramids joined base-to-base.

The equatorial "belt" forms a square with diagonal = distance between
opposite vertices along the equator. For edge length $a$, this diagonal
is $a\sqrt{2}$ (by the Pythagorean theorem on the square formed by 4 edges).
Therefore, the square side length is $(a\sqrt{2})/\sqrt{2} = a$.
Square base area = $a^2$.

The distance between top and bottom vertices (poles) is $a\sqrt{2}$.
Each pyramid has height $h = (a\sqrt{2})/2 = a/\sqrt{2}$.

Volume of one pyramid = $(1/3) \times base\_area \times height$
                      = $(1/3) \times a^2 \times (a/\sqrt{2})$
                      = $a^3/(3\sqrt{2})$

Total volume = $2 \times a^3/(3\sqrt{2}) = (2a^3)/(3\sqrt{2})$
             = $(\sqrt{2}/3)a^3$ ✓

SPHERE RADII FORMULAS & DERIVATIONS:
=====================================

Inradius (Inscribed Sphere): $r = a/\sqrt{6}$
--------------------------------------
The inscribed sphere touches the center of each face.

Derivation:
The distance from center to each face is $h/3$ for a regular tetrahedron,
but for octahedron, it is derived from the triangular face:
$r = (a\sqrt{6})/6 = a/\sqrt{6}$

Midradius (Midsphere): $\rho = a/2$
------------------------------
The midsphere touches the midpoint of each edge.
Each edge midpoint lies at distance $a/2$ from the center.

Circumradius (Circumscribed Sphere): $R = a/\sqrt{2}$
------------------------------------------------
The circumscribed sphere passes through all 6 vertices.

Derivation:
Vertex coordinates at $(\pm a/\sqrt{2}, 0, 0)$, etc.
Distance from origin = $\sqrt{(a/\sqrt{2})^2} = a/\sqrt{2}$

AHA MOMENT: SYMMETRY OF DUALITY
===============================
The octahedron is the dual of the cube.

- Octahedron faces $\leftrightarrow$ Cube vertices (8)
- Octahedron vertices $\leftrightarrow$ Cube faces (6)
- Both have 12 edges

Hermetic correspondence: Octahedron = Air, Cube = Earth.

The octahedron represents balance and equilibrium, suspended between
opposite poles, perfectly symmetric in all directions.

Its 8 triangular faces correspond to 8 directions of space and
encode the "breath" of the element of Air.
"""
