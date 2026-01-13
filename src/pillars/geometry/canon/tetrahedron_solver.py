"""
Geometry Pillar — Tetrahedron Solver.

Bidirectional solver for regular tetrahedron that converts user input
into Canon-compliant Declarations.

Reference: ADR-010: Canon DSL Adoption
Reference: ADR-011: Unified Geometry Viewer
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


# Base constants from TetrahedronSolidService
_BASE_EDGE_LENGTH = 2 * math.sqrt(2.0)
_BASE_HEIGHT = math.sqrt(2.0 / 3.0) * _BASE_EDGE_LENGTH
_BASE_FACE_AREA = (math.sqrt(3.0) / 4.0) * _BASE_EDGE_LENGTH ** 2
_BASE_SURFACE_AREA = 4.0 * _BASE_FACE_AREA
_BASE_VOLUME = _BASE_EDGE_LENGTH ** 3 / (6.0 * math.sqrt(2.0))
_BASE_INRADIUS = _BASE_EDGE_LENGTH * math.sqrt(6.0) / 12.0
_BASE_MIDRADIUS = _BASE_EDGE_LENGTH * math.sqrt(2.0) / 4.0
_BASE_CIRCUMRADIUS = _BASE_EDGE_LENGTH * math.sqrt(6.0) / 4.0
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS

# Face geometry
_BASE_FACE_INRADIUS = _BASE_EDGE_LENGTH * math.sqrt(3.0) / 6.0
_BASE_FACE_CIRCUMRADIUS = _BASE_EDGE_LENGTH / math.sqrt(3.0)

# Sphere metrics
_BASE_INSPHERE_SA = 4.0 * math.pi * _BASE_INRADIUS ** 2
_BASE_MIDSPHERE_SA = 4.0 * math.pi * _BASE_MIDRADIUS ** 2
_BASE_CIRCUMSPHERE_SA = 4.0 * math.pi * _BASE_CIRCUMRADIUS ** 2
_BASE_INSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_INRADIUS ** 3
_BASE_MIDSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_MIDRADIUS ** 3
_BASE_CIRCUMSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_CIRCUMRADIUS ** 3

# Moment of inertia (k coefficients from platonic_constants)
_MOI_K_SOLID = 1.0 / 20.0  # For uniform density solid
_MOI_K_SHELL = 1.0 / 12.0  # For thin shell
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH


class TetrahedronSolver(GeometrySolver):
    """
    Bidirectional solver for regular tetrahedron.
    
    Converts any valid property input into the canonical parameter (edge_length),
    then returns a SolveResult that can be used to build a Declaration.
    
    Canonical Parameter: edge_length (a)
    
    Relationships:
        - height: h = a√(2/3)
        - face_area: A_f = (√3/4)a²
        - surface_area: A = √3 a²
        - volume: V = a³/(6√2)
        - inradius: r = a√6/12
        - midradius: ρ = a√2/4
        - circumradius: R = a√6/4
        - All sphere and circumference properties
        - Moment of inertia properties
    
    Usage:
        solver = TetrahedronSolver()
        result = solver.solve_from("volume", 0.235)
        
        if result.ok:
            decl = solver.create_declaration(result.canonical_parameter)
            verdict = engine.validate(decl)
    """
    
    # ─────────────────────────────────────────────────────────────────
    # GeometrySolver Properties
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def dimensional_class(self) -> int:
        """Tetrahedron is a 3D form."""
        return 3
    
    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "Tetrahedron"
    
    @property
    def canonical_key(self) -> str:
        return "edge_length"
    
    @property
    def supported_keys(self) -> set[str]:
        return {
            "edge_length",
            "height",
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
                key="height",
                label="Height (h)",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Height from base to apex: h = a√(2/3)",
                format_spec=".6f",
                formula=r"h = a\sqrt{\frac{2}{3}}",
            ),
            PropertyDefinition(
                key="face_area",
                label="Face Area",
                unit="units²",
                editable=True,
                category="Surface",
                tooltip="Area of one equilateral triangle face",
                format_spec=".6f",
                formula=r"A_f = \frac{\sqrt{3}}{4}a^2",
            ),
            PropertyDefinition(
                key="surface_area",
                label="Surface Area",
                unit="units²",
                editable=True,
                category="Surface",
                tooltip="Total surface area: A = √3 a²",
                format_spec=".6f",
                formula=r"A = \sqrt{3}\,a^2",
            ),
            PropertyDefinition(
                key="volume",
                label="Volume",
                unit="units³",
                editable=True,
                category="Volume",
                tooltip="Volume: V = a³/(6√2)",
                format_spec=".6f",
                formula=r"V = \frac{a^3}{6\sqrt{2}}",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius (r)",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Inscribed sphere radius: r = a√6/12",
                format_spec=".6f",
                formula=r"r = \frac{a\sqrt{6}}{12}",
            ),
            PropertyDefinition(
                key="midradius",
                label="Midsphere Radius (ρ)",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Midsphere radius touching edge midpoints: ρ = a√2/4",
                format_spec=".6f",
                formula=r"\rho = \frac{a\sqrt{2}}{4}",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius (R)",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Circumscribed sphere radius: R = a√6/4",
                format_spec=".6f",
                formula=r"R = \frac{a\sqrt{6}}{4}",
            ),
            PropertyDefinition(
                key="incircle_circumference",
                label="Insphere Circumference",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Great circle of inscribed sphere: 2πr",
                format_spec=".6f",
                formula=r"C_{in} = 2\pi r",
            ),
            PropertyDefinition(
                key="midsphere_circumference",
                label="Midsphere Circumference",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Great circle of midsphere: 2πρ",
                format_spec=".6f",
                formula=r"C_{mid} = 2\pi \rho",
            ),
            PropertyDefinition(
                key="circumcircle_circumference",
                label="Circumsphere Circumference",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Great circle of circumscribed sphere: 2πR",
                format_spec=".6f",
                formula=r"C_{circ} = 2\pi R",
            ),
            PropertyDefinition(
                key="face_inradius",
                label="Face Inradius",
                unit="units",
                editable=True,
                category="Face",
                tooltip="Inradius of equilateral triangle face",
                format_spec=".6f",
                formula=r"r_f = \frac{a\sqrt{3}}{6}",
            ),
            PropertyDefinition(
                key="face_circumradius",
                label="Face Circumradius",
                unit="units",
                editable=True,
                category="Face",
                tooltip="Circumradius of equilateral triangle face",
                format_spec=".6f",
                formula=r"R_f = \frac{a}{\sqrt{3}}",
            ),
            PropertyDefinition(
                key="insphere_surface_area",
                label="Insphere Surface Area",
                unit="units²",
                editable=True,
                category="Sphere Metrics",
                tooltip="Surface area of inscribed sphere",
                format_spec=".6f",
                formula=r"A_{in} = 4\pi r^2",
            ),
            PropertyDefinition(
                key="insphere_volume",
                label="Insphere Volume",
                unit="units³",
                editable=True,
                category="Sphere Metrics",
                tooltip="Volume of inscribed sphere",
                format_spec=".6f",
                formula=r"V_{in} = \frac{4}{3}\pi r^3",
            ),
            PropertyDefinition(
                key="midsphere_surface_area",
                label="Midsphere Surface Area",
                unit="units²",
                editable=True,
                category="Sphere Metrics",
                tooltip="Surface area of midsphere",
                format_spec=".6f",
                formula=r"A_{mid} = 4\pi \rho^2",
            ),
            PropertyDefinition(
                key="midsphere_volume",
                label="Midsphere Volume",
                unit="units³",
                editable=True,
                category="Sphere Metrics",
                tooltip="Volume of midsphere",
                format_spec=".6f",
                formula=r"V_{mid} = \frac{4}{3}\pi \rho^3",
            ),
            PropertyDefinition(
                key="circumsphere_surface_area",
                label="Circumsphere Surface Area",
                unit="units²",
                editable=True,
                category="Sphere Metrics",
                tooltip="Surface area of circumscribed sphere",
                format_spec=".6f",
                formula=r"A_{circ} = 4\pi R^2",
            ),
            PropertyDefinition(
                key="circumsphere_volume",
                label="Circumsphere Volume",
                unit="units³",
                editable=True,
                category="Sphere Metrics",
                tooltip="Volume of circumscribed sphere",
                format_spec=".6f",
                formula=r"V_{circ} = \frac{4}{3}\pi R^3",
            ),
            PropertyDefinition(
                key="moment_inertia_solid",
                label="Moment of Inertia (Solid)",
                unit="units⁵",
                editable=True,
                category="Physics",
                tooltip="Moment of inertia for uniform density solid",
                format_spec=".8f",
                formula=r"I = \frac{1}{20}Ma^2",
            ),
            PropertyDefinition(
                key="moment_inertia_shell",
                label="Moment of Inertia (Shell)",
                unit="units⁴",
                editable=True,
                category="Physics",
                tooltip="Moment of inertia for thin shell",
                format_spec=".8f",
                formula=r"I = \frac{1}{12}Aa^2",
            ),
        ]
    
    def get_derived_properties(self) -> list[PropertyDefinition]:
        """Return readonly derived property definitions."""
        return [
            PropertyDefinition(
                key="faces",
                label="Faces",
                unit="",
                editable=False,
                readonly=True,
                category="Topology",
                tooltip="Number of faces",
                format_spec=".0f",
            ),
            PropertyDefinition(
                key="edges",
                label="Edges",
                unit="",
                editable=False,
                readonly=True,
                category="Topology",
                tooltip="Number of edges",
                format_spec=".0f",
            ),
            PropertyDefinition(
                key="vertices",
                label="Vertices",
                unit="",
                editable=False,
                readonly=True,
                category="Topology",
                tooltip="Number of vertices",
                format_spec=".0f",
            ),
            PropertyDefinition(
                key="dihedral_angle_deg",
                label="Dihedral Angle",
                unit="°",
                editable=False,
                readonly=True,
                category="Angles",
                tooltip="Angle between two adjacent faces",
                format_spec=".4f",
            ),
            PropertyDefinition(
                key="solid_angle_sr",
                label="Solid Angle",
                unit="sr",
                editable=False,
                readonly=True,
                category="Angles",
                tooltip="Solid angle at each vertex",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="sphericity",
                label="Sphericity",
                unit="",
                editable=False,
                readonly=True,
                category="Quality",
                tooltip="How sphere-like the solid is (0-1)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="isoperimetric_quotient",
                label="Isoperimetric Quotient",
                unit="",
                editable=False,
                readonly=True,
                category="Quality",
                tooltip="Volume efficiency metric",
                format_spec=".6f",
            ),
        ]
    
    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Solve for edge_length given any valid property.
        
        Args:
            key: The property being set
            value: The value entered by the user
        
        Returns:
            SolveResult with the derived edge_length and provenance
        """
        if value <= 0:
            return SolveResult.invalid(
                key=key,
                value=value,
                reason="Value must be positive"
            )
        
        if key not in self.supported_keys:
            return SolveResult.invalid(
                key=key,
                value=value,
                reason=f"Property '{key}' not supported for Tetrahedron"
            )
        
        # Solve using scaling formula: scale = (value / base_value) ** (1.0 / power)
        # then edge_length = scale * _BASE_EDGE_LENGTH
        
        edge_length: Optional[float] = None
        formula = ""
        intermediates: dict[str, float] = {}
        
        if key == "edge_length":
            edge_length = value
            formula = "a = (input)"
        
        elif key == "height":
            # h = a√(2/3) → a = h / √(2/3)
            scale = (value / _BASE_HEIGHT) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = h / √(2/3)"
        
        elif key == "face_area":
            # A_f = (√3/4)a² → a = √(4A_f/√3)
            scale = (value / _BASE_FACE_AREA) ** 0.5
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = √(4A_f/√3)"
        
        elif key == "surface_area":
            # A = √3 a² → a = √(A/√3)
            scale = (value / _BASE_SURFACE_AREA) ** 0.5
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = √(A/√3)"
        
        elif key == "volume":
            # V = a³/(6√2) → a = ∛(6√2 V)
            scale = (value / _BASE_VOLUME) ** (1.0 / 3.0)
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = ∛(6√2 V)"
        
        elif key == "inradius":
            # r = a√6/12 → a = 12r/√6
            scale = (value / _BASE_INRADIUS) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = 12r/√6"
        
        elif key == "midradius":
            # ρ = a√2/4 → a = 4ρ/√2
            scale = (value / _BASE_MIDRADIUS) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = 4ρ/√2"
        
        elif key == "circumradius":
            # R = a√6/4 → a = 4R/√6
            scale = (value / _BASE_CIRCUMRADIUS) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = 4R/√6"
        
        elif key == "incircle_circumference":
            # C = 2πr, r = a√6/12 → a = 12(C/2π)/√6
            scale = (value / _BASE_INCIRC_CIRC) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = 12(C/2π)/√6"
        
        elif key == "midsphere_circumference":
            # C = 2πρ, ρ = a√2/4 → a = 4(C/2π)/√2
            scale = (value / _BASE_MID_CIRC) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = 4(C/2π)/√2"
        
        elif key == "circumcircle_circumference":
            # C = 2πR, R = a√6/4 → a = 4(C/2π)/√6
            scale = (value / _BASE_CIRCUM_CIRC) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = 4(C/2π)/√6"
        
        elif key == "face_inradius":
            # r_f = a√3/6 → a = 6r_f/√3
            scale = (value / _BASE_FACE_INRADIUS) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = 6r_f/√3"
        
        elif key == "face_circumradius":
            # R_f = a/√3 → a = R_f√3
            scale = (value / _BASE_FACE_CIRCUMRADIUS) ** 1.0
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = R_f√3"
        
        elif key == "insphere_surface_area":
            # A_in = 4πr² → a via r = √(A_in/4π)
            scale = (value / _BASE_INSPHERE_SA) ** 0.5
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "r = √(A_in/4π), a = 12r/√6"
        
        elif key == "insphere_volume":
            # V_in = (4/3)πr³ → a via r = ∛(3V_in/4π)
            scale = (value / _BASE_INSPHERE_VOL) ** (1.0 / 3.0)
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "r = ∛(3V_in/4π), a = 12r/√6"
        
        elif key == "midsphere_surface_area":
            # A_mid = 4πρ² → a via ρ = √(A_mid/4π)
            scale = (value / _BASE_MIDSPHERE_SA) ** 0.5
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "ρ = √(A_mid/4π), a = 4ρ/√2"
        
        elif key == "midsphere_volume":
            # V_mid = (4/3)πρ³ → a via ρ = ∛(3V_mid/4π)
            scale = (value / _BASE_MIDSPHERE_VOL) ** (1.0 / 3.0)
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "ρ = ∛(3V_mid/4π), a = 4ρ/√2"
        
        elif key == "circumsphere_surface_area":
            # A_circ = 4πR² → a via R = √(A_circ/4π)
            scale = (value / _BASE_CIRCUMSPHERE_SA) ** 0.5
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "R = √(A_circ/4π), a = 4R/√6"
        
        elif key == "circumsphere_volume":
            # V_circ = (4/3)πR³ → a via R = ∛(3V_circ/4π)
            scale = (value / _BASE_CIRCUMSPHERE_VOL) ** (1.0 / 3.0)
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "R = ∛(3V_circ/4π), a = 4R/√6"
        
        elif key == "moment_inertia_solid":
            # I = k·M·a² where M = ρ·V, so I ∝ a⁵
            scale = (value / _BASE_MOI_SOLID) ** 0.2
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = (I/k)^(1/5) where k = (1/20)ρ"
        
        elif key == "moment_inertia_shell":
            # I = k·A·a² where A ∝ a², so I ∝ a⁴
            scale = (value / _BASE_MOI_SHELL) ** 0.25
            edge_length = scale * _BASE_EDGE_LENGTH
            formula = "a = (I/k)^(1/4) where k = (1/12)σ"
        
        if edge_length is None or not math.isfinite(edge_length) or edge_length <= 0:
            return SolveResult.invalid(key, value, "Solver produced invalid edge_length")
        
        return SolveResult.success(
            canonical_parameter=edge_length,
            canonical_key=self.canonical_key,
            provenance=SolveProvenance(
                source_key=key,
                source_value=value,
                formula_used=formula,
                intermediate_values=intermediates,
                assumptions=["Regular tetrahedron", "All edges equal length"],
            ),
        )
    
    def get_all_properties(self, edge_length: float) -> dict[str, float]:
        """
        Compute all geometric metrics for a regular tetrahedron from edge length.

        CORE DIMENSION FORMULAS & DERIVATIONS:
        ========================================

        Face Area: A_face = (√3/4)a²
        ----------------------------
        Each face is an equilateral triangle with side length a.
        For equilateral triangle:
        - Height of triangle = (√3/2)a
        - Area = (1/2) × base × height
               = (1/2) × a × (√3/2)a
               = (√3/4)a² ✓

        Surface Area: A = 4 × (√3/4)a² = √3 a²
        ----------------------------------------
        Tetrahedron has 4 identical equilateral triangle faces.
        Total surface area = 4 × (√3/4)a² = √3 a²

        Height: h = √(2/3) × a
        -----------------------
        Place tetrahedron with base on xy-plane, apex directly above centroid.
        Base is equilateral triangle with vertices forming a 2D centroid.

        Derivation using Pythagorean theorem in 3D:
        1. Centroid of base triangle is at distance r from each vertex
        2. For equilateral triangle: r = a/√3 (circumradius of triangle)
        3. Edge from apex to base vertex: length = a
        4. Using Pythagoras: a² = h² + r²
           a² = h² + (a/√3)²
           a² = h² + a²/3
           h² = a² - a²/3 = 2a²/3
           h = √(2/3) × a ✓

        Volume: V = a³/(6√2)
        --------------------
        Volume of pyramid = (1/3) × base_area × height

        For tetrahedral:
        V = (1/3) × (√3/4)a² × √(2/3)a
          = (1/3) × (√3/4) × √(2/3) × a³
          = (1/12) × √3 × √(2/3) × a³
          = (1/12) × √3 × √2/√3 × a³
          = (1/12) × √2 × a³
          = a³/(6√2) ✓

        Alternative via closed form:
        V = a³√2/12 = a³/(6√2) ✓

        AHA MOMENT #1: THE SIMPLEST PLATONIC SOLID
        ============================================
        The tetrahedron is the ONLY Platonic solid that cannot be decomposed
        into simpler polyhedra without introducing new vertex types.
        
        All other Platonic solids can be built from tetrahedra:
        - Octahedron = 8 tetrahedra arranged around a common vertex
        - Cube = 6 tetrahedra + 1 central octahedron (stella octangula decomposition)
        - Icosahedron = 20 tetrahedra arranged around vertices
        - Dodecahedron = dual of icosahedron, inherits tetrahedral substructure
        
        The tetrahedron is the ATOMIC UNIT of Platonic geometry—irreducible,
        fundamental, and generative. It is the 3D simplex: the minimal volume
        bounded by flat faces (0-simplex = point, 1-simplex = line, 2-simplex = triangle,
        3-simplex = tetrahedron).
        
        This is why it represents FIRE—the primal element from which all others emerge.

        SPHERE RADII FORMULAS & DERIVATIONS:
        =====================================

        Inradius (Inscribed Sphere): r = a√6/12 = a/(2√6)
        --------------------------------------------------
        The inscribed sphere touches the center of each face.

        Derivation using volume-to-surface-area ratio:
        For any polyhedron: r = 3V/A

        r = 3 × [a³/(6√2)] / [√3 a²]
          = 3a³/(6√2) × 1/(√3 a²)
          = 3a/(6√2 × √3)
          = a/(2√6)
          = a√6/12 ✓

        Geometric interpretation:
        - Distance from centroid to any face
        - Centroid at (1/4) of height from base
        - Inradius = (1/4)h for tetrahedron
        - r = (1/4) × √(2/3)a = √(2/3)a/4 = a√6/12 ✓

        Midradius (Midsphere): ρ = a√2/4 = a/(2√2)
        -------------------------------------------
        The midsphere touches the midpoint of each edge.

        Derivation via canonical coordinates:
        Using canonical vertices at (±1, ±1, ±1) with alternating signs,
        the edge length = 2√2, and edge midpoint is at (0, 0, 1).
        Distance from origin = 1.
        For general edge length a: scale factor = a/(2√2)
        Midradius = 1 × a/(2√2) = a/(2√2) = a√2/4 ✓

        Circumradius (Circumscribed Sphere): R = a√6/4
        -----------------------------------------------
        The circumscribed sphere passes through all 4 vertices.

        Derivation using height and centroid position:
        - Centroid is at (1/4)h from base, or (3/4)h from apex
        - Distance from centroid to apex vertex = R
        - R = (3/4)h = (3/4) × √(2/3)a
          = (3/4) × a√(2/3)
          = (3a/4) × √2/√3
          = (3a/4) × √(2/3)
          = a√6/4 ✓

        Alternative via base vertex distance:
        - Distance from centroid to base vertex = R
        - Centroid at height h/4 above base
        - Base vertex at distance a/√3 from base centroid (horizontal)
        - R² = (h/4)² + (a/√3)²
          = (√(2/3)a/4)² + (a/√3)²
          = (2a²/3)/16 + a²/3
          = a²/24 + a²/3
          = a²/24 + 8a²/24 = 9a²/24 = 3a²/8
        - R = a√(3/8) = a√3/(2√2) = a√6/4 ✓

        AHA MOMENT #2: SELF-DUAL PERFECTION
        =====================================
        The tetrahedron is SELF-DUAL: its dual polyhedron is another tetrahedron!
        
        When you connect the face centers of a tetrahedron, you get another
        tetrahedron rotated 180° and scaled by 1/3. This creates the "Merkaba"
        or "Star Tetrahedron"—two interpenetrating tetrahedra forming a 3D
        Star of David.
        
        Only the tetrahedron possesses this perfect self-symmetry among Platonic
        solids. All others have distinct duals:
        - Cube ↔ Octahedron (reciprocal duals)
        - Dodecahedron ↔ Icosahedron (reciprocal duals)
        - Tetrahedron ↔ Tetrahedron (SELF-DUAL)
        
        This self-reference is the geometric expression of the alchemical principle
        "As within, so without"—the tetrahedron contains its own reflection.

        AHA MOMENT #3: THE 1:3 RATIO
        =============================
        The tetrahedron has R/r = 3 EXACTLY—the only Platonic solid with this
        simple integer ratio!
        
        R/r = (a√6/4) / (a√6/12) = (a√6/4) × (12/a√6) = 12/4 = 3
        
        All other Platonic solids have irrational R/r ratios:
        - Cube: R/r = √3 ≈ 1.732
        - Octahedron: R/r = √3 ≈ 1.732
        - Dodecahedron: R/r ≈ 1.258 (φ-based)
        - Icosahedron: R/r ≈ 1.258 (φ-based)
        
        The 3:1 ratio reflects the Trinity principle—three persons in one essence.
        The circumsphere (manifestation) is exactly three times the insphere (essence).
        This perfect integer relationship makes the tetrahedron the most "pure"
        and "simple" of all Platonic solids.

        HERMETIC NOTE - THE FIRE ELEMENT:
        ==================================
        The tetrahedron represents FIRE in Platonic solid cosmology:

        Symbolism:
        - 4 triangular faces = upward aspiration, ascent
        - Sharpest vertices (largest angular defect = 180°)
        - Smallest volume-to-surface ratio (most "surface-like")
        - Self-dual (its dual is another tetrahedron, rotated)

        Spiritual Correspondences:
        - Insphere (r = a√6/12): The inner flame, spiritual heat
        - Midsphere (ρ = a√2/4): The radiant boundary
        - Circumsphere (R = a√6/4): The sphere of emanation

        Ratios: r : ρ : R = √6/12 : √2/4 : √6/4
                          = 1 : √3 : 3

        Dihedral Angle:
        - Exactly arccos(1/3) ≈ 70.53°
        - This is close to the tetrahedral bond angle in chemistry
        - sp³ hybridization (methane, diamond lattice)

        Packing Density:
        - Cannot fill space (leaves gaps)
        - Represents Fire's inability to be "contained"
        - Aspires upward, cannot be "stacked" perfectly
        """
        a = edge_length
        
        # Core dimensions
        height = a * math.sqrt(2.0 / 3.0)
        face_area = (math.sqrt(3.0) / 4.0) * a ** 2
        surface_area = 4.0 * face_area
        volume = a ** 3 / (6.0 * math.sqrt(2.0))
        
        # Sphere radii
        inradius = a * math.sqrt(6.0) / 12.0
        midradius = a * math.sqrt(2.0) / 4.0
        circumradius = a * math.sqrt(6.0) / 4.0
        
        # Circumferences
        incircle_circ = 2.0 * math.pi * inradius
        midsphere_circ = 2.0 * math.pi * midradius
        circumcircle_circ = 2.0 * math.pi * circumradius
        
        # Face geometry
        face_inradius = a * math.sqrt(3.0) / 6.0
        face_circumradius = a / math.sqrt(3.0)
        
        # Sphere metrics
        insphere_sa = 4.0 * math.pi * inradius ** 2
        insphere_vol = (4.0 / 3.0) * math.pi * inradius ** 3
        midsphere_sa = 4.0 * math.pi * midradius ** 2
        midsphere_vol = (4.0 / 3.0) * math.pi * midradius ** 3
        circumsphere_sa = 4.0 * math.pi * circumradius ** 2
        circumsphere_vol = (4.0 / 3.0) * math.pi * circumradius ** 3
        
        # Physics
        moi_solid = _MOI_K_SOLID * volume * a ** 2
        moi_shell = _MOI_K_SHELL * surface_area * a ** 2
        
        # Quality metrics
        sphericity = (math.pi ** (1.0 / 3.0) * (6.0 * volume) ** (2.0 / 3.0)) / surface_area
        isoperimetric = (36.0 * math.pi * volume ** 2) / (surface_area ** 3)
        surface_to_volume = surface_area / volume
        
        return {
            # Core editable
            "edge_length": a,
            "height": height,
            "face_area": face_area,
            "surface_area": surface_area,
            "volume": volume,
            "inradius": inradius,
            "midradius": midradius,
            "circumradius": circumradius,
            "incircle_circumference": incircle_circ,
            "midsphere_circumference": midsphere_circ,
            "circumcircle_circumference": circumcircle_circ,
            "face_inradius": face_inradius,
            "face_circumradius": face_circumradius,
            "insphere_surface_area": insphere_sa,
            "insphere_volume": insphere_vol,
            "midsphere_surface_area": midsphere_sa,
            "midsphere_volume": midsphere_vol,
            "circumsphere_surface_area": circumsphere_sa,
            "circumsphere_volume": circumsphere_vol,
            "moment_inertia_solid": moi_solid,
            "moment_inertia_shell": moi_shell,
            
            # Topology (constants)
            "faces": 4.0,
            "edges": 6.0,
            "vertices": 4.0,
            "face_sides": 3.0,
            "vertex_valence": 3.0,
            
            # Angles (constants)
            "dihedral_angle_deg": 70.528779365509308,
            "solid_angle_sr": 0.55129400845,
            
            # Quality metrics
            "sphericity": sphericity,
            "isoperimetric_quotient": isoperimetric,
            "surface_to_volume_ratio": surface_to_volume,
            
            # Advanced constants
            "angular_defect_vertex_deg": 180.0,
            "euler_characteristic": 2.0,
            "packing_density": 0.367346939,
            "symmetry_group_order": 24.0,
            "rotational_symmetry_order": 12.0,
        }
    
    def create_declaration(
        self,
        edge_length: float,
        *,
        title: Optional[str] = None,
    ) -> Declaration:
        """
        Create a Canon-compliant Declaration for the Tetrahedron.
        
        Args:
            edge_length: The canonical parameter
            title: Custom title for the declaration
        
        Returns:
            A Declaration ready for Canon validation
        """
        forms = [
            Form(
                id="tetrahedron",
                kind="Tetrahedron",
                params={"edge_length": edge_length},
                symmetry_class="tetrahedral",
                curvature_class="planar",
                dimensional_class=3,
                notes="Regular tetrahedron - simplest Platonic solid",
            ),
        ]
        
        return Declaration(
            title=title or f"Tetrahedron (a={edge_length:.4f})",
            forms=forms,
            constraints=[],
            metadata={"description": "Regular tetrahedron with 4 equilateral triangle faces"},
        )
    
    def get_derivation(self) -> str:
        """
        Return the mathematical derivation for the Tetrahedron.
        
        This is the sacred geometry commentary explaining why the formulas work.
        """
        return r"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   THE TETRAHEDRON — FIRE & FOUNDATION                         ║
