"""Square pyramid solid math utilities and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty


@dataclass(frozen=True)
class SquarePyramidMetrics:
    """
    Square Pyramid Metrics class definition.
    
    """
    base_edge: float
    height: float
    slant_height: float
    base_apothem: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float
    lateral_edge: float


@dataclass(frozen=True)
class SquarePyramidSolidResult:
    """
    Square Pyramid Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: SquarePyramidMetrics


def _compute_metrics(base_edge: float, height: float) -> SquarePyramidMetrics:
    half_edge = base_edge / 2.0
    slant_height = math.hypot(height, half_edge)
    base_area = base_edge ** 2
    lateral_area = 2.0 * base_edge * slant_height
    surface_area = base_area + lateral_area
    volume = (base_area * height) / 3.0
    half_diagonal = half_edge * math.sqrt(2.0)
    lateral_edge = math.hypot(height, half_diagonal)
    return SquarePyramidMetrics(
        base_edge=base_edge,
        height=height,
        slant_height=slant_height,
        base_apothem=half_edge,
        base_area=base_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        lateral_edge=lateral_edge,
    )


def _build_vertices(base_edge: float, height: float) -> List[tuple[float, float, float]]:
    half = base_edge / 2.0
    base_z = -height / 2.0
    apex_z = height / 2.0
    return [
        (-half, -half, base_z),
        (half, -half, base_z),
        (half, half, base_z),
        (-half, half, base_z),
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


class SquarePyramidSolidService:
    """Generates payloads for right square pyramids."""

    @staticmethod
    def build(base_edge: float = 1.0, height: float = 1.0) -> SquarePyramidSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of build operation.
        """
        if base_edge <= 0 or height <= 0:
            raise ValueError("Base edge and height must be positive")
        metrics = _compute_metrics(base_edge, height)
        payload = SolidPayload(
            vertices=_build_vertices(base_edge, height),
            edges=list(_BASE_EDGES),
            faces=[tuple(face) for face in _BASE_FACES],
            labels=[
                SolidLabel(text=f"a = {base_edge:.3f}", position=(-base_edge / 2.0, 0.0, -height / 2.0)),
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
                'lateral_edge': metrics.lateral_edge,
            },
            suggested_scale=max(base_edge, height),
        )
        return SquarePyramidSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(base_edge: float = 1.0, height: float = 1.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        Returns:
            Result of payload operation.
        """
        return SquarePyramidSolidService.build(base_edge, height).payload


class SquarePyramidSolidCalculator:
    """Calculator for right square pyramids with base edge and height inputs."""

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_height', 'Slant Height', 'units', 4, True),
        ('base_apothem', 'Base Apothem', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
        ('lateral_edge', 'Lateral Edge', 'units', 4, False),
    )

    def __init__(self, base_edge: float = 1.0, height: float = 1.0):
        """
          init   logic.
        
        Args:
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge if base_edge > 0 else 1.0
        self._height = height if height > 0 else 1.0
        self._result: Optional[SquarePyramidSolidResult] = None
        self._apply_dimensions(self._base_edge, self._height)

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
            self._apply_dimensions(value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_edge, value)
            return True
        if key == 'slant_height':
            half = self._base_edge / 2.0
            if value <= half:
                return False
            height = math.sqrt(value ** 2 - half ** 2)
            self._apply_dimensions(self._base_edge, height)
            return True
        if key == 'base_apothem':
            base_edge = value * 2.0
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'base_area':
            base_edge = math.sqrt(value)
            self._apply_dimensions(base_edge, self._height)
            return True
        if key == 'volume':
            if self._base_edge > 0:
                height = (3.0 * value) / (self._base_edge ** 2)
                self._apply_dimensions(self._base_edge, height)
                return True
            if self._height > 0:
                base_edge = math.sqrt((3.0 * value) / self._height)
                self._apply_dimensions(base_edge, self._height)
                return True
            return False
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_edge = 1.0
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

    def metrics(self) -> Optional[SquarePyramidMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, base_edge: float, height: float):
        if base_edge <= 0 or height <= 0:
            return
        self._base_edge = base_edge
        self._height = height
        result = SquarePyramidSolidService.build(base_edge, height)
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
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'SquarePyramidMetrics',
    'SquarePyramidSolidResult',
    'SquarePyramidSolidService',
    'SquarePyramidSolidCalculator',
]