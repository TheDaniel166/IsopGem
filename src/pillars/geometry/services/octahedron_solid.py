"""Octahedron solid math utilities and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_geometry import (
    Face,
    Vec3,
    compute_surface_area,
    compute_volume,
    edges_from_faces,
    plane_distance_from_origin,
    polygon_area,
    vec_length,
)
from .solid_property import SolidProperty


_BASE_VERTICES: List[Vec3] = [
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, -1.0),
]

_FACES: List[Face] = [
    (0, 2, 4),
    (2, 1, 4),
    (1, 3, 4),
    (3, 0, 4),
    (2, 0, 5),
    (1, 2, 5),
    (3, 1, 5),
    (0, 3, 5),
]

_EDGES = edges_from_faces(_FACES)
_BASE_EDGE_LENGTH = math.dist(_BASE_VERTICES[_EDGES[0][0]], _BASE_VERTICES[_EDGES[0][1]])
_BASE_FACE_AREA = polygon_area(_BASE_VERTICES, _FACES[0])
_BASE_SURFACE_AREA = compute_surface_area(_BASE_VERTICES, _FACES)
_BASE_VOLUME = compute_volume(_BASE_VERTICES, _FACES)
_BASE_INRADIUS = plane_distance_from_origin(_BASE_VERTICES, _FACES[0])
_mid_edge = (
    (_BASE_VERTICES[_EDGES[0][0]][0] + _BASE_VERTICES[_EDGES[0][1]][0]) / 2.0,
    (_BASE_VERTICES[_EDGES[0][0]][1] + _BASE_VERTICES[_EDGES[0][1]][1]) / 2.0,
    (_BASE_VERTICES[_EDGES[0][0]][2] + _BASE_VERTICES[_EDGES[0][1]][2]) / 2.0,
)
_BASE_MIDRADIUS = vec_length(_mid_edge)
_BASE_CIRCUMRADIUS = vec_length(_BASE_VERTICES[0])
_BASE_INCIRC_CIRC = 2.0 * math.pi * _BASE_INRADIUS
_BASE_MID_CIRC = 2.0 * math.pi * _BASE_MIDRADIUS
_BASE_CIRCUM_CIRC = 2.0 * math.pi * _BASE_CIRCUMRADIUS


@dataclass(frozen=True)
class OctahedronMetrics:
    edge_length: float
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
class OctahedronSolidResult:
    payload: SolidPayload
    metrics: OctahedronMetrics


def _scaled_value(base_value: float, edge_length: float, power: float) -> float:
    scale = edge_length / _BASE_EDGE_LENGTH
    return base_value * (scale ** power)


def _scale_vertices(edge_length: float) -> List[Vec3]:
    scale = edge_length / _BASE_EDGE_LENGTH
    return [
        (vx * scale, vy * scale, vz * scale)
        for vx, vy, vz in _BASE_VERTICES
    ]


def _compute_metrics(edge_length: float) -> OctahedronMetrics:
    return OctahedronMetrics(
        edge_length=edge_length,
        face_area=_scaled_value(_BASE_FACE_AREA, edge_length, 2.0),
        surface_area=_scaled_value(_BASE_SURFACE_AREA, edge_length, 2.0),
        volume=_scaled_value(_BASE_VOLUME, edge_length, 3.0),
        inradius=_scaled_value(_BASE_INRADIUS, edge_length, 1.0),
        midradius=_scaled_value(_BASE_MIDRADIUS, edge_length, 1.0),
        circumradius=_scaled_value(_BASE_CIRCUMRADIUS, edge_length, 1.0),
        incircle_circumference=_scaled_value(_BASE_INCIRC_CIRC, edge_length, 1.0),
        midsphere_circumference=_scaled_value(_BASE_MID_CIRC, edge_length, 1.0),
        circumcircle_circumference=_scaled_value(_BASE_CIRCUM_CIRC, edge_length, 1.0),
    )


class OctahedronSolidService:
    """Generates payloads for regular octahedra."""

    @staticmethod
    def build(edge_length: float = 1.0) -> OctahedronSolidResult:
        if edge_length <= 0:
            raise ValueError("Edge length must be positive")
        metrics = _compute_metrics(edge_length)
        payload = SolidPayload(
            vertices=_scale_vertices(edge_length),
            edges=list(_EDGES),
            faces=[tuple(face) for face in _FACES],
            labels=[
                SolidLabel(text=f"a = {edge_length:.3f}", position=(0.0, 0.0, 0.0)),
                SolidLabel(text=f"V = {metrics.volume:.3f}", position=(0.0, -edge_length * 0.35, 0.0)),
            ],
            metadata={
                'edge_length': metrics.edge_length,
                'face_area': metrics.face_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'inradius': metrics.inradius,
                'midradius': metrics.midradius,
                'circumradius': metrics.circumradius,
                'incircle_circumference': metrics.incircle_circumference,
                'midsphere_circumference': metrics.midsphere_circumference,
                'circumcircle_circumference': metrics.circumcircle_circumference,
            },
            suggested_scale=edge_length,
        )
        return OctahedronSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(edge_length: float = 1.0) -> SolidPayload:
        return OctahedronSolidService.build(edge_length).payload


class OctahedronSolidCalculator:
    """Bidirectional calculator for regular octahedra."""

    _PROPERTY_DEFINITIONS = (
        ('edge_length', 'Edge Length', 'units', 4, 1.0),
        ('surface_area', 'Surface Area', 'units²', 4, 2.0),
        ('volume', 'Volume', 'units³', 4, 3.0),
        ('face_area', 'Face Area', 'units²', 4, 2.0),
        ('inradius', 'Inradius', 'units', 4, 1.0),
        ('midradius', 'Midsphere Radius', 'units', 4, 1.0),
        ('circumradius', 'Circumradius', 'units', 4, 1.0),
        ('incircle_circumference', 'Insphere Circumference', 'units', 4, 1.0),
        ('midsphere_circumference', 'Midsphere Circumference', 'units', 4, 1.0),
        ('circumcircle_circumference', 'Circumsphere Circumference', 'units', 4, 1.0),
    )

    _BASE_VALUES = {
        'edge_length': _BASE_EDGE_LENGTH,
        'surface_area': _BASE_SURFACE_AREA,
        'volume': _BASE_VOLUME,
        'face_area': _BASE_FACE_AREA,
        'inradius': _BASE_INRADIUS,
        'midradius': _BASE_MIDRADIUS,
        'circumradius': _BASE_CIRCUMRADIUS,
        'incircle_circumference': _BASE_INCIRC_CIRC,
        'midsphere_circumference': _BASE_MID_CIRC,
        'circumcircle_circumference': _BASE_CIRCUM_CIRC,
    }

    def __init__(self, edge_length: float = 1.0):
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision)
            for key, label, unit, precision, _ in self._PROPERTY_DEFINITIONS
        }
        self._edge_solvers = {
            key: self._build_solver(self._BASE_VALUES[key], power)
            for key, _, _, _, power in self._PROPERTY_DEFINITIONS
        }
        self._result: Optional[OctahedronSolidResult] = None
        if edge_length > 0:
            self._apply_edge(edge_length)

    @staticmethod
    def _build_solver(base_value: float, power: float):
        def solver(value: Optional[float]) -> Optional[float]:
            if value is None or value <= 0 or base_value <= 0:
                return None
            scale = (value / base_value) ** (1.0 / power)
            return scale * _BASE_EDGE_LENGTH
        return solver

    def properties(self) -> List[SolidProperty]:
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        if key not in self._edge_solvers or value is None or value <= 0:
            return False
        solver = self._edge_solvers[key]
        edge_length = solver(value)
        if edge_length is None or not math.isfinite(edge_length) or edge_length <= 0:
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

    def metrics(self) -> Optional[OctahedronMetrics]:
        return self._result.metrics if self._result else None

    def _apply_edge(self, edge_length: float):
        result = OctahedronSolidService.build(edge_length)
        self._result = result
        metrics = result.metrics
        values = {
            'edge_length': metrics.edge_length,
            'surface_area': metrics.surface_area,
            'volume': metrics.volume,
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


__all__ = [
    'OctahedronMetrics',
    'OctahedronSolidResult',
    'OctahedronSolidService',
    'OctahedronSolidCalculator',
]
