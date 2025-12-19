"""Cylinder 3D Solid Service."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_geometry import Vec3, edges_from_faces
from .solid_property import SolidProperty


@dataclass(frozen=True)
class CylinderMetrics:
    radius: float
    height: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class CylinderResult:
    payload: SolidPayload
    metrics: CylinderMetrics


class CylinderSolidService:
    """Generates the geometry for a Cylinder."""

    @staticmethod
    def build(radius: float = 1.0, height: float = 2.0, segments: int = 32) -> CylinderResult:
        if radius <= 0 or height <= 0:
            raise ValueError("Radius and Height must be positive")

        metrics = CylinderSolidService._compute_metrics(radius, height)
        
        vertices: List[Vec3] = []
        faces: List[Tuple[int, ...]] = []
        
        # Center of bottom cap
        vertices.append((0.0, 0.0, 0.0)) # Index 0
        # Bottom ring
        for i in range(segments):
            angle = i * 2 * math.pi / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), 0.0))
            
        # Center of top cap
        vertices.append((0.0, 0.0, height)) # Index segments + 1
        # Top ring
        for i in range(segments):
            angle = i * 2 * math.pi / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), height))
            
        # Bottom Cap Faces
        for i in range(segments):
            faces.append((0, (i % segments) + 1, ((i + 1) % segments) + 1))
            
        # Top Cap Faces
        top_offset = segments + 1
        for i in range(segments):
            faces.append((top_offset, top_offset + ((i + 1) % segments) + 1, top_offset + (i % segments) + 1))
            
        # Side Faces (Quads)
        for i in range(segments):
            v1 = i + 1
            v2 = ((i + 1) % segments) + 1
            v3 = v2 + top_offset
            v4 = v1 + top_offset
            faces.append((v1, v2, v3, v4))
            
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
                'surface_area': metrics.surface_area,
                'volume': metrics.volume
            },
            suggested_scale=max(radius * 2, height),
        )
        return CylinderResult(payload=payload, metrics=metrics)

    @staticmethod
    def _compute_metrics(r: float, h: float) -> CylinderMetrics:
        base_area = math.pi * (r ** 2)
        lateral_area = 2 * math.pi * r * h
        return CylinderMetrics(
            radius=r,
            height=h,
            base_area=base_area,
            lateral_area=lateral_area,
            surface_area=2 * base_area + lateral_area,
            volume=base_area * h
        )


class CylinderSolidCalculator:
    """Bidirectional calculator for the 3D Cylinder."""

    def __init__(self, radius: float = 1.0, height: float = 2.0):
        self._properties = {
            'radius': SolidProperty('Radius (r)', 'radius', 'units', radius),
            'height': SolidProperty('Height (h)', 'height', 'units', height),
            'surface_area': SolidProperty('Surface Area (A)', 'surface_area', 'units²', 0.0, editable=False),
            'volume': SolidProperty('Volume (V)', 'volume', 'units³', 0.0, editable=True),
        }
        self._result: Optional[CylinderResult] = None
        self._recalculate()

    def properties(self) -> List[SolidProperty]:
        return list(self._properties.values())

    def set_property(self, key: str, value: Optional[float]) -> bool:
        if value is not None and value <= 0:
            return False
            
        prop = self._properties.get(key)
        if not prop:
            return False
            
        if key == 'volume':
            # Solve for radius keeping height constant
            h = self._properties['height'].value
            if h and h > 0:
                self._properties['radius'].value = math.sqrt(value / (math.pi * h))
                self._recalculate()
                return True
        else:
            prop.value = value
            self._recalculate()
            return True
            
        return False

    def _recalculate(self):
        r = self._properties['radius'].value
        h = self._properties['height'].value
        if r is None or h is None:
            return
            
        metrics = CylinderSolidService._compute_metrics(r, h)
        self._properties['surface_area'].value = metrics.surface_area
        self._properties['volume'].value = metrics.volume
        
        self._result = CylinderSolidService.build(r, h)

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

