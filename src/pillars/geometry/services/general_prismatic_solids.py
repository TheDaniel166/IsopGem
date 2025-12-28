"""General (n-gonal) Prismatic Solid Services and Calculators."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

from ..shared.solid_payload import SolidPayload
from .regular_prism_solids import (
    RegularPrismSolidServiceBase,
    RegularPrismSolidCalculatorBase,
    RegularPrismMetrics,
)
from .regular_antiprism_solids import (
    RegularAntiprismSolidServiceBase,
    RegularAntiprismSolidCalculatorBase,
    RegularAntiprismMetrics,
)
from .solid_property import SolidProperty


class GeneralPrismSolidService(RegularPrismSolidServiceBase):
    """Service for general n-gonal right regular prisms."""

    @classmethod
    def build_dynamic(cls, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        # Temporarily set SIDES for the base class methods if needed, 
        # but better to just call the helper functions directly.
        """
        Build dynamic logic.
        
        Args:
            sides: Description of sides.
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
        from .regular_prism_solids import _compute_metrics, _build_vertices, _build_edges, _build_faces
        from ..shared.solid_payload import SolidLabel
        
        if sides < 3:
            raise ValueError('A prism base must have at least 3 sides')
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
                'base_area': metrics.base_area,
                'base_perimeter': metrics.base_perimeter,
                'base_apothem': metrics.base_apothem,
                'base_circumradius': metrics.base_circumradius,
                'lateral_area': metrics.lateral_area,
                'surface_area': metrics.surface_area,
                'volume': metrics.volume,
            },
            suggested_scale=max(base_edge * 2, height),
        )
        # We wrap it in a mock result class or just return payload
        from .regular_prism_solids import RegularPrismSolidResult
        return RegularPrismSolidResult(payload=payload, metrics=metrics)


class GeneralPrismSolidCalculator(RegularPrismSolidCalculatorBase):
    """Calculator for general n-gonal right regular prisms."""

    _PROPERTY_DEFINITIONS = (
        ('sides', 'Sides (n)', 'n', 0, True),
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('base_area', 'Base Area', 'units²', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, False),
    )

    def __init__(self, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        """
          init   logic.
        
        Args:
            sides: Description of sides.
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
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
            
        if key == 'sides':
            n = int(value)
            if n < 3: return False
            self._apply_dimensions(self._base_edge, self._height, n)
            return True
            
        # Call base logic for other properties, but override _apply_dimensions
        return super().set_property(key, value)

    def _apply_dimensions(self, base_edge: float, height: float, sides: Optional[int] = None):
        if sides is not None:
            self._sides = int(sides)
        
        if base_edge <= 0 or height <= 0:
            return
            
        self._base_edge = base_edge
        self._height = height
        
        # Use our dynamic build
        result = GeneralPrismSolidService.build_dynamic(int(self._sides), base_edge, height)
        self._result = result
        
        values = {
            'sides': self._sides,
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'base_area': result.metrics.base_area,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            if key in values:
                prop.value = values[key]


class GeneralAntiprismSolidService(RegularAntiprismSolidServiceBase):
    """Service for general n-gonal right regular antiprisms."""

    @classmethod
    def build_dynamic(cls, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        """
        Build dynamic logic.
        
        Args:
            sides: Description of sides.
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
        from .regular_antiprism_solids import _create_payload, RegularAntiprismSolidResult
        
        if sides < 3:
            raise ValueError('An antiprism base must have at least 3 sides')
        if base_edge <= 0 or height <= 0:
            raise ValueError('Base edge and height must be positive')
            
        payload, metrics = _create_payload(sides, base_edge, height)
        return RegularAntiprismSolidResult(payload=payload, metrics=metrics)


class GeneralAntiprismSolidCalculator(RegularAntiprismSolidCalculatorBase):
    """Calculator for general n-gonal right regular antiprisms."""

    _PROPERTY_DEFINITIONS = (
        ('sides', 'Sides (n)', 'n', 0, True),
        ('base_edge', 'Base Edge', 'units', 4, True),
        ('height', 'Height', 'units', 4, True),
        ('volume', 'Volume', 'units³', 4, True),
        ('surface_area', 'Surface Area', 'units²', 4, False),
    )

    def __init__(self, sides: int = 5, base_edge: float = 2.0, height: float = 4.0):
        """
          init   logic.
        
        Args:
            sides: Description of sides.
            base_edge: Description of base_edge.
            height: Description of height.
        
        """
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
            
        if key == 'sides':
            n = int(value)
            if n < 3: return False
            self._apply_dimensions(self._base_edge, self._height, n)
            return True
            
        return super().set_property(key, value)

    def _apply_dimensions(self, base_edge: float, height: float, sides: Optional[int] = None):
        if sides is not None:
            self._sides = int(sides)
            
        if base_edge <= 0 or height <= 0:
            return
            
        self._base_edge = base_edge
        self._height = height
        
        result = GeneralAntiprismSolidService.build_dynamic(int(self._sides), base_edge, height)
        self._result = result
        
        values = {
            'sides': self._sides,
            'base_edge': result.metrics.base_edge,
            'height': result.metrics.height,
            'surface_area': result.metrics.surface_area,
            'volume': result.metrics.volume,
        }
        for key, prop in self._properties.items():
            if key in values:
                prop.value = values[key]