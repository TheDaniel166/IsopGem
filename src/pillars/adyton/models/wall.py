"""
THE WALL OF THE ADYTON (Solid Panel with Recessed Frustums)

A single wall entity with a solid body and 104 recessed frustums (8 high x 13 wide).
"""
from typing import Callable, List, Optional
from PyQt6.QtGui import QVector3D, QColor
from pillars.adyton.models.geometry_types import Object3D, Face3D
from pillars.adyton.constants import (
    BLOCK_UNIT,
    WALL_WIDTH_UNITS,
    WALL_HEIGHT_UNITS,
    FRUSTUM_BASE,
    FRUSTUM_TOP,
    FRUSTUM_HEIGHT,
    FRUSTUM_FACE_TOP,
    FRUSTUM_FACE_RIGHT,
    FRUSTUM_FACE_BOTTOM,
    FRUSTUM_FACE_LEFT,
)

class WallGeometry:
    """Constructs a solid wall with inset frustums on the interior face."""

    @staticmethod
    def build(
        color: QColor,
        wall_index: int = 0,
        center_color_fn: Optional[Callable[[int, int, int], QColor]] = None,
        side_color_fn: Optional[Callable[[int, int, int, int], QColor]] = None,
    ) -> Object3D:
        faces: List[Face3D] = []

        wall_width = WALL_WIDTH_UNITS * BLOCK_UNIT
        wall_height = WALL_HEIGHT_UNITS * BLOCK_UNIT
        half_w = wall_width / 2.0
        half_h = wall_height / 2.0
        half_d = BLOCK_UNIT / 2.0  # depth matches a single block

        # Colors
        frame_color = color.lighter(108)
        inner_color = color
        outer_color = color.darker(105)

        # Helper to add a quad with CCW order for +Z normal
        def quad(v1, v2, v3, v4, col):
            faces.append(Face3D([v1, v2, v3, v4], col))

        # --- Outer shell faces ---
        # Back (outer) face, normal +Z
        quad(
            QVector3D(-half_w, 0, half_d),
            QVector3D(half_w, 0, half_d),
            QVector3D(half_w, wall_height, half_d),
            QVector3D(-half_w, wall_height, half_d),
            outer_color,
        )
        # Top (+Y)
        quad(
            QVector3D(-half_w, wall_height, -half_d),
            QVector3D(half_w, wall_height, -half_d),
            QVector3D(half_w, wall_height, half_d),
            QVector3D(-half_w, wall_height, half_d),
            outer_color,
        )
        # Bottom (0)
        quad(
            QVector3D(-half_w, 0, -half_d),
            QVector3D(-half_w, 0, half_d),
            QVector3D(half_w, 0, half_d),
            QVector3D(half_w, 0, -half_d),
            outer_color,
        )
        # Left (-X)
        quad(
            QVector3D(-half_w, 0, -half_d),
            QVector3D(-half_w, wall_height, -half_d),
            QVector3D(-half_w, wall_height, half_d),
            QVector3D(-half_w, 0, half_d),
            outer_color,
        )
        # Right (+X)
        quad(
            QVector3D(half_w, 0, half_d),
            QVector3D(half_w, wall_height, half_d),
            QVector3D(half_w, wall_height, -half_d),
            QVector3D(half_w, 0, -half_d),
            outer_color,
        )

        # --- Interior frustum grid ---
        cell_w = BLOCK_UNIT
        cell_h = BLOCK_UNIT
        half_base = FRUSTUM_BASE / 2.0
        half_top = FRUSTUM_TOP / 2.0
        z_face = -half_d
        z_top = z_face - FRUSTUM_HEIGHT

        frame_color_bottom = frame_color
        frame_color_side = frame_color
        frustum_side_color = inner_color.darker(112)
        frustum_top_color_default = inner_color.lighter(120)

        for row in range(WALL_HEIGHT_UNITS):
            for col in range(WALL_WIDTH_UNITS):
                cx = -half_w + (cell_w / 2.0) + (col * cell_w)
                cy = (cell_h / 2.0) + (row * cell_h)

                x0 = cx - (cell_w / 2.0)
                x1 = cx + (cell_w / 2.0)
                y0 = cy - (cell_h / 2.0)
                y1 = cy + (cell_h / 2.0)

                xb0 = cx - half_base
                xb1 = cx + half_base
                yb0 = cy - half_base
                yb1 = cy + half_base

                xt0 = cx - half_top
                xt1 = cx + half_top
                yt0 = cy - half_top
                yt1 = cy + half_top

                # Frame quads on inner face (normals toward -Z)
                # Order vertices so normal points -Z
                quad(QVector3D(x0, y0, z_face), QVector3D(x1, y0, z_face), QVector3D(xb1, yb0, z_face), QVector3D(xb0, yb0, z_face), frame_color_bottom)  # bottom frame
                quad(QVector3D(xb1, yb0, z_face), QVector3D(x1, y0, z_face), QVector3D(x1, y1, z_face), QVector3D(xb1, yb1, z_face), frame_color_side)  # right frame
                quad(QVector3D(xb0, yb1, z_face), QVector3D(xb1, yb1, z_face), QVector3D(x1, y1, z_face), QVector3D(x0, y1, z_face), frame_color_bottom)  # top frame
                quad(QVector3D(x0, y0, z_face), QVector3D(xb0, yb0, z_face), QVector3D(xb0, yb1, z_face), QVector3D(x0, y1, z_face), frame_color_side)   # left frame

                # Frustum sides (connect base to cap)
                bottom_col = side_color_fn(wall_index, row, col, FRUSTUM_FACE_BOTTOM) if side_color_fn else frustum_side_color
                right_col = side_color_fn(wall_index, row, col, FRUSTUM_FACE_RIGHT) if side_color_fn else frustum_side_color
                top_col = side_color_fn(wall_index, row, col, FRUSTUM_FACE_TOP) if side_color_fn else frustum_side_color
                left_col = side_color_fn(wall_index, row, col, FRUSTUM_FACE_LEFT) if side_color_fn else frustum_side_color

                quad(QVector3D(xb0, yb0, z_face), QVector3D(xb1, yb0, z_face), QVector3D(xt1, yt0, z_top), QVector3D(xt0, yt0, z_top), bottom_col)  # bottom
                quad(QVector3D(xb1, yb0, z_face), QVector3D(xb1, yb1, z_face), QVector3D(xt1, yt1, z_top), QVector3D(xt1, yt0, z_top), right_col)  # right
                quad(QVector3D(xb0, yb1, z_face), QVector3D(xt0, yt1, z_top), QVector3D(xt1, yt1, z_top), QVector3D(xb1, yb1, z_face), top_col)  # top
                quad(QVector3D(xb0, yb0, z_face), QVector3D(xt0, yt0, z_top), QVector3D(xt0, yt1, z_top), QVector3D(xb0, yb1, z_face), left_col)  # left

                # Frustum cap (center face)
                cap_color = frustum_top_color_default
                if center_color_fn:
                    cap_color = center_color_fn(wall_index, row, col)
                quad(QVector3D(xt0, yt0, z_top), QVector3D(xt1, yt0, z_top), QVector3D(xt1, yt1, z_top), QVector3D(xt0, yt1, z_top), cap_color)

        wall_obj = Object3D(faces=faces)
        wall_obj.wall_index = wall_index
        return wall_obj
