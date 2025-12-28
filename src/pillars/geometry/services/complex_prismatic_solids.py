"""Complex Prismatic and Johnson Solids."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..shared.solid_payload import SolidLabel, SolidPayload
from .solid_geometry import Vec3, edges_from_faces
from .solid_property import SolidProperty


@dataclass(frozen=True)
class ComplexSolidResult:
    """
    Complex Solid Result class definition.
    
    """
    payload: SolidPayload
    metadata: Dict[str, float]


class SnubAntiprismSolidService:
    """Service for the Snub Square Antiprism (Johnson Solid J85)."""

    @staticmethod
    def build(edge: float = 2.0) -> ComplexSolidResult:
        # Canonical constants for edge=2
        """
        Build logic.
        
        Args:
            edge: Description of edge.
        
        Returns:
            Result of build operation.
        """
        A = 1.715731736910394
        B = 0.371214042564360
        C = 1.353737018062712
        sqrt2 = math.sqrt(2)
        
        # Scale factor
        s = edge / 2.0
        
        raw_verts = [
            (1, 1, C), (-1, 1, C), (-1, -1, C), (1, -1, C),      # 0-3
            (sqrt2*A, 0, B), (-sqrt2*A, 0, B),                  # 4, 5
            (0, sqrt2*A, B), (0, -sqrt2*A, B),                  # 6, 7
            (A, A, -B), (-A, A, -B), (-A, -A, -B), (A, -A, -B), # 8-11
            (sqrt2, 0, -C), (-sqrt2, 0, -C),                    # 12, 13
            (0, sqrt2, -C), (0, -sqrt2, -C)                     # 14, 15
        ]
        vertices = [(v[0]*s, v[1]*s, v[2]*s) for v in raw_verts]
        
        faces = [
            # Squares
            (0, 1, 2, 3), (12, 14, 13, 15),
            # Triangles
            (0, 1, 6), (0, 3, 4), (0, 4, 8), (0, 6, 8),
            (1, 2, 5), (1, 5, 9), (1, 6, 9),
            (2, 3, 7), (2, 5, 10), (2, 7, 10),
            (3, 4, 11), (3, 7, 11),
            (4, 8, 12), (4, 11, 12),
            (5, 9, 13), (5, 10, 13),
            (6, 8, 14), (6, 9, 14),
            (7, 10, 15), (7, 11, 15),
            (8, 12, 14), (9, 13, 14),
            (10, 13, 15), (11, 12, 15)
        ]
        
        edges = edges_from_faces(faces)
        
        # Approx Area: 2 * square + 24 * triangle
        # Area of square = edge^2
        # Area of equilateral triangle = (sqrt(3)/4) * edge^2
        surface_area = (2 + 6 * math.sqrt(3)) * (edge ** 2)
        
        # Approx Volume for edge=2 (canonical)
        # Numerical integration or derived formula for J85 volume is complex
        # Ref: V = (approx) 3.602 edge^3
        volume = 3.6024 * (edge ** 3)
        
        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=[SolidLabel(text="J85", position=(0,0, C*s + 0.5))],
            metadata={
                'edge': edge,
                'surface_area': surface_area,
                'volume': volume
            },
            suggested_scale=edge * 3.0
        )
        return ComplexSolidResult(payload, payload.metadata)


class SnubAntiprismSolidCalculator:
    """
    Snub Antiprism Solid Calculator class definition.
    
    Attributes:
        _properties: Description of _properties.
        _edge: Description of _edge.
        _result: Description of _result.
    
    """
    def __init__(self, edge: float = 2.0):
        """
          init   logic.
        
        Args:
            edge: Description of edge.
        
        """
        self._properties = {
            'edge': SolidProperty('Edge Length', 'edge', 'units', edge),
            'surface_area': SolidProperty('Surface Area', 'surface_area', 'units²', 0.0, editable=False),
            'volume': SolidProperty('Volume', 'volume', 'units³', 0.0, editable=False),
        }
        self._edge = edge
        self._result = None
        self._recalculate()

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        return list(self._properties.values())

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if key == 'edge' and value and value > 0:
            self._edge = value
            self._recalculate()
            return True
        return False

    def _recalculate(self):
        self._result = SnubAntiprismSolidService.build(self._edge)
        self._properties['edge'].value = self._edge
        self._properties['surface_area'].value = self._result.metadata['surface_area']
        self._properties['volume'].value = self._result.metadata['volume']

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
        return self._result.metadata if self._result else {}

    def clear(self):
        """
        Clear logic.
        
        """
        pass


class GyroelongatedSquarePrismSolidService:
    """A hybrid solid: Square Prism + Square Antiprism."""

    @staticmethod
    def build(edge: float = 2.0, prism_h: float = 2.0, anti_h: float = 1.414) -> ComplexSolidResult:
        # Square Prism Vertices (Bottom)
        # z from 0 to prism_h
        """
        Build logic.
        
        Args:
            edge: Description of edge.
            prism_h: Description of prism_h.
            anti_h: Description of anti_h.
        
        Returns:
            Result of build operation.
        """
        r_prism = edge / math.sqrt(2)
        v_prism = []
        for i in range(4):
            angle = (2 * math.pi * i) / 4 + math.pi/4
            v_prism.append((r_prism * math.cos(angle), r_prism * math.sin(angle), 0.0))
        for i in range(4):
            angle = (2 * math.pi * i) / 4 + math.pi/4
            v_prism.append((r_prism * math.cos(angle), r_prism * math.sin(angle), prism_h))
            
        # Square Antiprism (Top)
        # z from prism_h to prism_h + anti_h
        # Bottom ring of antiprism is the same as top ring of prism
        v_anti = []
        # Top ring rotated by 45 degrees
        for i in range(4):
            angle = (2 * math.pi * i) / 4 + math.pi/4 + math.pi/4
            v_anti.append((r_prism * math.cos(angle), r_prism * math.sin(angle), prism_h + anti_h))
            
        vertices = v_prism + v_anti
        
        faces = [
            # Bottom Square
            (0, 1, 2, 3),
            # Prism Sides
            (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
            # Antiprism Sides (Triangles)
            (4, 9, 8), (4, 5, 9),
            (5, 10, 9), (5, 6, 10),
            (6, 11, 10), (6, 7, 11),
            (7, 8, 11), (7, 4, 8),
            # Top Square
            (8, 11, 10, 9)
        ]
        
        edges = edges_from_faces(faces)
        
        # Area = Base + 4*PrismFace + 8*Triangle + Top
        # Area = a^2 + 4*(a*h_p) + 8*(sqrt(3)/4 * a^2) + a^2
        sa = 2 * (edge**2) + 4 * (edge * prism_h) + 2 * math.sqrt(3) * (edge**2)
        vol = (edge**2) * prism_h + (edge**2 * anti_h / 3.0) * (1 + math.sqrt(2)/2) # Approx vol for antiprism
        
        # Better vol for square antiprism: V = (a^3 / 3) * sqrt(4 - sec^2(pi/2n))? 
        # For n=4, h_a = a * sqrt(1 - 1/2) = a/sqrt(2).
        # Vol = (1/3) * a^2 * h_a * (something)?
        # For square antiprism: V = (a^3 / 3) * sqrt(2)
        vol = (edge**2) * prism_h + (edge**3 / 3.0) * math.sqrt(2)
        
        payload = SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            labels=[SolidLabel(text="Hybrid", position=(0,0, prism_h + anti_h + 0.5))],
            metadata={'edge': edge, 'prism_height': prism_h, 'antiprism_height': anti_h, 'surface_area': sa, 'volume': vol},
            suggested_scale=max(edge, prism_h + anti_h) * 2.5
        )
        return ComplexSolidResult(payload, payload.metadata)


class GyroelongatedSquarePrismSolidCalculator:
    """
    Gyroelongated Square Prism Solid Calculator class definition.
    
    Attributes:
        _properties: Description of _properties.
        _edge: Description of _edge.
        _prism_h: Description of _prism_h.
        _result: Description of _result.
    
    """
    def __init__(self, edge: float = 2.0, prism_h: float = 2.0):
        """
          init   logic.
        
        Args:
            edge: Description of edge.
            prism_h: Description of prism_h.
        
        """
        self._properties = {
            'edge': SolidProperty('Edge Length', 'edge', 'units', edge),
            'prism_height': SolidProperty('Prism Height', 'prism_h', 'units', prism_h),
            'surface_area': SolidProperty('Surface Area', 'surface_area', 'units²', 0.0, editable=False),
            'volume': SolidProperty('Volume', 'volume', 'units³', 0.0, editable=False),
        }
        self._edge = edge
        self._prism_h = prism_h
        self._result = None
        self._recalculate()

    def properties(self) -> List[SolidProperty]:
        """
        Properties logic.
        
        Returns:
            Result of properties operation.
        """
        return list(self._properties.values())

    def set_property(self, key: str, value: Optional[float]) -> bool:
        """
        Configure property logic.
        
        Args:
            key: Description of key.
            value: Description of value.
        
        Returns:
            Result of set_property operation.
        """
        if value and value > 0:
            if key == 'edge': self._edge = value
            elif key == 'prism_height': self._prism_h = value
            else: return False
            self._recalculate()
            return True
        return False

    def _recalculate(self):
        anti_h = self._edge / math.sqrt(2) # Natural height for regular triangle faces
        self._result = GyroelongatedSquarePrismSolidService.build(self._edge, self._prism_h, anti_h)
        self._properties['edge'].value = self._edge
        self._properties['prism_height'].value = self._prism_h
        self._properties['surface_area'].value = self._result.metadata['surface_area']
        self._properties['volume'].value = self._result.metadata['volume']

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
        return self._result.metadata if self._result else {}

    def clear(self):
        """
        Clear logic.
        
        """
        pass