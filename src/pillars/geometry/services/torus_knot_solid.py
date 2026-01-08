"""Torus Knot solid math utilities and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_geometry import (
    Vec3,
    vec_add,
    vec_cross,
    vec_normalize,
    vec_scale,
    edges_from_faces,
    vec_sub,
    vec_length
)
from .solid_property import SolidProperty


@dataclass(frozen=True)
class TorusKnotMetrics:
    """
    Torus Knot Metrics class definition.
    
    """
    p: int
    q: int
    major_radius: float
    minor_radius: float
    tube_radius: float
    arc_length: float
    approx_surface_area: float
    approx_volume: float


@dataclass(frozen=True)
class TorusKnotSolidResult:
    """
    Torus Knot Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: TorusKnotMetrics


@dataclass
class TorusKnotMeshConfig:
    """
    Torus Knot Mesh Config class definition.
    
    """
    tubular_segments: int = 120  # Reduced for filled rendering performance
    radial_segments: int = 10    # Reduced for filled rendering performance


class TorusKnotSolidService:
    """Generates payloads for (p,q) torus knot solids."""

    @staticmethod
    def build(
        p: int = 2,
        q: int = 3,
        major_radius: float = 3.0,
        minor_radius: float = 1.0,
        tube_radius: float = 0.4,
        config: TorusKnotMeshConfig = None
    ) -> TorusKnotSolidResult:
        """
        Build logic.
        
        Args:
            p: Description of p.
            q: Description of q.
            major_radius: Description of major_radius.
            minor_radius: Description of minor_radius.
            tube_radius: Description of tube_radius.
            config: Description of config.
        
        Returns:
            Result of build operation.
        """
        if major_radius <= 0 or minor_radius <= 0 or tube_radius <= 0:
            raise ValueError("Radii must be positive")
        if config is None:
            config = TorusKnotMeshConfig()

        metrics = TorusKnotSolidService._compute_metrics(p, q, major_radius, minor_radius, tube_radius)
        
        vertices, faces = TorusKnotSolidService._generate_mesh(p, q, major_radius, minor_radius, tube_radius, config)
        edges = edges_from_faces(faces)
        
        labels = [
            SolidLabel(text=f"P={p}, Q={q}", position=(0.0, major_radius + minor_radius + tube_radius, 0.0)),
        ]

        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=labels,
            metadata={
                'p': p,
                'q': q,
                'major_radius': metrics.major_radius,
                'minor_radius': metrics.minor_radius,
                'tube_radius': metrics.tube_radius,
                'arc_length': metrics.arc_length,
                'surface_area': metrics.approx_surface_area,
                'volume': metrics.approx_volume,
            },
            suggested_scale=major_radius + minor_radius + tube_radius,
        )
        return TorusKnotSolidResult(payload=payload, metrics=metrics)

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
        # Arc length is an integral, approximate numerically
        # L = Integral of |r'(t)| dt from 0 to 2pi
        # Simple numerical integration
        n_steps = 1000
        length = 0.0
        _dt = (2 * math.pi) / n_steps
        
        # Curve:
        # x = (R + r cos(qt)) cos(pt)
        # y = (R + r cos(qt)) sin(pt)
        # z = r sin(qt)
        
        prev_p = TorusKnotSolidService._curve_point(0, p, q, R, r)
        for i in range(1, n_steps + 1):
            t = (i / n_steps) * 2 * math.pi
            curr_p = TorusKnotSolidService._curve_point(t, p, q, R, r)
            dist = vec_length(vec_sub(curr_p, prev_p))
            length += dist
            prev_p = curr_p

        # Torus Volume ~ Length * (pi * tube_r^2)
        # Torus Area ~ Length * (2 * pi * tube_r)
        
        return TorusKnotMetrics(
            p=p,
            q=q,
            major_radius=R,
            minor_radius=r,
            tube_radius=tube_r,
            arc_length=length,
            approx_surface_area=length * (2 * math.pi * tube_r),
            approx_volume=length * (math.pi * (tube_r ** 2)),
        )

    @staticmethod
    def _curve_point(t: float, p: int, q: int, R: float, r: float) -> Vec3:
        # r_val = R + r * cos(q*t)
        r_val = R + r * math.cos(q * t)
        
        # x = r_val * cos(p*t)
        x = r_val * math.cos(p * t)
        
        # y = r_val * sin(p*t)
        y = r_val * math.sin(p * t)
        
        # z = r * sin(q*t)
        # Wait, usually z comes out of the R plane? 
        # Yes, standard torus parameterization axis is Z.
        z = r * math.sin(q * t)
        return (x, y, z)

    @staticmethod
    def _generate_mesh(p: int, q: int, R: float, r: float, tube_r: float, config: TorusKnotMeshConfig) -> Tuple[List[Vec3], List[Tuple[int, ...]]]:
        vertices = []
        faces = []
        
        segments = config.tubular_segments
        radial_seg = config.radial_segments
        
        # 1. Compute curve points & tangents using forward difference or analytical derivative
        _curve_frames = [] # List of (pos, T, N, B)
        
        # Calculate points for 0 to 2pi (inclusive to find total twist)
        total_steps = segments
        points = []
        tangents = []
        
        for i in range(total_steps + 1):
            t = (i / total_steps) * 2 * math.pi
            pos = TorusKnotSolidService._curve_point(t, p, q, R, r)
            points.append(pos)
            
            # Analytical derivative for T is better, but numerical is fine for now
            # Central difference or forward
            t_next = (t + 0.0001)
            pos_next = TorusKnotSolidService._curve_point(t_next, p, q, R, r)
            tangent = vec_normalize(vec_sub(pos_next, pos))
            tangents.append(tangent)

        # 2. Parallel Transport First Pass
        # Initial Frame at i=0
        T0 = tangents[0]
        # Robust initial Normal: use simplified heuristic or arbitrary axis
        # If T is up, use X. If T is X, use Y.
        if abs(T0[2]) < 0.9:
            up = (0, 0, 1)
        else:
            up = (1, 0, 0)
        N0 = vec_normalize(vec_cross(T0, up))
        B0 = vec_normalize(vec_cross(T0, N0))
        
        _current_N = N0
        parallel_frames = [(points[0], T0, N0, B0)]
        
        for i in range(1, total_steps + 1):
            _prev_pos, prev_T, prev_N, _prev_B = parallel_frames[-1]  # type: ignore[reportUnknownVariableType, reportUnusedVariable]
            curr_pos = points[i]
            curr_T = tangents[i]
            
            # Transport prev_N to current frame
            # Axis of rotation A = prev_T x curr_T
            axis = vec_cross(prev_T, curr_T)  # type: ignore[reportUndefinedVariable, reportUnknownArgumentType]
            
            # If collinear (straight line), just update T
            if vec_length(axis) < 1e-9:
                curr_N = prev_N
            else:
                 axis = vec_normalize(axis)
                 # Angle between tangents
                 dot = prev_T[0]*curr_T[0] + prev_T[1]*curr_T[1] + prev_T[2]*curr_T[2]  # type: ignore[reportUndefinedVariable, reportUnknownVariableType]
                 # Clamp for safety
                 phi = math.acos(max(-1.0, min(1.0, dot)))
                 
                 # Rotate prev_N around axis by phi
                 # Rodrigues rotation formula
                 # v_rot = v cos(phi) + (k x v) sin(phi) + k (k . v) (1 - cos(phi))
                 cos_phi = math.cos(phi)
                 sin_phi = math.sin(phi)
                 k_cross_v = vec_cross(axis, prev_N)
                 k_dot_v = axis[0]*prev_N[0] + axis[1]*prev_N[1] + axis[2]*prev_N[2]  # type: ignore[reportUndefinedVariable, reportUnknownVariableType]
                 
                 term1 = vec_scale(prev_N, cos_phi)
                 term2 = vec_scale(k_cross_v, sin_phi)
                 term3 = vec_scale(axis, k_dot_v * (1 - cos_phi))
                 
                 curr_N = vec_add(vec_add(term1, term2), term3)
                 curr_N = vec_normalize(curr_N)

            # Re-orthogonalize to ensure perfect N-T orthogonality
            # N = N - (N . T) * T
            dot_val = curr_N[0]*curr_T[0] + curr_N[1]*curr_T[1] + curr_N[2]*curr_T[2]
            curr_N = vec_sub(curr_N, vec_scale(curr_T, dot_val))
            curr_N = vec_normalize(curr_N)
            
            curr_B = vec_normalize(vec_cross(curr_T, curr_N))
            
            parallel_frames.append((curr_pos, curr_T, curr_N, curr_B))

        # 3. Calculate Correction Twist Angle
        # Compare frame at 2pi (index segments) with frame at 0
        # They are at the same spatial point.
        first_N = parallel_frames[0][2]
        last_N = parallel_frames[segments][2]
        
        # Angle alpha between first_N and last_N (in the plane normal to T)
        # We can use atan2(det, dot) where det = (first_N x last_N) . T
        cross_Ns = vec_cross(first_N, last_N)
        T_end = parallel_frames[segments][1]
        det = cross_Ns[0]*T_end[0] + cross_Ns[1]*T_end[1] + cross_Ns[2]*T_end[2]
        dot = first_N[0]*last_N[0] + first_N[1]*last_N[1] + first_N[2]*last_N[2]
        
        total_twist = math.atan2(det, dot)
        
        # 4. Generate Final Twisted Frames & Vertices
        for i in range(segments):
            pos, _T, N_transport, B_transport = parallel_frames[i]  # type: ignore[reportUnknownVariableType, reportUnusedVariable]
            
            # Twist adjustment
            # We want to distribute -total_twist over the length
            theta = -(total_twist * (i / segments))
            
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)
            
            # Rotate N, B around T
            # N_final = N cos + B sin
            # B_final = -N sin + B cos
            
            N_final_x = N_transport[0]*cos_theta + B_transport[0]*sin_theta
            N_final_y = N_transport[1]*cos_theta + B_transport[1]*sin_theta
            N_final_z = N_transport[2]*cos_theta + B_transport[2]*sin_theta
            N_final = (N_final_x, N_final_y, N_final_z)
            
            B_final_x = -N_transport[0]*sin_theta + B_transport[0]*cos_theta
            B_final_y = -N_transport[1]*sin_theta + B_transport[1]*cos_theta
            B_final_z = -N_transport[2]*sin_theta + B_transport[2]*cos_theta
            B_final = (B_final_x, B_final_y, B_final_z)
            
            # Generate Tube Ring
            for j in range(radial_seg):
                angle = (j / radial_seg) * 2 * math.pi
                cos_a = math.cos(angle)
                sin_a = math.sin(angle)
                
                off_x = vec_scale(N_final, tube_r * cos_a)
                off_y = vec_scale(B_final, tube_r * sin_a)
                offset = vec_add(off_x, off_y)
                
                vertex = vec_add(pos, offset)
                vertices.append(vertex)
                
        # 5. Generate Faces
        for i in range(segments):
            next_i = (i + 1) % segments
            
            for j in range(radial_seg):
                next_j = (j + 1) % radial_seg
                
                idx_bl = i * radial_seg + j
                idx_br = next_i * radial_seg + j
                idx_tr = next_i * radial_seg + next_j
                idx_tl = i * radial_seg + next_j
                
                faces.append((idx_bl, idx_br, idx_tr, idx_tl))

        return vertices, faces


