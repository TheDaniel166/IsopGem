"""
THE VAULT OF THE ADYTON (Prism Geometry)

"Seven walls, rising to the height of thirteen."
"""
import math
from typing import List, Tuple
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
        from .corner import CornerStoneGeometry
        from .wall import WallGeometry
        from .floor import FloorGeometry
        from pillars.adyton.services.frustum_color_service import FrustumColorService
        from ..constants import (
            WALL_COLORS, COLOR_ARGON, BLOCK_UNIT, 
            WALL_WIDTH_UNITS, WALL_HEIGHT_UNITS,
            Z_BIT_INCHES, WALL_HEIGHT_INCHES
        )
        
        objects = []
        
        # --- 1. Irregular 14-Gon Math (exact) ---
        # The perimeter consists of 7 segments of [Corner, Wall].
        c = Z_BIT_INCHES
        w = WALL_WIDTH_UNITS * BLOCK_UNIT

        alpha_rad, beta_rad, V = SevenSidedPrism._solve_corner_wall_angles(c, w)

        deg_per_sector = 360.0 / 7.0 # 51.42857
        rotation_offset_deg = 0.0  # restore original alignment

        # Calculate Apothems (Distance to Inner Faces)
        apothem_corner = V * math.cos(alpha_rad / 2.0)
        apothem_wall   = V * math.cos(beta_rad / 2.0)
        
        # --- Floor ---
        # The floor now uses internal constants for 185/166 side lengths
        floor_obj = FloorGeometry.build()
        objects.append(floor_obj)

        # --- 2. Construction Loop ---
        current_angle_deg = 0.0
        frustum_color_service = FrustumColorService()

        for i in range(7):
            # --- A. Place Corner Stone ---
            # Angle of Corner Center
            angle_c = (i * deg_per_sector) + rotation_offset_deg
            rad_c = math.radians(angle_c)
            
            # Center radius to place corner volume: apothem to inner face + half depth
            # Corner wedge depth along its normal is BLOCK_UNIT * cos(half-wedge-angle)
            half_wedge_rad = math.radians((180.0 - (180.0 * 5.0 / 7.0)) / 2.0)
            corner_depth_along_normal = BLOCK_UNIT * math.cos(half_wedge_rad)
            r_c = apothem_corner + (corner_depth_along_normal / 2.0)
            
            cx = math.sin(rad_c) * r_c
            cz = math.cos(rad_c) * r_c
            
            # Rotate so each corner bisects its sector
            c_rot = angle_c
            
            corner = CornerStoneGeometry.build(QVector3D(cx, 0, cz), c_rot, COLOR_ARGON)
            objects.append(corner)
            
            # --- B. Place Wall Panel ---
            # Angle of Wall Center (middle of its chord sector)
            angle_w = angle_c + math.degrees(alpha_rad) / 2.0 + math.degrees(beta_rad) / 2.0
            rad_w = math.radians(angle_w)
            
            # Radius to Block Grid Center: apothem to inner face + half depth (no extra offset)
            r_w = apothem_wall + (BLOCK_UNIT / 2.0)
            
            wx_center = math.sin(rad_w) * r_w
            wz_center = math.cos(rad_w) * r_w

            wall_color = WALL_COLORS[i]

            # Create a single wall mesh and position/rotate it
            wall_obj = WallGeometry.build(
                wall_color,
                wall_index=i,
                center_color_fn=frustum_color_service.get_center_color,
                side_color_fn=frustum_color_service.get_side_color,
            )
            wall_obj.position = QVector3D(wx_center, 0, wz_center)
            wall_obj.rotation = QVector3D(0, angle_w, 0)
            objects.append(wall_obj)
                    
        return objects

    @staticmethod
    def build_wall(wall_index: int) -> List[Object3D]:
        """Constructs a single wall placed in its canonical position (no floor)."""
        from .wall import WallGeometry
        from pillars.adyton.services.frustum_color_service import FrustumColorService
        from ..constants import (
            WALL_COLORS,
            BLOCK_UNIT,
            WALL_WIDTH_UNITS,
            Z_BIT_INCHES,
        )

        c = Z_BIT_INCHES
        w = WALL_WIDTH_UNITS * BLOCK_UNIT

        alpha_rad, beta_rad, V = SevenSidedPrism._solve_corner_wall_angles(c, w)

        deg_per_sector = 360.0 / 7.0
        rotation_offset_deg = 0.0

        apothem_wall = V * math.cos(beta_rad / 2.0)

        angle_c = (wall_index * deg_per_sector) + rotation_offset_deg
        angle_w = angle_c + math.degrees(alpha_rad) / 2.0 + math.degrees(beta_rad) / 2.0
        rad_w = math.radians(angle_w)
        r_w = apothem_wall + (BLOCK_UNIT / 2.0)

        wx_center = math.sin(rad_w) * r_w
        wz_center = math.cos(rad_w) * r_w

        wall_color = WALL_COLORS[wall_index % 7]
        frustum_color_service = FrustumColorService()

        wall_obj = WallGeometry.build(
            wall_color,
            wall_index=wall_index,
            center_color_fn=frustum_color_service.get_center_color,
            side_color_fn=frustum_color_service.get_side_color,
        )
        wall_obj.position = QVector3D(wx_center, 0, wz_center)
        wall_obj.rotation = QVector3D(0, angle_w, 0)

        return [wall_obj]

    @staticmethod
    def _solve_corner_wall_angles(c: float, w: float) -> Tuple[float, float, float]:
        """Solve alpha (corner) and beta (wall) exactly from chord constraints.

        Given corner chord c, wall chord w, shared vertex radius V:
          c = 2 V sin(alpha/2)
          w = 2 V sin(beta/2)
          7*(alpha + beta) = 360 degrees
        Returns (alpha_rad, beta_rad, V).
        """
        sector_rad = math.radians(360.0 / 7.0)

        def f(alpha: float) -> float:
            """
            F logic.
            
            Args:
                alpha: Description of alpha.
            
            Returns:
                Result of f operation.
            """
            beta = sector_rad - alpha
            return (c / math.sin(alpha / 2.0)) - (w / math.sin(beta / 2.0))

        lo = 1e-6
        hi = sector_rad - 1e-6
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if f(lo) * f(mid) <= 0:
                hi = mid
            else:
                lo = mid
        alpha = 0.5 * (lo + hi)
        beta = sector_rad - alpha

        V = c / (2.0 * math.sin(alpha / 2.0))
        return alpha, beta, V