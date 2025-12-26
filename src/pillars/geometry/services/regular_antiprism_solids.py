"""Regular antiprism solid services and calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

from ..shared.solid_payload import SolidLabel, SolidPayload, Vec3, Edge, Face
from .solid_property import SolidProperty
from .solid_geometry import compute_surface_area, compute_volume
from .regular_prism_solids import (
    _area as _regular_polygon_area,
    _apothem as _regular_polygon_apothem,
    _circumradius as _regular_polygon_circumradius,
)


@dataclass(frozen=True)
class RegularAntiprismMetrics:
    sides: int
    base_edge: float
    height: float
    base_area: float
    base_perimeter: float
    base_apothem: float
    base_circumradius: float
    lateral_edge_length: float
    lateral_chord_length: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class RegularAntiprismSolidResult:
    payload: SolidPayload
    metrics: RegularAntiprismMetrics


def _lateral_chord_length(sides: int, base_edge: float) -> float:
    radius = _regular_polygon_circumradius(sides, base_edge)
    return 2.0 * radius * math.sin(math.pi / (2.0 * sides))


def _build_vertices(sides: int, base_edge: float, height: float) -> List[Vec3]:
    radius = _regular_polygon_circumradius(sides, base_edge)
    half_height = height / 2.0
    vertices: List[Vec3] = []
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        vertices.append((radius * math.cos(angle), radius * math.sin(angle), -half_height))
    rotation = math.pi / sides
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides + rotation
        vertices.append((radius * math.cos(angle), radius * math.sin(angle), half_height))
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
        edges.append((i, offset + ((i - 1) % sides)))
    return edges


def _build_faces(sides: int) -> List[Face]:
    faces: List[Face] = [tuple(range(sides))]
    offset = sides
    faces.append(tuple(offset + i for i in range(sides)))
    for i in range(sides):
        next_i = (i + 1) % sides
        faces.append((i, offset + i, offset + next_i))
        faces.append((i, offset + next_i, next_i))
    return faces


def _create_payload(sides: int, base_edge: float, height: float) -> Tuple[SolidPayload, RegularAntiprismMetrics]:
    vertices = _build_vertices(sides, base_edge, height)
    edges = _build_edges(sides)
    faces = _build_faces(sides)

    base_area = _regular_polygon_area(sides, base_edge)
    base_perimeter = sides * base_edge
    base_apothem = _regular_polygon_apothem(sides, base_edge)
    base_circumradius = _regular_polygon_circumradius(sides, base_edge)
    lateral_chord = _lateral_chord_length(sides, base_edge)
    lateral_edge = math.sqrt(height ** 2 + lateral_chord ** 2)

    surface_area = compute_surface_area(vertices, faces)
    lateral_area = surface_area - 2.0 * base_area
    volume = compute_volume(vertices, faces)

    labels = [
        SolidLabel(text=f"a = {base_edge:.3f}", position=(base_apothem, 0.0, -height / 2.0)),
        SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
        SolidLabel(text=f"l = {lateral_edge:.3f}", position=(0.0, 0.0, height / 2.0)),
    ]

    payload = SolidPayload(
        vertices=vertices,
        edges=edges,
        faces=faces,
        labels=labels,
        metadata={
            'sides': sides,
            'base_edge': base_edge,
            'height': height,
            'base_area': base_area,
            'base_perimeter': base_perimeter,
            'base_apothem': base_apothem,
            'base_circumradius': base_circumradius,
            'lateral_edge_length': lateral_edge,
            'lateral_chord_length': lateral_chord,
            'lateral_area': lateral_area,
            'surface_area': surface_area,
            'volume': volume,
        },
        suggested_scale=max(base_edge, height, lateral_edge),
    )

    metrics = RegularAntiprismMetrics(
        sides=sides,
        base_edge=base_edge,
        height=height,
        base_area=base_area,
        base_perimeter=base_perimeter,
        base_apothem=base_apothem,
        base_circumradius=base_circumradius,
        lateral_edge_length=lateral_edge,
        lateral_chord_length=lateral_chord,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
    )
    return payload, metrics


def _volume_factor(sides: int, base_edge: float) -> float:
    _, metrics = _create_payload(sides, base_edge, height=1.0)
    return metrics.volume


class RegularAntiprismSolidServiceBase:
    """Base service for right regular antiprisms."""

    SIDES: int = 3

    @classmethod
    def build(cls, base_edge: float = 2.0, height: float = 4.0) -> RegularAntiprismSolidResult:
        if cls.SIDES < 3:
            raise ValueError('An antiprism base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')
        payload, metrics = _create_payload(cls.SIDES, base_edge, height)
        return RegularAntiprismSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, base_edge: float = 2.0, height: float = 4.0) -> SolidPayload:
        return cls.build(base_edge, height).payload


class RegularAntiprismSolidCalculatorBase:
    """Base calculator for right regular antiprisms."""

    SIDES: int = 3
    SERVICE: Type[RegularAntiprismSolidServiceBase] = RegularAntiprismSolidServiceBase

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('lateral_edge_length', 'Lateral Edge', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, False),
        ('base_perimeter', 'Base Perimeter', 'units', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
    )

    def __init__(self, base_edge: float = 2.0, height: float = 4.0):
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge if base_edge > 0 else 2.0
        self._height = height if height > 0 else 4.0
        self._result: Optional[RegularAntiprismSolidResult] = None
        self._apply_dimensions(self._base_edge, self._height)

    def properties(self) -> List[SolidProperty]:
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        if value is None or value <= 0:
            return False
        if key == 'base_edge':
            self._apply_dimensions(value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_edge, value)
            return True
        if key == 'lateral_edge_length':
            chord = _lateral_chord_length(self.SIDES, self._base_edge)
            if value <= chord:
                return False
            height = math.sqrt(max(value ** 2 - chord ** 2, 0.0))
            if height <= 0:
                return False
            self._apply_dimensions(self._base_edge, height)
            return True
        if key == 'lateral_area':
            # L = n * s * sqrt(e^2 - s^2/4)
            # L = n * s * h_tri
            # h_tri = L / (n * s)
            # h_tri^2 = e^2 - s^2/4 = h^2 + k^2 - s^2/4
            # h = sqrt(h_tri^2 - k^2 + s^2/4)
            n = self.SIDES
            s = self._base_edge
            if s <= 0: return False
            
            h_tri = value / (n * s)
            k = _lateral_chord_length(n, s)
            
            term = h_tri**2 - k**2 + (s**2 / 4.0)
            if term <= 0: return False
            
            height = math.sqrt(term)
            self._apply_dimensions(s, height)
            return True
            
        if key == 'surface_area':
            # S = 2*Base + L
            base_area = _regular_polygon_area(self.SIDES, self._base_edge)
            if value <= 2 * base_area: return False
            lateral_area = value - 2 * base_area
            # Delegate to logic above
            return self.set_property('lateral_area', lateral_area)

        if key == 'volume':
            factor = _volume_factor(self.SIDES, self._base_edge)
            if factor <= 0:
                return False
            height = value / factor
            if height <= 0:
                return False
            self._apply_dimensions(self._base_edge, height)
            return True
        return False

    def clear(self):
        self._base_edge = 2.0
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

    def metrics(self) -> Optional[RegularAntiprismMetrics]:
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_edge: float, height: float):
        if base_edge <= 0 or height <= 0:
            return
        self._base_edge = base_edge
        self._height = height
        result = self.SERVICE.build(base_edge, height)
        self._result = result
        values = {
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'lateral_edge_length': result.metrics.lateral_edge_length,
            'base_area': result.metrics.base_area,
            'base_perimeter': result.metrics.base_perimeter,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


class TriangularAntiprismSolidService(RegularAntiprismSolidServiceBase):
    SIDES = 3


class SquareAntiprismSolidService(RegularAntiprismSolidServiceBase):
    SIDES = 4


class PentagonalAntiprismSolidService(RegularAntiprismSolidServiceBase):
    SIDES = 5


class HexagonalAntiprismSolidService(RegularAntiprismSolidServiceBase):
    SIDES = 6


class OctagonalAntiprismSolidService(RegularAntiprismSolidServiceBase):
    SIDES = 8


class HeptagonalAntiprismSolidService(RegularAntiprismSolidServiceBase):
    SIDES = 7


class TriangularAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    SIDES = 3
    SERVICE = TriangularAntiprismSolidService


class SquareAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    SIDES = 4
    SERVICE = SquareAntiprismSolidService


class PentagonalAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    SIDES = 5
    SERVICE = PentagonalAntiprismSolidService


class HexagonalAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    SIDES = 6
    SERVICE = HexagonalAntiprismSolidService


class OctagonalAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    SIDES = 8
    SERVICE = OctagonalAntiprismSolidService


class HeptagonalAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    SIDES = 7
    SERVICE = HeptagonalAntiprismSolidService


__all__ = [
    'RegularAntiprismMetrics',
    'RegularAntiprismSolidResult',
    'RegularAntiprismSolidServiceBase',
    'RegularAntiprismSolidCalculatorBase',
    'TriangularAntiprismSolidService',
    'TriangularAntiprismSolidCalculator',
    'SquareAntiprismSolidService',
    'SquareAntiprismSolidCalculator',
    'PentagonalAntiprismSolidService',
    'PentagonalAntiprismSolidCalculator',
    'HexagonalAntiprismSolidService',
    'HexagonalAntiprismSolidCalculator',
    'OctagonalAntiprismSolidService',
    'OctagonalAntiprismSolidCalculator',
    'HeptagonalAntiprismSolidService',
    'HeptagonalAntiprismSolidCalculator',
]
