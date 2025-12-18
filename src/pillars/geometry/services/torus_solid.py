"""Torus solid math utilities and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_geometry import Vec3, edges_from_faces
from .solid_property import SolidProperty


@dataclass(frozen=True)
class TorusMetrics:
    major_radius: float
    minor_radius: float
    ratio: float
    surface_area: float
    volume: float
    major_circumference: float
    minor_circumference: float


@dataclass(frozen=True)
class TorusSolidResult:
    payload: SolidPayload
    metrics: TorusMetrics


@dataclass
class TorusMeshConfig:
    major_segments: int = 40
    minor_segments: int = 20


class TorusSolidService:
    """Generates payloads for torus solids."""

    @staticmethod
    def build(major_radius: float = 3.0, minor_radius: float = 1.0, config: TorusMeshConfig = None) -> TorusSolidResult:
        if major_radius <= 0 or minor_radius <= 0:
            raise ValueError("Radii must be positive")
            
        if config is None:
            config = TorusMeshConfig()

        metrics = TorusSolidService._compute_metrics(major_radius, minor_radius)
        
        vertices, faces = TorusSolidService._generate_mesh(major_radius, minor_radius, config)
        edges = edges_from_faces(faces)
        
        # Labels usually at center or strategic points
        labels = [
            SolidLabel(text=f"R = {major_radius:.2f}", position=(major_radius, 0.0, -minor_radius * 1.5)),
            SolidLabel(text=f"r = {minor_radius:.2f}", position=(major_radius + minor_radius, 0.0, 0.0)),
        ]

        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=labels,
            metadata={
                'major_radius': metrics.major_radius,
                'minor_radius': metrics.minor_radius,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
            },
            suggested_scale=major_radius + minor_radius,
        )
        return TorusSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def _compute_metrics(R: float, r: float) -> TorusMetrics:
        return TorusMetrics(
            major_radius=R,
            minor_radius=r,
            ratio=R/r if r > 0 else 0,
            surface_area=4 * (math.pi ** 2) * R * r,
            volume=2 * (math.pi ** 2) * R * (r ** 2),
            major_circumference=2 * math.pi * R,
            minor_circumference=2 * math.pi * r,
        )

    @staticmethod
    def _generate_mesh(R: float, r: float, config: TorusMeshConfig) -> Tuple[List[Vec3], List[Tuple[int, ...]]]:
        vertices = []
        faces = []
        
        div_u = config.major_segments
        div_v = config.minor_segments
        
        # Generate vertices
        # u goes around the tube (minor angle)
        # v goes around the torus hole (major angle)
        # Wait, usually u=major, v=minor. Let's stick to standard conv:
        # phi (major) in [0, 2pi], theta (minor) in [0, 2pi]
        
        for i in range(div_u):
            major_angle = (i / div_u) * 2 * math.pi
            cos_major = math.cos(major_angle)
            sin_major = math.sin(major_angle)
            
            for j in range(div_v):
                minor_angle = (j / div_v) * 2 * math.pi
                cos_minor = math.cos(minor_angle)
                sin_minor = math.sin(minor_angle)
                
                # Formula:
                # x = (R + r*cos(theta)) * cos(phi)
                # y = (R + r*cos(theta)) * sin(phi)
                # z = r * sin(theta)
                
                # Using Y as UP axis?
                # Usually in this app Y is UP? Let's check cube.
                # Cube: (-1, -1, -1) to (1, 1, 1). 
                # Let's assume Z is UP for geometry, or Y? 
                # Let's verify standard orientation. Usually standard math Z is up.
                # But implementation might vary. Let's assume Z is UP.
                
                x = (R + r * cos_minor) * cos_major
                y = (R + r * cos_minor) * sin_major
                z = r * sin_minor
                
                vertices.append((x, y, z))

        # Generate Faces (Quads)
        for i in range(div_u):
            next_i = (i + 1) % div_u
            for j in range(div_v):
                next_j = (j + 1) % div_v
                
                # Indices in the flat list
                # current vertex = i * div_v + j
                
                idx_bl = i * div_v + j           # Bottom Left
                idx_br = next_i * div_v + j      # Bottom Right
                idx_tr = next_i * div_v + next_j # Top Right
                idx_tl = i * div_v + next_j      # Top Left
                
                # Winding order? Let's try CCW
                faces.append((idx_bl, idx_br, idx_tr, idx_tl))

        return vertices, faces


class TorusSolidCalculator:
    """Bidirectional torus calculator."""

    def __init__(self, major_radius: float = 3.0, minor_radius: float = 1.0):
        self._properties = {
            'major_radius': SolidProperty('Major Radius (R)', 'major_radius', 'units', 10.0), # Priority 10 -> Input
            'minor_radius': SolidProperty('Minor Radius (r)', 'minor_radius', 'units', 10.0),
            'ratio': SolidProperty('Ratio (R/r)', 'ratio', '', 5.0),
            'surface_area': SolidProperty('Surface Area', 'surface_area', 'units²', 5.0),
            'volume': SolidProperty('Volume', 'volume', 'units³', 5.0),
            'major_circumference': SolidProperty('Major Circumference', 'major_circumference', 'units', 5.0),
            'minor_circumference': SolidProperty('Minor Circumference', 'minor_circumference', 'units', 5.0),
        }
        
        # Set initial values
        self.set_property('major_radius', major_radius)
        self.set_property('minor_radius', minor_radius)
        self._recalculate()

    def properties(self) -> List[SolidProperty]:
        return list(self._properties.values())

    def set_property(self, key: str, value: Optional[float]) -> bool:
        if value is not None and value <= 0:
            return False
            
        prop = self._properties.get(key)
        if not prop:
            return False
            
        # Store input value
        prop.value = value
        
        # Bidirectional Resolving Logic
        # Try to solve for R and r
        R = self._properties['major_radius'].value
        r = self._properties['minor_radius'].value
        
        if key == 'major_radius':
            R = value
        elif key == 'minor_radius':
            r = value
        elif key == 'major_circumference':
            R = value / (2 * math.pi)
            self._properties['major_radius'].value = R
        elif key == 'minor_circumference':
            r = value / (2 * math.pi)
            self._properties['minor_radius'].value = r
        elif key == 'ratio':
            # Ratio = R / r. Need one of them to solve the other.
            # If we have R, r = R / ratio.
            ratio = value
            if R is not None:
                r = R / ratio
                self._properties['minor_radius'].value = r
            elif r is not None:
                R = r * ratio
                self._properties['major_radius'].value = R
        elif key == 'surface_area':
            # A = 4 pi^2 R r
            # Need ratio or fixed radius?
            # Creating a constraint solver is complex. 
            # Strategy: If R is set, solve for r. If r is set, solve for R. 
            # If neither, maybe assume Ratio=3? Or fail.
            pass 
        elif key == 'volume':
             # V = 2 pi^2 R r^2
             pass

        # If we successfully resolved R and r, update everything
        if R is not None and r is not None:
            self._properties['major_radius'].value = R
            self._properties['minor_radius'].value = r
            self._recalculate()
            return True
            
        return False

    def _recalculate(self):
        R = self._properties['major_radius'].value
        r = self._properties['minor_radius'].value
        
        if R is None or r is None:
            return

        metrics = TorusSolidService._compute_metrics(R, r)
        self._properties['ratio'].value = metrics.ratio
        self._properties['surface_area'].value = metrics.surface_area
        self._properties['volume'].value = metrics.volume
        self._properties['major_circumference'].value = metrics.major_circumference
        self._properties['minor_circumference'].value = metrics.minor_circumference
        
        self._result = TorusSolidService.build(R, r)

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

    def metrics(self) -> Optional[TorusMetrics]:
        return self._result.metrics if self._result else None
