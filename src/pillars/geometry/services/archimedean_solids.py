"""Archimedean solid services and calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Type, cast

from ..shared.solid_payload import SolidLabel, SolidPayload, Vec3, Edge, Face
from .solid_property import SolidProperty
from .solid_geometry import (
    vec_sub,
    vec_cross,
    vec_length,
    vec_dot,
    vec_normalize,
    compute_surface_area,
    compute_volume,
    edges_from_faces,
)
from .archimedean_data import ARCHIMEDEAN_DATA


@dataclass(frozen=True)
class ArchimedeanSolidMetrics:
    edge_length: float
    surface_area: float
    volume: float
    face_count: int
    edge_count: int
    vertex_count: int
    face_sides: Dict[int, int]


@dataclass(frozen=True)
class ArchimedeanSolidResult:
    payload: SolidPayload
    metrics: ArchimedeanSolidMetrics


@dataclass(frozen=True)
class ArchimedeanSolidDefinition:
    key: str
    name: str
    canonical_vertices: List[Vec3]
    faces: List[Face]
    edges: List[Edge]
    base_edge_length: float
    base_surface_area: float
    base_volume: float
    face_sides: Dict[int, int]


_DEF_CACHE: Dict[str, ArchimedeanSolidDefinition] = {}

def _order_face_vertices(indices: List[int], vertices: List[Vec3]) -> Face:
    if len(indices) <= 2:
        return tuple(indices)
    centroid: Vec3 = cast(
        Vec3,
        tuple(sum(vertices[idx][k] for idx in indices) / len(indices) for k in range(3)),
    )
    normal = (0.0, 0.0, 1.0)
    for i in range(len(indices)):
        v1 = vec_sub(vertices[indices[i]], centroid)
        v2 = vec_sub(vertices[indices[(i + 1) % len(indices)]], centroid)
        cross = vec_cross(v1, v2)
        if vec_length(cross) > 1e-6:
            normal = vec_normalize(cross)
            break
    basis = None
    for idx in indices:
        vec = vec_sub(vertices[idx], centroid)
        if vec_length(vec) > 1e-6:
            basis = vec_normalize(vec)
            break
    if basis is None:
        return tuple(indices)
    perp = vec_cross(normal, basis)
    if vec_length(perp) < 1e-6:
        perp = (0.0, 1.0, 0.0)
    else:
        perp = vec_normalize(perp)
    ordered = []
    for idx in indices:
        rel = vec_sub(vertices[idx], centroid)
        x = vec_dot(rel, basis)
        y = vec_dot(rel, perp)
        angle = math.atan2(y, x)
        ordered.append((angle, idx))
    ordered.sort()
    return tuple(idx for _, idx in ordered)


def _definition_from_data(key: str) -> ArchimedeanSolidDefinition:
    data = ARCHIMEDEAN_DATA.get(key)
    if not data:
        raise KeyError(key)
    vertices: List[Vec3] = [cast(Vec3, tuple(v)) for v in data['vertices']]
    faces: List[Face] = [cast(Face, tuple(face)) for face in data['faces']]
    return _finalize_definition(key, data['name'], vertices, faces)


def _finalize_definition(key: str, name: str, vertices: List[Vec3], faces: List[Face]) -> ArchimedeanSolidDefinition:
    ordered_faces: List[Face] = [cast(Face, tuple(face)) for face in faces]
    edges = edges_from_faces(ordered_faces)
    if not edges:
        raise ValueError(f"No edges computed for Archimedean solid '{key}'")
    edge_vec = vec_sub(vertices[edges[0][0]], vertices[edges[0][1]])
    base_edge_length = vec_length(edge_vec)
    base_surface_area = compute_surface_area(vertices, ordered_faces)
    base_volume = compute_volume(vertices, ordered_faces)
    face_sides: Dict[int, int] = {}
    for face in ordered_faces:
        face_sides[len(face)] = face_sides.get(len(face), 0) + 1
    definition = ArchimedeanSolidDefinition(
        key=key,
        name=name,
        canonical_vertices=vertices,
        faces=ordered_faces,
        edges=edges,
        base_edge_length=base_edge_length,
        base_surface_area=base_surface_area,
        base_volume=base_volume,
        face_sides=face_sides,
    )
    _DEF_CACHE[key] = definition
    return definition


def _get_definition(key: str) -> ArchimedeanSolidDefinition:
    if key in _DEF_CACHE:
        return _DEF_CACHE[key]
    return _definition_from_data(key)


class ArchimedeanSolidServiceBase:
    """Base service for Archimedean solids with uniform edge length."""

    DEFINITION_KEY: str = ''

    @classmethod
    def build(cls, edge_length: float = 2.0) -> ArchimedeanSolidResult:
        if edge_length <= 0:
            raise ValueError('Edge length must be positive')
        definition = _get_definition(cls.DEFINITION_KEY)
        scale = edge_length / definition.base_edge_length
        vertices: List[Vec3] = [
            cast(Vec3, tuple(coord * scale for coord in v))
            for v in definition.canonical_vertices
        ]
        faces = definition.faces
        edges = definition.edges
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
                'face_sides': definition.face_sides,
            },
            suggested_scale=edge_length,
        )
        metrics = ArchimedeanSolidMetrics(
            edge_length=edge_length,
            surface_area=surface_area,
            volume=volume,
            face_count=len(faces),
            edge_count=len(edges),
            vertex_count=len(vertices),
            face_sides=definition.face_sides,
        )
        return ArchimedeanSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, edge_length: float = 2.0) -> SolidPayload:
        return cls.build(edge_length=edge_length).payload


class ArchimedeanSolidCalculatorBase:
    """Base calculator for Archimedean solids supporting uniform scaling."""

    SERVICE: Type[ArchimedeanSolidServiceBase] = ArchimedeanSolidServiceBase

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
        self._result: ArchimedeanSolidResult | None = None
        self._apply_edge_length(self._edge_length)

    def properties(self) -> List[SolidProperty]:
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: float | None) -> bool:
        if value is None or value <= 0:
            return False
        definition = _get_definition(self.SERVICE.DEFINITION_KEY)
        if key == 'edge_length':
            self._apply_edge_length(value)
            return True
        if key == 'volume' and definition.base_volume > 0:
            scale = (value / definition.base_volume) ** (1.0 / 3.0)
            edge_length = definition.base_edge_length * scale
            self._apply_edge_length(edge_length)
            return True
        if key == 'surface_area' and definition.base_surface_area > 0:
            scale = math.sqrt(value / definition.base_surface_area)
            edge_length = definition.base_edge_length * scale
            self._apply_edge_length(edge_length)
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

    def metrics(self) -> ArchimedeanSolidMetrics | None:
        return self._result.metrics if self._result else None

    def _apply_edge_length(self, edge_length: float):
        if edge_length <= 0:
            return
        self._edge_length = edge_length
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


class CuboctahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'cuboctahedron'


class CuboctahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = CuboctahedronSolidService


class TruncatedTetrahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'truncated_tetrahedron'


class TruncatedTetrahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = TruncatedTetrahedronSolidService


class TruncatedCubeSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'truncated_cube'


class TruncatedCubeSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = TruncatedCubeSolidService


class TruncatedOctahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'truncated_octahedron'


class TruncatedOctahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = TruncatedOctahedronSolidService


class RhombicuboctahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'rhombicuboctahedron'


class RhombicuboctahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = RhombicuboctahedronSolidService


class RhombicosidodecahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'rhombicosidodecahedron'


class RhombicosidodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = RhombicosidodecahedronSolidService


class TruncatedCuboctahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'truncated_cuboctahedron'


class TruncatedCuboctahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = TruncatedCuboctahedronSolidService


class IcosidodecahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'icosidodecahedron'


class IcosidodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = IcosidodecahedronSolidService


class TruncatedDodecahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'truncated_dodecahedron'


class TruncatedDodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = TruncatedDodecahedronSolidService


class TruncatedIcosahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'truncated_icosahedron'


class TruncatedIcosahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = TruncatedIcosahedronSolidService


class TruncatedIcosidodecahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'truncated_icosidodecahedron'


class TruncatedIcosidodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = TruncatedIcosidodecahedronSolidService


class SnubCubeSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'snub_cube'


class SnubCubeSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = SnubCubeSolidService


class SnubDodecahedronSolidService(ArchimedeanSolidServiceBase):
    DEFINITION_KEY = 'snub_dodecahedron'


class SnubDodecahedronSolidCalculator(ArchimedeanSolidCalculatorBase):
    SERVICE = SnubDodecahedronSolidService


__all__ = [
    'ArchimedeanSolidMetrics',
    'ArchimedeanSolidResult',
    'ArchimedeanSolidServiceBase',
    'ArchimedeanSolidCalculatorBase',
    'CuboctahedronSolidService',
    'CuboctahedronSolidCalculator',
    'TruncatedTetrahedronSolidService',
    'TruncatedTetrahedronSolidCalculator',
    'TruncatedCubeSolidService',
    'TruncatedCubeSolidCalculator',
    'TruncatedOctahedronSolidService',
    'TruncatedOctahedronSolidCalculator',
    'RhombicuboctahedronSolidService',
    'RhombicuboctahedronSolidCalculator',
    'RhombicosidodecahedronSolidService',
    'RhombicosidodecahedronSolidCalculator',
    'TruncatedCuboctahedronSolidService',
    'TruncatedCuboctahedronSolidCalculator',
    'IcosidodecahedronSolidService',
    'IcosidodecahedronSolidCalculator',
    'TruncatedDodecahedronSolidService',
    'TruncatedDodecahedronSolidCalculator',
    'TruncatedIcosahedronSolidService',
    'TruncatedIcosahedronSolidCalculator',
    'TruncatedIcosidodecahedronSolidService',
    'TruncatedIcosidodecahedronSolidCalculator',
    'SnubCubeSolidService',
    'SnubCubeSolidCalculator',
    'SnubDodecahedronSolidService',
    'SnubDodecahedronSolidCalculator',
]
