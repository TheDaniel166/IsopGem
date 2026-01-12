"""
Geometry Pillar — Vault of Hestia Solver.

Bidirectional solver for the Vault of Hestia that converts user input
into Canon-compliant Declarations.

This replaces the old VaultOfHestiaSolidCalculator (now removed) with
Canon-compliant solving that outputs Declarations instead of calling builders directly.

Reference: Hermetic Geometry Canon v1.0, Appendix A — Vault of Hestia
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
    InvariantConstraint,
)

from .geometry_solver import GeometrySolver, PropertyDefinition


# Golden ratio constant
PHI = (1 + math.sqrt(5)) / 2


class VaultOfHestiaSolver(GeometrySolver):
    """
    Bidirectional solver for the Vault of Hestia.
    
    Converts any valid property input into the canonical parameter (side_length),
    then returns a SolveResult that can be used to build a Declaration.
    
    Canonical Parameter: side_length (s)
    
    Relationships:
        - sphere_radius: r = s / (2φ)
        - cube_volume: V_c = s³
        - pyramid_volume: V_p = s³/3
        - sphere_volume: V_s = (4/3)πr³ = (4/3)π(s/2φ)³
        - sphere_surface_area: A_s = 4πr²
        - cube_surface_area: A_c = 6s²
    
    Usage:
        solver = VaultOfHestiaSolver()
        result = solver.solve_from("sphere_volume", 523.6)
        
        if result.ok:
            decl = solver.create_declaration(result.canonical_parameter)
            verdict = engine.validate(decl)
    """
    
    # ─────────────────────────────────────────────────────────────────
    # GeometrySolver Properties
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def dimensional_class(self) -> int:
        """Vault of Hestia is a 3D form."""
        return 3
    
    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "VaultOfHestia"
    
    @property
    def canonical_key(self) -> str:
        return "side_length"
    
    @property
    def supported_keys(self) -> set[str]:
        return {
            "side_length",
            "sphere_radius",
            "cube_volume",
            "cube_surface_area",
            "pyramid_volume",
            "sphere_volume",
            "sphere_surface_area",
        }
    
    def get_editable_properties(self) -> list[PropertyDefinition]:
        """Return editable property definitions for UI (Core properties)."""
        return [
            PropertyDefinition(
                key="side_length",
                label="Side Length (s)",
                unit="units",
                editable=True,
                category="Core",
                tooltip="The edge length of the containing cube (canonical parameter)",
                format_spec=".6f",
                formula=r"s = \text{(canonical parameter)}",
            ),
            PropertyDefinition(
                key="sphere_radius",
                label="Sphere Radius (r)",
                unit="units",
                editable=True,
                category="Core",
                tooltip="Radius of the inscribed sphere: r = s / (2φ)",
                format_spec=".6f",
                formula=r"r = \frac{s}{2\varphi} = \frac{s}{2 \cdot \frac{1+\sqrt{5}}{2}}",
            ),
            PropertyDefinition(
                key="cube_volume",
                label="Cube Volume",
                unit="units³",
                editable=True,
                category="Core",
                tooltip="Volume of the outer cube: V = s³",
                format_spec=".4f",
                formula=r"V_{\text{cube}} = s^3",
            ),
            PropertyDefinition(
                key="sphere_volume",
                label="Sphere Volume",
                unit="units³",
                editable=True,
                category="Core",
                tooltip="Volume of the inscribed sphere: V = (4/3)πr³",
                format_spec=".4f",
                formula=r"V_{\text{sphere}} = \frac{4}{3}\pi r^3 = \frac{4}{3}\pi \left(\frac{s}{2\varphi}\right)^3",
            ),
            PropertyDefinition(
                key="cube_surface_area",
                label="Cube Surface Area",
                unit="units²",
                editable=True,
                category="Core",
                tooltip="Surface area of the outer cube: A = 6s²",
                format_spec=".4f",
                formula=r"A_{\text{cube}} = 6s^2",
            ),
            PropertyDefinition(
                key="pyramid_volume",
                label="Pyramid Volume",
                unit="units³",
                editable=True,
                category="Core",
                tooltip="Volume of the inner pyramid: V = s³/3",
                format_spec=".4f",
                formula=r"V_{\text{pyramid}} = \frac{1}{3} \cdot s^2 \cdot s = \frac{s^3}{3}",
            ),
            PropertyDefinition(
                key="sphere_surface_area",
                label="Sphere Surface Area",
                unit="units²",
                editable=True,
                category="Core",
                tooltip="Surface area of the inscribed sphere: A = 4πr²",
                format_spec=".4f",
                formula=r"A_{\text{sphere}} = 4\pi r^2 = 4\pi \left(\frac{s}{2\varphi}\right)^2",
            ),
        ]
    
    def get_derived_properties(self) -> list[PropertyDefinition]:
        """Return readonly derived property definitions (Advanced properties)."""
        return [
            # Geometric dimensions
            PropertyDefinition(
                key="cube_diagonal",
                label="Cube Diagonal",
                unit="units",
                editable=False,
                readonly=True,
                category="Advanced",
                tooltip="Space diagonal of the cube: d = s√3",
                format_spec=".6f",
                formula=r"d = s\sqrt{3}",
            ),
            PropertyDefinition(
                key="pyramid_slant",
                label="Pyramid Slant Height",
                unit="units",
                editable=False,
                readonly=True,
                category="Advanced",
                tooltip="Slant height of pyramid face",
                format_spec=".6f",
                formula=r"\ell = \sqrt{\left(\frac{s}{2}\right)^2 + s^2} = \frac{s\sqrt{5}}{2}",
            ),
            PropertyDefinition(
                key="pyramid_tsa",
                label="Pyramid Total Surface",
                unit="units²",
                editable=False,
                readonly=True,
                category="Advanced",
                tooltip="Total surface area including base",
                format_spec=".4f",
                formula=r"A_{\text{pyr}} = s^2 + 4 \cdot \frac{1}{2} \cdot s \cdot \ell = s^2 + 2s\ell",
            ),
            # Void calculations (Canon VI)
            PropertyDefinition(
                key="void_cube_sphere",
                label="Void: Cube − Sphere",
                unit="units³",
                editable=False,
                readonly=True,
                category="Void",
                tooltip="Volume between cube and sphere",
                format_spec=".4f",
                formula=r"\Delta V = V_{\text{cube}} - V_{\text{sphere}} = s^3 - \frac{4}{3}\pi r^3",
            ),
            PropertyDefinition(
                key="void_cube_pyramid",
                label="Void: Cube − Pyramid",
                unit="units³",
                editable=False,
                readonly=True,
                category="Void",
                tooltip="Volume between cube and pyramid",
                format_spec=".4f",
                formula=r"\Delta V = V_{\text{cube}} - V_{\text{pyr}} = s^3 - \frac{s^3}{3} = \frac{2s^3}{3}",
            ),
            PropertyDefinition(
                key="void_pyr_sphere",
                label="Void: Pyramid − Sphere",
                unit="units³",
                editable=False,
                readonly=True,
                category="Void",
                tooltip="Volume between pyramid and sphere",
                format_spec=".4f",
                formula=r"\Delta V = V_{\text{pyr}} - V_{\text{sphere}} = \frac{s^3}{3} - \frac{4}{3}\pi r^3",
            ),
            # Ratios and resonance
            PropertyDefinition(
                key="hestia_ratio_3d",
                label="Hestia Ratio (3D)",
                unit="",
                editable=False,
                readonly=True,
                category="Ratio",
                tooltip="Sphere Vol / Cube Vol = π/(6φ³)",
                format_spec=".8f",
                formula=r"\mathcal{H}_{\text{3D}} = \frac{V_{\text{sphere}}}{V_{\text{cube}}} = \frac{\pi}{6\varphi^3}",
            ),
            PropertyDefinition(
                key="inradius_ratio",
                label="Inradius Resonance",
                unit="",
                editable=False,
                readonly=True,
                category="Ratio",
                tooltip="s/(2r) = φ (Golden Ratio)",
                format_spec=".10f",
                formula=r"\rho = \frac{s}{2r} = \varphi = \frac{1 + \sqrt{5}}{2}",
            ),
            PropertyDefinition(
                key="vol_efficiency",
                label="Volume Efficiency",
                unit="",
                editable=False,
                readonly=True,
                category="Ratio",
                tooltip="Sphere Vol / Cube Vol (packing density)",
                format_spec=".6f",
                formula=r"\eta = \frac{V_{\text{sphere}}}{V_{\text{cube}}} = \frac{4\pi r^3}{3s^3}",
            ),
            PropertyDefinition(
                key="phi",
                label="φ (Golden Ratio)",
                unit="",
                editable=False,
                readonly=True,
                category="Constant",
                tooltip="φ = (1 + √5) / 2 ≈ 1.618033988749895",
                format_spec=".15f",
                formula=r"\varphi = \frac{1 + \sqrt{5}}{2} \approx 1.6180339887...",
            ),
        ]
    
    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Solve for side_length given any valid property.
        
        Args:
            key: The property being set
            value: The value entered by the user
        
        Returns:
            SolveResult with the derived side_length and provenance
        """
        if value <= 0:
            return SolveResult.invalid(
                key=key,
                value=value,
                reason="Value must be positive (Canon I.4: Continuity as Ground)"
            )
        
        if key not in self.supported_keys:
            return SolveResult.invalid(
                key=key,
                value=value,
                reason=f"Unknown property: {key}"
            )
        
        s: Optional[float] = None
        formula: str = ""
        intermediates: dict[str, float] = {}
        warnings: list[str] = []
        
        if key == "side_length":
            s = value
            formula = "s = s (identity)"
            
        elif key == "sphere_radius":
            # r = s / (2φ) → s = r × 2φ
            s = value * 2 * PHI
            formula = "s = r × 2φ"
            intermediates["phi"] = PHI
            
        elif key == "cube_volume":
            # V = s³ → s = ∛V
            s = value ** (1/3)
            formula = "s = ∛V_cube"
            
        elif key == "cube_surface_area":
            # A = 6s² → s = √(A/6)
            s = math.sqrt(value / 6)
            formula = "s = √(A_cube / 6)"
            
        elif key == "pyramid_volume":
            # V = s³/3 → s³ = 3V → s = ∛(3V)
            s = (3 * value) ** (1/3)
            formula = "s = ∛(3 × V_pyramid)"
            
        elif key == "sphere_volume":
            # V = (4/3)πr³ → r = ∛(3V / 4π)
            # r = s / (2φ) → s = r × 2φ
            r = (3 * value / (4 * math.pi)) ** (1/3)
            s = r * 2 * PHI
            formula = "r = ∛(3V / 4π); s = r × 2φ"
            intermediates["sphere_radius"] = r
            intermediates["phi"] = PHI
            
        elif key == "sphere_surface_area":
            # A = 4πr² → r = √(A / 4π)
            # r = s / (2φ) → s = r × 2φ
            r = math.sqrt(value / (4 * math.pi))
            s = r * 2 * PHI
            formula = "r = √(A / 4π); s = r × 2φ"
            intermediates["sphere_radius"] = r
            intermediates["phi"] = PHI
        
        if s is None:
            return SolveResult.invalid(key, value, "Solver logic error")
        
        # Compute φ-resonance for validation hint
        r = s / (2 * PHI)
        inradius_resonance = s / (2 * r)  # Should equal φ
        if abs(inradius_resonance - PHI) > 1e-9:
            warnings.append(
                f"Numerical precision: inradius_resonance={inradius_resonance:.10f}, "
                f"expected φ={PHI:.10f}"
            )
        
        return SolveResult.success(
            canonical_parameter=s,
            canonical_key=self.canonical_key,
            provenance=SolveProvenance(
                source_key=key,
                source_value=value,
                formula_used=formula,
                intermediate_values=intermediates,
                assumptions=[
                    "Vault structure: Cube → Pyramid → Sphere",
                    "Sphere inscribed in pyramid, pyramid inscribed in cube",
                    "Pyramid height equals cube side (h = s)",
                ],
            ),
            warnings=warnings,
        )
    
    def get_all_properties(self, side_length: float) -> dict[str, float]:
        """
        Compute all derived properties from side_length.
        
        This is the forward direction, used to populate UI fields.
        Returns ALL properties including advanced/derived ones.
        """
        s = side_length
        r = s / (2 * PHI)
        
        # Core volumes
        cube_vol = s ** 3
        pyramid_vol = s ** 3 / 3
        sphere_vol = (4/3) * math.pi * r ** 3
        
        # Core areas
        cube_area = 6 * s ** 2
        sphere_area = 4 * math.pi * r ** 2
        
        # Advanced dimensions
        cube_diagonal = s * math.sqrt(3)
        # Pyramid slant height: from center of base edge to apex
        # Base is s×s, apex is at height s, so slant = sqrt((s/2)^2 + s^2)
        pyramid_slant = math.sqrt((s/2)**2 + s**2)
        # Pyramid lateral area (4 triangular faces)
        pyramid_lateral_area = 4 * (0.5 * s * pyramid_slant)
        pyramid_tsa = pyramid_lateral_area + s**2  # base area
        
        # Void volumes (Canon VI)
        void_cube_sphere = cube_vol - sphere_vol
        void_cube_pyramid = cube_vol - pyramid_vol
        void_pyr_sphere = pyramid_vol - sphere_vol
        
        # Ratios
        hestia_ratio = sphere_vol / cube_vol  # = π/(6φ³)
        vol_efficiency = sphere_vol / cube_vol
        
        return {
            # Core editable
            "side_length": s,
            "sphere_radius": r,
            "cube_volume": cube_vol,
            "sphere_volume": sphere_vol,
            "cube_surface_area": cube_area,
            "pyramid_volume": pyramid_vol,
            "sphere_surface_area": sphere_area,
            
            # Advanced geometric
            "cube_diagonal": cube_diagonal,
            "pyramid_slant": pyramid_slant,
            "pyramid_tsa": pyramid_tsa,
            "pyramid_height": s,  # Same as side_length
            
            # Void volumes
            "void_cube_sphere": void_cube_sphere,
            "void_cube_pyramid": void_cube_pyramid,
            "void_pyr_sphere": void_pyr_sphere,
            
            # Ratios and constants
            "hestia_ratio_3d": hestia_ratio,
            "inradius_ratio": PHI,  # s/(2r) = φ always
            "vol_efficiency": vol_efficiency,
            "phi": PHI,
            
            # Legacy aliases for compatibility
            "inradius_resonance_phi": PHI,
            "volume_efficiency": vol_efficiency,
        }
    
    def create_declaration(
        self,
        side_length: float,
        *,
        validate_phi: bool = True,
        title: Optional[str] = None,
    ) -> Declaration:
        """
        Create a Canon-compliant Declaration for the Vault of Hestia.
        
        This is the bridge from Solver output to Canon validation.
        
        Args:
            side_length: The canonical parameter
            validate_phi: Whether to include φ-resonance constraint
            title: Custom title for the declaration
        
        Returns:
            A Declaration ready for Canon validation
        """
        forms = [
            Form(
                id="vault",
                kind="VaultOfHestia",
                params={"side_length": side_length},
                symmetry_class="rotational_4",
                curvature_class="variable",
                dimensional_class=3,
                notes="Cube → Pyramid → Sphere with φ mediation",
            ),
        ]
        
        constraints = []
        if validate_phi:
            constraints.append(
                InvariantConstraint(
                    name="phi_resonance",
                    expr={"equals": "phi", "tolerance": 1e-6},
                    scope=["vault"],
                    notes="Inradius resonance should equal φ (golden ratio)",
                )
            )
        
        return Declaration(
            title=title or f"Vault of Hestia (s={side_length:.4f})",
            forms=forms,
            constraints=constraints,
            epsilon=1e-9,
            metadata={
                "canon_ref": "Appendix A — Vault of Hestia",
                "solver": "VaultOfHestiaSolver",
            },
        )
    
    def get_derivation(self) -> str:
        """
        Return the mathematical derivation for the Vault of Hestia.

        This is the sacred geometry commentary explaining why the formulas work.
        """
        return r"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    THE VAULT OF HESTIA — DERIVATIONS                          ║