║                     The Simplest Platonic Solid                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

THE ATOMIC UNIT OF PLATONIC GEOMETRY
═════════════════════════════════════

The tetrahedron is the ONLY Platonic solid that cannot be decomposed
into simpler polyhedra without introducing new vertex types.

All other Platonic solids can be built from tetrahedra:
• Octahedron = 8 tetrahedra arranged around a common vertex
• Cube = 6 tetrahedra + 1 central octahedron (stella octangula decomposition)
• Icosahedron = 20 tetrahedra arranged around vertices
• Dodecahedron = dual of icosahedron, inherits tetrahedral substructure

The tetrahedron is IRREDUCIBLE, FUNDAMENTAL, and GENERATIVE.
It is the 3D simplex: the minimal volume bounded by flat faces.
• 0-simplex = point
• 1-simplex = line
• 2-simplex = triangle
• 3-simplex = tetrahedron

This is why it represents FIRE—the primal element from which all others emerge.


CORE DIMENSION FORMULAS & DERIVATIONS
══════════════════════════════════════

FACE AREA: $A_{face} = \frac{\sqrt{3}}{4}a^2$
──────────────────────────────────────────────
Each face is an equilateral triangle with side length a.

For equilateral triangle:
• Height of triangle = $\frac{\sqrt{3}}{2}a$
• Area = $\frac{1}{2} \times base \times height$
       = $\frac{1}{2} \times a \times \frac{\sqrt{3}}{2}a$
       = $\frac{\sqrt{3}}{4}a^2$ ✓


