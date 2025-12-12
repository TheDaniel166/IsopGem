"""Irregular Polygon shape calculator."""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple

from .base_shape import GeometricShape, ShapeProperty
from .quadrilateral_shape import _shoelace_area, _polygon_centroid


class IrregularPolygonShape(GeometricShape):
    """
    Arbitrary polygon defined by a list of vertices.
    Supports calculating Area, Perimeter, and Centroid.
    Editors are generated dynamically for each vertex coordinate.
    """

    def __init__(self, points: Optional[List[Tuple[float, float]]] = None):
        self._points: List[Tuple[float, float]] = points if points else []
        super().__init__()
        # If points were passed, ensure properties exist match them
        if self._points:
             self._sync_coord_properties()
             self._recalculate()

    @property
    def name(self) -> str:
        return f"Irregular {len(self._points)}-gon" if self._points else "Irregular Polygon"

    @property
    def description(self) -> str:
        return "Custom polygon defined by 3+ vertices"

    @property
    def calculation_hint(self) -> str:
        return "Edit vertices in points table (Read-only properties)"

    def _init_properties(self):
        """Initialize base properties."""
        self.properties = {
            'area': ShapeProperty(name='Area', key='area', unit='units²', readonly=True),
            'perimeter': ShapeProperty(name='Perimeter', key='perimeter', unit='units', readonly=True),
            'centroid_x': ShapeProperty(name='Centroid X', key='centroid_x', unit='', readonly=True),
            'centroid_y': ShapeProperty(name='Centroid Y', key='centroid_y', unit='', readonly=True),
            'num_vertices': ShapeProperty(name='Vertex Count', key='num_vertices', unit='', readonly=True, precision=0),
        }

    def set_points(self, points: List[Tuple[float, float]]):
        """Set the vertices and update properties."""
        self._points = points
        self._sync_coord_properties()
        self._recalculate()

    def _sync_coord_properties(self):
        """Create x/y properties for current points."""
        # Use a consistent naming scheme: v0_x, v0_y, v1_x, ...
        # First, remove old vertex properties to avoid stale ones if count shrank
        keys_to_remove = [k for k in self.properties.keys() if k.startswith('v') and ('_x' in k or '_y' in k)]
        for k in keys_to_remove:
            del self.properties[k]
            
        for i, (x, y) in enumerate(self._points):
            self.properties[f'v{i}_x'] = ShapeProperty(
                name=f'Vertex {i+1} X',
                key=f'v{i}_x',
                value=x,
                readonly=False
            )
            self.properties[f'v{i}_y'] = ShapeProperty(
                name=f'Vertex {i+1} Y',
                key=f'v{i}_y',
                value=y,
                readonly=False
            )
        
        self.properties['num_vertices'].value = float(len(self._points))

    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """Update a coordinate."""
        if property_key.startswith('v') and ('_x' in property_key or '_y' in property_key):
            # Parse index
            try:
                parts = property_key.split('_')
                idx = int(parts[0][1:]) # v0 -> 0
                coord = parts[1] # x or y
                
                if idx < 0 or idx >= len(self._points):
                    return False
                
                x, y = self._points[idx]
                if coord == 'x':
                    self._points[idx] = (value, y)
                else:
                    self._points[idx] = (x, value)
                    
                self.properties[property_key].value = value
                self._recalculate()
                return True
            except (ValueError, IndexError):
                return False
                
        return False

    def _recalculate(self):
        """Update derived metrics."""
        if len(self._points) < 3:
            self.properties['area'].value = 0.0
            self.properties['perimeter'].value = 0.0
            return

        self.properties['area'].value = _shoelace_area(tuple(self._points))
        self.properties['perimeter'].value = self._calculate_perimeter()
        cx, cy = _polygon_centroid(tuple(self._points))
        self.properties['centroid_x'].value = cx
        self.properties['centroid_y'].value = cy

    def _calculate_perimeter(self) -> float:
        p = 0.0
        n = len(self._points)
        for i in range(n):
            p1 = self._points[i]
            p2 = self._points[(i + 1) % n]
            p += math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        return p

    def get_drawing_instructions(self) -> Dict:
        if not self._points or len(self._points) < 3:
             return {'type': 'empty'}
        return {
            'type': 'polygon',
            'points': self._points
        }

    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        if not self._points or len(self._points) < 3:
            return []
        
        labels = []
        cx, cy = _polygon_centroid(tuple(self._points))
        area = self.properties['area'].value
        labels.append((f"A = {area:.2f}", cx, cy))
        
        # Vertex labels?
        for i, (x, y) in enumerate(self._points):
            labels.append((f"{i+1}", x + 0.2, y + 0.2))
            
        return labels
