"""Regular polygon pyramid frustum services and calculators."""
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
class RegularPyramidFrustumMetrics:
    """
    Regular Pyramid Frustum Metrics class definition.
    
    """
    sides: int
    base_edge: float
    top_edge: float
    height: float
    slant_height: float
    base_apothem: float
    top_apothem: float
    base_area: float
    top_area: float
    lateral_area: float
    surface_area: float
    volume: float
    base_perimeter: float
    top_perimeter: float
    base_circumradius: float
    top_circumradius: float
    lateral_edge: float


@dataclass(frozen=True)
class RegularPyramidFrustumSolidResult:
    """
    Regular Pyramid Frustum Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: RegularPyramidFrustumMetrics


def _apothem(sides: int, edge: float) -> float:
    return edge / (2.0 * math.tan(math.pi / sides))


def _circumradius(sides: int, edge: float) -> float:
    return edge / (2.0 * math.sin(math.pi / sides))


def _area(sides: int, edge: float) -> float:
    return (sides * edge ** 2) / (4.0 * math.tan(math.pi / sides))


def _edge_from_area(sides: int, area: float) -> float:
    return math.sqrt((4.0 * math.tan(math.pi / sides) * area) / sides)


def _compute_metrics(sides: int, base_edge: float, top_edge: float, height: float) -> RegularPyramidFrustumMetrics:
    base_apothem = _apothem(sides, base_edge)
    top_apothem = _apothem(sides, top_edge)
    base_area = _area(sides, base_edge)
    top_area = _area(sides, top_edge)
    base_perimeter = sides * base_edge
    top_perimeter = sides * top_edge
    apothem_delta = abs(base_apothem - top_apothem)
    slant_height = math.sqrt(height ** 2 + apothem_delta ** 2)
    lateral_area = 0.5 * (base_perimeter + top_perimeter) * slant_height
    surface_area = base_area + top_area + lateral_area
    volume = (height / 3.0) * (base_area + math.sqrt(base_area * top_area) + top_area)
    base_circumradius = _circumradius(sides, base_edge)
    top_circumradius = _circumradius(sides, top_edge)
    lateral_edge = math.sqrt(height ** 2 + (base_circumradius - top_circumradius) ** 2)
    return RegularPyramidFrustumMetrics(
        sides=sides,
        base_edge=base_edge,
        top_edge=top_edge,
        height=height,
        slant_height=slant_height,
        base_apothem=base_apothem,
        top_apothem=top_apothem,
        base_area=base_area,
        top_area=top_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        base_perimeter=base_perimeter,
        top_perimeter=top_perimeter,
        base_circumradius=base_circumradius,
        top_circumradius=top_circumradius,
        lateral_edge=lateral_edge,
    )


def _build_vertices(sides: int, base_edge: float, top_edge: float, height: float) -> List[Vec3]:
    base_radius = _circumradius(sides, base_edge)
    top_radius = _circumradius(sides, top_edge)
    base_z = -height / 2.0
    top_z = height / 2.0
    vertices: List[Vec3] = []
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        vertices.append((base_radius * math.cos(angle), base_radius * math.sin(angle), base_z))
    for i in range(sides):
        angle = (2.0 * math.pi * i) / sides
        vertices.append((top_radius * math.cos(angle), top_radius * math.sin(angle), top_z))
    return vertices


def _build_edges(sides: int) -> List[Edge]:
    edges: List[Edge] = []
    # base polygon
    for i in range(sides):
        edges.append((i, (i + 1) % sides))
    # top polygon
    offset = sides
    for i in range(sides):
        edges.append((offset + i, offset + ((i + 1) % sides)))
    # lateral edges
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


class RegularPyramidFrustumSolidServiceBase:
    """Base class for regular n-gon pyramid frustum services."""

    SIDES: int = 5
    NAME: str = 'Regular Pyramid Frustum'

    @classmethod
    def build(cls, base_edge: float = 2.0, top_edge: float = 1.0, height: float = 1.0) -> RegularPyramidFrustumSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if cls.SIDES < 3:
            raise ValueError('A pyramid base must have at least 3 sides')
        if base_edge <= 0 or top_edge <= 0 or height <= 0:
            raise ValueError('Base edge, top edge, and height must be positive')
        metrics = _compute_metrics(cls.SIDES, base_edge, top_edge, height)
        payload = SolidPayload(
            vertices=_build_vertices(cls.SIDES, base_edge, top_edge, height),
            edges=_build_edges(cls.SIDES),
            faces=_build_faces(cls.SIDES),
            labels=[
                SolidLabel(text=f"a = {base_edge:.3f}", position=(metrics.base_apothem, 0.0, -height / 2.0)),
                SolidLabel(text=f"b = {top_edge:.3f}", position=(metrics.top_apothem, 0.0, height / 2.0)),
                SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
                'base_edge': metrics.base_edge,
                'top_edge': metrics.top_edge,
                'height': metrics.height,
                'slant_height': metrics.slant_height,
                'base_apothem': metrics.base_apothem,
                'top_apothem': metrics.top_apothem,
                'base_area': metrics.base_area,
                'top_area': metrics.top_area,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'base_perimeter': metrics.base_perimeter,
                'top_perimeter': metrics.top_perimeter,
                'lateral_edge': metrics.lateral_edge,
            },
            suggested_scale=max(base_edge, top_edge, height),
        )
        return RegularPyramidFrustumSolidResult(payload=payload, metrics=metrics)

    @classmethod
    def payload(cls, base_edge: float = 2.0, top_edge: float = 1.0, height: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return cls.build(base_edge, top_edge, height).payload


class RegularPyramidFrustumSolidCalculatorBase:
    """Base calculator for regular pyramid frustums."""

    SIDES: int = 5
    SERVICE: Type[RegularPyramidFrustumSolidServiceBase] = RegularPyramidFrustumSolidServiceBase

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('top_edge', 'Top Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_height', 'Slant Height', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('top_area', 'Top Area', 'units²', 4, True),
        ('lateral_area', 'Lateral Area', 'units²', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('base_apothem', 'Base Apothem', 'units', 4, False),
        ('top_apothem', 'Top Apothem', 'units', 4, False),
        ('lateral_edge', 'Lateral Edge', 'units', 4, False),
    )

    def __init__(self, base_edge: float = 2.0, top_edge: float = 1.0, height: float = 1.0):
        """
          init   logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge if base_edge > 0 else 2.0
        self._top_edge = top_edge if top_edge > 0 else 1.0
        self._height = height if height > 0 else 1.0
        self._result: Optional[RegularPyramidFrustumSolidResult] = None
        self._apply_dimensions(self._base_edge, self._top_edge, self._height)

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if value is None or value <= 0:
            return False
        if key == 'base_edge':
            self._apply_dimensions(value, self._top_edge, self._height)
            return True
        if key == 'top_edge':
            self._apply_dimensions(self._base_edge, value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_edge, self._top_edge, value)
            return True
        if key == 'slant_height':
            base_apothem = _apothem(self.SIDES, self._base_edge)
            top_apothem = _apothem(self.SIDES, self._top_edge)
            delta = abs(base_apothem - top_apothem)
            if value <= delta:
                return False
            height = math.sqrt(value ** 2 - delta ** 2)
            self._apply_dimensions(self._base_edge, self._top_edge, height)
            return True
        if key == 'base_area':
            base_edge = _edge_from_area(self.SIDES, value)
            self._apply_dimensions(base_edge, self._top_edge, self._height)
            return True
        if key == 'top_area':
            top_edge = _edge_from_area(self.SIDES, value)
            self._apply_dimensions(self._base_edge, top_edge, self._height)
            return True
        if key == 'lateral_area':
            # L = 0.5 * (P_base + P_top) * slant_height
            # slant_height = 2*L / (P_base + P_top)
            # height = sqrt(slant_height^2 - delta_apothem^2)
            p_base = self.SIDES * self._base_edge
            p_top = self.SIDES * self._top_edge
            peri_sum = p_base + p_top
            if peri_sum <= 0: return False
            
            slant_height = (2.0 * value) / peri_sum
            
            base_apothem = _apothem(self.SIDES, self._base_edge)
            top_apothem = _apothem(self.SIDES, self._top_edge)
            delta = abs(base_apothem - top_apothem)
            
            if slant_height < delta: return False
            
            height = math.sqrt(slant_height**2 - delta**2)
            self._apply_dimensions(self._base_edge, self._top_edge, height)
            return True
            
        if key == 'surface_area':
            # S = Base + Top + Lateral
            # L = S - Base - Top
            base_area = _area(self.SIDES, self._base_edge)
            top_area = _area(self.SIDES, self._top_edge)
            area_sum = base_area + top_area
            if value <= area_sum: return False
            
            lateral_area = value - area_sum
            return self.set_property('lateral_area', lateral_area)

        if key == 'volume':
            base_area = _area(self.SIDES, self._base_edge)
            top_area = _area(self.SIDES, self._top_edge)
            denom = base_area + math.sqrt(base_area * top_area) + top_area
            if denom <= 0:
                return False
            height = (3.0 * value) / denom
            self._apply_dimensions(self._base_edge, self._top_edge, height)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_edge = 2.0
        self._top_edge = 1.0
        self._height = 1.0
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        """
        Payload logic.
        
        Returns:
            Result of payload operation.
        """
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        """
        Metadata logic.
        
        Returns:
            Result of metadata operation.
        """
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> Optional[RegularPyramidFrustumMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_edge: float, top_edge: float, height: float):
        if base_edge <= 0 or top_edge <= 0 or height <= 0:
            return
        self._base_edge = base_edge
        self._top_edge = top_edge
        self._height = height
        result = self.SERVICE.build(base_edge, top_edge, height)
        self._result = result
        values = {
            'base_edge': result.metrics.base_edge,
            'top_edge': result.metrics.top_edge,
            'height': result.metrics.height,
            'slant_height': result.metrics.slant_height,
            'base_area': result.metrics.base_area,
            'top_area': result.metrics.top_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'base_apothem': result.metrics.base_apothem,
            'top_apothem': result.metrics.top_apothem,
            'lateral_edge': result.metrics.lateral_edge,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


class PentagonalPyramidFrustumSolidService(RegularPyramidFrustumSolidServiceBase):
    """
    Pentagonal Pyramid Frustum Solid Service class definition.
    
    """
    SIDES = 5
    NAME = 'Pentagonal Pyramid Frustum'


class PentagonalPyramidFrustumSolidCalculator(RegularPyramidFrustumSolidCalculatorBase):
    """
    Pentagonal Pyramid Frustum Solid Calculator class definition.
    
    """
    SIDES = 5
    SERVICE = PentagonalPyramidFrustumSolidService


class HexagonalPyramidFrustumSolidService(RegularPyramidFrustumSolidServiceBase):
    """
    Hexagonal Pyramid Frustum Solid Service class definition.
    
    """
    SIDES = 6
    NAME = 'Hexagonal Pyramid Frustum'


class HexagonalPyramidFrustumSolidCalculator(RegularPyramidFrustumSolidCalculatorBase):
    """
    Hexagonal Pyramid Frustum Solid Calculator class definition.
    
    """
    SIDES = 6
    SERVICE = HexagonalPyramidFrustumSolidService


__all__ = [
    'RegularPyramidFrustumMetrics',
    'RegularPyramidFrustumSolidResult',
    'RegularPyramidFrustumSolidServiceBase',
    'RegularPyramidFrustumSolidCalculatorBase',
    'PentagonalPyramidFrustumSolidService',
    'PentagonalPyramidFrustumSolidCalculator',
    'HexagonalPyramidFrustumSolidService',
    'HexagonalPyramidFrustumSolidCalculator',
]