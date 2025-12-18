"""Sphere 3D Solid Service."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..shared.solid_payload import SolidLabel, SolidPayload
固geometry import Vec3, edges_from_faces
固property import SolidProperty


@dataclass(frozen=True)
class SphereMetrics:
    radius: float
    diameter: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class SphereResult:
    payload: SolidPayload
    metrics: SphereMetrics


class SphereSolidService:
    """Generates the geometry for a Sphere (UV Sphere mesh)."""

    @staticmethod
    def build(radius: float = 1.0, rings: int = 16, segments: int = 32) -> SphereResult:
        if radius <= 0:
            raise ValueError("Radius must be positive")

        metrics = SphereSolidService._compute_metrics(radius)
        
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
            faces=faces,
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
    def _compute_metrics(r: float) -> SphereMetrics:
        return SphereMetrics(
            radius=r,
            diameter=2 * r,
            surface_area=4 * math.pi * (r ** 2),
            volume=(4/3) * math.pi * (r ** 3)
        )


class SphereSolidCalculator:
    """Bidirectional calculator for the 3D Sphere."""

    def __init__(self, radius: float = 1.0):
        self._properties = {
            'radius': SolidProperty('Radius (r)', 'radius', 'units', radius),
            'diameter': SolidProperty('Diameter (d)', 'diameter', 'units', 2 * radius),
            'surface_area': SolidProperty('Surface Area (A)', 'surface_area', 'units²', 4 * math.pi * radius**2),
            'volume': SolidProperty('Volume (V)', 'volume', 'units³', (4/3) * math.pi * radius**3),
        }
        self._result: Optional[SphereResult] = None
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
        
        r = None
        if key == 'radius':
            r = value
        elif key == 'diameter':
            r = value / 2
        elif key == 'surface_area':
            r = math.sqrt(value / (4 * math.pi))
        elif key == 'volume':
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
            
        metrics = SphereSolidService._compute_metrics(r)
        self._properties['radius'].value = metrics.radius
        self._properties['diameter'].value = metrics.diameter
        self._properties['surface_area'].value = metrics.surface_area
        self._properties['volume'].value = metrics.volume
        
        self._result = SphereSolidService.build(r)

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