║                         A 3D Sacred Geometry Form                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝

CONSTRUCTION
════════════
• CUBE with edge length s (the container)
• SQUARE PYRAMID inscribed: base = s×s (cube bottom), height = s (to cube top)
• SPHERE inscribed within the pyramid (tangent to base and 4 faces)

This 3D extension maintains the golden ratio relationship and reveals
profound volumetric sacred geometry!


SPHERE RADIUS: $r = \frac{s}{2\varphi}$
══════════════════════════

The sphere is inscribed in the square pyramid (tangent to base and 4 faces).

For a square pyramid with base side a and height h:
    Inradius formula: $r = \frac{h \cdot a}{a + \ell}$

Where:
    a = base side = s
    h = height = s (pyramid reaches to top of cube)
    ℓ = slant height along face

The slant height from apex to midpoint of base edge:
    $$\ell^2 = h^2 + \left(\frac{a}{2}\right)^2$$
    $$\ell^2 = s^2 + \frac{s^2}{4} = \frac{5s^2}{4}$$
    $$\ell = \frac{s\sqrt{5}}{2}$$

AHA MOMENT #1: The same $\sqrt{5}$ appears in 3D!
This is the SAME value as the 2D triangle leg!

The 2D cross-section through the pyramid apex and perpendicular to any
base edge is the SAME isosceles triangle as the 2D Vault of Hestia!

