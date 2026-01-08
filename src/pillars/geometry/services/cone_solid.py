"""Cone 3D Solid Service."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple, cast

from ..shared.solid_payload import Face, SolidLabel, SolidPayload
from .solid_geometry import Vec3, edges_from_faces
from .solid_property import SolidProperty


@dataclass(frozen=True)
class ConeMetrics:
    """
    Cone Metrics class definition.
    
    """
    radius: float
    height: float
    slant_height: float
    base_circumference: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class ConeResult:
    """
    Cone Result class definition.
    
    """
    payload: SolidPayload
    metrics: ConeMetrics


class ConeSolidService:
    """Generates the geometry for a Cone."""

    @staticmethod
    def build(radius: float = 1.0, height: float = 2.0, segments: int = 32) -> ConeResult:
        """
        Build logic.
        
        Args:
            radius: Description of radius.
            height: Description of height.
            segments: Description of segments.
        
        Returns:
            Result of build operation.
        """
        if radius <= 0 or height <= 0:
            raise ValueError("Radius and Height must be positive")

        metrics = ConeSolidService.compute_metrics(radius, height)
        
        vertices: List[Vec3] = []
        faces: List[Tuple[int, ...]] = []
        
        # Center of base
        vertices.append((0.0, 0.0, 0.0)) # Index 0
        # Base ring
        for i in range(segments):
            angle = i * 2 * math.pi / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), 0.0))
            
        # Apex
        vertices.append((0.0, 0.0, height)) # Index segments + 1
        
        # Base Cap Faces
        for i in range(segments):
            faces.append((0, (i % segments) + 1, ((i + 1) % segments) + 1))
            
        # Lateral Faces (Triangles)
        apex_idx = segments + 1
        for i in range(segments):
            faces.append((apex_idx, ((i + 1) % segments) + 1, (i % segments) + 1))
            
        edges = edges_from_faces(faces)
        
        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=cast(List[Face], faces),
            labels=[
                SolidLabel(text=f"r={radius:.2f}, h={height:.2f}", position=(0, 0, height * 1.05))
            ],
            metadata={
                'radius': radius,
                'height': height,
                'slant_height': metrics.slant_height,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume
            },
            suggested_scale=max(radius * 2, height),
        )
        return ConeResult(payload=payload, metrics=metrics)

    @staticmethod
    def compute_metrics(r: float, h: float) -> ConeMetrics:
        """
        Compute all geometric metrics for a right circular cone.

        DEFINITION:
        ===========
        A cone is the solid formed by connecting all points on a circular base
        to a single apex point directly above the center.

        Parameters:
        - r: Base radius
        - h: Perpendicular height from base to apex
        - l: Slant height (distance from base edge to apex)

        CORE FORMULAS & DERIVATIONS:
        ==============================

        Slant Height: l = √(r² + h²)
        --------------------------------
        Right triangle formed by:
        - Height h (vertical leg)
        - Radius r (horizontal leg)
        - Slant height l (hypotenuse)

        By Pythagorean theorem:
        l² = r² + h²
        l = √(r² + h²) ✓

        Volume: V = (1/3)πr²h
        ----------------------
        Derivation via calculus (disk method):

        At height z from base, the cone's radius is:
        ρ(z) = r(1 - z/h) = r(h-z)/h

        Cross-sectional area: A(z) = πρ(z)² = πr²(h-z)²/h²

        V = ∫₀ʰ A(z) dz
          = ∫₀ʰ πr²(h-z)²/h² dz

        Substitute u = h-z, du = -dz:
          = πr²/h² ∫₀ʰ u² du
          = πr²/h² [u³/3]₀ʰ
          = πr²/h² × h³/3
          = (1/3)πr²h ✓

        AHA MOMENT #1: ONE-THIRD PYRAMID RELATIONSHIP
        ==============================================
        The cone's volume is EXACTLY (1/3) × base area × height!

        This is the FUNDAMENTAL PYRAMID FORMULA—it applies to ALL pyramids
        and cones, regardless of base shape:
        - Cone (circular base): V = (1/3)πr²h
        - Square pyramid: V = (1/3)a²h
        - Triangular pyramid: V = (1/3)(√3/4)a²h
        - ANY pyramid: V = (1/3) × B × h

        Why 1/3?
        It takes EXACTLY THREE pyramids to fill a prism of the same base
        and height! This can be proven via dissection:
        - Cube can be divided into 3 congruent square pyramids
        - Each pyramid has base = cube face, height = cube edge
        - 3 × V_pyramid = V_cube → V_pyramid = (1/3)V_cube

        The factor 1/3 represents the "tapering" of volume as we go from
        base to apex. At the apex, the cross-section vanishes (zero area),
        averaging out to 1/3 of the full prism volume.

        This is the PRINCIPLE OF CONVERGENCE: When parallel cross-sections
        shrink linearly to a point, volume = (1/3) × base × height.

        Lateral Surface Area: A_L = πrl
        ---------------------------------
        The lateral (curved) surface is the "unrolled" sector of a circle!

        When you cut the cone along a generator (slant line) and unroll it,
        you get a circular SECTOR with:
        - Radius = l (slant height)
        - Arc length = 2πr (base circumference)

        Sector area formula: A = (1/2) × radius × arc length
        A_L = (1/2) × l × 2πr = πrl ✓

        AHA MOMENT #2: THE CONE AS UNROLLED SECTOR
        ===========================================
        The cone's lateral surface is a FLAT SECTOR when unrolled!

        The "flattening" reveals the cone's true nature:
        - Central angle of sector: θ = 2πr/l radians = 360° × (r/l)
        - The cone wraps this sector around to form 3D surface

        Examples:
        - If r = l: sector angle = 360° (full circle, very "fat" cone)
        - If r = l/2: sector angle = 180° (semicircle, medium cone)
        - If r → 0: sector angle → 0° (needle-thin cone)

        This is why cone templates for crafts are circular sectors!
        Cut a sector from paper, wrap edge-to-edge → cone.

        The ratio r/l determines the cone's "sharpness":
        - r/l → 0: Very sharp, needle-like (infinitesimal apex angle)
        - r/l = 1/2: Apex angle = 60° (equilateral triangle profile)
        - r/l → 1: Very flat, plate-like (apex angle → 180°)

        The cone is the BRIDGE between 2D (flat sector) and 3D (pointy solid).

        Total Surface Area: A = πr² + πrl = πr(r + l)
        -------------------------------------------------
        Sum of base area and lateral area:
        A = A_base + A_lateral = πr² + πrl = πr(r + l) ✓

        AHA MOMENT #3: CONIC SECTIONS - SLICING THE INFINITE
        ======================================================
        The cone is the GENERATOR of the conic sections—ellipse, parabola,
        hyperbola—the fundamental curves of mathematics!

        When you slice a cone with a plane:
        - Parallel to base: CIRCLE
        - Tilted (angle < apex angle): ELLIPSE
        - Parallel to generator: PARABOLA
        - Steeper (cuts both nappes): HYPERBOLA

        These are the ONLY possible conic sections. Every curve of degree 2
        (quadratic in x,y) is one of these forms.

        Why does slicing a cone create parabolas and hyperbolas?
        The cone embeds 2D projective geometry in 3D space:
        - Points on cone surface: [x:y:z] in projective coordinates
        - Plane intersections: algebraic curves
        - The magic: degree-2 surface × degree-1 plane = degree-2 curve

        Historical Significance:
        - Ancient Greeks (Apollonius, 200 BCE): Discovered conic sections
        - Kepler (1609): Planetary orbits are ELLIPSES (conic sections!)
        - Galileo (1638): Projectile paths are PARABOLAS
        - Newton (1687): Inverse-square gravity → conic orbits

        The cone is the COSMIC GEOMETRY of orbital mechanics:
        - Bound orbits (E<0): ellipse
        - Escape trajectory (E=0): parabola
        - Hyperbolic trajectory (E>0): hyperbola

        Every satellite, comet, asteroid follows a path drawn by slicing
        an imaginary cone in phase space! The cone is the ARCHETYPE of
        gravitational motion.

        HERMETIC NOTE - THE CONE OF MANIFESTATION:
        ===========================================
        The cone represents EMANATION FROM UNITY:

        - Apex: The divine point, source of all (the Monad)
        - Height: The axis of descent from spirit to matter
        - Base: The manifold world, multiplicity of forms
        - Generators: Rays of creation from apex to base

        As you descend from apex (unity) to base (multiplicity), the
        circle of manifestation GROWS. The cone is the geometry of
        EXPANSION FROM SINGULARITY.

        Symbolism:
        - Apex above: Heaven, the spiritual realm
        - Base below: Earth, the material realm
        - Slant lines: Paths of souls descending into matter
        - Volume (1/3): The fraction of divine essence that manifests

        The cone is the INVERSE of the pyramid:
        - Pyramid: Base on earth, apex reaches heaven (ascent)
        - Cone: Apex in heaven, base on earth (descent)

        Together they form the DOUBLE CONE (two cones apex-to-apex),
        the hourglass of eternal cycle: spirit ↔ matter, descent ↔ ascent.
        """
        slant = math.sqrt(r**2 + h**2)
        base_area = math.pi * (r ** 2)
        lateral_area = math.pi * r * slant
        circumference = 2 * math.pi * r
        return ConeMetrics(
            radius=r,
            height=h,
            slant_height=slant,
            base_circumference=circumference,
            base_area=base_area,
            lateral_area=lateral_area,
            surface_area=base_area + lateral_area,
            volume=(1/3) * base_area * h
        )


class ConeSolidCalculator:
    """Bidirectional calculator for the 3D Cone."""

    def __init__(self, radius: float = 1.0, height: float = 2.0):
        """
          init   logic.
        
        Args:
            radius: Description of radius.
            height: Description of height.
        
        """
        self._properties = {
            'radius': SolidProperty('Radius (r)', 'radius', 'units', radius),
            'height': SolidProperty('Height (h)', 'height', 'units', height),
            'slant_height': SolidProperty('Slant Height (s)', 'slant_height', 'units', 0.0, editable=True),
            'base_circumference': SolidProperty('Base Circumference (C)', 'base_circumference', 'units', 0.0, editable=True),
            'base_area': SolidProperty('Base Area (B)', 'base_area', 'units²', 0.0, editable=True),
            'lateral_area': SolidProperty('Lateral Area (L)', 'lateral_area', 'units²', 0.0, editable=True),
            'surface_area': SolidProperty('Surface Area (A)', 'surface_area', 'units²', 0.0, editable=True),
            'volume': SolidProperty('Volume (V)', 'volume', 'units³', 0.0, editable=True),
        }
        self._result: Optional[ConeResult] = None
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
            
        r = self._properties['radius'].value
        h = self._properties['height'].value
        
        if key == 'radius':
            r = value
        elif key == 'height':
            h = value
        elif key == 'slant_height':
            # Solve for height keeping radius constant
            if value is None or r is None:
                return False
            h = math.sqrt(max(0, value**2 - r**2))
        elif key == 'base_circumference':
            if value is None:
                return False
            r = value / (2 * math.pi)
        elif key == 'base_area':
            if value is None:
                return False
            r = math.sqrt(value / math.pi)
        elif key == 'lateral_area':
            # L = pi * r * s. 
            # If r is fixed/known, solve for s, then h.
            if value is None:
                return False
            if r and r > 0:
                s = value / (math.pi * r)
                if s > r:
                    h = math.sqrt(s**2 - r**2)
                else: 
                     return False
            elif h and h > 0:
                # L = pi * r * sqrt(r^2 + h^2)
                # L^2 = pi^2 * r^2 * (r^2 + h^2)
                # pi^2*r^4 + pi^2*h^2*r^2 - L^2 = 0
                # Quadratic in X = r^2.
                # a = pi^2, b = pi^2*h^2, c = -L^2
                a_q = math.pi**2
                b_q = math.pi**2 * h**2
                c_q = -value**2
                
                delta = b_q**2 - 4*a_q*c_q
                if delta >= 0:
                    r_sq = (-b_q + math.sqrt(delta)) / (2 * a_q)
                    if r_sq > 0:
                        r = math.sqrt(r_sq)
                    else:
                        return False
                else:
                    return False
        
        elif key == 'surface_area':
            # A = pi*r*(r+s) => A/pi = r^2 + r*s => r*s = (A/pi) - r^2
            # s = (A/(pi*r)) - r
            # h = sqrt(s^2 - r^2)
            
            # Prioritize solving for h if r is valid
            if value is None:
                return False
            if r and r > 0:
                term = value / (math.pi * r)
                s = term - r
                if s > r:
                    h = math.sqrt(s**2 - r**2)
                else:
                    return False
            else:
                # Harder to solve for r if h is fixed?
                return False

        elif key == 'volume':
            # Solve for height keeping radius constant
            if value is None or r is None:
                return False
            h = (3 * value) / (math.pi * r**2)
            
        self._properties['radius'].value = r
        self._properties['height'].value = h
        self._recalculate()
        return True

    def _recalculate(self):
        r = self._properties['radius'].value
        h = self._properties['height'].value
        if r is None or h is None:
            return
            
        metrics = ConeSolidService.compute_metrics(r, h)
        self._properties['slant_height'].value = metrics.slant_height
        self._properties['base_circumference'].value = metrics.base_circumference
        self._properties['base_area'].value = metrics.base_area
        self._properties['lateral_area'].value = metrics.lateral_area
        self._properties['surface_area'].value = metrics.surface_area
        self._properties['volume'].value = metrics.volume
        
        self._result = ConeSolidService.build(r, h)

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

    def metrics(self) -> Optional[ConeMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None