SURFACE AREA: $A = 4 \times \frac{\sqrt{3}}{4}a^2 = \sqrt{3}a^2$
───────────────────────────────────────────────────────────────────
Tetrahedron has 4 identical equilateral triangle faces.
Total surface area = $4 \times \frac{\sqrt{3}}{4}a^2 = \sqrt{3}a^2$


HEIGHT: $h = \sqrt{\frac{2}{3}} \times a$
─────────────────────────────────────────
Place tetrahedron with base on xy-plane, apex directly above centroid.

Derivation using Pythagorean theorem in 3D:
1. Centroid of base triangle is at distance r from each vertex
2. For equilateral triangle: $r = \frac{a}{\sqrt{3}}$ (circumradius of triangle)
3. Edge from apex to base vertex: length = a
4. Using Pythagoras: $a^2 = h^2 + r^2$
   $$a^2 = h^2 + \left(\frac{a}{\sqrt{3}}\right)^2$$
   $$a^2 = h^2 + \frac{a^2}{3}$$
   $$h^2 = a^2 - \frac{a^2}{3} = \frac{2a^2}{3}$$
   $$h = \sqrt{\frac{2}{3}} \times a$$ ✓


VOLUME: $V = \frac{a^3}{6\sqrt{2}}$
────────────────────────────────────
Volume of pyramid = $\frac{1}{3} \times base\_area \times height$

