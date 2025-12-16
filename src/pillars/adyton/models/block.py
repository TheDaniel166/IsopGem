"""
THE ASHLAR OF THE ADYTON

"The Stone that the builders rejected."

This module defines the geometry of the individual Component Block (Ashlar),
which consists of a Base Cube and an inner-facing Pyramidal Frustum.
"""
from typing import List
from PyQt6.QtGui import QVector3D, QColor, QMatrix4x4
from pillars.adyton.models.geometry_types import Object3D, Face3D
from pillars.adyton.constants import (
    BLOCK_UNIT,
    FRUSTUM_BASE,
    FRUSTUM_TOP,
    FRUSTUM_HEIGHT
)

class AshlarGeometry:
    """
    Generates the composite geometry for a single Adyton Block.
    """
    @staticmethod
    def build(position: QVector3D, rotation_y: float, color: QColor) -> Object3D:
        """
        Builds a block at the given position with Y-rotation.
        Supports a Margin/Frame around the Frustum Base.
        """
        
        half_size = BLOCK_UNIT / 2.0
        
        # --- 1. Base Cube Vertices ---
        # 8 corners
        # Back Face (Z-)
        c1 = QVector3D(-half_size, -half_size, -half_size)
        c2 = QVector3D( half_size, -half_size, -half_size)
        c3 = QVector3D( half_size,  half_size, -half_size)
        c4 = QVector3D(-half_size,  half_size, -half_size)
        
        # Front Face (Z+) - The Outer Frame
        c5 = QVector3D(-half_size, -half_size,  half_size)
        c6 = QVector3D( half_size, -half_size,  half_size)
        c7 = QVector3D( half_size,  half_size,  half_size)
        c8 = QVector3D(-half_size,  half_size,  half_size)
        
        # --- 2. Frustum Base Vertices (Recessed into Z-) ---
        half_base = FRUSTUM_BASE / 2.0
        z_face = -half_size  # sink into the stone rather than protrude

        b1 = QVector3D(-half_base, -half_base, z_face)
        b2 = QVector3D( half_base, -half_base, z_face)
        b3 = QVector3D( half_base,  half_base, z_face)
        b4 = QVector3D(-half_base,  half_base, z_face)

        # --- 3. Frustum Cap Vertices (Deeper recess) ---
        half_top = FRUSTUM_TOP / 2.0
        z_top = z_face - FRUSTUM_HEIGHT

        f1 = QVector3D(-half_top, -half_top, z_top)
        f2 = QVector3D( half_top, -half_top, z_top)
        f3 = QVector3D( half_top,  half_top, z_top)
        f4 = QVector3D(-half_top,  half_top, z_top)
        
        # --- 4. Construct Faces ---
        faces = []
        
        # Base Cube Faces (Excluding Front Center)
        # Back, Left, Right, Top, Bottom work as before
        faces.append(Face3D([c1, c2, c3, c4], color))       # Back
        faces.append(Face3D([c1, c4, c8, c5], color))       # Left
        faces.append(Face3D([c2, c6, c7, c3], color))       # Right
        faces.append(Face3D([c4, c3, c7, c8], color))       # Top
        faces.append(Face3D([c1, c5, c6, c2], color))       # Bottom
        
        # Front Frame (The margin around the recessed pyramid)
        # We can implement this as 4 quads
        frame_color = color.lighter(105)
        # Bottom Frame
        faces.append(Face3D([c5, c6, b2, b1], frame_color))
        # Right Frame
        faces.append(Face3D([c6, c7, b3, b2], frame_color))
        # Top Frame
        faces.append(Face3D([c7, c8, b4, b3], frame_color))
        # Left Frame
        faces.append(Face3D([c8, c5, b1, b4], frame_color))
        
        # Frustum Sides (b -> f)
        # Bottom Side
        faces.append(Face3D([b1, b2, f2, f1], color.darker(110)))
        # Right Side
        faces.append(Face3D([b2, b3, f3, f2], color.darker(115)))
        # Top Side
        faces.append(Face3D([b3, b4, f4, f3], color.darker(110)))
        # Left Side
        faces.append(Face3D([b4, b1, f1, f4], color.darker(115)))
        
        # Frustum Cap (The Eye)
        faces.append(Face3D([f1, f2, f3, f4], color.lighter(120)))
        
        # --- 4. Transform Faces (Translate/Rotate) ---
        # We assume Object3D handles its own transform via position/rotation fields,
        # BUT since we are merging many blocks into a "Wall" or "Room" mesh, 
        # keeping them as separate Object3Ds might be heavy if the Scene list is huge.
        # However, for now, let's return an Object3D and let the Scene handle it.
        # But wait, creating 700 Object3Ds is fine, but rendering them requires looping.
        # The prompt asks for "walls constructed as pillars".
        
        # Let's return the Object3D initialized.
        obj = Object3D(faces=faces, position=position)
        # Set rotation (Euler angles in degrees)
        # We only rotate around Y usually for walls.
        obj.rotation = QVector3D(0, rotation_y, 0)
        
        return obj
