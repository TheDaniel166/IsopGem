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
        return list(self._properties.values())

    def set_property(self, key: str, value: Optional[float]) -> bool:
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
        for p in self._properties.values():
            p.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)
