"""
THE FOUNDATION OF THE ADYTON (Floor Geometry)

A concentric heptagonal floor: outer MAAT blue field and an inner vowel ring.
"""
import math
from typing import List, Optional

from PyQt6.QtGui import QVector3D, QColor

from pillars.adyton.models.geometry_types import Face3D, Object3D
from pillars.adyton.constants import COLOR_MAAT_BLUE, VOWEL_RING_COLORS


class FloorGeometry:
    @staticmethod
    def build(
        apothem_outer: float,
        inset: float = 8.0,
        ring_colors: Optional[List[QColor]] = None,
    ) -> Object3D:
        """Build a two-layer floor with a vowel ring.

        apothem_outer: distance from center to the inner face of the walls.
        inset: margin to pull the floor inside the walls to avoid z-fighting.
        """
        # Slightly inset from wall interior to avoid overlap
        outer_apothem = max(1.0, apothem_outer - inset)
        ring_inner_apothem = outer_apothem * 0.9  # ~ratio of 166/185
        core_apothem = ring_inner_apothem * 0.7

        base_y = 0.0
        ring_y = base_y + 0.02
        core_y = ring_y + 0.02

        outer_pts = FloorGeometry._heptagon_points(outer_apothem, base_y)
        ring_pts = FloorGeometry._heptagon_points(ring_inner_apothem, ring_y)
        core_pts = FloorGeometry._heptagon_points(core_apothem, core_y)

        ring_palette = ring_colors or VOWEL_RING_COLORS

        faces: List[Face3D] = []

        # Outer heptagon field
        faces.append(Face3D(vertices=outer_pts, color=COLOR_MAAT_BLUE))

        segment_centers: List[QVector3D] = []

        # Vowel ring segments (7 quads between outer and ring heptagons)
        for i in range(7):
            o0 = outer_pts[i]
            o1 = outer_pts[(i + 1) % 7]
            r1 = ring_pts[(i + 1) % 7]
            r0 = ring_pts[i]
            cx = (o0.x() + o1.x() + r1.x() + r0.x()) / 4.0
            cy = (o0.y() + o1.y() + r1.y() + r0.y()) / 4.0
            cz = (o0.z() + o1.z() + r1.z() + r0.z()) / 4.0
            segment_centers.append(QVector3D(cx, cy + 0.02, cz))
            faces.append(
                Face3D(
                    vertices=[o0, o1, r1, r0],
                    color=ring_palette[i % len(ring_palette)],
                )
            )

        # Core heptagon (slightly lighter)
        faces.append(Face3D(vertices=core_pts, color=COLOR_MAAT_BLUE))

        obj = Object3D(faces=faces)
        # Attach label helper metadata
        obj.label_positions = segment_centers  # type: ignore[attr-defined]
        obj.label_colors = ring_palette        # type: ignore[attr-defined]
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
