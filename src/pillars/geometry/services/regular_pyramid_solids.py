"""Right regular n-gonal pyramid solid services and calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Type

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty

Vec3 = Tuple[float, float, float]
Edge = Tuple[int, int]
Face = Sequence[int]


@dataclass(frozen=True)
class RegularPyramidMetrics:
    sides: int
    base_edge: float
    height: float
    slant_height: float
    base_apothem: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float
    base_perimeter: float
    base_circumradius: float
    lateral_edge: float


@dataclass(frozen=True)
class RegularPyramidSolidResult:
    payload: SolidPayload
    metrics: RegularPyramidMetrics


def _apothem(sides: int, base_edge: float) -> float:
    return base_edge / (2.0 * math.tan(math.pi / sides))


def _circumradius(sides: int, base_edge: float) -> float:
    return base_edge / (2.0 * math.sin(math.pi / sides))


def _base_area(sides: int, base_edge: float) -> float:
    return (sides * base_edge ** 2) / (4.0 * math.tan(math.pi / sides))


def _edge_from_area(sides: int, area: float) -> float:
    return math.sqrt((4.0 * math.tan(math.pi / sides) * area) / sides)


def _edge_from_apothem(sides: int, apothem: float) -> float:
    return 2.0 * apothem * math.tan(math.pi / sides)


def _compute_metrics(sides: int, base_edge: float, height: float) -> RegularPyramidMetrics:
    perimeter = sides * base_edge
    apothem = _apothem(sides, base_edge)
    base_area = _base_area(sides, base_edge)
    slant_height = math.sqrt(height ** 2 + apothem ** 2)
    lateral_area = 0.5 * perimeter * slant_height
    surface_area = base_area + lateral_area
    volume = (base_area * height) / 3.0
    circumradius = _circumradius(sides, base_edge)
    lateral_edge = math.sqrt(height ** 2 + circumradius ** 2)
    return RegularPyramidMetrics(
        sides=sides,
        base_edge=base_edge,
        height=height,
        slant_height=slant_height,
        base_apothem=apothem,
        base_area=base_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        base_perimeter=perimeter,
        base_circumradius=circumradius,
        lateral_edge=lateral_edge,
    )


def _build_vertices(sides: int, base_edge: float, height: float) -> List[Vec3]:
    radius = _circumradius(sides, base_edge)
    base_z = -height / 2.0
    apex_z = height / 2.0
    vertices = []
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        vertices.append((radius * math.cos(angle), radius * math.sin(angle), base_z))
    vertices.append((0.0, 0.0, apex_z))
    return vertices


def _build_edges(sides: int) -> List[Edge]:
    edges: List[Edge] = []
    for i in range(sides):
        edges.append((i, (i + 1) % sides))
        edges.append((i, sides))  # apex index is sides
    return edges


def _build_faces(sides: int) -> List[Face]:
    faces: List[Face] = [tuple(range(sides))]
    for i in range(sides):
        faces.append((i, (i + 1) % sides, sides))
    return faces


class RegularPyramidSolidServiceBase:
    """Base implementation for right regular n-gonal pyramids."""

    SIDES: int = 3
    NAME: str = 'Regular Pyramid'

    @classmethod
    def build(cls, base_edge: float = 1.0, height: float = 1.0) -> RegularPyramidSolidResult:
        if cls.SIDES < 3:
            raise ValueError('A pyramid base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')
        metrics = _compute_metrics(cls.SIDES, base_edge, height)
        payload = SolidPayload(
            vertices=_build_vertices(cls.SIDES, base_edge, height),
            edges=_build_edges(cls.SIDES),
            faces=_build_faces(cls.SIDES),
            labels=[
                SolidLabel(text=f"a = {base_edge:.3f}", position=(metrics.base_apothem, 0.0, -height / 2.0)),
                SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
                'base_edge': metrics.base_edge,
                'height': metrics.height,
                'slant_height': metrics.slant_height,
                'base_apothem': metrics.base_apothem,
                'base_area': metrics.base_area,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'base_perimeter': metrics.base_perimeter,
                'base_circumradius': metrics.base_circumradius,
                'lateral_edge': metrics.lateral_edge,
            },
            suggested_scale=max(base_edge, height),
        )
        return RegularPyramidSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, base_edge: float = 1.0, height: float = 1.0) -> SolidPayload:
        return cls.build(base_edge, height).payload


class RegularPyramidSolidCalculatorBase:
    """Base calculator for right regular n-gonal pyramids."""

    SIDES: int = 3
    SERVICE: Type[RegularPyramidSolidServiceBase] = RegularPyramidSolidServiceBase

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_height', 'Slant Height', 'units', 4, True),
        ('base_apothem', 'Base Apothem', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('lateral_area', 'Lateral Area', 'units²', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('lateral_edge', 'Lateral Edge', 'units', 4, False),
        ('base_perimeter', 'Base Perimeter', 'units', 4, False),
    )

    def __init__(self, base_edge: float = 1.0, height: float = 1.0):
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge if base_edge > 0 else 1.0
        self._height = height if height > 0 else 1.0
        self._result: Optional[RegularPyramidSolidResult] = None
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
        if key == 'slant_height':
            apothem = _apothem(self.SIDES, self._base_edge)
            if value <= apothem:
                return False
            height = math.sqrt(value ** 2 - apothem ** 2)
            self._apply_dimensions(self._base_edge, height)
            return True
        if key == 'base_apothem':
            base_edge = _edge_from_apothem(self.SIDES, value)
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'base_area':
            base_edge = _edge_from_area(self.SIDES, value)
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'volume':
            base_area = _base_area(self.SIDES, self._base_edge)
            if base_area <= 0:
                return False
            height = (3.0 * value) / base_area
            self._apply_dimensions(self._base_edge, height)
            return True
            
        if key == 'lateral_area':
            # L = 0.5 * P * s_height
            # P = n * base_edge
            # s_height = 2*L / P
            perimeter = self.SIDES * self._base_edge
            if perimeter <= 0: return False
            slant_height = (2.0 * value) / perimeter
            
            # Now solve for height from slant_height
            # s^2 = h^2 + a^2 => h = sqrt(s^2 - a^2)
            apothem = _apothem(self.SIDES, self._base_edge)
            if slant_height < apothem: return False
            height = math.sqrt(slant_height**2 - apothem**2)
            self._apply_dimensions(self._base_edge, height)
            return True
            
        if key == 'surface_area':
            # S = BaseArea + LateralArea
            # L = S - BaseArea
            base_area = _base_area(self.SIDES, self._base_edge)
            if value <= base_area: return False
            lateral_area = value - base_area
            
            # Now solve for height via L logic above
            perimeter = self.SIDES * self._base_edge
            slant_height = (2.0 * lateral_area) / perimeter
            apothem = _apothem(self.SIDES, self._base_edge)
            if slant_height < apothem: return False
            height = math.sqrt(slant_height**2 - apothem**2)
            self._apply_dimensions(self._base_edge, height)
            return True
        return False

    def clear(self):
        self._base_edge = 1.0
        self._height = 1.0
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> Optional[RegularPyramidMetrics]:
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
            'slant_height': result.metrics.slant_height,
            'base_apothem': result.metrics.base_apothem,
            'base_area': result.metrics.base_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'lateral_edge': result.metrics.lateral_edge,
            'base_perimeter': result.metrics.base_perimeter,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


class TriangularPyramidSolidService(RegularPyramidSolidServiceBase):
    SIDES = 3
    NAME = 'Equilateral Triangular Pyramid'


class PentagonalPyramidSolidService(RegularPyramidSolidServiceBase):
    SIDES = 5
    NAME = 'Regular Pentagonal Pyramid'


class HexagonalPyramidSolidService(RegularPyramidSolidServiceBase):
    SIDES = 6
    NAME = 'Regular Hexagonal Pyramid'


class HeptagonalPyramidSolidService(RegularPyramidSolidServiceBase):
    SIDES = 7
    NAME = 'Regular Heptagonal Pyramid'


class TriangularPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    SIDES = 3
    SERVICE = TriangularPyramidSolidService


class PentagonalPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    SIDES = 5
    SERVICE = PentagonalPyramidSolidService


class HexagonalPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    SIDES = 6
    SERVICE = HexagonalPyramidSolidService


class HeptagonalPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    SIDES = 7
    SERVICE = HeptagonalPyramidSolidService


__all__ = [
    'RegularPyramidMetrics',
    'RegularPyramidSolidResult',
    'RegularPyramidSolidServiceBase',
    'RegularPyramidSolidCalculatorBase',
    'TriangularPyramidSolidService',
    'TriangularPyramidSolidCalculator',
    'PentagonalPyramidSolidService',
    'PentagonalPyramidSolidCalculator',
    'HexagonalPyramidSolidService',
    'HexagonalPyramidSolidCalculator',
    'HeptagonalPyramidSolidService',
    'HeptagonalPyramidSolidCalculator',
]
