"""
Geometry Pillar — Cube Solver.

Bidirectional solver for regular cube that converts user input
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


# Base constants from CubeSolidService
_BASE_EDGE_LENGTH = 2.0
_BASE_FACE_AREA = 4.0
_BASE_SURFACE_AREA = 24.0
_BASE_VOLUME = 8.0
_BASE_FACE_DIAGONAL = 2.0 * math.sqrt(2.0)
_BASE_SPACE_DIAGONAL = 2.0 * math.sqrt(3.0)
_BASE_INRADIUS = 1.0
_BASE_MIDRADIUS = math.sqrt(2.0)
_BASE_CIRCUMRADIUS = math.sqrt(3.0)
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS

# Face geometry
_BASE_FACE_INRADIUS = 1.0  # For square face: r_f = a/2
_BASE_FACE_CIRCUMRADIUS = math.sqrt(2.0)  # For square face: R_f = a√2/2

# Sphere metrics
_BASE_INSPHERE_SA = 4.0 * math.pi * _BASE_INRADIUS ** 2
_BASE_MIDSPHERE_SA = 4.0 * math.pi * _BASE_MIDRADIUS ** 2
_BASE_CIRCUMSPHERE_SA = 4.0 * math.pi * _BASE_CIRCUMRADIUS ** 2
_BASE_INSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_INRADIUS ** 3
_BASE_MIDSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_MIDRADIUS ** 3
_BASE_CIRCUMSPHERE_VOL = (4.0 / 3.0) * math.pi * _BASE_CIRCUMRADIUS ** 3

# Moment of inertia (k coefficients from platonic_constants)
_MOI_K_SOLID = 1.0 / 6.0  # For uniform density solid cube
_MOI_K_SHELL = 1.0 / 3.0  # For thin shell cube
_BASE_MOI_SOLID = _MOI_K_SOLID * _BASE_VOLUME * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH
_BASE_MOI_SHELL = _MOI_K_SHELL * _BASE_SURFACE_AREA * _BASE_EDGE_LENGTH * _BASE_EDGE_LENGTH


class CubeSolver(GeometrySolver):
    """
    Bidirectional solver for regular cube.
    
    Converts any valid property input into the canonical parameter (edge_length),
    then returns a SolveResult that can be used to build a Declaration.
    
    Canonical Parameter: edge_length (a)
    
    Relationships:
        - face_area: A_f = a²
        - surface_area: A = 6a²
        - volume: V = a³
        - face_diagonal: d_f = a√2
        - space_diagonal: d_s = a√3
        - inradius: r = a/2
        - midradius: ρ = a√2/2
        - circumradius: R = a√3/2
        - All sphere and circumference properties
        - Moment of inertia properties
    
    Usage:
        solver = CubeSolver()
        result = solver.solve_from("volume", 1.0)
        
        if result.ok:
            decl = solver.create_declaration(result.canonical_parameter)
            verdict = engine.validate(decl)
    """
    
    # ─────────────────────────────────────────────────────────────────
    # GeometrySolver Properties
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def dimensional_class(self) -> int:
        """Cube is a 3D form."""
        return 3
    
    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "Cube"
    
    @property
    def canonical_key(self) -> str:
        return "edge_length"
    
    @property
    def supported_keys(self) -> set[str]:
        """Return set of property keys that can be solved from."""
        return {
            "edge_length",
            "face_area",
            "surface_area",
            "volume",
            "face_diagonal",
            "space_diagonal",
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
        """Return property definitions for user-editable fields (22 total)."""
        return [
            PropertyDefinition(
                key="edge_length",
                label="Edge Length (a)",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Length of cube edge: a",
                format_spec=".6f",
                formula=r"a",
            ),
            PropertyDefinition(
                key="face_area",
                label="Face Area",
                unit="units²",
                editable=True,
                category="Surface",
                tooltip="Area of one square face: A_f = a²",
                format_spec=".6f",
                formula=r"A_f = a^2",
            ),
            PropertyDefinition(
                key="surface_area",
                label="Surface Area",
                unit="units²",
                editable=True,
                category="Surface",
                tooltip="Total surface area: A = 6a²",
                format_spec=".6f",
                formula=r"A = 6a^2",
            ),
            PropertyDefinition(
                key="volume",
                label="Volume",
                unit="units³",
                editable=True,
                category="Volume",
                tooltip="Volume: V = a³",
                format_spec=".6f",
                formula=r"V = a^3",
            ),
            PropertyDefinition(
                key="face_diagonal",
                label="Face Diagonal",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Diagonal across square face: d_f = a√2",
                format_spec=".6f",
                formula=r"d_f = a\sqrt{2}",
            ),
            PropertyDefinition(
                key="space_diagonal",
                label="Space Diagonal",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Diagonal through cube: d_s = a√3",
                format_spec=".6f",
                formula=r"d_s = a\sqrt{3}",
            ),
            PropertyDefinition(
                key="inradius",
                label="Inradius (r)",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Inscribed sphere radius: r = a/2",
                format_spec=".6f",
                formula=r"r = \frac{a}{2}",
            ),
            PropertyDefinition(
                key="midradius",
                label="Midsphere Radius (ρ)",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Midsphere radius touching edge midpoints: ρ = a√2/2",
                format_spec=".6f",
                formula=r"\rho = \frac{a\sqrt{2}}{2}",
            ),
            PropertyDefinition(
                key="circumradius",
                label="Circumradius (R)",
                unit="units",
                editable=True,
                category="Spheres",
                tooltip="Circumscribed sphere radius: R = a√3/2",
                format_spec=".6f",
                formula=r"R = \frac{a\sqrt{3}}{2}",
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
                tooltip="Inradius of square face: r_f = a/2",
                format_spec=".6f",
                formula=r"r_f = \frac{a}{2}",
            ),
            PropertyDefinition(
                key="face_circumradius",
                label="Face Circumradius",
                unit="units",
                editable=True,
                category="Face",
                tooltip="Circumradius of square face: R_f = a√2/2",
                format_spec=".6f",
                formula=r"R_f = \frac{a\sqrt{2}}{2}",
            ),
            PropertyDefinition(
                key="insphere_surface_area",
                label="Insphere Surface Area",
                unit="units²",
                editable=True,
                category="Sphere Metrics",
                tooltip="Surface area of inscribed sphere: 4πr²",
                format_spec=".6f",
                formula=r"A_{in} = 4\pi r^2",
            ),
            PropertyDefinition(
                key="insphere_volume",
                label="Insphere Volume",
                unit="units³",
                editable=True,
                category="Sphere Metrics",
                tooltip="Volume of inscribed sphere: (4/3)πr³",
                format_spec=".6f",
                formula=r"V_{in} = \frac{4}{3}\pi r^3",
            ),
            PropertyDefinition(
                key="midsphere_surface_area",
                label="Midsphere Surface Area",
                unit="units²",
                editable=True,
                category="Sphere Metrics",
                tooltip="Surface area of midsphere: 4πρ²",
                format_spec=".6f",
                formula=r"A_{mid} = 4\pi \rho^2",
            ),
            PropertyDefinition(
                key="midsphere_volume",
                label="Midsphere Volume",
                unit="units³",
                editable=True,
                category="Sphere Metrics",
                tooltip="Volume of midsphere: (4/3)πρ³",
                format_spec=".6f",
                formula=r"V_{mid} = \frac{4}{3}\pi \rho^3",
            ),
            PropertyDefinition(
                key="circumsphere_surface_area",
                label="Circumsphere Surface Area",
                unit="units²",
                editable=True,
                category="Sphere Metrics",
                tooltip="Surface area of circumscribed sphere: 4πR²",
                format_spec=".6f",
                formula=r"A_{circ} = 4\pi R^2",
            ),
            PropertyDefinition(
                key="circumsphere_volume",
                label="Circumsphere Volume",
                unit="units³",
                editable=True,
                category="Sphere Metrics",
                tooltip="Volume of circumscribed sphere: (4/3)πR³",
                format_spec=".6f",
                formula=r"V_{circ} = \frac{4}{3}\pi R^3",
            ),
            PropertyDefinition(
                key="moment_inertia_solid",
                label="Moment of Inertia (Solid)",
                unit="units⁵",
                editable=True,
                category="Physics",
                tooltip="Moment of inertia for solid cube about centroid",
                format_spec=".8f",
                formula=r"I_{solid} = \frac{1}{6}ma^2",
            ),
            PropertyDefinition(
                key="moment_inertia_shell",
                label="Moment of Inertia (Shell)",
                unit="units⁴",
                editable=True,
                category="Physics",
                tooltip="Moment of inertia for hollow shell about centroid",
                format_spec=".8f",
                formula=r"I_{shell} = \frac{1}{3}Aa^2",
            ),
        ]
    
    def get_derived_properties(self) -> list[PropertyDefinition]:
        """Return readonly derived property definitions (topology/constants only)."""
        return [
            PropertyDefinition(
                key="faces",
                label="Faces",
                unit="",
                editable=False,
                readonly=True,
                category="Topology",
                tooltip="Number of faces (constant)",
                format_spec=".0f",
            ),
            PropertyDefinition(
                key="edges",
                label="Edges",
                unit="",
                editable=False,
                readonly=True,
                category="Topology",
                tooltip="Number of edges (constant)",
                format_spec=".0f",
            ),
            PropertyDefinition(
                key="vertices",
                label="Vertices",
                unit="",
                editable=False,
                readonly=True,
                category="Topology",
                tooltip="Number of vertices (constant)",
                format_spec=".0f",
            ),
            PropertyDefinition(
                key="face_sides",
                label="Face Sides",
                unit="",
                editable=False,
                readonly=True,
                category="Topology",
                tooltip="Number of sides per face",
                format_spec=".0f",
            ),
            PropertyDefinition(
                key="vertex_valence",
                label="Vertex Valence",
                unit="",
                editable=False,
                readonly=True,
                category="Topology",
                tooltip="Number of edges meeting at each vertex",
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
                reason=f"Property '{key}' not supported for Cube"
            )
        
        # Solve using scaling formula: scale = (value / base_value) ** (1.0 / power)
        # then edge_length = scale * _BASE_EDGE_LENGTH
        
        edge_length: Optional[float] = None
        formula = ""
        
        # Core dimensions
        if key == "edge_length":
            edge_length = value
            formula = "a = input"
        elif key == "face_area":
            # A_f = a² → a = √A_f
            edge_length = math.sqrt(value)
            formula = "a = √A_f"
        elif key == "surface_area":
            # A = 6a² → a = √(A/6)
            edge_length = math.sqrt(value / 6.0)
            formula = "a = √(A/6)"
        elif key == "volume":
            # V = a³ → a = ∛V
            edge_length = value ** (1.0 / 3.0)
            formula = "a = ∛V"
        elif key == "face_diagonal":
            # d_f = a√2 → a = d_f/√2
            edge_length = value / math.sqrt(2.0)
            formula = "a = d_f/√2"
        elif key == "space_diagonal":
            # d_s = a√3 → a = d_s/√3
            edge_length = value / math.sqrt(3.0)
            formula = "a = d_s/√3"
        
        # Sphere radii
        elif key == "inradius":
            # r = a/2 → a = 2r
            edge_length = value * 2.0
            formula = "a = 2r"
        elif key == "midradius":
            # ρ = a√2/2 → a = 2ρ/√2 = ρ√2
            edge_length = value * math.sqrt(2.0)
            formula = "a = ρ√2"
        elif key == "circumradius":
            # R = a√3/2 → a = 2R/√3 = 2R√3/3
            edge_length = value * 2.0 / math.sqrt(3.0)
            formula = "a = 2R/√3"
        
        # Circumferences
        elif key == "incircle_circumference":
            # C = 2πr, r = a/2 → a = C/π
            edge_length = value / math.pi
            formula = "a = C_in/π"
        elif key == "midsphere_circumference":
            # C = 2πρ, ρ = a√2/2 → a = C/(π√2)
            edge_length = value / (math.pi * math.sqrt(2.0))
            formula = "a = C_mid/(π√2)"
        elif key == "circumcircle_circumference":
            # C = 2πR, R = a√3/2 → a = C/(π√3)
            edge_length = value / (math.pi * math.sqrt(3.0))
            formula = "a = C_circ/(π√3)"
        
        # Face geometry
        elif key == "face_inradius":
            # r_f = a/2 → a = 2r_f
            edge_length = value * 2.0
            formula = "a = 2r_f"
        elif key == "face_circumradius":
            # R_f = a√2/2 → a = R_f√2
            edge_length = value * math.sqrt(2.0)
            formula = "a = R_f√2"
        
        # Sphere surface areas (4πr²)
        elif key == "insphere_surface_area":
            # A_in = 4πr², r = a/2 → a = 2√(A_in/(4π)) = √(A_in/π)
            r = math.sqrt(value / (4.0 * math.pi))
            edge_length = r * 2.0
            formula = "a = 2r where r = √(A_in/(4π))"
        elif key == "midsphere_surface_area":
            # A_mid = 4πρ², ρ = a√2/2 → a = √(A_mid/π) / √2
            rho = math.sqrt(value / (4.0 * math.pi))
            edge_length = rho * math.sqrt(2.0)
            formula = "a = ρ√2 where ρ = √(A_mid/(4π))"
        elif key == "circumsphere_surface_area":
            # A_circ = 4πR², R = a√3/2 → a = 2R/√3 where R = √(A_circ/(4π))
            R_circ = math.sqrt(value / (4.0 * math.pi))
            edge_length = R_circ * 2.0 / math.sqrt(3.0)
            formula = "a = 2R/√3 where R = √(A_circ/(4π))"
        
        # Sphere volumes ((4/3)πr³)
        elif key == "insphere_volume":
            # V_in = (4/3)πr³, r = a/2 → a = 2r where r = ∛(3V_in/(4π))
            r = (3.0 * value / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = r * 2.0
            formula = "a = 2r where r = ∛(3V_in/(4π))"
        elif key == "midsphere_volume":
            # V_mid = (4/3)πρ³, ρ = a√2/2 → a = ρ√2 where ρ = ∛(3V_mid/(4π))
            rho = (3.0 * value / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = rho * math.sqrt(2.0)
            formula = "a = ρ√2 where ρ = ∛(3V_mid/(4π))"
        elif key == "circumsphere_volume":
            # V_circ = (4/3)πR³, R = a√3/2 → a = 2R/√3 where R = ∛(3V_circ/(4π))
            R_circ = (3.0 * value / (4.0 * math.pi)) ** (1.0 / 3.0)
            edge_length = R_circ * 2.0 / math.sqrt(3.0)
            formula = "a = 2R/√3 where R = ∛(3V_circ/(4π))"
        
        # Moments of inertia
        elif key == "moment_inertia_solid":
            # I = k*V*a², V = a³ → I = k*a⁵ → a = (I/k)^(1/5)
            edge_length = (value / _MOI_K_SOLID / _BASE_VOLUME) ** (1.0 / 5.0) * _BASE_EDGE_LENGTH
            formula = "a = (I/k)^(1/5) where k = 1/6"
        elif key == "moment_inertia_shell":
            # I = k*A*a², A = 6a² → I = k*6a⁴ → a = (I/(6k))^(1/4)
            edge_length = (value / _MOI_K_SHELL / _BASE_SURFACE_AREA) ** (1.0 / 4.0) * _BASE_EDGE_LENGTH
            formula = "a = (I/(6k))^(1/4) where k = 1/3"
        
        if edge_length is None or not math.isfinite(edge_length) or edge_length <= 0:
            return SolveResult.invalid(key, value, f"Solver produced invalid edge_length for '{key}'")
        
        return SolveResult.success(
            canonical_parameter=edge_length,
            canonical_key=self.canonical_key,
            provenance=SolveProvenance(
                source_key=key,
                source_value=value,
                formula_used=formula,
                assumptions=["Regular cube", "All edges equal", "All angles 90°"],
            ),
        )
    
    def get_all_properties(self, canonical_value: float) -> dict[str, float]:
        """
        Compute all geometric metrics for a cube from edge length.

        CORE DIMENSION FORMULAS & DERIVATIONS:
        ========================================

        Face Area: A_face = a²
        -----------------------
        Each face is a square with side length a.
        Area of square = side² = a²

        Surface Area: A = 6a²
        ---------------------
        Cube has 6 identical square faces.
        Total surface area = 6 × a² = 6a²

        Volume: V = a³
        ---------------
        Volume of rectangular prism = length × width × height
        For cube: all dimensions equal = a × a × a = a³

        Face Diagonal: d_face = a√2
        ----------------------------
        Diagonal of square face using Pythagorean theorem:
        d² = a² + a² = 2a²
        d = a√2

        Space Diagonal: d_space = a√3
        ------------------------------
        Diagonal through cube connecting opposite vertices.
        Using 3D Pythagorean theorem:
        d² = a² + a² + a² = 3a²
        d = a√3

        AHA MOMENT #1: PERFECT SYMMETRY
        =================================
        The cube is the ONLY Platonic solid where all face angles, dihedral angles,
        and coordinate alignments are 90°—the angle of perfect orthogonality.
        
        This creates three independent, perpendicular axes of fourfold rotational
        symmetry (through opposite face centers). No other Platonic solid achieves
        this perfect Cartesian alignment.
        
        The cube is the geometric embodiment of the coordinate system itself:
        - 3 pairs of parallel faces → 3 perpendicular planes
        - 8 vertices → 8 octants of 3D space (±x, ±y, ±z combinations)
        - 12 edges → 12 coordinate-aligned segments (4 per axis)

        SPHERE RADII FORMULAS & DERIVATIONS:
        =====================================

        Inradius (Inscribed Sphere): r = a/2
        -------------------------------------
        The inscribed sphere touches the center of each face.
        Distance from cube center to face center = half edge length.
        r = a/2

        Geometric Intuition:
        - Place cube with vertices at (±a/2, ±a/2, ±a/2)
        - Center at origin (0,0,0)
        - Face centers at (±a/2, 0, 0), (0, ±a/2, 0), (0, 0, ±a/2)
        - Distance from origin to any face center = a/2 ✓

        Derivation using volume-to-surface-area ratio:
        For any polyhedron with an inscribed sphere: r = 3V/A
        
        r = 3 × a³ / (6a²)
          = 3a³ / 6a²
          = a/2 ✓
        
        This confirms the geometric result and shows the cube's elegant simplicity:
        the ratio 3V/A reduces perfectly to half the edge length.

        Midradius (Midsphere): ρ = a√2/2
        ---------------------------------
        The midsphere touches the midpoint of each edge.
        
        Edge midpoint calculation (for canonical cube centered at origin):
        Midpoint of bottom front edge: (0, -a/2, -a/2)
        Distance from origin = √(0² + (a/2)² + (a/2)²)
                            = √(a²/4 + a²/4)
                            = √(a²/2)
                            = a/√2
                            = a√2/2 ✓

        Rationalized form:
        ρ = a/√2 × (√2/√2) = a√2/2
        
        Numerical value: ρ ≈ 0.7071067812a

        Alternative derivation via face diagonal:
        - Face diagonal = a√2
        - Edge midpoint lies at distance (face_diagonal / 2) from center
        - ρ = a√2 / 2 ✓

        Circumradius (Circumscribed Sphere): R = a√3/2
        -----------------------------------------------
        The circumscribed sphere passes through all 8 vertices.
        
        Canonical vertex at (a/2, a/2, a/2):
        Distance from origin = √((a/2)² + (a/2)² + (a/2)²)
                            = √(3 × a²/4)
                            = √(3a²/4)
                            = a√3/2 ✓

        Rationalized form already optimal.
        Numerical value: R ≈ 0.8660254038a

        Alternative Derivation via Space Diagonal:
        - Space diagonal connects opposite vertices
        - Length = a√3 (derived above)
        - Circumradius = half the space diagonal = a√3/2 ✓

        SPHERE RATIO RELATIONSHIPS:
        ===========================
        r : ρ : R = a/2 : a√2/2 : a√3/2
                   = 1 : √2 : √3
        
        Key ratios:
        - R/r = (a√3/2) / (a/2) = √3 ≈ 1.732
          The circumradius is exactly √3 times the inradius!
        - ρ/r = (a√2/2) / (a/2) = √2 ≈ 1.414
        - R/ρ = (a√3/2) / (a√2/2) = √3/√2 = √(3/2) ≈ 1.225

        AHA MOMENT #2: PYTHAGOREAN PROGRESSION
        ========================================
        The cube's three radii form a Pythagorean sequence:
        
        r : ρ : R = 1 : √2 : √3
        
        These are the square roots of the first three integers—the most fundamental
        sequence in geometry! This pattern reflects the cube's dimensional hierarchy:
        - Inradius (r = a/2): Distance along ONE axis (1D) → factor of √1 = 1
        - Midradius (ρ = a√2/2): Distance across TWO axes (2D) → factor of √2
        - Circumradius (R = a√3/2): Distance through THREE axes (3D) → factor of √3
        
        Each radius encodes the dimensionality it spans. No other Platonic solid
        exhibits such a clean progression from 1D through 3D.

        Dihedral Angle: 90° (π/2 radians)
        ==================================
        The dihedral angle is the angle between two adjacent faces along a shared edge.
        
        For the cube, this is trivially 90° because all faces are perpendicular to
        each other by construction (orthogonal coordinate planes).
        
        Formal derivation via face normals:
        Consider two adjacent square faces:
        - Bottom face (z = -a/2): normal = (0, 0, -1)
        - Front face (y = -a/2): normal = (0, -1, 0)
        
        Dot product of outward normals:
        (0, 0, -1) · (0, -1, 0) = 0
        
        Angle between normals: arccos(0) = 90°
        
        The dihedral angle is π minus the angle between outward normals:
        θ = π - π/2 = π/2 = 90° ✓

        AHA MOMENT #3: THE ONLY RIGHT-ANGLED PLATONIC SOLID
        =====================================================
        The cube is the ONLY Platonic solid with a right-angle (90°) dihedral.
        
        All other Platonic solids have acute or obtuse dihedrals:
        - Tetrahedron: ≈ 70.53° (acute)
        - Octahedron: ≈ 109.47° (obtuse)
        - Dodecahedron: ≈ 116.57° (obtuse)
        - Icosahedron: ≈ 138.19° (obtuse)
        
        The 90° dihedral is the geometric signature of the cube's space-filling
        property: only right angles allow perfect tessellation with no gaps.
        This makes the cube the ONLY Platonic solid that can tile 3D space.
        
        The cube is the "building block" of reality—literally!

        HERMETIC NOTE - THE EARTH ELEMENT:
        ====================================
        The cube represents EARTH in Platonic solid cosmology:

        Symbolism:
        - 6 faces = 6 directions of space (±x, ±y, ±z) = perfect containment
        - 90° angles everywhere = absolute stability and grounding
        - Packing density = 1.0 (fills space perfectly, no voids)
        - Only space-filling Platonic solid = foundation of all structure
        - Dual to octahedron (Air) = Earth as complement to Air

        Spiritual Correspondences:
        - Insphere (r = a/2): The kernel, the seed, potential compressed to unity
        - Midsphere (ρ = a√2/2): The growing boundary, expansion into 2D plane
        - Circumsphere (R = a√3/2): Full manifestation, actualization in 3D space

        The 1:√2:√3 progression encodes the unfolding of dimensionality:
        - Unity (√1) → the point (0D principle)
        - Duality (√2) → the diagonal (1D + 1D = 2D surface)
        - Trinity (√3) → the body (1D + 1D + 1D = 3D volume)

        Connection to Octahedron (Dual):
        - Cube vertices → Octahedron face centers
        - Cube face centers → Octahedron vertices
        - Cube edges → Octahedron edges (both have 12)
        
        This duality expresses the hermetic axiom: "As above, so below."
        Earth (Cube) and Air (Octahedron) are reciprocal manifestations—
        one dense and filling, the other sparse and flowing.

        Packing & Crystallography:
        - The cube is the fundamental unit of the cubic lattice
        - Salt crystals (NaCl), galena (PbS), pyrite (FeS₂) all form cubic structures
        - The physical universe's most stable configuration
        - Represents the principle of ORDER imposed on chaos
        """
        a = canonical_value
        
        # Core dimensions
        face_area = a ** 2
        surface_area = 6.0 * a ** 2
        volume = a ** 3
        face_diagonal = a * math.sqrt(2.0)
        space_diagonal = a * math.sqrt(3.0)
        
        # Sphere radii
        inradius = a / 2.0
        midradius = a * math.sqrt(2.0) / 2.0
        circumradius = a * math.sqrt(3.0) / 2.0
        
        # Circumferences
        incircle_circ = 2.0 * math.pi * inradius
        midsphere_circ = 2.0 * math.pi * midradius
        circumcircle_circ = 2.0 * math.pi * circumradius
        
        # Face geometry
        face_inradius = a / 2.0
        face_circumradius = a * math.sqrt(2.0) / 2.0
        
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
            "face_area": face_area,
            "surface_area": surface_area,
            "volume": volume,
            "face_diagonal": face_diagonal,
            "space_diagonal": space_diagonal,
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
            "faces": 6.0,
            "edges": 12.0,
            "vertices": 8.0,
            "face_sides": 4.0,
            "vertex_valence": 3.0,
            
            # Angles (constants)
            "dihedral_angle_deg": 90.0,
            "solid_angle_sr": 1.5707963268,  # π/2
            
            # Quality metrics
            "sphericity": sphericity,
            "isoperimetric_quotient": isoperimetric,
            "surface_to_volume_ratio": surface_to_volume,
            
            # Advanced constants
            "angular_defect_vertex_deg": 90.0,
            "euler_characteristic": 2.0,
            "packing_density": 1.0,  # Perfect space-filling
            "symmetry_group_order": 48.0,
            "rotational_symmetry_order": 24.0,
        }
    
    def create_declaration(
        self,
        canonical_value: float,
        *,
        title: Optional[str] = None,
    ) -> Declaration:
        """
        Create a Canon-compliant Declaration for the Cube.
        
        Args:
            canonical_value: The canonical parameter (edge_length)
            title: Custom title for the declaration
        
        Returns:
            A Declaration ready for Canon validation
        """
        forms = [
            Form(
                id="cube",
                kind="Cube",
                params={"edge_length": canonical_value},
                symmetry_class="octahedral",
                curvature_class="planar",
                dimensional_class=3,
                notes="Regular cube - Earth element, space-filling solid",
            ),
        ]
        
        return Declaration(
            title=title or f"Cube (a={canonical_value:.4f})",
            forms=forms,
            constraints=[],
            metadata={"description": "Regular cube with 6 square faces and perfect right angles"},
        )
    
    def get_derivation(self) -> str:
        """
        Return the mathematical derivation for the Cube.
        
        This is the sacred geometry commentary explaining why the formulas work.
        """
        return r"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      THE CUBE — EARTH & STABILITY                             ║
║                        The Foundation of Space                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

PERFECT SYMMETRY
════════════════

The cube is the ONLY Platonic solid where all face angles, dihedral angles,
and coordinate alignments are 90°—the angle of perfect orthogonality.

This creates three independent, perpendicular axes of fourfold rotational
symmetry (through opposite face centers). No other Platonic solid achieves
this perfect Cartesian alignment.

The cube is the geometric embodiment of the coordinate system itself:
• 3 pairs of parallel faces → 3 perpendicular planes
• 8 vertices → 8 octants of 3D space (±x, ±y, ±z combinations)
• 12 edges → 12 coordinate-aligned segments (4 per axis)


CORE DIMENSION FORMULAS & DERIVATIONS
══════════════════════════════════════

FACE AREA: $A_{face} = a^2$
──────────────────────────────
Each face is a square with side length a.
Area of square = side² = a²

SURFACE AREA: $A = 6a^2$
─────────────────────────
Cube has 6 identical square faces.
Total surface area = 6 × a² = 6a²

VOLUME: $V = a^3$
─────────────────
Volume of rectangular prism = length × width × height
For cube: all dimensions equal = a × a × a = a³

FACE DIAGONAL: $d_{face} = a\sqrt{2}$
──────────────────────────────────────
Diagonal of square face using Pythagorean theorem:
$$d^2 = a^2 + a^2 = 2a^2$$
$$d = a\sqrt{2}$$

SPACE DIAGONAL: $d_{space} = a\sqrt{3}$
────────────────────────────────────────
Diagonal through cube connecting opposite vertices.
Using 3D Pythagorean theorem:
$$d^2 = a^2 + a^2 + a^2 = 3a^2$$
$$d = a\sqrt{3}$$


SPHERE RADII FORMULAS & DERIVATIONS
════════════════════════════════════

INRADIUS (Inscribed Sphere): $r = \frac{a}{2}$
───────────────────────────────────────────────
The inscribed sphere touches the center of each face.
Distance from cube center to face center = half edge length.

Geometric Intuition:
• Place cube with vertices at (±a/2, ±a/2, ±a/2)
• Center at origin (0,0,0)
• Face centers at (±a/2, 0, 0), (0, ±a/2, 0), (0, 0, ±a/2)
• Distance from origin to any face center = a/2 ✓

Derivation using volume-to-surface-area ratio:
For any polyhedron with an inscribed sphere: r = 3V/A

$$r = \frac{3 \times a^3}{6a^2} = \frac{3a^3}{6a^2} = \frac{a}{2}$$ ✓

This confirms the geometric result and shows the cube's elegant simplicity:
the ratio 3V/A reduces perfectly to half the edge length.

MIDRADIUS (Midsphere): $\rho = \frac{a\sqrt{2}}{2}$
────────────────────────────────────────────────────
The midsphere touches the midpoint of each edge.

Edge midpoint calculation (for canonical cube centered at origin):
Midpoint of bottom front edge: (0, -a/2, -a/2)
Distance from origin:
$$= \sqrt{0^2 + (a/2)^2 + (a/2)^2}$$
$$= \sqrt{a^2/4 + a^2/4} = \sqrt{a^2/2}$$
$$= \frac{a}{\sqrt{2}} = \frac{a\sqrt{2}}{2}$$ ✓

Alternative derivation via face diagonal:
• Face diagonal = a√2
• Edge midpoint lies at distance (face_diagonal / 2) from center
• ρ = a√2 / 2 ✓

CIRCUMRADIUS (Circumscribed Sphere): $R = \frac{a\sqrt{3}}{2}$
───────────────────────────────────────────────────────────────
The circumscribed sphere passes through all 8 vertices.

Canonical vertex at (a/2, a/2, a/2):
Distance from origin:
$$= \sqrt{(a/2)^2 + (a/2)^2 + (a/2)^2}$$
$$= \sqrt{3 \times a^2/4} = \sqrt{3a^2/4}$$
$$= \frac{a\sqrt{3}}{2}$$ ✓

Alternative Derivation via Space Diagonal:
• Space diagonal connects opposite vertices
• Length = a√3 (derived above)
• Circumradius = half the space diagonal = a√3/2 ✓


AHA MOMENT #1: PYTHAGOREAN PROGRESSION
═══════════════════════════════════════

The cube's three radii form a Pythagorean sequence:

$$r : \rho : R = \frac{a}{2} : \frac{a\sqrt{2}}{2} : \frac{a\sqrt{3}}{2} = 1 : \sqrt{2} : \sqrt{3}$$

These are the square roots of the first three integers—the most fundamental
sequence in geometry! This pattern reflects the cube's dimensional hierarchy:
• Inradius (r = a/2): Distance along ONE axis (1D) → factor of √1 = 1
• Midradius (ρ = a√2/2): Distance across TWO axes (2D) → factor of √2
• Circumradius (R = a√3/2): Distance through THREE axes (3D) → factor of √3

Each radius encodes the dimensionality it spans. No other Platonic solid
exhibits such a clean progression from 1D through 3D.

Key ratios:
• $\frac{R}{r} = \frac{a\sqrt{3}/2}{a/2} = \sqrt{3} \approx 1.732$
  The circumradius is exactly √3 times the inradius!
• $\frac{\rho}{r} = \frac{a\sqrt{2}/2}{a/2} = \sqrt{2} \approx 1.414$
• $\frac{R}{\rho} = \frac{a\sqrt{3}/2}{a\sqrt{2}/2} = \sqrt{3/2} \approx 1.225$


AHA MOMENT #2: THE ONLY RIGHT-ANGLED PLATONIC SOLID
═════════════════════════════════════════════════════

The cube is the ONLY Platonic solid with a right-angle (90°) dihedral.

All other Platonic solids have acute or obtuse dihedrals:
• Tetrahedron: ≈ 70.53° (acute)
• Octahedron: ≈ 109.47° (obtuse)
• Dodecahedron: ≈ 116.57° (obtuse)
• Icosahedron: ≈ 138.19° (obtuse)

The 90° dihedral is the geometric signature of the cube's space-filling
property: only right angles allow perfect tessellation with no gaps.
This makes the cube the ONLY Platonic solid that can tile 3D space.

The cube is the "building block" of reality—literally!


HERMETIC INSIGHT: THE EARTH ELEMENT
════════════════════════════════════

The cube represents EARTH in Platonic solid cosmology:

SYMBOLISM:
• 6 faces = 6 directions of space (±x, ±y, ±z) = perfect containment
• 90° angles everywhere = absolute stability and grounding
• Packing density = 1.0 (fills space perfectly, no voids)
• Only space-filling Platonic solid = foundation of all structure
• Dual to octahedron (Air) = Earth as complement to Air

SPIRITUAL CORRESPONDENCES:
• Insphere ($r = \frac{a}{2}$): The kernel, the seed, potential compressed
• Midsphere ($\rho = \frac{a\sqrt{2}}{2}$): The growing boundary, expansion into 2D plane
• Circumsphere ($R = \frac{a\sqrt{3}}{2}$): Full manifestation, actualization in 3D space

The 1:√2:√3 progression encodes the unfolding of dimensionality:
• Unity (√1) → the point (0D principle)
• Duality (√2) → the diagonal (1D + 1D = 2D surface)
• Trinity (√3) → the body (1D + 1D + 1D = 3D volume)

CONNECTION TO OCTAHEDRON (DUAL):
• Cube vertices → Octahedron face centers
• Cube face centers → Octahedron vertices
• Cube edges → Octahedron edges (both have 12)

This duality expresses the hermetic axiom: "As above, so below."
Earth (Cube) and Air (Octahedron) are reciprocal manifestations—
one dense and filling, the other sparse and flowing.

PACKING & CRYSTALLOGRAPHY:
• The cube is the fundamental unit of the cubic lattice
• Salt crystals (NaCl), galena (PbS), pyrite (FeS₂) all form cubic structures
• The physical universe's most stable configuration
• Represents the principle of ORDER imposed on chaos
"""
    
    def get_derivation_title(self) -> str:
        """Return the title for the derivation dialog."""
        return "Cube — Earth & Stability · Mathematical Derivations"
