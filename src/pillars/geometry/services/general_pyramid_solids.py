"""General (n-gonal) Pyramid Solid Services and Calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

from ..shared.solid_payload import SolidPayload
from .regular_pyramid_solids import (
    RegularPyramidSolidServiceBase,
    RegularPyramidSolidCalculatorBase,
    RegularPyramidMetrics,
)
from .solid_property import SolidProperty


class GeneralPyramidSolidService(RegularPyramidSolidServiceBase):
    """Service for general n-gonal right regular pyramids."""

    @classmethod
    def build_dynamic(cls, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        from .regular_pyramid_solids import _compute_metrics, _build_vertices, _build_edges, _build_faces
        from ..shared.solid_payload import SolidLabel, SolidPayload

        if sides < 3:
            raise ValueError('A pyramid base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')

        metrics = _compute_metrics(sides, base_edge, height)
        payload = SolidPayload(
            vertices=_build_vertices(sides, base_edge, height),
            edges=_build_edges(sides),
            faces=_build_faces(sides),
            labels=[
                SolidLabel(text=f"n = {sides}", position=(0.0, 0.0, height / 2.0 + 0.2)),
                SolidLabel(text=f"a = {base_edge:.3f}", position=(metrics.base_apothem, 0.0, -height / 2.0)),
                SolidLabel(text=f"h = {height:.3f}", position=(0.0, 0.0, 0.0)),
            ],
            metadata={
                'sides': sides,
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
            suggested_scale=max(base_edge * 2, height),
        )
        
        # Manually construct result since Base class expects class attributes
        from .regular_pyramid_solids import RegularPyramidSolidResult
        return RegularPyramidSolidResult(payload=payload, metrics=metrics)


class GeneralPyramidSolidCalculator(RegularPyramidSolidCalculatorBase):
    """Calculator for general n-gonal right regular pyramids."""

    _PROPERTY_DEFINITIONS = (
        ('sides', 'Sides (n)', 'n', 0, True),
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('slant_height', 'Slant Height', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, False),
    )

    def __init__(self, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        self._properties: Dict[str, SolidProperty] = {
            key: SolidProperty(name=label, key=key, unit=unit, precision=precision, editable=editable)
            for key, label, unit, precision, editable in self._PROPERTY_DEFINITIONS
        }
        self._sides = int(sides) if sides >= 3 else 5
        self._base_edge = base_edge if base_edge > 0 else 2.0
        self._height = height if height > 0 else 4.0
        self._result = None
        self._apply_dimensions(self._base_edge, self._height, self._sides)

    def set_property(self, key: str, value: Optional[float]) -> bool:
        if value is None or value <= 0:
            return False
            
        if key == 'sides':
            n = int(value)
            if n < 3: return False
            self._apply_dimensions(self._base_edge, self._height, n)
            return True
            
        # For typical properties, we delegate to base logic BUT 
        # the base logic relies on self.SIDES, which is class-level.
        # So we must override the property setters logic or dynamically patch self.SIDES (which doesn't exist on instance).
        # We must re-implement the setter logic fully or hack it.
        # Since the logic is simple equations, cleaner to just copy/adapt it here using self._sides.
        
        return self._handle_dynamic_property_set(key, value)

    def _handle_dynamic_property_set(self, key: str, value: float) -> bool:
        sides = self._sides
        # Import helpers locally to avoid code dupe or just use them from module imports
        from .regular_pyramid_solids import _apothem, _edge_from_apothem, _edge_from_area, _base_area
        
        if key == 'base_edge':
            self._apply_dimensions(value, self._height, sides)
            return True
        if key == 'height':
            self._apply_dimensions(self._base_edge, value, sides)
            return True
        if key == 'slant_height':
            apothem = _apothem(sides, self._base_edge)
            if value <= apothem:
                return False
            height = math.sqrt(value ** 2 - apothem ** 2)
            self._apply_dimensions(self._base_edge, height, sides)
            return True
        # NOTE: base_apothem not in current defs but good to support? 
        # It's not in _PROPERTY_DEFINITIONS above, so skipped for now.
        
        if key == 'base_area':
            base_edge = _edge_from_area(sides, value)
            self._apply_dimensions(base_edge, self._height, sides)
            return True
        if key == 'volume':
            base_area_val = _base_area(sides, self._base_edge)
            if base_area_val <= 0:
                return False
            height = (3.0 * value) / base_area_val
            self._apply_dimensions(self._base_edge, height, sides)
            return True
            
        return False

    def _apply_dimensions(self, base_edge: float, height: float, sides: Optional[int] = None):
        if sides is not None:
            self._sides = int(sides)
        
        if base_edge <= 0 or height <= 0:
            return
            
        self._base_edge = base_edge
        self._height = height
        
        # Use our dynamic build
        result = GeneralPyramidSolidService.build_dynamic(int(self._sides), base_edge, height)
        self._result = result
        
        values = {
            'sides': self._sides,
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'slant_height': result.metrics.slant_height,
            'base_area': result.metrics.base_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            if key in values:
                prop.value = values[key]
