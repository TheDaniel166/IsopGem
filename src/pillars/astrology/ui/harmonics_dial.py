"""Harmonics Dial widget - circular visualization of harmonic positions."""
from __future__ import annotations

import math
from typing import List, Optional

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient
from PyQt6.QtWidgets import QWidget, QToolTip


class HarmonicsDial(QWidget):
    """Circular dial showing harmonic planet positions with interactivity."""

    # Zodiac sign glyphs
    ZODIAC_SIGNS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

    def __init__(self, parent: Optional[QWidget] = None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setMouseTracking(True)  # Enable hover detection
        
        self._harmonic_positions: List[tuple[str, float]] = []
        self._harmonic_number = 1
        self._hovered_planet: Optional[tuple[str, float]] = None
        self._planet_hitboxes: List[tuple[QRectF, str, float]] = []
        
        # Celestia palette
        self.c_background_start = QColor("#1a1a2e")
        self.c_background_end = QColor("#0f0f13")
        self.c_gold = QColor("#D4AF37")
        self.c_silver = QColor("#E0E0E0")
        self.c_zodiac_ring = QColor(255, 255, 255, 25)
        self.c_degree_marks = QColor(255, 255, 255, 50)
        
        # Planet colors
        self.planet_colors = {
            "Sun": QColor("#FFD700"),
            "Moon": QColor("#C0C0C0"),
            "Mercury": QColor("#87CEEB"),
            "Venus": QColor("#FFB6C1"),
            "Mars": QColor("#FF6347"),
            "Jupiter": QColor("#FFA500"),
            "Saturn": QColor("#8B4513"),
            "Uranus": QColor("#40E0D0"),
            "Neptune": QColor("#4169E1"),
            "Pluto": QColor("#9370DB"),
        }
        
        # Planet glyphs
        self.glyphs = {
            "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
            "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
            "Neptune": "♆", "Pluto": "♇",
        }

    def set_data(self, positions: List[tuple[str, float]], harmonic: int) -> None:
        """Set harmonic positions. positions = [(name, harmonic_degree), ...]"""
        self._harmonic_positions = positions
        self._harmonic_number = harmonic
        self.update()

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for tooltips."""
        pos = event.position()
        
        for rect, name, degree in self._planet_hitboxes:
            if rect.contains(pos):
                # Format degree as zodiacal position
                sign_idx = int(degree // 30) % 12
                sign_deg = degree % 30
                sign = self.ZODIAC_SIGNS[sign_idx]
                tooltip = f"{name}: {sign_deg:.1f}° {sign}"
                QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
                self._hovered_planet = (name, degree)
                self.update()
                return
        
        self._hovered_planet = None
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
        
        # Clear hitboxes
        self._planet_hitboxes = []
        
        # Get dimensions
        w, h = self.width(), self.height()
        size = min(w, h) - 20
        cx, cy = w / 2, h / 2
        radius = size / 2
        
        # Draw background gradient
        gradient = QRadialGradient(cx, cy, radius)
        gradient.setColorAt(0, self.c_background_start)
        gradient.setColorAt(1, self.c_background_end)
        p.setBrush(QBrush(gradient))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), radius, radius)
        
        # Draw zodiac ring
        r_outer = radius * 0.92
        r_inner = radius * 0.78
        r_sign = radius * 0.85  # Position for sign glyphs
        
        p.setPen(QPen(self.c_zodiac_ring, 1))
        p.drawEllipse(QPointF(cx, cy), r_outer, r_outer)
        p.drawEllipse(QPointF(cx, cy), r_inner, r_inner)
        
        # Draw zodiac divisions and signs
        font_sign = QFont("Arial", 12)
        p.setFont(font_sign)
        
        for i in range(12):
            # Division line at start of each sign
            angle = math.radians(i * 30 - 90)
            x1 = cx + math.cos(angle) * r_inner
            y1 = cy + math.sin(angle) * r_inner
            x2 = cx + math.cos(angle) * r_outer
            y2 = cy + math.sin(angle) * r_outer
            p.setPen(QPen(self.c_zodiac_ring, 1))
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Sign glyph in middle of each sign
            sign_angle = math.radians((i * 30) + 15 - 90)
            sx = cx + math.cos(sign_angle) * r_sign
            sy = cy + math.sin(sign_angle) * r_sign
            p.setPen(self.c_gold)
            p.drawText(QRectF(sx - 8, sy - 8, 16, 16), Qt.AlignmentFlag.AlignCenter, self.ZODIAC_SIGNS[i])
        
        # Draw degree marks (every 10°)
        r_tick_outer = r_inner
        r_tick_inner = r_inner - 5
        p.setPen(QPen(self.c_degree_marks, 1))
        font_deg = QFont("Arial", 7)
        p.setFont(font_deg)
        
        for deg in range(0, 360, 10):
            angle = math.radians(deg - 90)
            x1 = cx + math.cos(angle) * r_tick_inner
            y1 = cy + math.sin(angle) * r_tick_inner
            x2 = cx + math.cos(angle) * r_tick_outer
            y2 = cy + math.sin(angle) * r_tick_outer
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Draw degree label at 0° of each sign
            if deg % 30 == 0:
                lx = cx + math.cos(angle) * (r_tick_inner - 10)
                ly = cy + math.sin(angle) * (r_tick_inner - 10)
                p.drawText(QRectF(lx - 10, ly - 6, 20, 12), Qt.AlignmentFlag.AlignCenter, f"{deg}°")
        
        # Draw harmonic number in center
        p.setPen(self.c_gold)
        font = QFont("Arial", 28, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(QRectF(cx - 35, cy - 18, 70, 36), Qt.AlignmentFlag.AlignCenter, f"H{self._harmonic_number}")
        
        # Draw planets
        r_planet = radius * 0.55
        font_small = QFont("Arial", 12)
        p.setFont(font_small)
        
        for name, degree in self._harmonic_positions:
            angle = math.radians(-degree + 90)
            
            px = cx + math.cos(angle) * r_planet
            py = cy + math.sin(angle) * r_planet
            
            # Get color and glyph
            color = self.planet_colors.get(name.title(), self.c_silver)
            glyph = self.glyphs.get(name.title(), name[:2])
            
            # Highlight if hovered
            marker_size = 14 if self._hovered_planet and self._hovered_planet[0] == name else 12
            
            # Draw marker
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(QPointF(px, py), marker_size, marker_size)
            
            # Draw glyph
            p.setPen(QColor("#0f0f13"))
            p.drawText(QRectF(px - 10, py - 8, 20, 16), Qt.AlignmentFlag.AlignCenter, glyph)
            
            # Store hitbox for interactivity
            hitbox = QRectF(px - 15, py - 15, 30, 30)
            self._planet_hitboxes.append((hitbox, name, degree))
        
        # Draw aspect lines from hovered planet
        if self._hovered_planet:
            self._draw_aspects(p, cx, cy, r_planet)
        
        p.end()

    def _draw_aspects(self, p: QPainter, cx: float, cy: float, r_planet: float) -> None:
        """Draw aspect lines from the hovered planet to others."""
        if not self._hovered_planet:
            return
        
        hovered_name, hovered_deg = self._hovered_planet
        
        # Aspect definitions: (angle, orb, color)
        aspects = [
            (0, 8, QColor("#ffee00")),     # Conjunction - Yellow
            (60, 4, QColor("#74ee15")),    # Sextile - Lime
            (90, 6, QColor("#f000ff")),    # Square - Magenta
            (120, 8, QColor("#4deeea")),   # Trine - Cyan
            (180, 8, QColor("#ff2a6d")),   # Opposition - Red
        ]
        
        # Calculate hovered planet position
        h_angle = math.radians(-hovered_deg + 90)
        hx = cx + math.cos(h_angle) * r_planet
        hy = cy + math.sin(h_angle) * r_planet
        
        for name, degree in self._harmonic_positions:
            if name == hovered_name:
                continue
            
            # Calculate angular difference
            diff = abs(degree - hovered_deg)
            if diff > 180:
                diff = 360 - diff
            
            # Check for aspects
            for aspect_angle, orb, color in aspects:
                if abs(diff - aspect_angle) <= orb:
                    # Calculate target position
                    t_angle = math.radians(-degree + 90)
                    tx = cx + math.cos(t_angle) * r_planet
                    ty = cy + math.sin(t_angle) * r_planet
                    
                    # Draw aspect line
                    pen = QPen(color)
                    pen.setWidthF(2.0)
                    p.setPen(pen)
                    p.drawLine(QPointF(hx, hy), QPointF(tx, ty))
                    break