"""Right rectangular pyramid solid service and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty


@dataclass(frozen=True)
class RectangularPyramidMetrics:
    """
    Rectangular Pyramid Metrics class definition.
    
    """
    base_length: float
    base_width: float
    height: float
    slant_length: float
    slant_width: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float
    base_diagonal: float
    lateral_edge: float


@dataclass(frozen=True)
class RectangularPyramidSolidResult:
    """
    Rectangular Pyramid Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: RectangularPyramidMetrics


def _compute_metrics(base_length: float, base_width: float, height: float) -> RectangularPyramidMetrics:
    half_length = base_length / 2.0
    half_width = base_width / 2.0
    slant_length = math.hypot(height, half_width)
    slant_width = math.hypot(height, half_length)
    base_area = base_length * base_width
    lateral_area = base_length * slant_length + base_width * slant_width
    surface_area = base_area + lateral_area
    volume = (base_area * height) / 3.0
    base_diagonal = math.hypot(base_length, base_width)
    lateral_edge = math.hypot(height, base_diagonal / 2.0)
    return RectangularPyramidMetrics(
        base_length=base_length,
        base_width=base_width,
        height=height,
        slant_length=slant_length,
        slant_width=slant_width,
        base_area=base_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        base_diagonal=base_diagonal,
        lateral_edge=lateral_edge,
    )


def _build_vertices(base_length: float, base_width: float, height: float) -> List[tuple[float, float, float]]:
    half_length = base_length / 2.0
    half_width = base_width / 2.0
    base_z = -height / 2.0
    apex_z = height / 2.0
    return [
        (-half_length, -half_width, base_z),
        (half_length, -half_width, base_z),
        (half_length, half_width, base_z),
        (-half_length, half_width, base_z),
        (0.0, 0.0, apex_z),
    ]


_BASE_EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (0, 4),
    (1, 4),
    (2, 4),
    (3, 4),
]

_BASE_FACES = [
    (0, 1, 2, 3),
    (0, 1, 4),
    (1, 2, 4),
    (2, 3, 4),
    (3, 0, 4),
]


class RectangularPyramidSolidService:
    """Generates payloads for right rectangular pyramids."""

    @staticmethod
    def build(base_length: float = 1.0, base_width: float = 1.0, height: float = 1.0) -> RectangularPyramidSolidResult:
        """
        Build logic.
        
        Args:
            base_length: Description of base_length.
            base_width: Description of base_width.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if base_length <= 0 or base_width <= 0 or height <= 0:
            raise ValueError("Base length, base width, and height must be positive")
        metrics = _compute_metrics(base_length, base_width, height)
        payload = SolidPayload(
            vertices=_build_vertices(base_length, base_width, height),
            edges=list(_BASE_EDGES),
            faces=[tuple(face) for face in _BASE_FACES],
            labels=[
                SolidLabel(text=f"a = {base_length:.3f}", position=(-base_length / 2.0, 0.0, -height / 2.0)),
                SolidLabel(text=f"b = {base_width:.3f}", position=(0.0, -base_width / 2.0, -height / 2.0)),
                SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
                'base_length': metrics.base_length,
                'base_width': metrics.base_width,
                'height': metrics.height,
                'slant_length': metrics.slant_length,
                'slant_width': metrics.slant_width,
                'base_area': metrics.base_area,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'base_diagonal': metrics.base_diagonal,
                'lateral_edge': metrics.lateral_edge,
            },
            suggested_scale=max(base_length, base_width, height),
        )
        return RectangularPyramidSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(base_length: float = 1.0, base_width: float = 1.0, height: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_length: Description of base_length.
            base_width: Description of base_width.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return RectangularPyramidSolidService.build(base_length, base_width, height).payload


class RectangularPyramidSolidCalculator:
    """Calculator for right rectangular pyramids."""

    _PROPERTY_DEFINITIONS = (
        ('base_length', 'Base Length', 'units', 4, True),
        ('base_width', 'Base Width', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_length', 'Slant Height (length faces)', 'units', 4, True),
        ('slant_width', 'Slant Height (width faces)', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
        ('base_diagonal', 'Base Diagonal', 'units', 4, False),
        ('lateral_edge', 'Lateral Edge', 'units', 4, False),
    )

    def __init__(self, base_length: float = 1.0, base_width: float = 1.0, height: float = 1.0):
        """
          init   logic.
        
        Args:
            base_length: Description of base_length.
            base_width: Description of base_width.
            height: Description of height.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_length = base_length if base_length > 0 else 1.0
        self._base_width = base_width if base_width > 0 else 1.0
        self._height = height if height > 0 else 1.0
        self._result: Optional[RectangularPyramidSolidResult] = None
        self._apply_dimensions(self._base_length, self._base_width, self._height)

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
        if key == 'base_length':
            self._apply_dimensions(value, self._base_width, self._height)
            return True
        if key == 'base_width':
            self._apply_dimensions(self._base_length, value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_length, self._base_width, value)
            return True
        if key == 'slant_length':
            half_width = self._base_width / 2.0
            if value <= half_width:
                return False
            height = math.sqrt(value ** 2 - half_width ** 2)
            self._apply_dimensions(self._base_length, self._base_width, height)
            return True
        if key == 'slant_width':
            half_length = self._base_length / 2.0
            if value <= half_length:
                return False
            height = math.sqrt(value ** 2 - half_length ** 2)
            self._apply_dimensions(self._base_length, self._base_width, height)
            return True
        if key == 'volume':
            base_area = self._base_length * self._base_width
            if base_area <= 0:
                return False
            height = (3.0 * value) / base_area
            self._apply_dimensions(self._base_length, self._base_width, height)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_length = 1.0
        self._base_width = 1.0
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

    def metrics(self) -> Optional[RectangularPyramidMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_length: float, base_width: float, height: float):
        if base_length <= 0 or base_width <= 0 or height <= 0:
            return
        self._base_length = base_length
        self._base_width = base_width
        self._height = height
        result = RectangularPyramidSolidService.build(base_length, base_width, height)
        self._result = result
        values = {
            'base_length': result.metrics.base_length,
            'base_width': result.metrics.base_width,
            'height': result.metrics.height,
            'slant_length': result.metrics.slant_length,
            'slant_width': result.metrics.slant_width,
            'base_area': result.metrics.base_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'base_diagonal': result.metrics.base_diagonal,
            'lateral_edge': result.metrics.lateral_edge,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'RectangularPyramidMetrics',
    'RectangularPyramidSolidResult',
    'RectangularPyramidSolidService',
    'RectangularPyramidSolidCalculator',
]