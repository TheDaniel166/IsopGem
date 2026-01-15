"""Ellipse Solver - Canon-compliant bidirectional solver."""

from __future__ import annotations

import math
from typing import Any, Optional

from canon_dsl import Declaration, Form, SolveProvenance, SolveResult

from .geometry_solver import GeometrySolver, PropertyDefinition


class EllipseSolver(GeometrySolver):
    """
    Bidirectional solver for ellipses.
    
    Canonical Parameters:
        - semi_major_axis (a)
        - semi_minor_axis (b)
    
    IMPORTANT: Derivations preserved from legacy EllipseShape.
    """

    def __init__(
        self,
        semi_major_axis: float = 2.0,
        semi_minor_axis: float = 1.0,
    ) -> None:
        self._state = {
            "semi_major_axis": max(float(semi_major_axis), 1e-9),
            "semi_minor_axis": max(float(semi_minor_axis), 1e-9),
        }

    @property
    def form_type(self) -> str:
        return "Ellipse"

    @property
    def dimensional_class(self) -> int:
        return 2

    @property
    def canonical_key(self) -> str:
        # Ellipse has two parameters; treat them as a grouped canonical dict.
        return "ellipse"
    
    @property
    def supported_keys(self) -> set[str]:
        return {
            "semi_major_axis", "semi_minor_axis",
            "major_axis", "minor_axis",
            "area", "perimeter",
        }

    def get_editable_properties(self) -> list[PropertyDefinition]:
        """Return editable properties (Dimensions)."""
        return [
            PropertyDefinition(
                key="semi_major_axis",
                label="Semi-Major Axis (a)",
                unit="units",
                editable=True,
                category="Dimensions",
            ),
            PropertyDefinition(
                key="semi_minor_axis",
                label="Semi-Minor Axis (b)",
                unit="units",
                editable=True,
                category="Dimensions",
            ),
            PropertyDefinition(
                key="major_axis",
                label="Major Axis (2a)",
                unit="units",
                editable=True,
                category="Dimensions",
            ),
            PropertyDefinition(
                key="minor_axis",
                label="Minor Axis (2b)",
                unit="units",
                editable=True,
                category="Dimensions",
            ),
        ]

    def get_derived_properties(self) -> list[PropertyDefinition]:
        """Return derived (read-only) properties."""
        return [
            PropertyDefinition(
                key="area",
                label="Area",
                unit="units²",
                editable=False,
                readonly=True,
                category="Measurements",
                tooltip="A = pi a b",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="perimeter",
                label="Perimeter (Approx.)",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                tooltip="Ramanujan approximation",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="eccentricity",
                label="Eccentricity (e)",
                unit="",
                editable=False,
                readonly=True,
                category="Measurements",
                tooltip="e = sqrt(1 - b^2/a^2)",
                format_spec=".6f",
            ),
            PropertyDefinition(
                key="focal_distance",
                label="Focal Distance (c)",
                unit="units",
                editable=False,
                readonly=True,
                category="Measurements",
                tooltip="c = sqrt(a² - b²)",
                format_spec=".6f",
            ),
        ]

    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Solve for canonical parameters (a, b) given a property value.
        
        Note: Since we cannot solve for BOTH a and b from a single value,
        this method returns a partial update designed to be merged with current state
        by the Canon Engine or UI.
        
        However, since GeometrySolver assumes statelessness, for 2-param shapes
        we typically only support updating the parameters directly.
        """
        if key not in self.supported_keys:
            return SolveResult.invalid(key, value, "Unsupported property for ellipse")

        if key in {"area", "perimeter"}:
            return SolveResult.invalid(
                key,
                value,
                "Cannot solve ellipse from derived property (underdetermined system)",
            )

        if value <= 0:
            return SolveResult.invalid(key, value, "Axis lengths must be positive")

        canonical = self._state.copy()

        if key == "semi_major_axis":
            canonical["semi_major_axis"] = value
            formula = "a = a"
        elif key == "semi_minor_axis":
            canonical["semi_minor_axis"] = value
            formula = "b = b"
        elif key == "major_axis":
            canonical["semi_major_axis"] = value / 2.0
            formula = "a = major_axis / 2"
        elif key == "minor_axis":
            canonical["semi_minor_axis"] = value / 2.0
            formula = "b = minor_axis / 2"
        else:
            return SolveResult.invalid(key, value, "Unsupported property for ellipse")

        self._state = canonical

        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
        )

        return SolveResult.success(
            canonical_parameter=canonical,  # type: ignore[arg-type]
            canonical_key=self.canonical_key,
            provenance=provenance,
        )

    def get_all_properties(self, canonical: dict | float) -> dict[str, float]:
        """Compute all properties from canonical params {a, b}."""
        canonical_dict = self._normalize_canonical(canonical)
        a = canonical_dict.get("semi_major_axis", 0.0)
        b = canonical_dict.get("semi_minor_axis", 0.0)

        return self._compute_all_properties(a, b)

    @staticmethod
    def _compute_all_properties(a: float, b: float) -> dict[str, float]:
        r"""
        Compute ellipse properties.
        
        EARTH MEASURE (ELLIPSE DERIVATIONS):
        ====================================
        
        AHA MOMENT #1: Eccentricity (From Circle to Line)
        ═══════════════════════════════════════════════════════════════════════════════════════
        
        An ellipse is defined by two semi-axes:
        • **Semi-major axis** a (half the longest diameter)
        • **Semi-minor axis** b (half the shortest diameter), where a ≥ b
        
        The **eccentricity** e measures how "stretched" the ellipse is:
        
          e = √(1 - b²/a²) = c/a
        
          where c = √(a² - b²) is the **focal distance** (center to focus)
        
        **Eccentricity spectrum**:
        • e = 0: Circle (b = a, foci coincide at center)
        • 0 < e < 1: Ellipse (planetary orbits)
        • e = 1: Parabola (escape trajectory, comet on one-time pass)
        • e > 1: Hyperbola (interstellar object passing through solar system)
        
        As e → 1 (b → 0), the ellipse becomes increasingly "needle-like," approaching a line
        segment of length 2a.
        
        **Defining property** (two-focus definition):
        For any point P on the ellipse, if F₁ and F₂ are the foci:
        
          |PF₁| + |PF₂| = 2a    (constant sum)
        
        This is the **gardener's ellipse** construction: tie a string of length 2a to two stakes
        (foci), pull taut with a pencil, and trace the curve!
        
        **Cartesian equation** (centered at origin, axes aligned):
        
          x²/a² + y²/b² = 1
        
        **Parametric form**:
          x = a·cos(t),  y = b·sin(t),  t ∈ [0, 2π]
        
        ═══════════════════════════════════════════════════════════════════════════════════════
        AHA MOMENT #2: Kepler's Planetary Orbits (Celestial Mechanics)
        ═══════════════════════════════════════════════════════════════════════════════════════
        
        **Kepler's First Law** (1609): Planets orbit the Sun in elliptical paths, with the Sun
        at one focus (the other focus is empty space).
        
        Before Kepler:
        • Aristotle/Ptolemy: Circular orbits with epicycles (circles upon circles)
        • Copernicus: Heliocentric circles (still assumed perfect circles)
        • Kepler realized: Mars's orbit is NOT a circle—it's an ellipse! (e ≈ 0.0934 for Mars)
        
        This shattered the ancient dogma that celestial motion must be perfectly circular
        (divine perfection = circles). The cosmos is elliptical!
        
        **Orbital elements**:
        • **Perihelion**: Closest approach to Sun = a(1-e)
        • **Aphelion**: Farthest from Sun = a(1+e)
        • **Semi-major axis** a determines orbital period via Kepler's Third Law:
            T² ∝ a³    (period squared proportional to semi-major axis cubed)
        
        **Examples**:
        • Earth: e = 0.0167 (nearly circular!)
        • Mercury: e = 0.2056 (most eccentric planet)
        • Pluto: e = 0.2488 (highly elliptical, crosses Neptune's orbit)
        • Halley's Comet: e = 0.967 (very elongated, perihelion inside Venus, aphelion beyond Neptune)
        
        **Why ellipses?** Newton's law of gravitation (F ∝ 1/r²) + conservation of energy/momentum
        → orbits are conic sections (ellipse, parabola, hyperbola depending on total energy).
        Bound orbits (negative energy) → ellipses.
        
        **Reflective property**: Light/sound emanating from one focus reflects off the ellipse
        and converges to the other focus. This is used in:
        • Whispering galleries (elliptical domes)
        • Lithotripsy (kidney stone treatment: shock wave from one focus breaks stone at other)
        
        ═══════════════════════════════════════════════════════════════════════════════════════
        AHA MOMENT #3: The Perimeter Problem (No Closed-Form Formula!)
        ═══════════════════════════════════════════════════════════════════════════════════════
        
        **Area**: Simple! A = πab (generalization of πr² for circle when a=b=r)
        
        **Perimeter**: No elementary closed-form formula exists!
        
        The exact perimeter involves an **elliptic integral** (hence the name):
        
          P = 4a ∫₀^(π/2) √(1 - e²sin²θ) dθ    (complete elliptic integral of 2nd kind)
        
        This cannot be expressed using elementary functions (polynomials, trig, exp, log).
        
        **Approximations** (many exist, none exact!):
        
        1) **Ramanujan's approximation** (1914):
        
          P ≈ π[3(a+b) - √((3a+b)(a+3b))]
        
          This is accurate to within ~0.5% for most ellipses!
        
        2) **Infinite series** (exact but never terminates):
        
          P = 2πa · [1 - (1/2)²e² - (1·3/2·4)²(e⁴/3) - (1·3·5/2·4·6)²(e⁶/5) - ...]
        
        3) **Limit cases**:
          • Circle (a=b): P = 2πa (exact!)
          • Line (b→0): P → 4a (approaches perimeter of degenerate "line segment" traversed twice)
        
        **Why is this hard?** The arc length integral ds = √(dx²+dy²) for the ellipse leads to:
        
          ds = √((a²sin²t + b²cos²t)) dt    (no elementary antiderivative!)
        
        This is a fundamental limitation—ellipses are "transcendental" in a deeper sense than
        just containing π. Computing their perimeter requires infinite series or numerical
        integration.
        
        **Historical note**: This problem motivated the development of elliptic functions and
        elliptic integrals in 18th-19th century (Euler, Legendre, Jacobi, Abel). These special
        functions are now fundamental in number theory, cryptography, and string theory!
        
        ═══════════════════════════════════════════════════════════════════════════════════════
        🪐 HERMETIC SIGNIFICANCE 🪐
        ═══════════════════════════════════════════════════════════════════════════════════════
        
        The ellipse embodies **Duality, Balance, and Imperfect Perfection**:
        
        • **Two Foci** (vs. One Center): The ellipse has TWO centers of attention, not one.
          This represents duality: masculine/feminine, heaven/earth, spirit/matter. The circle
          is monadic unity; the ellipse is dyadic relationship.
        
        • **The Cosmic Egg**: Many creation myths describe the universe as born from an egg
          (Orphic Egg, Brahmanda, World Egg). The ellipse/ovoid is the primordial form—not
          perfectly spherical (which would be static) but slightly elongated (implying motion,
          potential, becoming).
        
        • **Planetary Orbits as Divine Imperfection**: Kepler's discovery that orbits are
          elliptical was initially shocking—the heavens were supposed to be PERFECT (circles).
          But ellipses reveal a deeper truth: the cosmos is dynamic, not static. Eccentricity
          is not error—it's design. The ellipse is the geometry of *perpetual motion toward
          a center that is never reached* (the Sun at one focus, the empty focus as unrealized
          potential).
        
        • **Stretched Circle**: The ellipse is what happens when circular perfection is
          subjected to a FORCE (stretching, gravity, perspective). It represents the descent
          of the ideal (circle) into manifestation (ellipse). In Neoplatonism, the One
          emanates into the Many—the circle becomes ellipse, then parabola, then hyperbola
          (increasingly open, less bound).
        
        • **Fertility and Growth**: The egg shape (ovoid, slightly tapered ellipse) is the
          universal symbol of fertility, new life, potential. The ellipse contains the future
          (the as-yet-unhatched).
        
        The ellipse teaches: **Perfection in motion is not static symmetry—it is dynamic balance
        between two poles.** 🪐
        """
        if a is None or b is None:
            return {}
            
        # Re-sort for calculation purposes (mathematical a >= b)
        math_a = max(a, b)
        math_b = min(a, b)
        
        area = math.pi * math_a * math_b
        
        try:
            ecc = math.sqrt(1 - (math_b * math_b) / (math_a * math_a)) if math_a > 0 else 0
        except ValueError:
            ecc = 0
            
        focal_dist = math.sqrt(max(math_a * math_a - math_b * math_b, 0.0))
        
        perimeter = 0.0
        if (math_a + math_b) > 0:
            h = ((math_a - math_b) ** 2) / ((math_a + math_b) ** 2)
            # Ramanujan's Approximation
            perimeter = math.pi * (math_a + math_b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))
            
        return {
            "semi_major_axis": a, # Return original orientation
            "semi_minor_axis": b,
            "major_axis": 2 * a,
            "minor_axis": 2 * b,
            "area": area,
            "perimeter": perimeter,
            "eccentricity": ecc,
            "focal_distance": focal_dist,
        }
    
    def create_declaration(
        self,
        canonical_value: float | dict,
        *,
        title: Optional[str] = None,
    ) -> Declaration:
        """Create a Canon-compliant Declaration for an Ellipse."""
        canonical = self._normalize_canonical(canonical_value)
        a = canonical.get("semi_major_axis", 2.0)
        b = canonical.get("semi_minor_axis", 1.0)
        metrics = self._compute_all_properties(a, b)

        params = {
            "ellipse": {"semi_major_axis": a, "semi_minor_axis": b},
            "semi_major_axis": a,
            "semi_minor_axis": b,
            "major_axis": metrics.get("major_axis", 2 * a),
            "minor_axis": metrics.get("minor_axis", 2 * b),
            "area": metrics.get("area", math.pi * a * b),
            "perimeter": metrics.get("perimeter", 0.0),
            "eccentricity": metrics.get("eccentricity", 0.0),
            "focal_distance": metrics.get("focal_distance", 0.0),
        }

        return Declaration(
            title=title or f"Ellipse (a={a:.4f}, b={b:.4f})",
            forms=[
                Form(
                    id="ellipse",
                    kind="Ellipse",
                    params=params,
                    dimensional_class=2,
                    curvature_class="variable",
                )
            ],
            epsilon=1e-9,
            metadata={
                "solver": "EllipseSolver",
            },
        )

    def get_derivation(self) -> str:
        # Use the docstring from _compute_all_properties
        return self._compute_all_properties.__doc__ or ""

    def _normalize_canonical(self, canonical_value: Any) -> dict[str, float]:
        canonical = self._state.copy()
        if isinstance(canonical_value, dict):
            if canonical_value.get("semi_major_axis") is not None:
                canonical["semi_major_axis"] = float(canonical_value["semi_major_axis"])
            if canonical_value.get("semi_minor_axis") is not None:
                canonical["semi_minor_axis"] = float(canonical_value["semi_minor_axis"])
            if canonical_value.get("major_axis") is not None:
                canonical["semi_major_axis"] = float(canonical_value["major_axis"]) / 2.0
            if canonical_value.get("minor_axis") is not None:
                canonical["semi_minor_axis"] = float(canonical_value["minor_axis"]) / 2.0
        else:
            try:
                canonical["semi_major_axis"] = float(canonical_value)
            except (TypeError, ValueError):
                pass

        canonical["semi_major_axis"] = max(canonical["semi_major_axis"], 1e-9)
        canonical["semi_minor_axis"] = max(canonical["semi_minor_axis"], 1e-9)
        self._state = canonical
        return canonical