For tetrahedron:
$$V = \frac{1}{3} \times \frac{\sqrt{3}}{4}a^2 \times \sqrt{\frac{2}{3}}a$$
$$= \frac{1}{3} \times \frac{\sqrt{3}}{4} \times \sqrt{\frac{2}{3}} \times a^3$$
$$= \frac{1}{12} \times \sqrt{3} \times \sqrt{\frac{2}{3}} \times a^3$$
$$= \frac{1}{12} \times \sqrt{3} \times \frac{\sqrt{2}}{\sqrt{3}} \times a^3$$
$$= \frac{1}{12} \times \sqrt{2} \times a^3$$
$$= \frac{a^3}{6\sqrt{2}}$$ ✓


SPHERE RADII FORMULAS & DERIVATIONS
════════════════════════════════════

INRADIUS (Inscribed Sphere): $r = \frac{a\sqrt{6}}{12} = \frac{a}{2\sqrt{6}}$
──────────────────────────────────────────────────────────────────────────────
The inscribed sphere touches the center of each face.

Derivation using volume-to-surface-area ratio:
For any polyhedron: $r = \frac{3V}{A}$

$$r = \frac{3 \times \frac{a^3}{6\sqrt{2}}}{\sqrt{3}a^2}$$
$$= \frac{3a^3}{6\sqrt{2}} \times \frac{1}{\sqrt{3}a^2}$$
$$= \frac{3a}{6\sqrt{2} \times \sqrt{3}}$$
$$= \frac{a}{2\sqrt{6}}$$
$$= \frac{a\sqrt{6}}{12}$$ ✓

