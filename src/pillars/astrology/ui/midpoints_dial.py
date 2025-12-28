"""Midpoints Dial widget - circular visualization of midpoint positions."""
from __future__ import annotations

import math
from typing import List, Optional, Dict

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from PyQt6.QtWidgets import QWidget, QToolTip


class MidpointsDial(QWidget):
    """Circular dial showing midpoint positions with planet-on-midpoint detection."""

    ZODIAC_SIGNS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

    def __init__(self, parent: Optional[QWidget] = None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setMouseTracking(True)
        
        self._midpoints: List[tuple[str, str, float]] = []  # (planet_a, planet_b, midpoint_deg)
        self._planet_positions: Dict[str, float] = {}  # For planet-on-midpoint detection
        self._hovered_midpoint: Optional[tuple[str, str, float]] = None
        self._midpoint_hitboxes: List[tuple[QRectF, str, str, float]] = []
        
        # Palette
        self.c_background_start = QColor("#1a1a2e")
        self.c_background_end = QColor("#0f0f13")
        self.c_gold = QColor("#D4AF37")
        self.c_silver = QColor("#E0E0E0")
        self.c_zodiac_ring = QColor(255, 255, 255, 25)
        self.c_midpoint = QColor("#88aaff")  # Light blue for midpoints
        self.c_planet_on_mp = QColor("#ff6600")  # Orange for planet on midpoint
        
        # Planet glyphs
        self.glyphs = {
            "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
            "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
            "Neptune": "♆", "Pluto": "♇",
        }

    def set_data(self, midpoints: List[tuple[str, str, float]], planet_positions: Dict[str, float]) -> None:
        """Set midpoint data and planet positions for planet-on-midpoint detection."""
        self._midpoints = midpoints
        self._planet_positions = planet_positions
        self.update()

    def mouseMoveEvent(self, event) -> None:
        """
        Mousemoveevent logic.
        
        Args:
            event: Description of event.
        
        Returns:
            Result of mouseMoveEvent operation.
        """
        pos = event.position()
        
        for rect, p_a, p_b, degree in self._midpoint_hitboxes:
            if rect.contains(pos):
                sign_idx = int(degree // 30) % 12
                sign_deg = degree % 30
                sign = self.ZODIAC_SIGNS[sign_idx]
                g_a = self.glyphs.get(p_a.title(), p_a[:2])
                g_b = self.glyphs.get(p_b.title(), p_b[:2])
                tooltip = f"{g_a}/{g_b}: {sign_deg:.1f}° {sign}"
                
                # Check if any planet is on this midpoint
                for pname, plon in self._planet_positions.items():
                    diff = abs(plon - degree)
                    if diff > 180:
                        diff = 360 - diff
                    if diff <= 2.0:  # 2° orb
                        tooltip += f"\n⚠ {pname} on midpoint!"
                
                QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
                self._hovered_midpoint = (p_a, p_b, degree)
                self.update()
                return
        
        self._hovered_midpoint = None
        QToolTip.hideText()
        self.update()

    def paintEvent(self, event) -> None:
        """
        Paintevent logic.
        
        Args:
            event: Description of event.
        
        Returns:
            Result of paintEvent operation.
        """
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self._midpoint_hitboxes = []
        
        w, h = self.width(), self.height()
        size = min(w, h) - 20
        cx, cy = w / 2, h / 2
        radius = size / 2
        
        # Background
        gradient = QRadialGradient(cx, cy, radius)
        gradient.setColorAt(0, self.c_background_start)
        gradient.setColorAt(1, self.c_background_end)
        p.setBrush(QBrush(gradient))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), radius, radius)
        
        # Zodiac ring
        r_outer = radius * 0.92
        r_inner = radius * 0.78
        r_sign = radius * 0.85
        
        p.setPen(QPen(self.c_zodiac_ring, 1))
        p.drawEllipse(QPointF(cx, cy), r_outer, r_outer)
        p.drawEllipse(QPointF(cx, cy), r_inner, r_inner)
        
        # Zodiac divisions and signs
        font_sign = QFont("Arial", 12)
        p.setFont(font_sign)
        
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = cx + math.cos(angle) * r_inner
            y1 = cy + math.sin(angle) * r_inner
            x2 = cx + math.cos(angle) * r_outer
            y2 = cy + math.sin(angle) * r_outer
            p.setPen(QPen(self.c_zodiac_ring, 1))
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            sign_angle = math.radians((i * 30) + 15 - 90)
            sx = cx + math.cos(sign_angle) * r_sign
            sy = cy + math.sin(sign_angle) * r_sign
            p.setPen(self.c_gold)
            p.drawText(QRectF(sx - 8, sy - 8, 16, 16), Qt.AlignmentFlag.AlignCenter, self.ZODIAC_SIGNS[i])
        
        # Draw midpoints
        r_mp = radius * 0.6
        font_small = QFont("Arial", 8)
        p.setFont(font_small)
        
        for p_a, p_b, degree in self._midpoints:
            angle = math.radians(-degree + 90)
            px = cx + math.cos(angle) * r_mp
            py = cy + math.sin(angle) * r_mp
            
            # Check if any planet is on this midpoint
            planet_on_mp = False
            for pname, plon in self._planet_positions.items():
                diff = abs(plon - degree)
                if diff > 180:
                    diff = 360 - diff
                if diff <= 2.0:
                    planet_on_mp = True
                    break
            
            # Choose color
            color = self.c_planet_on_mp if planet_on_mp else self.c_midpoint
            is_hovered = self._hovered_midpoint and self._hovered_midpoint[2] == degree
            marker_size = 8 if is_hovered else 5
            
            # Draw marker
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(QPointF(px, py), marker_size, marker_size)
            
            # Store hitbox
            hitbox = QRectF(px - 10, py - 10, 20, 20)
            self._midpoint_hitboxes.append((hitbox, p_a, p_b, degree))
        
        # Title
        p.setPen(self.c_gold)
        font = QFont("Arial", 14, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(QRectF(cx - 50, cy - 10, 100, 20), Qt.AlignmentFlag.AlignCenter, "Midpoints")
        
        p.end()