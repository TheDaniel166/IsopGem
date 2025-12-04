"""Tesseract (hypercube) solid service and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Type

from ..shared.solid_payload import SolidLabel, SolidPayload, Vec3, Face
from .solid_geometry import (
    compute_surface_area,
    compute_volume,
    edges_from_faces,
    vec_length,
    vec_sub,
)
from .solid_property import SolidProperty


def _build_vertices() -> List[Vec3]:
    outer = [
        (-1.0, -1.0, -1.0),
        (1.0, -1.0, -1.0),
        (1.0, 1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
        (1.0, -1.0, 1.0),
        (1.0, 1.0, 1.0),
        (-1.0, 1.0, 1.0),
    ]
    inner = [(vx * 0.5, vy * 0.5, vz * 0.5) for vx, vy, vz in outer]
    return outer + inner


_BASE_VERTICES: List[Vec3] = _build_vertices()
_OUTER_FACES: List[Face] = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (1, 2, 6, 5),
    (2, 3, 7, 6),
    (3, 0, 4, 7),
]
_INNER_FACE_OFFSET = 8
_INNER_FACES: List[Face] = [
    tuple(vertex + _INNER_FACE_OFFSET for vertex in face)
    for face in _OUTER_FACES
]
_CUBE_EDGES: List[Tuple[int, int]] = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]
_CONNECTOR_FACES: List[Face] = [
    (u, v, v + _INNER_FACE_OFFSET, u + _INNER_FACE_OFFSET)
    for u, v in _CUBE_EDGES
]
_FACES: List[Face] = [*_OUTER_FACES, *_INNER_FACES, *_CONNECTOR_FACES]
_EDGES = edges_from_faces(_FACES)
edge_vec = vec_sub(_BASE_VERTICES[_EDGES[0][0]], _BASE_VERTICES[_EDGES[0][1]])
_BASE_EDGE_LENGTH = vec_length(edge_vec)
_BASE_SURFACE_AREA = compute_surface_area(_BASE_VERTICES, _FACES)
_BASE_VOLUME = compute_volume(_BASE_VERTICES, _FACES)
_FACE_SIDES: Dict[int, int] = {}
for face in _FACES:
    _FACE_SIDES[len(face)] = _FACE_SIDES.get(len(face), 0) + 1


@dataclass(frozen=True)
class TesseractMetrics:
    edge_length: float
    surface_area: float
    volume: float
    face_count: int
    edge_count: int
    vertex_count: int
    face_sides: Dict[int, int]


@dataclass(frozen=True)
class TesseractSolidResult:
    payload: SolidPayload
    metrics: TesseractMetrics


class TesseractSolidService:
    """Service for generating Schlegel projection of a tesseract."""

    @staticmethod
    def build(edge_length: float = 2.0) -> TesseractSolidResult:
        if edge_length <= 0:
            raise ValueError('Edge length must be positive')
        scale = edge_length / _BASE_EDGE_LENGTH
        vertices: List[Vec3] = [
            (vx * scale, vy * scale, vz * scale)
            for vx, vy, vz in _BASE_VERTICES
        ]
        faces: List[Face] = list(_FACES)
        edges = list(_EDGES)
        surface_area = compute_surface_area(vertices, faces)
        volume = compute_volume(vertices, faces)
        bbox_max_z = max(v[2] for v in vertices)
        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=[
                SolidLabel(text=f"e = {edge_length:.3f}", position=(0.0, 0.0, bbox_max_z + edge_length * 0.25)),
            ],
            metadata={
                'edge_length': edge_length,
                'surface_area': surface_area,
                'volume': volume,
                'face_count': len(faces),
                'edge_count': len(edges),
                'vertex_count': len(vertices),
                'face_sides': dict(_FACE_SIDES),
            },
            suggested_scale=edge_length,
        )
        metrics = TesseractMetrics(
            edge_length=edge_length,
            surface_area=surface_area,
            volume=volume,
            face_count=len(faces),
            edge_count=len(edges),
            vertex_count=len(vertices),
            face_sides=dict(_FACE_SIDES),
        )
        return TesseractSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(edge_length: float = 2.0) -> SolidPayload:
        return TesseractSolidService.build(edge_length).payload


class TesseractSolidCalculator:
    """Simple calculator enabling edge/area/volume control for the tesseract."""

    SERVICE: Type[TesseractSolidService] = TesseractSolidService

    _PROPERTY_DEFINITIONS = (
        ('edge_length', 'Edge Length', 'units', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
        ('face_count', 'Faces', '', 0, False),
        ('edge_count', 'Edges', '', 0, False),
        ('vertex_count', 'Vertices', '', 0, False),
    )

    def __init__(self, edge_length: float = 2.0):
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._edge_length = edge_length if edge_length > 0 else 2.0
        self._result: TesseractSolidResult | None = None
        self._apply_edge_length(self._edge_length)

    def properties(self) -> List[SolidProperty]:
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: float | None) -> bool:
        if value is None or value <= 0:
            return False
        if key == 'edge_length':
            self._apply_edge_length(value)
            return True
        if key == 'volume' and _BASE_VOLUME > 0:
            scale = (value / _BASE_VOLUME) ** (1.0 / 3.0)
            target_edge = _BASE_EDGE_LENGTH * scale
            self._apply_edge_length(target_edge)
            return True
        if key == 'surface_area' and _BASE_SURFACE_AREA > 0:
            scale = math.sqrt(value / _BASE_SURFACE_AREA)
            target_edge = _BASE_EDGE_LENGTH * scale
            self._apply_edge_length(target_edge)
            return True
        return False

    def clear(self):
        self._edge_length = 2.0
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> SolidPayload | None:
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> TesseractMetrics | None:
        return self._result.metrics if self._result else None

    def _apply_edge_length(self, edge_length: float):
        if edge_length <= 0:
            return
        result = self.SERVICE.build(edge_length=edge_length)
        self._result = result
        values = {
            'edge_length': result.metrics.edge_length,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'face_count': float(result.metrics.face_count),
            'edge_count': float(result.metrics.edge_count),
            'vertex_count': float(result.metrics.vertex_count),
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'TesseractMetrics',
    'TesseractSolidResult',
    'TesseractSolidService',
    'TesseractSolidCalculator',
]