That triangle has base s, height s, and incircle radius $\frac{s}{2\varphi}$.
Therefore the sphere radius MUST be the same: $r = \frac{s}{2\varphi}$ ✓

AHA MOMENT #2: The 3D structure preserves the 2D golden relationship!
The sphere radius relates to the cube edge by INVERSE PHI, just like
the 2D circle relates to the square!


VOLUME FORMULAS
═══════════════

CUBE VOLUME: $V_{cube} = s^3$
    Standard cube volume.

PYRAMID VOLUME: $V_{pyr} = \frac{1}{3} \times base \times height = \frac{1}{3} \times s^2 \times s = \frac{s^3}{3}$
    The pyramid occupies exactly ONE-THIRD of the cube volume!

SPHERE VOLUME: $$V_{sphere} = \frac{4}{3}\pi r^3 = \frac{4}{3}\pi\left(\frac{s}{2\varphi}\right)^3$$
    $$= \frac{4}{3}\pi \times \frac{s^3}{8\varphi^3} = \frac{\pi s^3}{6\varphi^3}$$


THE HESTIA RATIO (3D)
═════════════════════

The ratio of sphere volume to cube volume:

$$H_{3D} = \frac{V_{sphere}}{V_{cube}} = \frac{\frac{\pi s^3}{6\varphi^3}}{s^3} = \frac{\pi}{6\varphi^3} \approx 0.123605...$$

