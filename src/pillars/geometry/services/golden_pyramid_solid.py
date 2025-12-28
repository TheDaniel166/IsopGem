"""Golden ratio-aligned square pyramid service and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty

PHI = (1.0 + math.sqrt(5.0)) / 2.0
_HEIGHT_FACTOR = math.sqrt(PHI ** 2 - 1.0) / 2.0  # height = base_edge * factor


def _height_from_base(base_edge: float) -> float:
    return base_edge * _HEIGHT_FACTOR


def _base_from_height(height: float) -> float:
    return height / _HEIGHT_FACTOR if _HEIGHT_FACTOR else 0.0


def _slant_from_base(base_edge: float) -> float:
    return PHI * (base_edge / 2.0)


def _compute_metrics(base_edge: float) -> 'GoldenPyramidMetrics':
    height = _height_from_base(base_edge)
    slant_height = _slant_from_base(base_edge)
    base_apothem = base_edge / 2.0
    base_area = base_edge ** 2
    lateral_area = 2.0 * base_edge * slant_height
    surface_area = base_area + lateral_area
    volume = (base_area * height) / 3.0
    return GoldenPyramidMetrics(
        base_edge=base_edge,
        height=height,
        slant_height=slant_height,
        phi_ratio=PHI,
        base_apothem=base_apothem,
        base_area=base_area,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
    )


@dataclass(frozen=True)
class GoldenPyramidMetrics:
    """
    Golden Pyramid Metrics class definition.
    
    """
    base_edge: float
    height: float
    slant_height: float
    phi_ratio: float
    base_apothem: float
    base_area: float
    lateral_area: float
    surface_area: float
    volume: float


@dataclass(frozen=True)
class GoldenPyramidSolidResult:
    """
    Golden Pyramid Solid Result class definition.
    
    """
    payload: SolidPayload
    metrics: GoldenPyramidMetrics


class GoldenPyramidSolidService:
    """Generates payloads for golden ratio square pyramids."""

    @staticmethod
    def build(base_edge: float = 440.0) -> GoldenPyramidSolidResult:
        """
        Build logic.
        
        Args:
            base_edge: Description of base_edge.
        
        Returns:
            Result of build operation.
        """
        if base_edge <= 0:
            raise ValueError('Base edge must be positive')
        metrics = _compute_metrics(base_edge)
        half = base_edge / 2.0
        height = metrics.height
        payload = SolidPayload(
            vertices=[
                (-half, -half, -height / 2.0),
                (half, -half, -height / 2.0),
                (half, half, -height / 2.0),
                (-half, half, -height / 2.0),
                (0.0, 0.0, height / 2.0),
            ],
            edges=[
                (0, 1), (1, 2), (2, 3), (3, 0),
                (0, 4), (1, 4), (2, 4), (3, 4),
            ],
            faces=[
                (0, 1, 2, 3),
                (0, 1, 4),
                (1, 2, 4),
                (2, 3, 4),
                (3, 0, 4),
            ],
            labels=[
                SolidLabel(text=f"a = {base_edge:.2f}", position=(-half, 0.0, -height / 2.0)),
                SolidLabel(text=f"h = {height:.2f}", position=(0.0, 0.0, 0.0)),
                SolidLabel(text=f"φ = {PHI:.5f}", position=(0.0, half, 0.0)),
            ],
            metadata={
                'base_edge': metrics.base_edge,
                'height': metrics.height,
                'slant_height': metrics.slant_height,
                'phi_ratio': metrics.phi_ratio,
                'base_apothem': metrics.base_apothem,
                'base_area': metrics.base_area,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
            },
            suggested_scale=base_edge,
        )
        return GoldenPyramidSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(base_edge: float = 440.0) -> SolidPayload:
        """
        Payload logic.
        
        Args:
            base_edge: Description of base_edge.
        
        Returns:
            Result of payload operation.
        """
        return GoldenPyramidSolidService.build(base_edge).payload


class GoldenPyramidSolidCalculator:
    """Calculator enforcing the golden-ratio relationship between slant and base."""

    _PROPERTY_DEFINITIONS = (
        ('base_edge', 'Base Edge', 'units', 3, True),
        ('height', 'Height', 'units', 3, True),
        ('slant_height', 'Slant Height', 'units', 3, True),
        ('phi_ratio', 'Phi Ratio', '', 5, False),
        ('base_apothem', 'Half Base Edge', 'units', 3, False),
        ('base_area', 'Base Area', 'units²', 3, False),
        ('lateral_area', 'Lateral Area', 'units²', 3, False),
        ('surface_area', 'Surface Area', 'units²', 3, False),
        ('volume', 'Volume', 'units³', 3, True),
    )

    def __init__(self, base_edge: float = 440.0):
        """
          init   logic.
        
        Args:
            base_edge: Description of base_edge.
        
        """
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._base_edge = base_edge if base_edge > 0 else 440.0
        self._result: Optional[GoldenPyramidSolidResult] = None
        self._apply_base_edge(self._base_edge)

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
            self._apply_base_edge(value)
            return True
        if key == 'height':
            base_edge = _base_from_height(value)
            self._apply_base_edge(base_edge)
            return True
        if key == 'slant_height':
            base_edge = (2.0 * value) / PHI
            self._apply_base_edge(base_edge)
            return True
        if key == 'volume':
            base_edge = (3.0 * value / _HEIGHT_FACTOR) ** (1.0 / 3.0)
            self._apply_base_edge(base_edge)
            return True
        return False

    def clear(self):
        """
        Clear logic.
        
        """
        self._base_edge = 440.0
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

    def metrics(self) -> Optional[GoldenPyramidMetrics]:
        """
        Metrics logic.
        
        Returns:
            Result of metrics operation.
        """
        return self._result.metrics if self._result else None

    def _apply_base_edge(self, base_edge: float):
        if base_edge <= 0:
            return
        self._base_edge = base_edge
        result = GoldenPyramidSolidService.build(base_edge)
        self._result = result
        values = {
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'slant_height': result.metrics.slant_height,
            'phi_ratio': result.metrics.phi_ratio,
            'base_apothem': result.metrics.base_apothem,
            'base_area': result.metrics.base_area,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'GoldenPyramidMetrics',
    'GoldenPyramidSolidResult',
    'GoldenPyramidSolidService',
    'GoldenPyramidSolidCalculator',
]