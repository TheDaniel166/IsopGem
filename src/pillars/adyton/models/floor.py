"""
THE FOUNDATION OF THE ADYTON (Floor Geometry)

A concentric heptagonal floor: outer MAAT blue field and an inner vowel ring.
"""
import math
from typing import List, Optional

from PyQt6.QtGui import QVector3D, QColor

from pillars.adyton.models.geometry_types import Face3D, Object3D
from pillars.adyton.constants import (
    COLOR_MAAT_BLUE, 
    VOWEL_RING_COLORS,
    PERIMETER_SIDE_LENGTH,
    KATALYSIS_SIDE_LENGTH,
    COLOR_SILVER
)


class FloorGeometry:
    @staticmethod
    def build(
        ring_colors: Optional[List[QColor]] = None,
    ) -> Object3D:
        """Build the ceremonial floor with the precise 185/166 unit heptagons.
        """
        # Apothems derived from side lengths
        # a = s / (2 * tan(pi/n))
        tan_pi_7 = math.tan(math.pi / 7.0)
        
        outer_apothem = PERIMETER_SIDE_LENGTH / (2.0 * tan_pi_7)
        ring_inner_apothem = KATALYSIS_SIDE_LENGTH / (2.0 * tan_pi_7)

        # BEVEL ARCHITECTURE: Outer is at 0, Inner floor is sunken
        BEVEL_DEPTH = 10.0
        outer_y = 0.0
        sunken_y = -BEVEL_DEPTH

        outer_pts = FloorGeometry._heptagon_points(outer_apothem, outer_y)
        ring_pts = FloorGeometry._heptagon_points(ring_inner_apothem, sunken_y)

        ring_palette = ring_colors or VOWEL_RING_COLORS

        faces: List[Face3D] = []
        SLAB_BOTTOM_Y = -30.0 # Depth of the Maat Stone
        
        # 1. OUTER LEDGE & SIDE WALLS (Y=0 foundation)
        # Create the top surface and the vertical extrusion of the perimeter
        for i in range(7):
            o0 = outer_pts[i]
            o1 = outer_pts[(i + 1) % 7]
            # Create Y=0 inner points explicitly
            p_i1 = ring_pts[(i + 1) % 7]
            p_i0 = ring_pts[i]
            i1 = QVector3D(p_i1.x(), 0, p_i1.z())
            i0 = QVector3D(p_i0.x(), 0, p_i0.z())
            
            # Top Surface (Ledge)
            faces.append(Face3D(vertices=[o0, o1, i1, i0], color=QColor(40, 40, 50), outline_color=COLOR_SILVER))
            
            # EXTERNAL SIDE WALLS (Extrusion to create solidity)
            # From Y=0 to Y=SLAB_BOTTOM_Y
            sw0 = QVector3D(o0.x(), SLAB_BOTTOM_Y, o0.z())
            sw1 = QVector3D(o1.x(), SLAB_BOTTOM_Y, o1.z())
            faces.append(Face3D(vertices=[o1, o0, sw0, sw1], color=QColor(20, 20, 25), outline_color=COLOR_SILVER))

        # 2. VOWEL RING (Slanted descend)
        segment_centers: List[QVector3D] = []
        for i in range(7):
            p_cur = ring_pts[i]
            p_nxt = ring_pts[(i + 1) % 7]
            
            o_in_top = QVector3D(p_cur.x(), 0, p_cur.z())
            o_in_nxt = QVector3D(p_nxt.x(), 0, p_nxt.z())
            r_nxt_bot = p_nxt # already at sunken_y (-10)
            r_cur_bot = p_cur # already at sunken_y (-10)
            
            # Label center (on the slant)
            mid = (o_in_top + o_in_nxt + r_nxt_bot + r_cur_bot) * 0.25
            segment_centers.append(mid)
            
            faces.append(Face3D(
                vertices=[o_in_top, o_in_nxt, r_nxt_bot, r_cur_bot],
                color=ring_palette[i % len(ring_palette)],
                outline_color=COLOR_SILVER,
                shading=False
            ))

        # 3. SUNKEN SANCTUARY FLOOR (Top & Bottom)
        faces.append(Face3D(vertices=ring_pts, color=COLOR_MAAT_BLUE, outline_color=COLOR_SILVER))
        
        # 4. THE ABSOLUTE BASE (Closing the manifold)
        # A single heptagon at SLAB_BOTTOM_Y to ensure zero transparency from below.
        base_pts = [QVector3D(v.x(), SLAB_BOTTOM_Y, v.z()) for v in reversed(outer_pts)]
        faces.append(Face3D(vertices=base_pts, color=QColor(10, 10, 15), outline_color=COLOR_SILVER))

        obj = Object3D(faces=faces)
        # Attach label helper metadata
        obj.label_positions = segment_centers  # type: ignore[attr-defined]
        obj.label_colors = ring_palette        # type: ignore[attr-defined]
        obj.label_planets = [                  # type: ignore[attr-defined]
            "sun", "mercury", "moon", "venus", "jupiter", "mars", "saturn"
        ]
        return obj

    @staticmethod
    def _heptagon_points(apothem: float, y: float) -> List[QVector3D]:
        """Generate CCW heptagon vertices at height y given apothem length."""
        radius = apothem / math.cos(math.pi / 7.0)
        pts: List[QVector3D] = []
        # Start at +Z axis
        for i in range(7):
            theta = math.pi / 2.0 + i * (2.0 * math.pi / 7.0)
            x = radius * math.cos(theta)
            z = radius * math.sin(theta)
            pts.append(QVector3D(x, y, z))
        return pts
