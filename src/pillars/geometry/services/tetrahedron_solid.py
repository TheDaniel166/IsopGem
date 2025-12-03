"""Equilateral tetrahedron solid math + payload builder."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from ..shared.solid_payload import Edge, Face, SolidLabel, SolidPayload, Vec3
from .solid_property import SolidProperty

# Canonical tetrahedron coordinates centered at the origin with edge length 2*sqrt(2).
_BASE_VERTICES: Tuple[Vec3, ...] = (
    (1.0, 1.0, 1.0),
    (-1.0, -1.0, 1.0),
    (-1.0, 1.0, -1.0),
    (1.0, -1.0, -1.0),
)
_BASE_EDGE_LENGTH = 2 * math.sqrt(2.0)
_EDGES: Tuple[Edge, ...] = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
)
_FACES: Tuple[Face, ...] = (
    (0, 1, 2),
    (0, 1, 3),
    (0, 2, 3),
    (1, 2, 3),
)


@dataclass(frozen=True)
class TetrahedronMetrics:
    """Key measurements for an equilateral tetrahedron."""

    edge_length: float
    height: float
    face_area: float
    surface_area: float
    volume: float
    inradius: float
    midradius: float
    circumradius: float
    incircle_circumference: float
    midsphere_circumference: float
    circumcircle_circumference: float


@dataclass(frozen=True)
class TetrahedronSolidResult:
    """Bundled payload + metrics so callers can choose what they need."""

    payload: SolidPayload
    metrics: TetrahedronMetrics


class TetrahedronSolidService:
    """Generates payloads for equilateral tetrahedra."""

    @staticmethod
    def build(edge_length: float = 1.0) -> TetrahedronSolidResult:
        if edge_length <= 0:
            raise ValueError("Edge length must be positive")

        metrics = _compute_metrics(edge_length)
        vertices = _scale_vertices(edge_length)
        metadata = {
            'edge_length': edge_length,
            'height': metrics.height,
            'face_area': metrics.face_area,
            'surface_area': metrics.surface_area,
            'volume': metrics.volume,
            'inradius': metrics.inradius,
            'midradius': metrics.midradius,
            'circumradius': metrics.circumradius,
            'incircle_circumference': metrics.incircle_circumference,
            'midsphere_circumference': metrics.midsphere_circumference,
            'circumcircle_circumference': metrics.circumcircle_circumference,
        }
        labels = [
            SolidLabel(text=f"a = {edge_length:.3f}", position=(0.0, 0.0, 0.0)),
            SolidLabel(text=f"V = {metrics.volume:.3f}", position=(0.0, -metrics.height * 0.25, 0.0)),
        ]
        payload = SolidPayload(
            vertices=vertices,
            edges=list(_EDGES),
            faces=[tuple(face) for face in _FACES],
            labels=labels,
            metadata=metadata,
            suggested_scale=edge_length,
        )
        return TetrahedronSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(edge_length: float = 1.0) -> SolidPayload:
        """Convenience accessor when only the payload is required."""
        return TetrahedronSolidService.build(edge_length).payload


class TetrahedronSolidCalculator:
    """Bidirectional tetrahedron calculator mirroring 2D pane behavior."""

    _PROPERTY_ORDER = (
        ('edge_length', 'Edge Length', 'units', 4),
        ('surface_area', 'Surface Area', 'units²', 4),
        ('volume', 'Volume', 'units³', 4),
        ('height', 'Height', 'units', 4),
        ('face_area', 'Face Area', 'units²', 4),
        ('inradius', 'Inradius', 'units', 4),
        ('midradius', 'Midsphere Radius', 'units', 4),
        ('circumradius', 'Circumradius', 'units', 4),
        ('incircle_circumference', 'Incircle Circumference', 'units', 4),
        ('midsphere_circumference', 'Midsphere Circumference', 'units', 4),
        ('circumcircle_circumference', 'Circumcircle Circumference', 'units', 4),
    )

    def __init__(self, edge_length: float = 1.0):
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision)
            for key, label, unit, precision in self._PROPERTY_ORDER
        }
        self._result: Optional[TetrahedronSolidResult] = None
        self._edge_solvers = {
            'edge_length': lambda value: value,
            'surface_area': lambda value: math.sqrt(value / math.sqrt(3.0)),
            'volume': lambda value: (6.0 * math.sqrt(2.0) * value) ** (1.0 / 3.0),
            'height': lambda value: value * math.sqrt(3.0 / 2.0),
            'face_area': lambda value: math.sqrt((4.0 * value) / math.sqrt(3.0)),
            'inradius': lambda value: value * 12.0 / math.sqrt(6.0),
            'midradius': lambda value: value * 4.0 / math.sqrt(2.0),
            'circumradius': lambda value: value * 4.0 / math.sqrt(6.0),
            'incircle_circumference': lambda value: (value / (2.0 * math.pi)) * 12.0 / math.sqrt(6.0),
            'midsphere_circumference': lambda value: (value / (2.0 * math.pi)) * 4.0 / math.sqrt(2.0),
            'circumcircle_circumference': lambda value: (value / (2.0 * math.pi)) * 4.0 / math.sqrt(6.0),
        }
        if edge_length > 0:
            self._apply_edge(edge_length)

    def properties(self) -> List[SolidProperty]:
        return [self._properties[key] for key, *_ in self._PROPERTY_ORDER]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        if value is None or key not in self._edge_solvers:
            return False
        if value <= 0:
            return False
        edge_solver = self._edge_solvers[key]
        edge_length = edge_solver(value)
        if not math.isfinite(edge_length) or edge_length <= 0:
            return False
        self._apply_edge(edge_length)
        return True

    def clear(self):
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> Optional[TetrahedronMetrics]:
        return self._result.metrics if self._result else None

    def _apply_edge(self, edge_length: float):
        result = TetrahedronSolidService.build(edge_length)
        self._result = result
        metrics = result.metrics
        values = {
            'edge_length': edge_length,
            'surface_area': metrics.surface_area,
            'volume': metrics.volume,
            'height': metrics.height,
            'face_area': metrics.face_area,
            'inradius': metrics.inradius,
            'midradius': metrics.midradius,
            'circumradius': metrics.circumradius,
            'incircle_circumference': metrics.incircle_circumference,
            'midsphere_circumference': metrics.midsphere_circumference,
            'circumcircle_circumference': metrics.circumcircle_circumference,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


def _scale_vertices(edge_length: float) -> List[Vec3]:
    scale = edge_length / _BASE_EDGE_LENGTH
    return [
        (
            vx * scale,
            vy * scale,
            vz * scale,
        )
        for vx, vy, vz in _BASE_VERTICES
    ]


def _compute_metrics(edge_length: float) -> TetrahedronMetrics:
    height = math.sqrt(2.0 / 3.0) * edge_length
    face_area = (math.sqrt(3.0) / 4.0) * edge_length ** 2
    surface_area = 4.0 * face_area
    volume = edge_length ** 3 / (6.0 * math.sqrt(2.0))
    inradius = edge_length * math.sqrt(6.0) / 12.0
    midradius = edge_length * math.sqrt(2.0) / 4.0
    circumradius = edge_length * math.sqrt(6.0) / 4.0
    incircle_circumference = 2.0 * math.pi * inradius
    midsphere_circumference = 2.0 * math.pi * midradius
    circumcircle_circumference = 2.0 * math.pi * circumradius
    return TetrahedronMetrics(
        edge_length=edge_length,
        height=height,
        face_area=face_area,
        surface_area=surface_area,
        volume=volume,
        inradius=inradius,
        midradius=midradius,
        circumradius=circumradius,
        incircle_circumference=incircle_circumference,
        midsphere_circumference=midsphere_circumference,
        circumcircle_circumference=circumcircle_circumference,
    )


__all__ = [
    'TetrahedronMetrics',
    'TetrahedronSolidResult',
    'TetrahedronSolidService',
    'TetrahedronSolidCalculator',
]