This is a universal constant depending only on $\pi$ and $\varphi$!


VOID VOLUMES (SACRED SPACES)
════════════════════════════

The "voids" between the nested forms have mystical significance:

VOID: Cube − Sphere = s³ − πs³/(6φ³)
    The space where the sphere DOESN'T touch the cube.

VOID: Cube − Pyramid = s³ − s³/3 = 2s³/3
    Exactly TWO-THIRDS of the cube!

VOID: Pyramid − Sphere = s³/3 − πs³/(6φ³)
    The space within the pyramid but outside the sphere.


THE GOLDEN RATIO CONNECTION
═══════════════════════════

The key relationship: $$\varphi = \frac{1 + \sqrt{5}}{2} \approx 1.618033988749895...$$

From $r = \frac{s}{2\varphi}$, we derive:
    $$s = 2\varphi r$$
    $$\frac{s}{r} = 2\varphi$$

The INRADIUS RESONANCE: $$\frac{s}{2r} = \varphi$$

This means the ratio of the cube side to the sphere diameter
EQUALS THE GOLDEN RATIO! This is the 3D manifestation of the
same divine proportion found in the 2D Vault of Hestia.


HERMETIC INSIGHT
════════════════

"As above, so below; as below, so above."

The Vault of Hestia demonstrates this principle:
• The 2D relationship (circle in triangle in square) extends perfectly to 3D
• The same golden ratio φ governs both dimensions
• The √5 that appears in the 2D construction reappears in the 3D slant height

The three nested forms represent:
• CUBE: The material realm, stability, the four elements
• PYRAMID: Aspiration, the marriage of base (4) and apex (1)
• SPHERE: Perfection, unity, the divine

Their volumetric relationship encodes the proportion between realms.
"""
    
    def get_derivation_title(self) -> str:
        """Return the title for the derivation dialog."""
        return "Vault of Hestia — Sacred Geometry Derivations"