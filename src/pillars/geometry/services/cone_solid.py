"""Cone 3D Solid Service."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_geometry import Vec3, edges_from_faces
from .solid_property import SolidProperty


@dataclass(frozen=True)
class ConeMetrics:
    radius: float
    height: float
    slant_height: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class ConeResult:
    payload: SolidPayload
    metrics: ConeMetrics


class ConeSolidService:
    """Generates the geometry for a Cone."""

    @staticmethod
    def build(radius: float = 1.0, height: float = 2.0, segments: int = 32) -> ConeResult:
        if radius <= 0 or height <= 0:
            raise ValueError("Radius and Height must be positive")

        metrics = ConeSolidService._compute_metrics(radius, height)
        
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
            faces=faces,
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
    def _compute_metrics(r: float, h: float) -> ConeMetrics:
        slant = math.sqrt(r**2 + h**2)
        base_area = math.pi * (r ** 2)
        lateral_area = math.pi * r * slant
        return ConeMetrics(
            radius=r,
            height=h,
            slant_height=slant,
            base_area=base_area,
            lateral_area=lateral_area,
            surface_area=base_area + lateral_area,
            volume=(1/3) * base_area * h
        )


class ConeSolidCalculator:
    """Bidirectional calculator for the 3D Cone."""

    def __init__(self, radius: float = 1.0, height: float = 2.0):
        self._properties = {
            'radius': SolidProperty('Radius (r)', 'radius', 'units', radius),
            'height': SolidProperty('Height (h)', 'height', 'units', height),
            'slant_height': SolidProperty('Slant Height (s)', 'slant_height', 'units', 0.0, editable=True),
            'surface_area': SolidProperty('Surface Area (A)', 'surface_area', 'units²', 0.0, editable=False),
            'volume': SolidProperty('Volume (V)', 'volume', 'units³', 0.0, editable=True),
        }
        self._result: Optional[ConeResult] = None
        self._recalculate()

    def properties(self) -> List[SolidProperty]:
        return list(self._properties.values())

    def set_property(self, key: str, value: Optional[float]) -> bool:
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
            h = math.sqrt(max(0, value**2 - r**2))
        elif key == 'volume':
            # Solve for height keeping radius constant
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
            
        metrics = ConeSolidService._compute_metrics(r, h)
        self._properties['slant_height'].value = metrics.slant_height
        self._properties['surface_area'].value = metrics.surface_area
        self._properties['volume'].value = metrics.volume
        
        self._result = ConeSolidService.build(r, h)

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

