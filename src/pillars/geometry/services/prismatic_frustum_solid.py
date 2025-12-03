"""Prismatic frustum solid service and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload, Vec3, Edge, Face
from .solid_property import SolidProperty
from .solid_geometry import compute_surface_area, compute_volume
from .regular_prism_solids import _apothem as _regular_apothem
from .regular_prism_solids import _circumradius as _regular_circumradius
from .regular_prism_solids import _area as _regular_area


@dataclass(frozen=True)
class PrismaticFrustumMetrics:
    sides: int
    bottom_edge: float
    top_edge: float
    height: float
    bottom_area: float
    top_area: float
    bottom_perimeter: float
    top_perimeter: float
    bottom_apothem: float
    top_apothem: float
    bottom_circumradius: float
    top_circumradius: float
    lateral_edge_length: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class PrismaticFrustumSolidResult:
    payload: SolidPayload
    metrics: PrismaticFrustumMetrics


class PrismaticFrustumSolidService:
    """Generates payloads for truncated regular prisms with similar parallel bases."""

    SIDES: int = 6

    @classmethod
    def build(
        cls,
        bottom_edge: float = 3.0,
        top_edge: float = 1.75,
        height: float = 4.0,
    ) -> PrismaticFrustumSolidResult:
        if cls.SIDES < 3:
            raise ValueError('A prism base must have at least 3 sides')
        if bottom_edge <= 0 or top_edge <= 0 or height <= 0:
            raise ValueError('Edge lengths and height must be positive')

        bottom_area = _regular_area(cls.SIDES, bottom_edge)
        top_area = _regular_area(cls.SIDES, top_edge)
        bottom_perimeter = cls.SIDES * bottom_edge
        top_perimeter = cls.SIDES * top_edge
        bottom_apothem = _regular_apothem(cls.SIDES, bottom_edge)
        top_apothem = _regular_apothem(cls.SIDES, top_edge)
        bottom_radius = _regular_circumradius(cls.SIDES, bottom_edge)
        top_radius = _regular_circumradius(cls.SIDES, top_edge)
        radial_delta = abs(bottom_radius - top_radius)
        lateral_edge = math.sqrt(height ** 2 + radial_delta ** 2)

        vertices = _build_vertices(cls.SIDES, bottom_edge, top_edge, height)
        faces = _build_faces(cls.SIDES)
        edges = _build_edges(cls.SIDES)
        surface_area = compute_surface_area(vertices, faces)
        lateral_area = surface_area - (bottom_area + top_area)
        volume = compute_volume(vertices, faces)

        labels = [
            SolidLabel(text=f"a₁ = {bottom_edge:.3f}", position=(bottom_apothem, 0.0, -height / 2.0)),
            SolidLabel(text=f"a₂ = {top_edge:.3f}", position=(top_apothem * 0.7, 0.0, height / 2.0)),
            SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
        ]

        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=labels,
            metadata={
                'sides': cls.SIDES,
                'bottom_edge': bottom_edge,
                'top_edge': top_edge,
                'height': height,
                'bottom_area': bottom_area,
                'top_area': top_area,
                'bottom_perimeter': bottom_perimeter,
                'top_perimeter': top_perimeter,
                'bottom_apothem': bottom_apothem,
                'top_apothem': top_apothem,
                'lateral_edge_length': lateral_edge,
                'lateral_area': lateral_area,
                'surface_area': surface_area,
                'volume': volume,
            },
            suggested_scale=max(bottom_edge, height),
        )

        metrics = PrismaticFrustumMetrics(
            sides=cls.SIDES,
            bottom_edge=bottom_edge,
            top_edge=top_edge,
            height=height,
            bottom_area=bottom_area,
            top_area=top_area,
            bottom_perimeter=bottom_perimeter,
            top_perimeter=top_perimeter,
            bottom_apothem=bottom_apothem,
            top_apothem=top_apothem,
            bottom_circumradius=bottom_radius,
            top_circumradius=top_radius,
            lateral_edge_length=lateral_edge,
            lateral_area=lateral_area,
            surface_area=surface_area,
            volume=volume,
        )
        return PrismaticFrustumSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, bottom_edge: float = 3.0, top_edge: float = 1.75, height: float = 4.0) -> SolidPayload:
        return cls.build(bottom_edge=bottom_edge, top_edge=top_edge, height=height).payload


def _build_vertices(sides: int, bottom_edge: float, top_edge: float, height: float) -> List[Vec3]:
    bottom_radius = _regular_circumradius(sides, bottom_edge)
    top_radius = _regular_circumradius(sides, top_edge)
    half_height = height / 2.0
    vertices: List[Vec3] = []
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        vertices.append((bottom_radius * cos_val, bottom_radius * sin_val, -half_height))
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        vertices.append((top_radius * cos_val, top_radius * sin_val, half_height))
    return vertices


def _build_edges(sides: int) -> List[Edge]:
    edges: List[Edge] = []
    for i in range(sides):
        edges.append((i, (i + 1) % sides))
    offset = sides
    for i in range(sides):
        edges.append((offset + i, offset + ((i + 1) % sides)))
    for i in range(sides):
        edges.append((i, offset + i))
    return edges


def _build_faces(sides: int) -> List[Face]:
    faces: List[Face] = [tuple(range(sides))]
    offset = sides
    faces.append(tuple(offset + i for i in range(sides)))
    for i in range(sides):
        next_i = (i + 1) % sides
        faces.append((i, next_i, offset + next_i, offset + i))
    return faces


class PrismaticFrustumSolidCalculator:
    """Calculator with bidirectional updates for prismatic frustums."""

    _PROPERTY_DEFINITIONS = (
        ('bottom_edge', 'Bottom Edge', 'units', 4, True),
        ('top_edge', 'Top Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('bottom_area', 'Bottom Area', 'units²', 4, False),
        ('top_area', 'Top Area', 'units²', 4, False),
        ('bottom_perimeter', 'Bottom Perimeter', 'units', 4, False),
        ('top_perimeter', 'Top Perimeter', 'units', 4, False),
        ('lateral_edge_length', 'Lateral Edge Length', 'units', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
    )

    def __init__(self, bottom_edge: float = 3.0, top_edge: float = 1.75, height: float = 4.0):
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._bottom_edge = bottom_edge if bottom_edge > 0 else 3.0
        self._top_edge = top_edge if top_edge > 0 else 1.75
        self._height = height if height > 0 else 4.0
        self._result: Optional[PrismaticFrustumSolidResult] = None
        self._apply_dimensions(self._bottom_edge, self._top_edge, self._height)

    def properties(self) -> List[SolidProperty]:
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        if value is None or value <= 0:
            return False
        if key == 'bottom_edge':
            self._apply_dimensions(value, self._top_edge, self._height)
            return True
        if key == 'top_edge':
            self._apply_dimensions(self._bottom_edge, value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._bottom_edge, self._top_edge, value)
            return True
        if key == 'volume':
            base_bottom = _regular_area(PrismaticFrustumSolidService.SIDES, self._bottom_edge)
            base_top = _regular_area(PrismaticFrustumSolidService.SIDES, self._top_edge)
            term = base_bottom + base_top + math.sqrt(base_bottom * base_top)
            if term <= 0:
                return False
            height = (3.0 * value) / term
            self._apply_dimensions(self._bottom_edge, self._top_edge, height)
            return True
        return False

    def clear(self):
        self._bottom_edge = 3.0
        self._top_edge = 1.75
        self._height = 4.0
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> Optional[PrismaticFrustumMetrics]:
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, bottom_edge: float, top_edge: float, height: float):
        if bottom_edge <= 0 or top_edge <= 0 or height <= 0:
            return
        self._bottom_edge = bottom_edge
        self._top_edge = top_edge
        self._height = height
        result = PrismaticFrustumSolidService.build(bottom_edge, top_edge, height)
        self._result = result
        values = {
            'bottom_edge': result.metrics.bottom_edge,
            'top_edge': result.metrics.top_edge,
            'height': result.metrics.height,
            'bottom_area': result.metrics.bottom_area,
            'top_area': result.metrics.top_area,
            'bottom_perimeter': result.metrics.bottom_perimeter,
            'top_perimeter': result.metrics.top_perimeter,
            'lateral_edge_length': result.metrics.lateral_edge_length,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'PrismaticFrustumMetrics',
    'PrismaticFrustumSolidResult',
    'PrismaticFrustumSolidService',
    'PrismaticFrustumSolidCalculator',
]