class TorusKnotSolidCalculator:
    """Torus Knot calculator."""

    def __init__(
        self,
        p: int = 2,
        q: int = 3,
        major_radius: float = 3.0,
        minor_radius: float = 1.0,
        tube_radius: float = 0.4,
    ):
        """
          init   logic.
        
        Args:
            p: Description of p.
            q: Description of q.
            major_radius: Description of major_radius.
            minor_radius: Description of minor_radius.
            tube_radius: Description of tube_radius.
        
        """
        self._properties = {
            'p': SolidProperty('P (Lobes)', 'p', 'int', 1.0),
            'q': SolidProperty('Q (Twists)', 'q', 'int', 1.0),
            'major_radius': SolidProperty('Major Radius (R)', 'major_radius', 'units', 10.0),
            'minor_radius': SolidProperty('Minor Radius (r)', 'minor_radius', 'units', 10.0),
            'tube_radius': SolidProperty('Tube Radius', 'tube_radius', 'units', 10.0),
            
            # Read-only metrics
            'arc_length': SolidProperty('Arc Length', 'arc_length', 'units', 0.0, editable=False),
            'surface_area': SolidProperty('Approx. Surface Area', 'surface_area', 'units²', 0.0, editable=False),
            'volume': SolidProperty('Approx. Volume', 'volume', 'units³', 0.0, editable=False),
        }
        
        self.set_property('p', float(p))
        self.set_property('q', float(q))
        self.set_property('major_radius', major_radius)
        self.set_property('minor_radius', minor_radius)
        self.set_property('tube_radius', tube_radius)
        
        self._recalculate()

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        return list(self._properties.values())

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if value is not None and value <= 0 and key not in ('p', 'q'):
            return False
            
        prop = self._properties.get(key)
        if not prop:
            return False
            
        if key in ('p', 'q'):
             # Ensure integer
             prop.value = float(int(value)) if value else 0.0
        else:
             prop.value = value
             
        self._recalculate()
        return True

    def _recalculate(self):
        p = int(self._properties['p'].value or 2)
        q = int(self._properties['q'].value or 3)
        R = self._properties['major_radius'].value
        r = self._properties['minor_radius'].value
        tube_r = self._properties['tube_radius'].value
        
        if R is None or r is None or tube_r is None:
            return

        metrics = TorusKnotSolidService._compute_metrics(p, q, R, r, tube_r)
        
        self._properties['arc_length'].value = metrics.arc_length
        self._properties['surface_area'].value = metrics.approx_surface_area
        self._properties['volume'].value = metrics.approx_volume
        
        self._result = TorusKnotSolidService.build(p, q, R, r, tube_r)

    def clear(self):
        # Reset to defaults
        # self.__init__() # Actually cleaner to just clear values?
        # But UI expects None?
        """
        Clear logic.
        
        """
        pass

    def payload(self) -> Optional[SolidPayload]:
        """
        Payload logic.
        
        Returns:
            Result of payload operation.
        """
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        """
        Metadata logic.
        
        Returns:
            Result of metadata operation.
        """
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)