Geometric interpretation:
• Distance from centroid to any face
• Centroid at $\frac{1}{4}$ of height from base
• Inradius = $\frac{1}{4}h$ for tetrahedron
• $r = \frac{1}{4} \times \sqrt{\frac{2}{3}}a = \frac{a\sqrt{6}}{12}$ ✓


MIDRADIUS (Midsphere): $\rho = \frac{a\sqrt{2}}{4} = \frac{a}{2\sqrt{2}}$
─────────────────────────────────────────────────────────────────────────
The midsphere touches the midpoint of each edge.

Derivation via canonical coordinates:
Using canonical vertices at (±1, ±1, ±1) with alternating signs,
the edge length = $2\sqrt{2}$, and edge midpoint is at (0, 0, 1).
Distance from origin = 1.
For general edge length a: scale factor = $\frac{a}{2\sqrt{2}}$
Midradius = $1 \times \frac{a}{2\sqrt{2}} = \frac{a\sqrt{2}}{4}$ ✓


CIRCUMRADIUS (Circumscribed Sphere): $R = \frac{a\sqrt{6}}{4}$
───────────────────────────────────────────────────────────────
The circumscribed sphere passes through all 4 vertices.

Derivation using height and centroid position:
• Centroid is at $\frac{1}{4}h$ from base, or $\frac{3}{4}h$ from apex
• Distance from centroid to apex vertex = R
• $R = \frac{3}{4}h = \frac{3}{4} \times \sqrt{\frac{2}{3}}a$
  $= \frac{3}{4} \times a\sqrt{\frac{2}{3}}$
  $= \frac{3a}{4} \times \frac{\sqrt{2}}{\sqrt{3}}$
  $= \frac{a\sqrt{6}}{4}$ ✓


