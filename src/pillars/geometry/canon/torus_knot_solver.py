"""
Geometry Pillar — Torus Knot Solver.

Bidirectional solver for (p, q) torus knots that converts user inputs
into Canon-compliant declarations while preserving the full mathematical
and hermetic derivations from the legacy torus knot calculator.

Reference: ADR-012 — Complete Canon Migration
Reference: ADR-010 — Canon DSL Adoption
Reference: ADR-011 — Unified Geometry Viewer
"""

from __future__ import annotations

import math
from math import gcd
from typing import Any, Dict

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition
from ..services.torus_knot_solid import TorusKnotMetrics, TorusKnotSolidService


class TorusKnotSolver(GeometrySolver):
    """Bidirectional solver for (p, q) torus knots."""

    def __init__(self) -> None:
        self._state: Dict[str, float] = {
            "p": 2.0,
            "q": 3.0,
            "major_radius": 3.0,
            "minor_radius": 1.0,
            "tube_radius": 0.4,
        }

    # ── GeometrySolver properties ──────────────────────────────────────────
    @property
    def dimensional_class(self) -> int:
        return 3

    @property
    def form_type(self) -> str:
        return "TorusKnot"

    @property
    def canonical_key(self) -> str:
        # Store the full parameter set as a canonical dict
        return "torus_knot"

    @property
    def supported_keys(self) -> set[str]:
        return {"p", "q", "major_radius", "minor_radius", "tube_radius"}

    # ── Property metadata for UI ──────────────────────────────────────────
    def get_editable_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="p",
                label="P (Lobes)",
                unit="cycles",
                editable=True,
                tooltip="Number of toroidal windings (p > 0, integer)",
                format_spec=".0f",
                category="Core",
            ),
            PropertyDefinition(
                key="q",
                label="Q (Twists)",
                unit="cycles",
                editable=True,
                tooltip="Number of poloidal twists (q > 0, integer)",
                format_spec=".0f",
                category="Core",
            ),
            PropertyDefinition(
                key="major_radius",
                label="Major Radius (R)",
                unit="units",
                editable=True,
                tooltip="Distance from torus center to tube center",
                format_spec=".6f",
                category="Core",
            ),
            PropertyDefinition(
                key="minor_radius",
                label="Minor Radius (r)",
                unit="units",
                editable=True,
                tooltip="Tube radius of the ambient torus",
                format_spec=".6f",
                category="Core",
            ),
            PropertyDefinition(
                key="tube_radius",
                label="Tube Radius",
                unit="units",
                editable=True,
                tooltip="Radius of the tube drawn around the knot curve",
                format_spec=".6f",
                category="Core",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        return [
            PropertyDefinition(
                key="major_minor_ratio",
                label="R/r Ratio",
                unit="",
                editable=False,
                readonly=True,
                tooltip="Major to minor radius ratio controlling torus family",
                format_spec=".6f",
                category="Derived",
            ),
            PropertyDefinition(
                key="arc_length",
                label="Arc Length",
                unit="units",
                editable=False,
                readonly=True,
                tooltip="Numerically integrated arc length of the knot",
                format_spec=".6f",
                category="Derived",
            ),
            PropertyDefinition(
                key="approx_surface_area",
                label="Approx. Surface Area",
                unit="units²",
                editable=False,
                readonly=True,
                tooltip="Tubular surface area (small-tube approximation)",
                format_spec=".6f",
                category="Derived",
            ),
            PropertyDefinition(
                key="approx_volume",
                label="Approx. Volume",
                unit="units³",
                editable=False,
                readonly=True,
                tooltip="Tubular volume (small-tube approximation)",
                format_spec=".6f",
                category="Derived",
            ),
            PropertyDefinition(
                key="major_circumference",
                label="Major Circumference",
                unit="units",
                editable=False,
                readonly=True,
                tooltip="Circumference of the major circle (2πR)",
                format_spec=".6f",
                category="Derived",
            ),
            PropertyDefinition(
                key="minor_circumference",
                label="Minor Circumference",
                unit="units",
                editable=False,
                readonly=True,
                tooltip="Circumference of the minor circle (2πr)",
                format_spec=".6f",
                category="Derived",
            ),
            PropertyDefinition(
                key="gcd",
                label="gcd(p, q)",
                unit="",
                editable=False,
                readonly=True,
                tooltip="If gcd > 1 the curve is a link with multiple components",
                format_spec=".0f",
                category="Derived",
            ),
        ]

    # ── Solving & computation ─────────────────────────────────────────────
    def solve_from(self, key: str, value: float) -> SolveResult:
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for torus knot")

        canonical = self._state.copy()

        if key in {"p", "q"}:
            if value <= 0:
                return SolveResult.invalid(key, value, "p and q must be positive integers")
            canonical[key] = float(int(value))
        else:
            if value <= 0:
                return SolveResult.invalid(key, value, "Radii must be positive")
            canonical[key] = float(value)

        self._state = canonical

        d = gcd(int(canonical["p"]), int(canonical["q"]))
        warnings: list[str] = []
        if d > 1:
            warnings.append(
                f"gcd(p, q) = {d}; curve is a {d}-component torus link instead of a prime knot"
            )

        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=SolveProvenance(
                source_key=key,
                source_value=value,
                formula_used="Direct parameter assignment (no inversion needed)",
                intermediate_values={"p": canonical["p"], "q": canonical["q"]},
                assumptions=["All radii > 0", "p and q are treated as integers"],
            ),
            warnings=warnings,
        )

    def get_all_properties(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._normalize_canonical(canonical_value)
        metrics = self._compute_metrics(
            int(canonical["p"]),
            int(canonical["q"]),
            canonical["major_radius"],
            canonical["minor_radius"],
            canonical["tube_radius"],
        )

        ratio = canonical["major_radius"] / canonical["minor_radius"] if canonical["minor_radius"] else math.inf
        return {
            "p": canonical["p"],
            "q": canonical["q"],
            "major_radius": canonical["major_radius"],
            "minor_radius": canonical["minor_radius"],
            "tube_radius": canonical["tube_radius"],
            "major_minor_ratio": ratio,
            "arc_length": metrics.arc_length,
            "approx_surface_area": metrics.approx_surface_area,
            "approx_volume": metrics.approx_volume,
            "major_circumference": 2 * math.pi * canonical["major_radius"],
            "minor_circumference": 2 * math.pi * canonical["minor_radius"],
            "gcd": float(gcd(int(canonical["p"]), int(canonical["q"]))),
        }

    @staticmethod
    def _compute_metrics(p: int, q: int, R: float, r: float, tube_r: float) -> TorusKnotMetrics:
        """
        Compute all geometric metrics for a (p,q)-torus knot.

        DERIVATIONS:
        ===========

        Parametric Definition:
        ----------------------
        A (p,q)-torus knot is a closed curve that winds p times around the
        major axis and q times around the minor axis of a torus before closing.

        Standard Parameterization (t ∈ [0, 2π]):
        x(t) = (R + r·cos(q·t))·cos(p·t)
        y(t) = (R + r·cos(q·t))·sin(p·t)
        z(t) = r·sin(q·t)

        Where:
        - p: Number of lobes (toroidal windings)
        - q: Number of twists (poloidal windings)
        - R: Major radius of ambient torus
        - r: Minor radius of ambient torus
        - tube_r: Radius of tube around the knot curve

        The curve closes after traveling 2π because:
        - p·(2π) = 2πp (p full rotations around major axis)
        - q·(2π) = 2πq (q full rotations around minor axis)

        Topology:
        ---------
        **Knot Type**: The (p,q)-torus knot is a **prime knot** if gcd(p,q) = 1.

        - If gcd(p,q) = d > 1: The knot is actually d separate components
        - **Linking Number**: L = p·q (for two-component link)
        - **Crossing Number**: c = min(p(q-1), q(p-1)) for p,q coprime
        - **Bridge Number**: b = min(p, q)

        Common Examples:
        - (2,3): Trefoil knot (simplest non-trivial knot, 3 crossings)
        - (3,2): Trefoil mirror image
        - (2,5): Cinquefoil knot (5 crossings)
        - (3,4): 8-crossing torus knot
        - (3,7): 21-crossing torus knot

        **Alexander Polynomial**:
        For (p,q)-torus knot:
        Δ(t) = [(t^(pq) - 1)(t - 1)] / [(t^p - 1)(t^q - 1)]

        **Jones Polynomial**: More complex, involves q-series

        AHA MOMENT #1: THE (p,q) PARAMETRIZATION - TWO RHYTHMS, ONE DANCE
        ===================================================================
        The (p,q)-torus knot is defined by TWO COPRIME INTEGERS that encode
        TWO INDEPENDENT RHYTHMS winding together into one eternal loop!

        p = number of times the knot winds around the MAJOR circle (toroidal)
        q = number of times the knot winds around the MINOR circle (poloidal)

        When gcd(p,q) = 1 (coprime), the rhythms are INCOMMENSURATE—they
        share no common divisor except 1. This means:
        - The curve never repeats a partial pattern
        - It traces out ONE continuous path before closing
        - The knot is PRIME (cannot be decomposed into simpler knots)

        When gcd(p,q) = d > 1:
        - The "knot" is actually d SEPARATE strands
        - Each strand is a (p/d, q/d)-torus knot
        - Not a true knot, but a LINK of multiple components

        The (p,q) parametrization is like MUSICAL INTERVALS:
        - (2,3): 2 beats against 3 = 3:2 perfect fifth (trefoil)
        - (3,4): 3 against 4 = 4:3 perfect fourth
        - (5,7): 5 against 7 = tritone-like dissonance (complex knot)

        Coprimality = HARMONIC PURITY. When p and q share no common factor,
        they create a MAXIMALLY COMPLEX winding pattern that explores every
        possible combination before returning to the start.

        This is the mathematical essence of BRAIDING, WEAVING, and RHYTHM.
        Every torus knot is a frozen dance of two circular motions in
        perpetual lockstep.

        Arc Length:
        -----------
        The arc length L is computed via numerical integration:
        L = ∫₀²π |r'(t)| dt

        where r'(t) is the velocity vector:
        r'(t) = (dx/dt, dy/dt, dz/dt)

        Analytical derivatives:
        dx/dt = -rq·sin(qt)·cos(pt) - (R + r·cos(qt))·p·sin(pt)
        dy/dt = -rq·sin(qt)·sin(pt) + (R + r·cos(qt))·p·cos(pt)
        dz/dt = rq·cos(qt)

        |r'(t)|² = (dx/dt)² + (dy/dt)² + (dz/dt)²
                = r²q² + p²(R + r·cos(qt))²

        For general (p,q), this integral has no closed form and must be
        computed numerically. We use trapezoidal/Simpson integration.

        **Numerical Integration** (implemented):
        - Discretize t into n_steps = 1000
        - Compute curve points: r(tᵢ) for i = 0..n
        - Sum distances: L ≈ Σ |r(tᵢ₊₁) - r(tᵢ)|

        AHA MOMENT #2: KNOT INVARIANTS - ETERNAL TRUTHS
        =================================================
        Torus knots possess TOPOLOGICAL INVARIANTS—properties that remain
        unchanged under any continuous deformation (stretching, bending,
        twisting) as long as the knot doesn't pass through itself!

        These invariants are ETERNAL TRUTHS about the knot:

        1. **Crossing Number**: c = min(p(q-1), q(p-1))
           - The MINIMUM number of crossings in any 2D projection
           - Cannot be reduced by clever repositioning
           - Trefoil (2,3): c = min(2·2, 3·1) = min(4,3) = 3
           - Measures the knot's COMPLEXITY

        2. **Bridge Number**: b = min(p, q)
           - Minimum number of "maxima" when knot hangs from above
           - How many times must you "go up and over"
           - Trefoil (2,3): b = min(2,3) = 2

        3. **Alexander Polynomial**: Δ(t) = [(t^(pq) - 1)(t - 1)] / [(t^p - 1)(t^q - 1)]
           - Algebraic signature distinguishing knots
           - Trefoil (2,3): Δ(t) = t² - t + 1
           - Different knots → different polynomials (usually)

        4. **Knot Genus**: g = (p-1)(q-1)/2
           - Genus of the minimal Seifert surface (disk with handles)
           - Trefoil (2,3): g = (2-1)(3-1)/2 = 1 (one handle)
           - Measures the knot's "depth" in 3D space

        These invariants are the knot's IDENTITY—its mathematical fingerprint.
        No matter how you twist, stretch, or contort a (2,3)-torus knot, it
        will ALWAYS have exactly 3 crossings, bridge number 2, Alexander
        polynomial t²-t+1, and genus 1.

        This is the power of TOPOLOGY: certain truths transcend geometry.
        While the knot's shape (arc length, curvature, embedding) can vary
        infinitely, its topological essence remains IMMUTABLE.

        In mystical terms: the knot's SOUL (topology) is eternal, while its
        BODY (geometry) is mutable. The invariants are the knot's karma—
        unbreakable truths carried through all transformations.

        Surface Area (Approximation):
        ------------------------------
        The tubular neighborhood around the knot curve has surface area:
        A ≈ L × (2π·tube_r)

        This assumes:
        1. The tube radius is small relative to knot curvature
        2. The tube doesn't self-intersect (true for small tube_r)
        3. Parallel transport maintains circular cross-sections

        **Formula: A ≈ 2π·tube_r·L**

        More precise formula accounts for curvature:
        A = ∫₀²π 2π·tube_r·√(1 + κ²·tube_r²) |r'(t)| dt
        where κ(t) is the curvature. For small tube_r, this reduces to above.

        Volume (Approximation):
        -----------------------
        The volume of the tubular neighborhood:
        V ≈ L × (π·tube_r²)

        This assumes circular cross-sections of radius tube_r along the
        arc length L. Again, precise calculation requires integration:
        V = ∫₀²π π·tube_r²·(1 - κ·tube_r·cos(θ)) |r'(t)| dt

        For small tube_r relative to curvature radius 1/κ:
        **Formula: V ≈ π·tube_r²·L**

        Curvature & Torsion:
        --------------------
        **Curvature**: κ(t) = |r'(t) × r''(t)| / |r'(t)|³
        Measures how sharply the curve bends.

        **Torsion**: τ(t) = (r'(t) × r''(t))·r'''(t) / |r'(t) × r''(t)|²
        Measures how much the curve twists out of its osculating plane.

        For torus knots:
        - κ and τ are periodic with period 2π/gcd(p,q)
        - Both are always non-zero (knot never straightens or lies flat)
        - κ oscillates as knot goes around major/minor cycles

        Framing & Linking:
        ------------------
        The tubular neighborhood requires a **framing** (choice of normal
        direction at each point). We use **parallel transport** to maintain
        a continuous, twist-minimized frame.

        **Writhe**: Wr = (total twist of framing) / 2π
        For (p,q)-torus knot with natural framing: Wr = pq

        HERMETIC NOTE - THE ETERNAL KNOT:
        =================================
        The torus knot represents the **INTERWEAVING OF FATE**, the
        **ETERNAL KNOT OF EXISTENCE**:

        - **Closed Loop**: No beginning, no end (like Ouroboros)
        - **p Lobes**: Macrocosmic cycles (solar, cosmic, universal)
        - **q Twists**: Microcosmic cycles (lunar, personal, karmic)
        - **Knot Invariants**: Eternal truths that transcend transformation

        Symbolism by Type:
        - **(2,3) Trefoil**: Trinity knot (Father-Son-Spirit, Maiden-Mother-Crone)
        - **(2,5) Cinquefoil**: Five elements, five wounds of Christ, pentagram
        - **(3,4)**: Union of triangle (3) and square (4) = spirit + matter
        - **(3,7)**: Sacred 3 × 7 = 21 (three worlds × seven planets)

        In Mystical Traditions:
        - **Celtic**: Endless knots symbolizing eternal love, interconnection
        - **Buddhist**: Endless knot (śrīvatsa) = interdependence of all things
        - **Norse**: Valknut ("knot of the slain") = Odin's symbol
        - **Hermetic**: The knot of Isis, secret knowledge binding opposites

        The (p,q)-torus knot encodes **two periodicities** in one curve,
        representing the **marriage of two cosmic rhythms**. When gcd(p,q)=1,
        the knot is irreducible = a **prime truth**, indivisible unity.

        AHA MOMENT #3: THE TREFOIL (2,3) - THE SIMPLEST NONTRIVIAL KNOT
        =================================================================
        The (2,3)-torus knot—the TREFOIL—is the SIMPLEST nontrivial knot
        that exists. It is the HYDROGEN ATOM of knot theory!

        Why is it the simplest?
        - Crossing number = 3 (minimum for any nontrivial knot)
        - No knot with fewer than 3 crossings can exist (except unknot)
        - Prime (cannot be decomposed)
        - Alternating (crossings alternate over-under-over-under...)

        The trefoil is to knots what the TRIANGLE is to polygons:
        the irreducible minimum, the first step beyond triviality.

        Historical Significance:
        - Studied since antiquity (Celtic, Norse, Buddhist art)
        - First knot proven distinct from unknot (19th century)
        - Gauss's linking integral applied to trefoil (1833)
        - Dehn proved (2,3) ≠ (2,5) using fundamental group (1914)
        - Jones polynomial revolution started with trefoil (1984)

        The Trefoil's Properties:
        - **Chiral**: Has distinct left and right-handed forms (mirror images)
        - **Fibered**: Complement in S³ fibers over circle
        - **Algebraic**: Link of singularity z² + w³ = 0
        - **3-colorable**: Can tricolor strands (red-blue-green)
        - **Genus 1**: Bounds a punctured torus (one handle)

        The trefoil appears EVERYWHERE in nature:
        - DNA supercoiling (overwound DNA forms trefoil loops)
        - Protein folding (trefoil knot in ubiquitin hydrolase)
        - Fluid vortices (knotted vortex tubes in turbulence)
        - Celtic art (trinity knot, triquetra)
        - Japanese mon (family crests)

        In Sacred Geometry:
        The trefoil is the TRINITY KNOT—three lobes, three crossings,
        three-fold rotational symmetry (order 3).
        - Christian: Father-Son-Spirit
        - Pagan: Maiden-Mother-Crone
        - Hermetic: Sulfur-Mercury-Salt
        - Alchemical: Body-Soul-Spirit

        The trefoil is the geometric embodiment of THREEFOLD UNITY:
        three distinct aspects woven into one indivisible whole.
        You cannot untangle the three without destroying the knot.

        Mathematical Beauty:
        The trefoil demonstrates that COMPLEXITY emerges from SIMPLICITY.
        With just two parameters (p=2, q=3), we generate an object with:
        - Infinite embeddings in 3-space
        - Rich algebraic structure (fundamental group, Alexander polynomial)
        - Deep connections to quantum invariants
        - Appearance across mathematics, physics, biology

        The trefoil is EMERGENT COMPLEXITY from minimal data.
        This is the essence of sacred geometry: profound structure
        arising from simple rules.

        Notable Properties:
        -------------------
        1. **Chirality**: (p,q) and (q,p) are mirror images (except when p=q)
        2. **Prime Knots**: All torus knots with gcd(p,q)=1 are prime (indecomposable)
        3. **Alternating**: All (p,q) torus knots are alternating knots
        4. **Fibered**: Complement in S³ fibers over S¹ (mathematical beauty)
        5. **Algebraic Knots**: Can be defined as links of singularities

        Mathematical Curiosities:
        -------------------------
        • **Knot Polynomials**: Alexander, Jones, HOMFLY polynomials distinguish knots
        • **Seifert Surface**: Torus knots bound canonical minimal genus surfaces
        • **Braid Representation**: Every torus knot is a closed braid
        • **Quantum Invariants**: Torus knots central to Chern-Simons theory
        • **DNA**: Torus knots appear in DNA supercoiling and protein folding
        • **Fluid Dynamics**: Vortex knots in ideal fluids

        Historical & Cultural Context:
        ------------------------------
        • **Ancient**: Celtic, Norse, and Buddhist endless knots (pre-1000 CE)
        • **1771**: Vandermonde begins study of knot diagrams
        • **1867**: Lord Kelvin proposes atoms as knotted vortices in ether
        • **1877**: Tait begins systematic enumeration of knots
        • **1914**: Max Dehn proves (2,3) and (2,5) knots inequivalent
        • **1984**: Jones discovers Jones polynomial (Fields Medal 1990)
        • **1990s**: Knot theory + quantum field theory (Witten, Atiyah)

        In Art & Symbology:
        • **Book of Kells** (9th century): Elaborate Celtic knot illuminations
        • **Islamic Art**: Geometric endless knots in tilework
        • **Tibetan Buddhism**: Auspicious endless knot (ashtamangala)
        • **Modern Sculpture**: Knot theory inspires mathematical art

        In Science & Technology:
        • **Molecular Knots**: Synthesized in laboratory (1980s-present)
        • **DNA Topology**: Knot theory applied to genetic recombination
        • **Quantum Computing**: Topological quantum computation uses anyons (knot-like)
        • **Plasma Physics**: Knotted flux tubes in magnetohydrodynamics

        References:
        -----------
        [1] Adams, C. (2004). The Knot Book. American Mathematical Society.
        [2] Rolfsen, D. (1976). Knots and Links. Publish or Perish Press.
        [3] Kauffman, L. (1987). On Knots. Princeton University Press.
        [4] Lickorish, W.B.R. (1997). An Introduction to Knot Theory. Springer.
        [5] Cromwell, P. (2004). Knots and Links. Cambridge University Press.
        [6] Witten, E. (1989). "Quantum Field Theory and the Jones Polynomial." Comm. Math. Phys.
        [7] Jones, V. (1985). "A Polynomial Invariant for Knots via von Neumann Algebras."
        """
        return TorusKnotSolidService._compute_metrics(p, q, R, r, tube_r)

    def create_declaration(self, canonical_value: Any, *, title: str | None = None) -> Declaration:
        canonical = self._normalize_canonical(canonical_value)
        p = int(canonical["p"])
        q = int(canonical["q"])
        major = canonical["major_radius"]
        minor = canonical["minor_radius"]
        tube = canonical["tube_radius"]

        forms = [
            Form(
                id="torus_knot",
                kind="TorusKnot",
                params={
                    self.canonical_key: canonical,
                    "p": p,
                    "q": q,
                    "major_radius": major,
                    "minor_radius": minor,
                    "tube_radius": tube,
                },
                dimensional_class=3,
                symmetry_class="toroidal",
                notes="(p,q) torus knot embedded in torus with radii R, r",
            )
        ]

        return Declaration(
            title=title
            or f"Torus Knot p={p}, q={q}, R={major:.4f}, r={minor:.4f}, tube={tube:.4f}",
            forms=forms,
            metadata={
                "solver": "TorusKnotSolver",
                "version": "1.0.0",
                "gcd": gcd(p, q),
            },
        )

    def get_derivation(self) -> str:
        return self._compute_metrics.__doc__ or ""

    # ── Helpers ───────────────────────────────────────────────────────────
    def _normalize_canonical(self, canonical_value: Any) -> Dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            for key in self.supported_keys:
                if key in canonical_value and canonical_value[key] is not None:
                    if key in {"p", "q"}:
                        canonical[key] = float(int(canonical_value[key]))
                    else:
                        canonical[key] = float(canonical_value[key])
        else:
            # If only a single value is provided, treat it as major_radius for quick entry
            try:
                canonical["major_radius"] = float(canonical_value)
            except Exception:
                pass

        # Persist normalized state for subsequent solves
        self._state = canonical
        return canonical
