"""
THE KEYSTONE OF THE CORNER

"The Stone that links the Walls."

This module defines the geometry of the Corner Column (Keystone),
a Trapezoidal Prism that bridges the 128.57 degree angle between walls.
"""
import math
from typing import List
from PyQt6.QtGui import QVector3D, QColor
from pillars.adyton.models.geometry_types import Object3D, Face3D
from pillars.adyton.constants import (
    BLOCK_UNIT,
    Z_BIT_INCHES,
    WALL_HEIGHT_INCHES
)

class CornerStoneGeometry:
    """
    Generates the geometry for the Corner Column.
    
    Dimensions:
    - Inner Face Width: 1 Z'BIT (19.0")
    - Side Depth: 2 Z'BITS (38.0") -> Matches block depth
    - Outer Face Width determined by the Heptagon Angle.
    """
    
    @staticmethod
    def build(position: QVector3D, rotation_y: float, color: QColor, height: float = WALL_HEIGHT_INCHES) -> Object3D:
        """
        Builds a full-height corner column.
        Center is at the midpoint of the Prism.
        """
        
        # 1. Dimensions
        inner_w = Z_BIT_INCHES
        depth = BLOCK_UNIT # 38.0
        h = height
        
        # We need to calculate the Outer Width based on the angle.
        # Heptagon Internal Angle = 128.57 degrees.
        # The Corner Stone acts as a wedge.
        # If the sides are perpendicular to the adjacent walls?
        # No, the sides usually mate with the adjacent walls.
        # So the angle between the sides of this trapezoid should be?
        # If walls meet at 128.57 deg, the wedge fills the gap? 
        # Actually, the user says "2 sides of 2 zbits".
        # This implies it's a specific shape. 
        # Let's assume it's an Isosceles Trapezoid.
        # Inner Face = 19".
        # Sides = 38".
        # The angle of the wedge depends on the walls?
        # Actually, let's just make the trapezoid symmetrical.
        # We calculate the outer width based on the assumption that
        # the sides are perpendicular to the Heptagon Radius? 
        # No, that makes a rectangle.
        
        # Let's calculate based on the Heptagon Sector.
        # Angle of sector = 360/7 = 51.42 deg.
        # The corner stone is AT the vertex.
        # Its sides should align with the wall planes.
        # So the angle between the SIDES of the trapezoid is the Heptagon Angle (128.57).
        # Wait, if the sides align with walls, the angle between them IS the wall angle.
        # So the trapezoid tapers OUTWARDS?
        # No, he said "Inner Face 19".
        # If sides are 38" and angle is 128.57...
        # Let's construct vertices in Local Space (Z+ is OUT).
        
        half_inner = inner_w / 2.0
        
        # Inner Face (Back) is at Z = -something?
        # Let's align center of Inner Face to Z=0?
        # Actually, let's align geometric center.
        
        # Angle from normal to side: (180 - 128.57) / 2 = 25.715 degrees?
        # Or is the angle INSIDE the trapezoid?
        # Let's assume the sides radiate from the center of the room?
        # If they radiate, then it's a sector.
        # But walls are flat panels.
        
        # Let's try:
        # Inner Face at Z=0, width 19.
        # Sides angle back at 128.57/2 = 64.28 deg from the face?
        # No, the walls are at 128.57 to each other.
        # So the corner piece bisects this.
        # Side angle from "Forward" (Z+) = (180 - 128.57)/2 = 25.71 deg.
        
        angle_deg = (180.0 - (180.0 * 5.0 / 7.0)) / 2.0 # ~25.71 deg
        angle_rad = math.radians(angle_deg)
        
        dx = depth * math.sin(angle_rad) # Width increase per side
        dz = depth * math.cos(angle_rad) # Depth
        
        # Outer Width = Inner Width + 2*dx
        outer_w = inner_w + (2 * dx)
        
        half_outer = outer_w / 2.0
        
        # Vertices (Bottom) (y=0)
        # Inner Face (At Z_inner)
        # Outer Face (At Z_outer)
        # Let's center it locally on Z.
        mid_z = dz / 2.0
        
        # Inner (Back) - Z localized
        vib_l = QVector3D(-half_inner, 0, -mid_z)
        vib_r = QVector3D( half_inner, 0, -mid_z)
        
        # Outer (Front)
        vob_l = QVector3D(-half_outer, 0, mid_z)
        vob_r = QVector3D( half_outer, 0, mid_z)
        
        # Top Vertices (y=h)
        vit_l = QVector3D(-half_inner, h, -mid_z)
        vit_r = QVector3D( half_inner, h, -mid_z)
        vot_l = QVector3D(-half_outer, h, mid_z)
        vot_r = QVector3D( half_outer, h, mid_z)
        
        vertices = [vib_l, vib_r, vob_r, vob_l, vit_l, vit_r, vot_r, vot_l]
        
        faces = []
        
        # Front (Outer)
        faces.append(Face3D([vot_l, vot_r, vob_r, vob_l], color))
        # Back (Inner) - The 19" Face
        faces.append(Face3D([vib_r, vib_l, vib_l + QVector3D(0,h,0), vib_r + QVector3D(0,h,0)], color.lighter(110)))
        # Actually need correct indices for back face (CCW)
        # vib_r, vib_l, vit_l, vit_r
        faces[-1] = Face3D([vib_r, vib_l, vit_l, vit_r], color.lighter(110))
        
        # Left Side
        faces.append(Face3D([vib_l, vob_l, vot_l, vit_l], color.darker(110)))
        # Right Side
        faces.append(Face3D([vob_r, vib_r, vit_r, vot_r], color.darker(110)))
        # Top
        faces.append(Face3D([vot_l, vot_r, vit_r, vit_l], color.darker(120)))
        # Bottom
        faces.append(Face3D([vob_l, vob_r, vib_r, vib_l], color.darker(120)))
        
        obj = Object3D(faces=faces, position=position)
        obj.rotation = QVector3D(0, rotation_y, 0)
        return obj

