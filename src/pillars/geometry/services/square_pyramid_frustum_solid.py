"""Square pyramid frustum solid service and calculator.

THE SQUARE PYRAMID FRUSTUM - TRUNCATED FOUR-FOLD FORM:
=======================================================

This is the square (n=4) special case of the regular pyramid frustum.

The square frustum is the MOST COMMON frustum in daily life and architecture:
- Buckets, planters, waste baskets (stable, stackable)
- Lampshades (diffuses light evenly)
- Ancient monuments (stepped pyramid platforms)
- Modern tapered buildings (structural efficiency + aesthetics)

Special property: All four lateral faces are congruent isosceles trapezoids!

ESSENTIAL FORMULAS (Square Frustum):
-------------------------------------

Volume (Heronian formula for square case):
    V = (h/3) × (a² + ab + b²)
    
    where a = base_edge, b = top_edge
    
    This expands to: V = (h/3) × (a² + b² + √(a²b²))
                     = (h/3) × (a² + b² + ab)  [geometric mean = ab for squares]

Lateral Area (4 congruent trapezoids):
    A_lateral = 2 × (a + b) × s
    
    where s = slant height = √(h² + ((a-b)/2)²)
    
    Each trapezoid: bases a and b, height s
    Area = ((a+b)/2) × s
    Total: 4 × ((a+b)/2) × s = 2(a+b) × s

Total Surface Area:
    A_total = a² + b² + 2(a+b)s

Simplification: The square case (n=4) has simpler formulas than general n-gon
because square geometry uses simple Pythagorean relationships!
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty


@dataclass(frozen=True)
class SquarePyramidFrustumMetrics:
    """
    Square Pyramid Frustum Metrics class definition.
    
    """
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
    lateral_edge: float


@dataclass(frozen=True)
class SquarePyramidFrustumSolidResult:
    """
    Square Pyramid Frustum Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: SquarePyramidFrustumMetrics


def _compute_metrics(base_edge: float, top_edge: float, height: float) -> SquarePyramidFrustumMetrics:
    base_apothem = base_edge / 2.0
    top_apothem = top_edge / 2.0
    apothem_delta = base_apothem - top_apothem
    slant_height = math.sqrt(height ** 2 + apothem_delta ** 2)
    base_area = base_edge ** 2
    top_area = top_edge ** 2
    lateral_area = 2.0 * (base_edge + top_edge) * slant_height
    surface_area = base_area + top_area + lateral_area
    volume = (height / 3.0) * (base_area + math.sqrt(base_area * top_area) + top_area)
    lateral_edge_offset = (base_edge - top_edge) * math.sqrt(2.0) / 2.0
    lateral_edge = math.sqrt(height ** 2 + lateral_edge_offset ** 2)
    return SquarePyramidFrustumMetrics(
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
        lateral_edge=lateral_edge,
    )


def _build_vertices(base_edge: float, top_edge: float, height: float) -> List[tuple[float, float, float]]:
    half_base = base_edge / 2.0
    half_top = top_edge / 2.0
    base_z = -height / 2.0
    top_z = height / 2.0
    return [
        (-half_base, -half_base, base_z),
        (half_base, -half_base, base_z),
        (half_base, half_base, base_z),
        (-half_base, half_base, base_z),
        (-half_top, -half_top, top_z),
        (half_top, -half_top, top_z),
        (half_top, half_top, top_z),
        (-half_top, half_top, top_z),
    ]


_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]

_FACES = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (1, 2, 6, 5),
    (2, 3, 7, 6),
    (3, 0, 4, 7),
]


class SquarePyramidFrustumSolidService:
    """Generates payloads for right square pyramid frustums."""

    @staticmethod
    def build(base_edge: float = 2.0, top_edge: float = 1.0, height: float = 1.0) -> SquarePyramidFrustumSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if base_edge <= 0 or top_edge <= 0 or height <= 0:
            raise ValueError('Base edge, top edge, and height must be positive')
        metrics = _compute_metrics(base_edge, top_edge, height)
        payload = SolidPayload(
            vertices=_build_vertices(base_edge, top_edge, height),
            edges=list(_EDGES),
            faces=[tuple(face) for face in _FACES],
            labels=[
                SolidLabel(text=f"a = {base_edge:.3f}", position=(-base_edge / 2.0, 0.0, -height / 2.0)),
                SolidLabel(text=f"b = {top_edge:.3f}", position=(0.0, -top_edge / 2.0, height / 2.0)),
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
                'lateral_edge': metrics.lateral_edge,
            },
            suggested_scale=max(base_edge, height),
        )
        return SquarePyramidFrustumSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(base_edge: float = 2.0, top_edge: float = 1.0, height: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            top_edge: Description of top_edge.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return SquarePyramidFrustumSolidService.build(base_edge, top_edge, height).payload


class SquarePyramidFrustumSolidCalculator:
    """Calculator for right square pyramid frustums."""

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('top_edge', 'Top Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_height', 'Slant Height', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('top_area', 'Top Area', 'units²', 4, True),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
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
        self._result: Optional[SquarePyramidFrustumSolidResult] = None
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
            apothem_delta = abs(self._base_edge - self._top_edge) / 2.0
            if value <= apothem_delta:
                return False
            height = math.sqrt(value ** 2 - apothem_delta ** 2)
            self._apply_dimensions(self._base_edge, self._top_edge, height)
            return True
        if key == 'base_area':
            base_edge = math.sqrt(value)
            self._apply_dimensions(base_edge, self._top_edge, self._height)
            return True
        if key == 'top_area':
            top_edge = math.sqrt(value)
            self._apply_dimensions(self._base_edge, top_edge, self._height)
            return True
        if key == 'volume':
            denom = (self._base_edge ** 2 + self._base_edge * self._top_edge + self._top_edge ** 2)
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

    def metrics(self) -> Optional[SquarePyramidFrustumMetrics]:
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
        result = SquarePyramidFrustumSolidService.build(base_edge, top_edge, height)
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


__all__ = [
    'SquarePyramidFrustumMetrics',
    'SquarePyramidFrustumSolidResult',
    'SquarePyramidFrustumSolidService',
    'SquarePyramidFrustumSolidCalculator',
]