AHA MOMENT #1: SELF-DUAL PERFECTION
════════════════════════════════════

The tetrahedron is SELF-DUAL: its dual polyhedron is another tetrahedron!

When you connect the face centers of a tetrahedron, you get another
tetrahedron rotated 180° and scaled by 1/3. This creates the "Merkaba"
or "Star Tetrahedron"—two interpenetrating tetrahedra forming a 3D
Star of David.

Only the tetrahedron possesses this perfect self-symmetry among Platonic
solids. All others have distinct duals:
• Cube ↔ Octahedron (reciprocal duals)
• Dodecahedron ↔ Icosahedron (reciprocal duals)
• Tetrahedron ↔ Tetrahedron (SELF-DUAL)

This self-reference is the geometric expression of the alchemical principle
"As within, so without"—the tetrahedron contains its own reflection.


AHA MOMENT #2: THE 1:3 RATIO
═════════════════════════════

The tetrahedron has $\frac{R}{r} = 3$ EXACTLY—the only Platonic solid
with this simple integer ratio!

$$\frac{R}{r} = \frac{\frac{a\sqrt{6}}{4}}{\frac{a\sqrt{6}}{12}} = \frac{a\sqrt{6}}{4} \times \frac{12}{a\sqrt{6}} = \frac{12}{4} = 3$$

