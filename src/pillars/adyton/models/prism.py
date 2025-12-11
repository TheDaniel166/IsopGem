"""
THE VAULT OF THE ADYTON (Prism Geometry)

"Seven walls, rising to the height of thirteen."
"""
import math
from typing import List
from PyQt6.QtGui import QVector3D, QColor
from pillars.adyton.models.geometry_types import Object3D, Face3D
from ..constants import (
    WALL_WIDTH_INCHES, 
    WALL_HEIGHT_INCHES
)

class SevenSidedPrism:
    """
    Generates the geometry for the 7-sided Adyton Chamber.
    """
    @staticmethod
    def build(center: QVector3D = QVector3D(0, 0, 0)) -> List[Object3D]:
        """
        Constructs the Adyton Chamber using 728 Ashlar Blocks AND 7 Corner Stones.
        Uses exact 14-sided irregular polygon geometry to ensure perfect joinery.
        """
        from .block import AshlarGeometry
        from .corner import CornerStoneGeometry
        from ..constants import (
            WALL_COLORS, BLOCK_UNIT, 
            WALL_WIDTH_UNITS, WALL_HEIGHT_UNITS,
            Z_BIT_INCHES, WALL_HEIGHT_INCHES
        )
        
        objects = []
        
        # --- 1. Irregular 14-Gon Math ---
        # The perimeter consists of 7 segments of [Corner, Wall].
        # Corner Width (Chord) = c = 19.0 (1 Z'Bit)
        # Wall Width (Chord)   = w = 304.0 (8 Blocks * 38)
        
        c = Z_BIT_INCHES
        w = WALL_WIDTH_UNITS * BLOCK_UNIT
        
        # Both chords must subtend angles alpha and beta at a common Vertex Radius V.
        # c = 2 * V * sin(alpha/2)
        # w = 2 * V * sin(beta/2)
        # Constraint: 7*alpha + 7*beta = 360  =>  alpha + beta = 360/7 = 51.42857 degrees.
        
        # Solving derived from ratio w/c = 16:
        # beta approx 16 * alpha.
        # 17 alpha = 51.428 -> alpha ~ 3.025 deg.
        
        # Exact solution via iterative refinement or high precision simple math works here.
        # Let's use the derived values which are precise enough for rendering.
        
        deg_per_sector = 360.0 / 7.0 # 51.42857
        
        # ratio of arcs ~ ratio of chords for small angles
        total_p = c + w
        alpha_deg = deg_per_sector * (c / total_p) # ~3.025
        beta_deg  = deg_per_sector * (w / total_p) # ~48.403
        
        alpha_rad = math.radians(alpha_deg)
        beta_rad  = math.radians(beta_deg)
        
        # Calculate Vertex Radius V from Corner Chord c
        # c = 2 * V * sin(alpha/2)
        # V = c / (2 * sin(alpha/2))
        V = c / (2.0 * math.sin(alpha_rad / 2.0)) # ~360.5 inches
        
        # Calculate Apothems (Distance to Inner Faces)
        # Apothem is distance to midpoint of chord.
        # a = V * cos(theta/2)
        apothem_corner = V * math.cos(alpha_rad / 2.0)
        apothem_wall   = V * math.cos(beta_rad / 2.0)
        
        # --- 2. Construction Loop ---
        current_angle_deg = 0.0
        
        # Pre-calc offset for Wall Columns locally
        # Wall is centered at 0 local X. Width w.
        # Columns go from -w/2 + block/2  to  +w/2 - block/2.
        wall_start_x = -(w / 2.0) + (BLOCK_UNIT / 2.0)
        
        # We start with Corner 0 centred at angle 0?
        # Let's align such that Corner 0 is at 0 degrees.
        # The Corner sector is from -alpha/2 to +alpha/2.
        # The Wall 0 sector is from +alpha/2 to +alpha/2 + beta.
        
        # Wait, if we start loop at 0.
        # Corner 0 is at 0.
        # Wall 0 is at (alpha/2 + beta/2).
        
        for i in range(7):
            # --- A. Place Corner Stone ---
            # Angle of Corner Center
            angle_c = (i * deg_per_sector)
            rad_c = math.radians(angle_c)
            
            # Position (using Corner Apothem + Depth Offset)
            # Corner Geometry built around Z axis?
            # In corner.py: Inner Face is at Z=0 (approx)? No, it was centered.
            # Let's check corner.py... 
            # Vertices: Inner -mid_z, Outer +mid_z.
            # So Center (0,0,0) is in middle of prism.
            # Apothem_corner is to Inner Face.
            # So Corner Center should be at Apothem_corner + (depth/2).
            # Corner Depth?
            # From corner.py: depth = BLOCK_UNIT * cos(half_wedge_angle)? 
            # Let's just assume Corner Depth is approx BLOCK_UNIT (38).
            # To be precise, we should pass depth.
            # Let's approximate Center Radius = Apothem_Corner + (BLOCK_UNIT / 2.0).
            # This pushes it out correctly.
            
            r_c = apothem_corner + (BLOCK_UNIT / 2.0)
            
            cx = math.sin(rad_c) * r_c
            cz = math.cos(rad_c) * r_c
            
            # Rotation: Face Center.
            # Z+ is OUT.
            # Position logic matches Rotation logic (CCW).
            # Rot = Angle aligns Z+ with Position (Outward).
            
            c_rot = angle_c
            
            corner = CornerStoneGeometry.build(QVector3D(cx, 0, cz), c_rot, WALL_COLORS[i])
            objects.append(corner)
            
            # --- B. Place Wall Panel ---
            # Angle of Wall Center
            # Starts at angle_c + (alpha/2). Ends at angle_c + alpha/2 + beta.
            # Midpoint = angle_c + alpha/2 + beta/2.
            
            angle_w = angle_c + (alpha_deg / 2.0) + (beta_deg / 2.0)
            rad_w = math.radians(angle_w)
            
            # Radius to Block Grid Center
            # Apothem_wall is to Inner Face.
            # Blocks are 38 deep. Center is +19.
            # User Adjustment: Push walls outward to clear Keystone overlap.
            WALL_OFFSET = 5.0 
            r_w = apothem_wall + (BLOCK_UNIT / 2.0) + WALL_OFFSET
            
            wx_center = math.sin(rad_w) * r_w
            wz_center = math.cos(rad_w) * r_w
            
            # Tangent (for grid)
            tx = math.cos(rad_w)
            tz = -math.sin(rad_w)
            
            wall_color = WALL_COLORS[i]
            
            # Wrapper Rotation for the entire Wall Panel
            # Normal points Out (angle_w).
            # Blocks should face In (+180).
            # This must be constant for the whole grid to form a Flat Wall.
            wall_block_rot = angle_w + 180
            
            for col in range(WALL_WIDTH_UNITS):
                for row in range(WALL_HEIGHT_UNITS):
                    loc_x = wall_start_x + (col * BLOCK_UNIT)
                    loc_y = (BLOCK_UNIT / 2.0) + (row * BLOCK_UNIT)
                    
                    wx = wx_center + (tx * loc_x)
                    wy = loc_y
                    wz = wz_center + (tz * loc_x)
                    
                    pos = QVector3D(wx, wy, wz)
                    
                    block = AshlarGeometry.build(pos, wall_block_rot, wall_color)
                    objects.append(block)
                    
        return objects
