"""Sphere 3D Solid Service."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

from ..shared.solid_payload import Face, SolidLabel, SolidPayload, Vec3
from .solid_geometry import Vec3, edges_from_faces
from .solid_property import SolidProperty


@dataclass(frozen=True)
class SphereMetrics:
    """
    Sphere Metrics class definition.
    
    """
    radius: float
    diameter: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class SphereResult:
    """
    Sphere Result class definition.
    
    """
    payload: SolidPayload
    metrics: SphereMetrics


class SphereSolidService:
    """Generates the geometry for a Sphere (UV Sphere mesh)."""

    @staticmethod
    def build(radius: float = 1.0, rings: int = 16, segments: int = 32) -> SphereResult:
        """
        Build logic.
        
        Args:
            radius: Description of radius.
            rings: Description of rings.
            segments: Description of segments.
        
        Returns:
            Result of build operation.
        """
        if radius <= 0:
            raise ValueError("Radius must be positive")

        metrics = SphereSolidService.compute_metrics(radius)
        
        vertices: List[Vec3] = []
        faces: List[Tuple[int, ...]] = []
        
        # Generate UV Sphere
        for ring in range(rings + 1):
            theta = ring * math.pi / rings # 0 to pi
            sin_theta = math.sin(theta)
            cos_theta = math.cos(theta)
            
            for seg in range(segments):
                phi = seg * 2 * math.pi / segments # 0 to 2pi
                sin_phi = math.sin(phi)
                cos_phi = math.cos(phi)
                
                x = radius * sin_theta * cos_phi
                y = radius * sin_theta * sin_phi
                z = radius * cos_theta
                
                vertices.append((x, y, z))
                
        # Faces
        for ring in range(rings):
            for seg in range(segments):
                v1 = ring * segments + seg
                v2 = ring * segments + (seg + 1) % segments
                v3 = (ring + 1) * segments + (seg + 1) % segments
                v4 = (ring + 1) * segments + seg
                
                faces.append((v1, v2, v3, v4))
                
        edges = edges_from_faces(faces)
        
        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=cast(List[Face], faces),
            labels=[
                SolidLabel(text=f"r = {radius:.2f}", position=(0, 0, radius * 1.1))
            ],
            metadata={
                'radius': radius,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume
            },
            suggested_scale=radius * 2.0,
        )
        return SphereResult(payload=payload, metrics=metrics)

    @staticmethod
    def compute_metrics(r: float) -> SphereMetrics:
        """
        Compute all geometric metrics for a perfect sphere from radius.

        THE PERFECT FORM:
        =================
        The sphere is the MOST PERFECT three-dimensional form—the embodiment
        of absolute symmetry, optimal efficiency, and divine proportion.

        Every point on the sphere's surface is EXACTLY the same distance (r)
        from the center. This defines the sphere as the LOCUS of points
        equidistant from a central point in 3D space.

        CORE FORMULAS & DERIVATIONS:
        ==============================

        Surface Area: A = 4πr²
        ----------------------
        Derivation via spherical coordinates:

        Parametrize the sphere:
        x(θ,φ) = r·sin(θ)·cos(φ)
        y(θ,φ) = r·sin(θ)·sin(φ)
        z(θ,φ) = r·cos(θ)

        Where θ ∈ [0,π] (polar angle from z-axis), φ ∈ [0,2π] (azimuthal angle).

        Surface area element: dA = |∂r/∂θ × ∂r/∂φ| dθ dφ

        After computing the cross product:
        |∂r/∂θ × ∂r/∂φ| = r²·sin(θ)

        A = ∫₀²π ∫₀π r²·sin(θ) dθ dφ
          = r² ∫₀²π dφ ∫₀π sin(θ) dθ
          = r² · 2π · [-cos(θ)]₀π
          = r² · 2π · [1 - (-1)]
          = r² · 2π · 2
          = 4πr² ✓

        Alternative derivation (Archimedes' method):
        The sphere fits perfectly inside a cylinder of radius r and height 2r.
        Cylinder lateral surface: A_cyl = 2πr · 2r = 4πr²
        Archimedes proved the sphere's surface area EQUALS the cylinder's! ✓

        Volume: V = (4/3)πr³
        ---------------------
        Derivation via spherical shells:

        Consider concentric spherical shells of thickness dr at radius ρ.
        Shell surface area = 4πρ²
        Shell volume = 4πρ² dρ

        Integrate from ρ=0 to ρ=r:
        V = ∫₀ʳ 4πρ² dρ
          = 4π [ρ³/3]₀ʳ
          = 4π · r³/3
          = (4/3)πr³ ✓

        Alternative derivation (Cavalieri's principle):
        Compare sphere to hemisphere inscribed in cylinder:
        At height z, the sphere's circular cross-section has radius √(r²-z²).
        Cross-sectional area = π(r²-z²).
        Integrate from -r to +r → V = (4/3)πr³ ✓

        AHA MOMENT #1: PERFECT SYMMETRY - INFINITE AXES
        ================================================
        The sphere possesses MAXIMAL SYMMETRY—more than any other 3D object!

        Rotational Symmetry:
        - INFINITE rotational axes (every diameter is an axis of rotation)
        - Continuous rotational symmetry (rotate by ANY angle → identical)
        - Symmetry group: O(3) (orthogonal group, ALL rotations in 3D)

        Reflection Symmetry:
        - INFINITE planes of symmetry (any plane through center)
        - Every great circle divides sphere into identical hemispheres

        Point Symmetry:
        - Inversion through center: (x,y,z) → (-x,-y,-z) leaves sphere unchanged

        This is why the sphere appears in nature whenever forces act UNIFORMLY
        in all directions:
        - Soap bubbles (surface tension equal in all directions)
        - Planets (gravity pulls equally toward center)
        - Atoms (electron probability clouds)
        - Ball bearings (minimal friction requires isotropy)

        The sphere is the EQUILIBRIUM FORM under isotropic conditions.
        It is the 3D realization of the circle's 2D perfection.

        No other shape has this property. Even the Platonic solids have
        discrete symmetries (finite axes, finite planes). Only the sphere
        has CONTINUOUS, INFINITE symmetry.

        AHA MOMENT #2: ISOPERIMETRIC PROPERTY - MAXIMUM VOLUME
        =======================================================
        The sphere has the LARGEST VOLUME for a given surface area—or
        equivalently, the SMALLEST SURFACE AREA for a given volume!

        This is the ISOPERIMETRIC THEOREM in 3D:

        For any 3D body with surface area A and volume V:
        V ≤ √(A³/(36π))

        With EQUALITY if and only if the body is a SPHERE.

        Equivalently, the sphericity (measure of how sphere-like):
        Ψ = π^(1/3)·(6V)^(2/3) / A

        For sphere: Ψ = 1 (perfect sphericity)
        For cube: Ψ ≈ 0.806
        For tetrahedron: Ψ ≈ 0.671

        The sphere MAXIMIZES Ψ. No other shape is "rounder."

        Why does nature favor spheres?
        - Soap bubbles minimize surface energy → sphere
        - Planets minimize gravitational potential → sphere
        - Water droplets minimize surface tension → sphere
        - Cells often approximate spheres to maximize volume/minimize membrane

        The sphere is the OPTIMAL FORM for:
        1. Maximizing enclosed volume (given surface constraint)
        2. Minimizing exposed surface (given volume constraint)
        3. Minimizing surface energy (physics)
        4. Maximizing structural efficiency (engineering)

        This is the PRINCIPLE OF ECONOMY—nature chooses the sphere when
        efficiency matters. The sphere is the MINIMUM ENERGY configuration
        under isotropic forces.

        AHA MOMENT #3: THE SPHERE AS LIMIT OF PLATONIC SOLIDS
        =======================================================
        The sphere can be viewed as the LIMIT of increasingly complex
        Platonic solids—the form approached as faces → ∞!

        The Platonic Progression:
        - Tetrahedron: 4 faces (least sphere-like, Ψ ≈ 0.671)
        - Cube: 6 faces (Ψ ≈ 0.806)
        - Octahedron: 8 faces (Ψ ≈ 0.846)
        - Dodecahedron: 12 faces (Ψ ≈ 0.910)
        - Icosahedron: 20 faces (Ψ ≈ 0.939, most sphere-like)
        - Sphere: ∞ faces (Ψ = 1.000, PERFECT)

        As we inscribe Platonic solids in a sphere and increase face count,
        the polyhedron's surface approaches the sphere asymptotically:

        lim (faces → ∞) [Platonic solid] = Sphere

        This construction is used in computer graphics (UV sphere mesh):
        - Start with icosahedron (20 triangular faces)
        - Subdivide each triangle into 4 smaller triangles
        - Project new vertices onto circumsphere
        - Repeat → smooth sphere approximation

        The sphere is the CONTINUOUS LIMIT of the discrete Platonic sequence.
        It is the Platonic solid with "infinite symmetry."

        Polyhedral Sphere Approximations:
        - Geodesic domes (Buckminster Fuller): icosahedron subdivisions
        - Soccer ball: truncated icosahedron (32 faces: 12 pentagons + 20 hexagons)
        - Viruses: icosahedral protein shells approximate spheres
        - Fullerenes (C₆₀): truncated icosahedron carbon structure

        The Platonic solids are FINITE SYMMETRY approximations to the
        sphere's INFINITE SYMMETRY. As complexity increases, they approach
        the divine perfection of the sphere.

        HERMETIC NOTE - THE UNIVERSAL MONAD:
        ====================================
        The sphere represents the MONAD—the primordial unity from which
        all forms emerge:

        - **Completeness**: No beginning, no end (like the circle in 3D)
        - **Self-Containment**: Center equidistant from all surface points
        - **Undifferentiated Potential**: All directions equivalent
        - **Divine Perfection**: Maximal symmetry = maximal unity

        Symbolism:
        - **Center**: The unknowable source, the divine spark
        - **Radius**: The distance of manifestation, the ray of creation
        - **Surface**: The boundary of the manifest, the veil of phenomena

        In Mystical Traditions:
        - **Neoplatonic**: The One (infinite, perfect, undivided)
        - **Hermetic**: The cosmic egg, prima materia before differentiation
        - **Kabbalistic**: Kether (Crown), the first emanation
        - **Christian**: The divine perfection, "God is a sphere whose center
          is everywhere and circumference is nowhere" (Pseudo-Dionysius)
        - **Buddhist**: Emptiness (śūnyatā) containing all potential forms

        The sphere is the symbol of THE ABSOLUTE before creation's
        differentiation into the many. All Platonic solids (representing
        elements/forces) are LIMITATIONS of the sphere's infinite perfection.

        Physical Manifestations:
        - **Celestial Bodies**: Planets, stars, moons (gravity → sphere)
        - **Atoms**: Electron probability clouds (quantum spherical harmonics)
        - **Bubbles**: Surface tension minimization
        - **Cells**: Biological efficiency (maximum volume, minimum membrane)

        The sphere is the PRIMORDIAL FORM—the shape of totality, unity,
        and undifferentiated wholeness. It is geometry's symbol of the
        divine, the perfect, the eternal, and the One.

        KEY RATIOS AND PROPERTIES:
        ==========================
        - Surface area to volume ratio: A/V = 3/r
        - Sphere packs optimally: Face-centered cubic = 74% efficiency (Kepler's conjecture)
        - Minimal surface property: A = √(36πV²) for any given V
        - Isoperimetric quotient: Q = V²/(4πA³/3²) = 1 (maximum possible)

        HISTORICAL NOTES:
        =================
        - Archimedes (287-212 BCE): Derived A = 4πr² and V = (4/3)πr³
        - Archimedes' tombstone depicted sphere inscribed in cylinder (his proudest achievement)
        - Kepler (1611): Sphere packing conjecture (proved 1998, Hales)
        - Gauss (1827): Gaussian curvature = constant = 1/r² for sphere
        - Riemann (1854): Sphere as model space (constant positive curvature)
        """
        return SphereMetrics(
            radius=r,
            diameter=2 * r,
            surface_area=4 * math.pi * (r ** 2),
            volume=(4/3) * math.pi * (r ** 3)
        )


class SphereSolidCalculator:
    """Bidirectional calculator for the 3D Sphere."""

    def __init__(self, radius: float = 1.0):
        """
          init   logic.
        
        Args:
            radius: Description of radius.
        
        """
        self._properties = {
            'radius': SolidProperty('Radius (r)', 'radius', 'units', radius),
            'diameter': SolidProperty('Diameter (d)', 'diameter', 'units', 2 * radius),
            'surface_area': SolidProperty('Surface Area (A)', 'surface_area', 'units²', 4 * math.pi * radius**2),
            'volume': SolidProperty('Volume (V)', 'volume', 'units³', (4/3) * math.pi * radius**3),
        }
        self._result: Optional[SphereResult] = None
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
        if value is not None and value <= 0:
            return False
            
        prop = self._properties.get(key)
        if not prop:
            return False
            
        prop.value = value
        
        r = None
        if key == 'radius':
            r = value
        elif key == 'diameter':
            if value is None:
                return False
            r = value / 2
        elif key == 'surface_area':
            if value is None:
                return False
            r = math.sqrt(value / (4 * math.pi))
        elif key == 'volume':
            if value is None:
                return False
            r = (3 * value / (4 * math.pi)) ** (1/3)

        if r is not None:
            self._properties['radius'].value = r
            self._recalculate()
            return True
            
        return False

    def _recalculate(self):
        r = self._properties['radius'].value
        if r is None:
            return
            
        metrics = SphereSolidService.compute_metrics(r)
        self._properties['radius'].value = metrics.radius
        self._properties['diameter'].value = metrics.diameter
        self._properties['surface_area'].value = metrics.surface_area
        self._properties['volume'].value = metrics.volume
        
        self._result = SphereSolidService.build(r)

    def clear(self):
        """
        Clear logic.
        
        """
        for p in self._properties.values():
            p.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        """
        Payload logic.
        
        Returns:
            Result of payload operation.
        """
        return self._result.payload if self._result else None

    def metadata(self) -> dict[str, float]:
        """
        Metadata logic.
        
        Returns:
            Result of metadata operation.
        """
        if not self._result:
            return {}
        return cast(dict[str, float], self._result.payload.metadata)