"""
THE THRONE OF THE CHARIOTEER (Geometry)

A truncated tetrahedron (frustum) representing the seat of the adept.
Height is derived from the 19-inch sacred cubit.
"""
import math
from typing import List
from PyQt6.QtGui import QVector3D, QColor

from pillars.adyton.models.geometry_types import Face3D, Object3D
from pillars.adyton.constants import COLOR_GOLD, COLOR_SILVER

# Subtractive Colors (CMYK)
COLOR_CYAN    = QColor(0, 255, 255)
COLOR_MAGENTA = QColor(255, 0, 255)
COLOR_YELLOW  = QColor(255, 255, 0)
COLOR_KEY     = QColor(20, 20, 20)      # Black

class ThroneGeometry:
    """
    Throne Geometry class definition.
    
    Attributes:
        todo: Add public attributes.
    """

    @staticmethod
    def build(
        height: float = 19.0,
        base_side: float = 60.0,
        y_offset: float = -10.0
    ) -> Object3D:
        """
        Build the Throne as a frustum of a tetrahedron.
        """
        top_side = (3.0 / 7.0) * base_side
        
        # Triangle geometry helper
        r_base = base_side / math.sqrt(3.0)
        r_top  = top_side / math.sqrt(3.0)
        
        # Vertices for Base (y = y_offset)
        # One point aligned to the central column of the central Wall (-Z axis)
        b0 = QVector3D(0, y_offset, -r_base)
        b1 = QVector3D(r_base * math.cos(math.pi / 6), y_offset, r_base * math.sin(math.pi / 6))
        b2 = QVector3D(r_base * math.cos(5 * math.pi / 6), y_offset, r_base * math.sin(5 * math.pi / 6))
        
        # Vertices for Top (y = y_offset + height)
        t_y = y_offset + height
        t0 = QVector3D(0, t_y, -r_top)
        t1 = QVector3D(r_top * math.cos(math.pi / 6), t_y, r_top * math.sin(math.pi / 6))
        t2 = QVector3D(r_top * math.cos(5 * math.pi / 6), t_y, r_top * math.sin(5 * math.pi / 6))
        
        faces: List[Face3D] = []
        
        # 1. Base (Key/Black)
        faces.append(Face3D(
            vertices=[b0, b2, b1], 
            color=COLOR_KEY,
            outline_color=COLOR_KEY,
            shading=False
        ))
        
        # 2. Top (Crown of the Charioteer - Black)
        faces.append(Face3D(
            vertices=[t0, t1, t2], 
            color=COLOR_KEY,
            outline_color=COLOR_KEY,
            shading=False
        ))
        
        # 3. Slanted Sides (CMYK)
        # Side 0: b0-b1-t1-t0 (Front-Right face relative to Venus-vertex b0)
        faces.append(Face3D(
            vertices=[b0, b1, t1, t0],
            color=COLOR_CYAN,
            outline_color=COLOR_CYAN,
            shading=False
        ))
        
        # Side 1: b1-b2-t2-t1 (Back face, facing toward the entrance/Sun - Yellow)
        faces.append(Face3D(
            vertices=[b1, b2, t2, t1],
            color=COLOR_YELLOW,
            outline_color=COLOR_YELLOW,
            shading=False
        ))
        
        # Side 2: b2-b0-t0-t2 (Front-Left face relative to Venus-vertex b0)
        faces.append(Face3D(
            vertices=[b2, b0, t0, t2],
            color=COLOR_MAGENTA,
            outline_color=COLOR_MAGENTA,
            shading=False
        ))
        
        obj = Object3D(faces=faces)
        return obj