All other Platonic solids have irrational R/r ratios:
• Cube: $\frac{R}{r} = \sqrt{3} \approx 1.732$
• Octahedron: $\frac{R}{r} = \sqrt{3} \approx 1.732$
• Dodecahedron: $\frac{R}{r} \approx 1.258$ (φ-based)
• Icosahedron: $\frac{R}{r} \approx 1.258$ (φ-based)

The 3:1 ratio reflects the Trinity principle—three persons in one essence.
The circumsphere (manifestation) is exactly three times the insphere (essence).
This perfect integer relationship makes the tetrahedron the most "pure"
and "simple" of all Platonic solids.


HERMETIC INSIGHT: THE FIRE ELEMENT
═══════════════════════════════════

The tetrahedron represents FIRE in Platonic solid cosmology:

SYMBOLISM:
• 4 triangular faces = upward aspiration, ascent
• Sharpest vertices (largest angular defect = 180°)
• Smallest volume-to-surface ratio (most "surface-like")
• Self-dual (its dual is another tetrahedron, rotated)

SPIRITUAL CORRESPONDENCES:
• Insphere ($r = \frac{a\sqrt{6}}{12}$): The inner flame, spiritual heat
• Midsphere ($\rho = \frac{a\sqrt{2}}{4}$): The radiant boundary
• Circumsphere ($R = \frac{a\sqrt{6}}{4}$): The sphere of emanation

RATIOS: $r : \rho : R = \frac{\sqrt{6}}{12} : \frac{\sqrt{2}}{4} : \frac{\sqrt{6}}{4} = 1 : \sqrt{3} : 3$

DIHEDRAL ANGLE:
• Exactly $\arccos(\frac{1}{3}) \approx 70.53°$
• This is close to the tetrahedral bond angle in chemistry
• sp³ hybridization (methane, diamond lattice)

PACKING DENSITY:
• Cannot fill space (leaves gaps)
• Represents Fire's inability to be "contained"
• Aspires upward, cannot be "stacked" perfectly
"""
    
    def get_derivation_title(self) -> str:
        """Return the title for the derivation dialog."""
        return "Tetrahedron — Fire & Foundation · Mathematical Derivations"
