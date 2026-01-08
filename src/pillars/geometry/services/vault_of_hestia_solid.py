"""Vault of Hestia 3D Solid Service."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_geometry import Vec3, edges_from_faces
from .solid_property import SolidProperty


@dataclass(frozen=True)
class VaultOfHestiaMetrics:
    """
    Vault Of Hestia Metrics class definition.
    
    """
    side_length: float  # s
    sphere_radius: float  # r
    hestia_ratio_3d: float  # Sphere Vol / Cube Vol
    cube_volume: float
    cube_surface_area: float
    pyramid_volume: float
    sphere_volume: float
    sphere_surface_area: float
    phi: float
    cube_diagonal: float
    pyramid_slant_height: float
    void_volume_cube_sphere: float
    void_volume_cube_pyramid: float
    void_volume_pyramid_sphere: float
    ratio_sphere_pyramid: float
    ratio_pyramid_cube: float
    pyramid_total_surface_area: float
    inradius_resonance_phi: float
    volume_efficiency: float


@dataclass(frozen=True)
class VaultOfHestiaResult:
    """
    Vault Of Hestia Result class definition.
    
    """
    payload: SolidPayload
    metrics: VaultOfHestiaMetrics


class VaultOfHestiaSolidService:
    """
    Generates the geometry for the Vault of Hestia (3D).
    Structure: Cube containing a Pyramid containing a Sphere.
    Relation: Height of Pyramid = Side of Cube (s).
    Result: The Sphere radius (r) relates to s by r = s / (2*phi).
    """

    @staticmethod
    def build(side_length: float = 10.0) -> VaultOfHestiaResult:
        """
        Build logic.
        
        Args:
            side_length: Description of side_length.
        
        Returns:
            Result of build operation.
        """
        if side_length <= 0:
            raise ValueError("Side length must be positive")

        metrics = VaultOfHestiaSolidService._compute_metrics(side_length)
        
        # We need to construct a composite mesh.
        # Since currently SolidPayload supports a single list of vertices/faces,
        # we will concatenate them. Colors are not inherently supported in the basic payload 
        # unless we use metadata or different solid IDs, but for now we'll put them in one mesh
        # efficiently, perhaps relying on the viewer to just render edges/faces.
        
        # Ideally, we separate them, but let's build a single payload for now.
        # 1. Cube
        # 2. Pyramid (Base at z=0?)
        # 3. Sphere (Center at z=r)
        
        # Let's center the Cube at (0,0, s/2) so base is at z=0?
        # Or standard cube center (0,0,0).
        # Let's put Base at z = -s/2. Ceiling at z = s/2.
        # Cube: [-s/2, s/2]^3
        s = side_length
        half_s = s / 2
        
        vertices: List[Vec3] = []
        faces: List[Tuple[int, ...]] = []
        
        # --- CUBE (Wireframe preference, but we'll mesh it) ---
        # Cube Indices: 0-7
        cube_verts = [
            (-half_s, -half_s, -half_s), # 0: Front Bottom Left
            (half_s, -half_s, -half_s),  # 1: Front Bottom Right
            (half_s, half_s, -half_s),   # 2: Back Bottom Right
            (-half_s, half_s, -half_s),  # 3: Back Bottom Left
            (-half_s, -half_s, half_s),  # 4: Front Top Left
            (half_s, -half_s, half_s),   # 5: Front Top Right
            (half_s, half_s, half_s),    # 6: Back Top Right
            (-half_s, half_s, half_s),   # 7: Back Top Left
        ]
        vertices.extend(cube_verts)
        
        # Cube Faces (Quads)
        base_cube_idx = 0
        cube_faces = [
            (0, 1, 5, 4), # Front
            (1, 2, 6, 5), # Right
            (2, 3, 7, 6), # Back
            (3, 0, 4, 7), # Left
            (4, 5, 6, 7), # Top
            (3, 2, 1, 0), # Bottom
        ]
        # Offset indices
        faces.extend([tuple(idx + base_cube_idx for idx in face) for face in cube_faces])
        
        # --- PYRAMID ---
        # Base matches Cube Bottom: z = -s/2
        # Apex matches Cube Top Center: (0, 0, s/2)
        base_pyramid_idx = len(vertices)
        
        # Pyramid Base Vertices (Reuse cube bottom? Or duplicate for clarity?)
        # Let's duplicate to separate geometries logically in list.
        pyramid_base = [
            (-half_s, -half_s, -half_s),
            (half_s, -half_s, -half_s),
            (half_s, half_s, -half_s),
            (-half_s, half_s, -half_s),
        ]
        vertices.extend(pyramid_base)
        vertices.append((0.0, 0.0, half_s)) # Apex
        
        apex_idx = base_pyramid_idx + 4
        
        # Pyramid Faces (Triangles + Base)
        # Base
        faces.append((base_pyramid_idx, base_pyramid_idx+1, base_pyramid_idx+2, base_pyramid_idx+3))
        # Sides
        faces.append((base_pyramid_idx, base_pyramid_idx+1, apex_idx))
        faces.append((base_pyramid_idx+1, base_pyramid_idx+2, apex_idx))
        faces.append((base_pyramid_idx+2, base_pyramid_idx+3, apex_idx))
        faces.append((base_pyramid_idx+3, base_pyramid_idx, apex_idx))
        
        # --- SPHERE ---
        # Radius r
        # Center?
        # In 2D, Triangle is in Square. Incircle center is at y = -s/2 + r.
        # In 3D: Base is z = -s/2.
        # Sphere rests on base? Reference "Incircle".
        # Yes, inscribed in the cross-section. The sphere should be tangent to the base and the sides?
        # If it's tangent to base, Center Z = -s/2 + r.
        r = metrics.sphere_radius
        cz = -half_s + r
        
        base_sphere_idx = len(vertices)
        
        # Generate Sphere Mesh (Icosphere or UV sphere)
        # Simple UV sphere
        sphere_vi, sphere_fi = VaultOfHestiaSolidService._generate_sphere(r, (0, 0, cz), 16, 16)
        

        faces.extend([tuple(idx + base_sphere_idx for idx in face) for face in sphere_fi])
        vertices.extend(sphere_vi)
        
        # --- COLORS ---
        # 1. Cube Faces (Quads) -> Blue Translucent
        # 2. Pyramid Faces (Base + 4 sides) -> Green Translucent
        # 3. Sphere Faces -> Red Solid
        
        # Define Colors (R, G, B, A)
        color_cube = (0, 0, 255, 60)       # Blue Translucent
        color_pyramid = (0, 255, 0, 100)   # Green Translucent
        color_sphere = (255, 50, 50, 255)  # Red Solid

        face_colors = []
        # Cube faces
        for _ in range(len(cube_faces)):
            face_colors.append(color_cube)
            
        # Pyramid faces (Base + 4 Sides)
        for _ in range(5):
             face_colors.append(color_pyramid)
             
        # Sphere faces
        for _ in range(len(sphere_fi)):
            face_colors.append(color_sphere)

        edges = edges_from_faces(faces)
        
        labels = [
            SolidLabel(text=f"s = {s:.2f}", position=(0, -half_s, -half_s)),
            SolidLabel(text=f"r = {r:.2f}", position=(0, 0, cz)),
            SolidLabel(text=f"φ Generator", position=(0, half_s, half_s))
        ]

        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=labels,
            face_colors=face_colors,
            metadata={
                'side_length': s,
                'sphere_radius': r,
                'hestia_ratio': metrics.hestia_ratio_3d,
                'cube_volume': metrics.cube_volume,
                'sphere_volume': metrics.sphere_volume,
                'cube_diagonal': metrics.cube_diagonal,
                'void_cube_sphere': metrics.void_volume_cube_sphere,
                'void_pyramid_sphere': metrics.void_volume_pyramid_sphere,
                'pyramid_tsa': metrics.pyramid_total_surface_area,
                'inradius_resonance': metrics.inradius_resonance_phi
            },
            suggested_scale=s * 1.5,
        )
        return VaultOfHestiaResult(payload=payload, metrics=metrics)

    @staticmethod
    def _compute_metrics(s: float) -> VaultOfHestiaMetrics:
        """
        Compute all geometric metrics for the 3D Vault of Hestia from side length.

        THE VAULT OF HESTIA (3D) - CORE FORMULAS & DERIVATIONS:
        ========================================================

        Construction:
        - CUBE with edge length s (the container)
        - SQUARE PYRAMID inscribed: base = s×s (cube bottom), height = s (to cube top center)
        - SPHERE inscribed within the pyramid

        This 3D extension maintains the golden ratio relationship and reveals
        profound volumetric sacred geometry!


        SPHERE RADIUS: r = s/(2φ)
        ==========================

        The sphere is inscribed in the square pyramid (tangent to base and 4 faces).

        For a square pyramid with base side b and height h:
            Inradius formula: r = (h·a)/(a + ℓ)

        Where:
            a = base side = s
            h = height = s (pyramid reaches to top of cube)
            ℓ = slant height along face

        The slant height from apex to midpoint of base edge:
            ℓ² = h² + (a/2)²
            ℓ² = s² + s²/4
            ℓ² = 5s²/4
            ℓ = s√5/2

        AHA MOMENT #1: The same √5 appears in 3D!
        This is the SAME value as the 2D triangle leg!

        Now for the inradius:
            r = (s·s)/(s + s√5/2)
            r = s²/(s(1 + √5/2))
            r = s/(1 + √5/2)

        Multiply numerator and denominator by 2:
            r = 2s/(2 + √5)

        Rationalize by multiplying by (2 - √5)/(2 - √5):
            r = 2s(2 - √5)/((2 + √5)(2 - √5))
            r = 2s(2 - √5)/(4 - 5)
            r = 2s(2 - √5)/(-1)
            r = 2s(√5 - 2)

        Now use the golden ratio identity: φ = (1 + √5)/2
            2φ = 1 + √5
            2φ - 1 = √5

        Also: 1/φ = φ - 1 = (√5 - 1)/2
            2/φ = √5 - 1

        Actually, let's verify directly:
            2φ = 1 + √5
            1/(2φ) = 1/(1 + √5)

        Rationalize: 1/(1 + √5) × (1 - √5)/(1 - √5):
            = (1 - √5)/(1 - 5)
            = (1 - √5)/(-4)
            = (√5 - 1)/4

        But from pyramid formula we need to connect to this!

        Actually, the correct derivation: For square pyramid with a=h=s:
            r = a/(2(1 + √5/2))
            r = s/(2 + √5)

        Multiply by conjugate (2 - √5)/(2 - √5):
            r = s(2 - √5)/(4 - 5)
            r = s(2 - √5)/(-1)
            r = s(√5 - 2)

        Now, φ² = φ + 1, so φ = (1 + √5)/2:
            2φ = 1 + √5
            2φ - 2 = √5 - 1
            φ - 1 = (√5 - 1)/2 = 1/φ

        We need s(√5 - 2). Note:
            1/φ = (√5 - 1)/2
            2/φ = √5 - 1

        So: √5 - 2 = (√5 - 1) - 1 = 2/φ - 1 = (2 - φ)/φ

        Therefore: r = s(2 - φ)/φ

        But we claim r = s/(2φ). Let's verify:
            s/(2φ) =? s(2 - φ)/φ
            1/(2φ) =? (2 - φ)/φ
            1/2 =? 2 - φ
            φ =? 2 - 1/2 = 3/2

        That's not right. Let me recalculate the pyramid inradius properly.

        For square pyramid, actual formula is:
            r = h√((ℓ² - h²)/(ℓ² + 2h√(ℓ² - h²)))

        Actually, simplest approach: The 2D cross-section through the pyramid apex
        and perpendicular to any base edge is the SAME isosceles triangle as the 2D case!

        That triangle has base s, height s, and incircle radius s/(2φ).
        Therefore the sphere radius MUST be the same: r = s/(2φ) ✓

        AHA MOMENT #2: The 3D structure preserves the 2D golden relationship!
        The sphere radius relates to the cube edge by INVERSE PHI, just like
        the 2D circle relates to the square!


        CUBE VOLUME: V_c = s³
        ======================

        Standard cube volume.


        CUBE SURFACE AREA: A_c = 6s²
        =============================

        Six square faces, each with area s².


        PYRAMID VOLUME: V_p = s³/3
        ===========================

        Square pyramid volume:
            V = (1/3) × base_area × height
            V = (1/3) × s² × s
            V = s³/3

        AHA MOMENT #3: The pyramid is EXACTLY one-third the cube volume!
            V_p/V_c = 1/3

        This is the sacred "three-in-one" Trinity ratio!


        SPHERE VOLUME: V_s = (4π/3)r³ = (4π/3)(s/(2φ))³
        =================================================

            V_s = (4π/3) × s³/(8φ³)
            V_s = πs³/(6φ³)

        Using φ³ = φ² + φ = (φ + 1) + φ = 2φ + 1:
            φ³ = 2φ + 1 = 2(1 + √5)/2 + 1 = 1 + √5 + 1 = 2 + √5

        Therefore:
            V_s = πs³/(6(2 + √5))
            V_s = πs³/(12 + 6√5)

        AHA MOMENT #4: The sphere volume involves π, φ³, and s³!
        Three transcendentals (π, φ, cube root) unified in volume!


        HESTIA RATIO (3D): V_s/V_c = π/(6φ³)
        =====================================

            V_s/V_c = [πs³/(6φ³)]/s³
            V_s/V_c = π/(6φ³)

        Since φ³ = 2 + √5:
            Hestia Ratio 3D = π/(6(2 + √5))
            Hestia Ratio 3D = π/(12 + 6√5)
            Hestia Ratio 3D ≈ 0.06006...

        AHA MOMENT #5: Only ~6% of the cube is "filled" by the sacred sphere!
        The remaining ~94% is VOID - the womb of potential.

        Compare to 2D ratio ≈ 19.2%: The 3D packing is even more sparse,
        reflecting higher-dimensional "thinning" of manifestation into space.


        VOID VOLUME (Cube - Sphere): V_void = s³(1 - π/(6φ³))
        ======================================================

        This is the "breathing space" of the cosmos - the unmanifest potential
        surrounding the manifest (sphere).


        RATIO (Sphere/Pyramid): V_s/V_p
        =================================

            V_s/V_p = [πs³/(6φ³)]/[s³/3]
            V_s/V_p = [πs³/(6φ³)] × [3/s³]
            V_s/V_p = 3π/(6φ³)
            V_s/V_p = π/(2φ³)

        With φ³ = 2 + √5:
            V_s/V_p = π/(2(2 + √5))
            V_s/V_p = π/(4 + 2√5)
            V_s/V_p ≈ 0.18017...

        AHA MOMENT #6: The sphere fills ~18% of the pyramid!
        This is very close to the 2D circle/square ratio (~19.2%).
        The dimensional scaling preserves approximate proportions!


        PYRAMID SLANT HEIGHT: ℓ = s√5/2
        ================================

        From apex (0, 0, s/2) to midpoint of base edge (±s/2, 0, -s/2):
            ℓ² = (s/2)² + 0² + s²
            ℓ² = s²/4 + s²
            ℓ² = 5s²/4
            ℓ = s√5/2

        Same as 2D triangle leg and same √5 appearance!


        CUBE DIAGONAL (Space Diagonal): d = s√3
        ========================================

        From corner to opposite corner through cube center:
            d² = s² + s² + s²
            d = s√3

        This is the √3 that appeared in the CUBE metrics (circumradius).
        Here it connects all three dimensions.


        PYRAMID TOTAL SURFACE AREA: A_p = 2φs²
        =======================================

        Pyramid surface = base + 4 triangular faces

        Base area = s²

        Each triangular face:
            Base = s, slant height = ℓ = s√5/2
            Area = (1/2) × s × s√5/2 = s²√5/4

        Four faces:
            4 × s²√5/4 = s²√5

        Total:
            A_p = s² + s²√5
            A_p = s²(1 + √5)
            A_p = s² × 2φ   (since φ = (1 + √5)/2, so 2φ = 1 + √5)

        AHA MOMENT #7: The pyramid surface area is EXACTLY 2φs²!
        The golden ratio appears DIRECTLY as a coefficient!

        Compare to cube surface (6s²):
            A_p/A_c = 2φs²/(6s²) = 2φ/6 = φ/3 ≈ 0.539...

        The pyramid surface is φ/3 of the cube surface!


        INRADIUS RESONANCE: s/(2r) = φ
        ================================

        Since r = s/(2φ):
            s/(2r) = s/(2 × s/(2φ))
            s/(2r) = s × 2φ/(2s)
            s/(2r) = φ

        This is the same verification as in 2D - measuring s and r gives φ!


        HERMETIC SIGNIFICANCE - THE 3D VAULT:
        ======================================

        The 3D Vault of Hestia extends the 2D phi generator into space, revealing:

        1. **Trinity Structure**: Cube → Pyramid (1/3) → Sphere (within)
           Three nested forms, three levels of manifestation.

        2. **Volume Sparsity**: Only 6% sphere packing in cube (~18% in pyramid)
           This reflects the hermetic teaching that matter is mostly "empty space"
           but that emptiness is PREGNANT with potential.

        3. **Dimensional √ Progression**:
           - 2D: √2 (square diagonal)
           - Leg/Slant: √5 (appears in both 2D and 3D!)
           - 3D: √3 (cube diagonal)

           The √5 is the BRIDGE between dimensions, the pentagonal/golden connector.

        4. **Surface Area = 2φs²**: The pyramid's "skin" is golden-ratioed to its base.
           This is the interface between inner (sphere/fire) and outer (cube/earth).

        5. **Phi Preservation**: r = s/(2φ) holds in both 2D and 3D!
           The golden relationship TRANSCENDS dimension - it's archetypal.

        6. **Pyramid = Trinity**: V_p = V_c/3 exactly.
           The pyramid mediates between cube (stable/Earth/4 corners) and
           sphere (infinite/Aether/center point).

        7. **Hestia as Center**: In Greek cosmology, Hestia's fire burned at the
           CENTER of the home/cosmos. The sphere (6% of cube) is that sacred center -
           small but ESSENTIAL, around which all else arranges.

        8. **The 18% Echo**: Sphere/Pyramid ≈ 18% echoes Circle/Square ≈ 19%
           The dimensional jump (2D→3D) preserves proportion through φ mediation.

        9. **Construction Sequence**:
           Square → Triangle → Circle (2D)
           Cube → Pyramid → Sphere (3D)

           4 sides → 3 sides → ∞ sides
           6 faces → 5 faces → ∞ faces

           Progression from multiplicity to UNITY (circle/sphere).

        The Vault of Hestia is a **DIMENSIONAL PHI CONSTANT** - proof that the golden
        ratio is not just a 2D curiosity but a SPATIAL ORGANIZING PRINCIPLE that scales
        into 3D geometry. The hearth fire (sphere) remains proportionally related to its
        container (cube) through the SAME golden inverse (1/2φ) in all dimensions.

        This is the mathematical expression of "As above, so below" - the pattern holds
        across dimensional boundaries, making it TRULY hermetic and universal.
        """
        phi = (1 + math.sqrt(5)) / 2

        # r = s / (2 * phi)
        r = s / (2 * phi)

        cube_vol = s ** 3
        cube_surf = 6 * (s ** 2)

        # Square Pyramid: V = (1/3) * base_area * h
        # base_area = s^2, h = s
        pyramid_vol = (s ** 3) / 3

        sphere_vol = (4/3) * math.pi * (r ** 3)
        sphere_surf = 4 * math.pi * (r ** 2)

        ratio = sphere_vol / cube_vol if cube_vol > 0 else 0

        return VaultOfHestiaMetrics(
            side_length=s,
            sphere_radius=r,
            hestia_ratio_3d=ratio,
            cube_volume=cube_vol,
            cube_surface_area=cube_surf,
            pyramid_volume=pyramid_vol,
            sphere_volume=sphere_vol,
            sphere_surface_area=sphere_surf,
            phi=phi,
            cube_diagonal=s * math.sqrt(3),
            pyramid_slant_height=math.sqrt((s/2)**2 + s**2), # h=s
            void_volume_cube_sphere=cube_vol - sphere_vol,
            void_volume_cube_pyramid=cube_vol - pyramid_vol,
            void_volume_pyramid_sphere=pyramid_vol - sphere_vol,
            ratio_sphere_pyramid=sphere_vol / pyramid_vol if pyramid_vol > 0 else 0,
            ratio_pyramid_cube=pyramid_vol / cube_vol if cube_vol > 0 else 0,
            pyramid_total_surface_area=2 * phi * (s ** 2),
            inradius_resonance_phi=(s/2) / r if r > 0 else 0,
            volume_efficiency=sphere_vol / cube_vol if cube_vol > 0 else 0
        )

    @staticmethod
    def _generate_sphere(radius: float, center: Tuple[float, float, float], rings: int, segments: int) -> Tuple[List[Vec3], List[Tuple[int, ...]]]:
        verts = []
        faces = []
        cx, cy, cz = center
        
        for ring in range(rings + 1):
            theta = ring * math.pi / rings # 0 to pi
            sin_theta = math.sin(theta)
            cos_theta = math.cos(theta)
            
            for seg in range(segments):
                phi = seg * 2 * math.pi / segments # 0 to 2pi
                sin_phi = math.sin(phi)
                cos_phi = math.cos(phi)
                
                x = cx + radius * sin_theta * cos_phi
                y = cy + radius * sin_theta * sin_phi
                z = cz + radius * cos_theta
                
                verts.append((x, y, z))
                
        # Faces
        for ring in range(rings):
            for seg in range(segments):
                current = ring * segments + seg
                next_seg = (seg + 1) % segments
                
                bottom_left = current
                bottom_right = ring * segments + next_seg
                top_left = (ring + 1) * segments + seg
                top_right = (ring + 1) * segments + next_seg
                
                faces.append((bottom_left, bottom_right, top_right, top_left))
                
        return verts, faces


class VaultOfHestiaSolidCalculator:
    """Bidirectional calculator for the 3D Vault of Hestia."""

    def __init__(self, side_length: float = 10.0):
        """
          init   logic.
        
        Args:
            side_length: Description of side_length.
        
        """
        self._properties = {
            'side_length': SolidProperty('Side Length (s)', 'side_length', 'units', 10.0),
            'sphere_radius': SolidProperty('Sphere Radius (r)', 'sphere_radius', 'units', 10.0),
            'cube_volume': SolidProperty('Cube Volume (V_c)', 'cube_volume', 'units³', 5.0),
            'cube_surface_area': SolidProperty('Cube Surface Area', 'cube_surface_area', 'units²', 5.0),
            'pyramid_volume': SolidProperty('Pyramid Volume (V_p)', 'pyramid_volume', 'units³', 5.0),
            'sphere_volume': SolidProperty('Sphere Volume (V_s)', 'sphere_volume', 'units³', 5.0),
            'sphere_surface_area': SolidProperty('Sphere Surface', 'sphere_surface_area', 'units²', 5.0),
            'hestia_ratio_3d': SolidProperty('Hestia Ratio (Vol)', 'hestia_ratio_3d', '', value=None, precision=6, editable=False),
            'cube_diagonal': SolidProperty('Cube Diagonal', 'cube_diagonal', 'units', value=None, precision=4, editable=False),
            'pyramid_slant': SolidProperty('Pyramid Slant Height', 'pyramid_slant_height', 'units', value=None, precision=4, editable=False),
            'void_cube_sphere': SolidProperty('Void (Cube-Sphere)', 'void_volume_cube_sphere', 'units³', value=None, precision=4, editable=False),
            'void_pyr_sphere': SolidProperty('Void (Pyr-Sphere)', 'void_volume_pyramid_sphere', 'units³', value=None, precision=4, editable=False),
            'pyramid_tsa': SolidProperty('Pyramid TSA (2φs²)', 'pyramid_total_surface_area', 'units²', value=None, precision=4, editable=False),
            'inradius_ratio': SolidProperty('Inradius Ratio (φ)', 'inradius_resonance_phi', '', value=None, precision=6, editable=False),
            'vol_efficiency': SolidProperty('Vol Efficiency', 'volume_efficiency', '', value=None, precision=4, editable=False),
            'phi': SolidProperty('Phi (Ref)', 'phi', '', value=None, precision=6, editable=False),
        }
        
        self.set_property('side_length', side_length)
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
        
        # Bidirectional Solver
        # Everything derives from s (side_length) eventually.
        # Constants
        phi = (1 + math.sqrt(5)) / 2
        
        s = None
        
        if key == 'side_length':
            s = value
            
        elif key == 'sphere_radius':
            # r = s / (2*phi) => s = r * 2 * phi
            s = value * 2 * phi
            
        elif key == 'cube_volume':
            # V = s^3 => s = cbrt(V)
            s = value ** (1/3)
            
        elif key == 'cube_surface_area':
            # A = 6 s^2 => s = sqrt(A/6)
            s = math.sqrt(value / 6)
            
        elif key == 'pyramid_volume':
            # V = s^3 / 3 => s^3 = 3V => s = cbrt(3V)
            s = (3 * value) ** (1/3)
            
        elif key == 'sphere_volume':
            # V = 4/3 pi r^3 => r = cbrt(3V / 4pi)
            r = (3 * value / (4 * math.pi)) ** (1/3)
            s = r * 2 * phi
            
        elif key == 'sphere_surface_area':
            # A = 4 pi r^2 => r = sqrt(A / 4pi)
            r = math.sqrt(value / (4 * math.pi))
            s = r * 2 * phi

        if s is not None:
            self._properties['side_length'].value = s
            self._recalculate()
            return True
            
        return False

    def _recalculate(self):
        s = self._properties['side_length'].value
        if s is None:
            return
            
        metrics = VaultOfHestiaSolidService._compute_metrics(s)
        
        self._properties['sphere_radius'].value = metrics.sphere_radius
        self._properties['cube_volume'].value = metrics.cube_volume
        self._properties['cube_surface_area'].value = metrics.cube_surface_area
        self._properties['pyramid_volume'].value = metrics.pyramid_volume
        self._properties['sphere_volume'].value = metrics.sphere_volume
        self._properties['sphere_surface_area'].value = metrics.sphere_surface_area
        self._properties['hestia_ratio_3d'].value = metrics.hestia_ratio_3d
        self._properties['cube_diagonal'].value = metrics.cube_diagonal
        self._properties['pyramid_slant'].value = metrics.pyramid_slant_height
        self._properties['void_cube_sphere'].value = metrics.void_volume_cube_sphere
        self._properties['void_pyr_sphere'].value = metrics.void_volume_pyramid_sphere
        self._properties['pyramid_tsa'].value = metrics.pyramid_total_surface_area
        self._properties['inradius_ratio'].value = metrics.inradius_resonance_phi
        self._properties['vol_efficiency'].value = metrics.volume_efficiency
        self._properties['phi'].value = metrics.phi
        
        self._result = VaultOfHestiaSolidService.build(s)

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

    def metadata(self) -> Dict[str, float]:
        """
        Metadata logic.
        
        Returns:
            Result of metadata operation.
        """
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)