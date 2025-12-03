"""Right rectangular prism solid service and calculator."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_property import SolidProperty


@dataclass(frozen=True)
class RectangularPrismMetrics:
    length: float
    width: float
    height: float
    base_area: float
    base_perimeter: float
    lateral_area: float
    surface_area: float
    volume: float
    face_diagonal_length: float
    face_diagonal_width: float
    space_diagonal: float


@dataclass(frozen=True)
class RectangularPrismSolidResult:
    payload: SolidPayload
    metrics: RectangularPrismMetrics


def _compute_metrics(length: float, width: float, height: float) -> RectangularPrismMetrics:
    base_area = length * width
    base_perimeter = 2.0 * (length + width)
    lateral_area = base_perimeter * height
    surface_area = 2.0 * (base_area + length * height + width * height)
    volume = base_area * height
    face_diagonal_length = math.hypot(length, height)
    face_diagonal_width = math.hypot(width, height)
    space_diagonal = math.sqrt(length ** 2 + width ** 2 + height ** 2)
    return RectangularPrismMetrics(
        length=length,
        width=width,
        height=height,
        base_area=base_area,
        base_perimeter=base_perimeter,
        lateral_area=lateral_area,
        surface_area=surface_area,
        volume=volume,
        face_diagonal_length=face_diagonal_length,
        face_diagonal_width=face_diagonal_width,
        space_diagonal=space_diagonal,
    )


def _build_vertices(length: float, width: float, height: float) -> List[tuple[float, float, float]]:
    half_l = length / 2.0
    half_w = width / 2.0
    half_h = height / 2.0
    return [
        (-half_l, -half_w, -half_h),
        (half_l, -half_w, -half_h),
        (half_l, half_w, -half_h),
        (-half_l, half_w, -half_h),
        (-half_l, -half_w, half_h),
        (half_l, -half_w, half_h),
        (half_l, half_w, half_h),
        (-half_l, half_w, half_h),
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


class RectangularPrismSolidService:
    """Generates payloads for axis-aligned right rectangular prisms."""

    @staticmethod
    def build(length: float = 4.0, width: float = 2.0, height: float = 3.0) -> RectangularPrismSolidResult:
        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError('Length, width, and height must be positive')
        metrics = _compute_metrics(length, width, height)
        payload = SolidPayload(
            vertices=_build_vertices(length, width, height),
            edges=list(_EDGES),
            faces=[tuple(face) for face in _FACES],
            labels=[
                SolidLabel(text=f"L = {length:.3f}", position=(0.0, -width / 2.0, -height / 2.0)),
                SolidLabel(text=f"W = {width:.3f}", position=(-length / 2.0, 0.0, -height / 2.0)),
                SolidLabel(text=f"H = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
                'length': metrics.length,
                'width': metrics.width,
                'height': metrics.height,
                'base_area': metrics.base_area,
                'base_perimeter': metrics.base_perimeter,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
                'face_diagonal_length': metrics.face_diagonal_length,
                'face_diagonal_width': metrics.face_diagonal_width,
                'space_diagonal': metrics.space_diagonal,
            },
            suggested_scale=max(length, width, height),
        )
        return RectangularPrismSolidResult(payload=payload, metrics=metrics)

    @staticmethod
    def payload(length: float = 4.0, width: float = 2.0, height: float = 3.0) -> SolidPayload:
        return RectangularPrismSolidService.build(length, width, height).payload


class RectangularPrismSolidCalculator:
    """Calculator for right rectangular prisms allowing bidirectional updates."""

    _PROPERTY_DEFINITIONS = (
        ('length', 'Length', 'units', 4, True),
        ('width', 'Width', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, False),
        ('base_perimeter', 'Base Perimeter', 'units', 4, False),
        ('lateral_area', 'Lateral Area', 'units²', 4, False),
        ('surface_area', 'Surface Area', 'units²', 4, False),
        ('volume', 'Volume', 'units³', 4, True),
        ('face_diagonal_length', 'Face Diagonal (length faces)', 'units', 4, False),
        ('face_diagonal_width', 'Face Diagonal (width faces)', 'units', 4, False),
        ('space_diagonal', 'Space Diagonal', 'units', 4, False),
    )

    def __init__(self, length: float = 4.0, width: float = 2.0, height: float = 3.0):
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._length = length if length > 0 else 4.0
        self._width = width if width > 0 else 2.0
        self._height = height if height > 0 else 3.0
        self._result: Optional[RectangularPrismSolidResult] = None
        self._apply_dimensions(self._length, self._width, self._height)

    def properties(self) -> List[SolidProperty]:
        return [self._properties[key] for key, *_ in self._PROPERTY_DEFINITIONS]

    def set_property(self, key: str, value: Optional[float]) -> bool:
        if value is None or value <= 0:
            return False
        if key == 'length':
            self._apply_dimensions(value, self._width, self._height)
            return True
        if key == 'width':
            self._apply_dimensions(self._length, value, self._height)
            return True
        if key == 'height':
            self._apply_dimensions(self._length, self._width, value)
            return True
        if key == 'volume':
            base_area = self._length * self._width
            if base_area <= 0:
                return False
            height = value / base_area
            self._apply_dimensions(self._length, self._width, height)
            return True
        return False

    def clear(self):
        self._length = 4.0
        self._width = 2.0
        self._height = 3.0
        for prop in self._properties.values():
            prop.value = None
        self._result = None

    def payload(self) -> Optional[SolidPayload]:
        return self._result.payload if self._result else None

    def metadata(self) -> Dict[str, float]:
        if not self._result:
            return {}
        return dict(self._result.payload.metadata)

    def metrics(self) -> Optional[RectangularPrismMetrics]:
        return self._result.metrics if self._result else None

    def _apply_dimensions(self, length: float, width: float, height: float):
        if length <= 0 or width <= 0 or height <= 0:
            return
        self._length = length
        self._width = width
        self._height = height
        result = RectangularPrismSolidService.build(length, width, height)
        self._result = result
        values = {
            'length': result.metrics.length,
            'width': result.metrics.width,
            'height': result.metrics.height,
            'base_area': result.metrics.base_area,
            'base_perimeter': result.metrics.base_perimeter,
            'lateral_area': result.metrics.lateral_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
            'face_diagonal_length': result.metrics.face_diagonal_length,
            'face_diagonal_width': result.metrics.face_diagonal_width,
            'space_diagonal': result.metrics.space_diagonal,
        }
        for key, prop in self._properties.items():
            prop.value = values.get(key)


__all__ = [
    'RectangularPrismMetrics',
    'RectangularPrismSolidResult',
    'RectangularPrismSolidService',
    'RectangularPrismSolidCalculator',
]
