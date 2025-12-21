"""
Zodiacal Circle Widget - Interactive circular visualization.

Displays a 360-degree zodiacal circle with clickable degrees.
Clicking reveals the Conrune pair for that position.
Features Astronomicon font for zodiac signs and Prime Ditrune Gates.
"""
from __future__ import annotations

import math
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QRadialGradient,
    QFontDatabase
)
from PyQt6.QtWidgets import QWidget, QToolTip

from ..services.thelemic_calendar_service import ThelemicCalendarService
from ..models.thelemic_calendar_models import (
    ConrunePair, ZODIAC_SIGNS, ASTRONOMICON_CHARS
)


class ZodiacalCircleWidget(QWidget):
    """
    Interactive Zodiacal Circle displaying 360 degrees + 4 Prime Ditrune Gates.
    
    Clicking on a degree emits the degree_clicked signal with the selected
    Conrune pair data.
    """
    
    # Emitted when a degree is clicked: (ConrunePair or None)
    degree_clicked = pyqtSignal(object)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(450, 450)
        self.setMouseTracking(True)
        
        # Data
        self._service = ThelemicCalendarService()
        self._service.load_calendar()
        self._all_pairs = self._service.get_all_pairs()
        
        # Interaction state
        self._hovered_degree: Optional[int] = None
        self._selected_degree: Optional[int] = None
        self._degree_hitboxes: List[Tuple[QRectF, int]] = []  # (rect, difference)
        
        # Colors - Celestia palette
        self.c_background_start = QColor("#1a1a2e")
        self.c_background_end = QColor("#0f0f13")
        self.c_gold = QColor("#D4AF37")
        self.c_silver = QColor("#E0E0E0")
        self.c_zodiac_ring = QColor(255, 255, 255, 40)
        self.c_degree_marks = QColor(255, 255, 255, 60)
        self.c_selected = QColor("#4deeea")
        self.c_prime_gate = QColor("#ff2a6d")  # Red for Prime Ditrune Gates
        self.c_current_day = QColor("#74ee15")  # Green for today
        
        # All divisors of 360 with colors (excluding 1 and 360)
        self.DIVISORS_360 = {
            2: ("#ff2a6d", "Opposition", 180),      # Red
            3: ("#4deeea", "Trine", 120),           # Cyan
            4: ("#f000ff", "Square", 90),           # Magenta
            5: ("#ff8c00", "Quintile", 72),         # Orange
            6: ("#74ee15", "Sextile", 60),          # Green
            8: ("#ffa07a", "Semi-square", 45),      # Light Salmon
            9: ("#9370db", "Novile", 40),           # Purple
            10: ("#20b2aa", "Decile", 36),          # Teal
            12: ("#ffee00", "Semi-sextile", 30),    # Yellow
            15: ("#87ceeb", "24°", 24),             # Sky Blue
            18: ("#dda0dd", "20°", 20),             # Plum
            20: ("#98fb98", "18°", 18),             # Pale Green
            24: ("#f0e68c", "15°", 15),             # Khaki
            30: ("#e6e6fa", "12°", 12),             # Lavender
            36: ("#ffdab9", "10°", 10),             # Peach
            40: ("#afeeee", "9°", 9),               # Pale Turquoise
            45: ("#ffe4b5", "8°", 8),               # Moccasin
            60: ("#b0c4de", "6°", 6),               # Light Steel Blue
            72: ("#d8bfd8", "5°", 5),               # Thistle
            90: ("#faebd7", "4°", 4),               # Antique White
            120: ("#e0ffff", "3°", 3),              # Light Cyan
            180: ("#fff0f5", "2°", 2),              # Lavender Blush
        }
        
        # Active divisors (which aspect lines to show)
        self._active_divisors: List[int] = []
        
        # Reversal pair option
        self._show_reversal = False
        self.c_reversal = QColor("#FF69B4")  # Hot Pink for reversal line
        
        # Center perspective mode
        self._center_perspective = False
        self.c_gold = QColor("#D4AF37")  # Gold for selected point line
        self.c_silver = QColor("#C0C0C0")  # Silver for divisor lines
        
        # Load Astronomicon font
        self._astro_font_family = self._load_astronomicon_font()
        
        # Get today's pair for highlighting
        self._today_difference = self._get_today_difference()
    
    def _load_astronomicon_font(self) -> str:
        """Return the Astronomicon font family name if available."""
        # Fonts are now loaded globally by src/shared/ui/font_loader.py
        # We just need to check if it's available
        families = QFontDatabase.families()
        
        # Check for Astronomicon (or typical variations)
        target = "Astronomicon"
        for family in families:
            if target.lower() in family.lower():
                return family
                
        # Fallback to default font
        return "Arial"
    
    def _get_today_difference(self) -> Optional[int]:
        """Get the difference value for today's date."""
        today = datetime.now()
        # Format: "21-Mar", "1-Apr", etc.
        date_str = today.strftime("%-d-%b")
        pair = self._service.get_pair_by_date(date_str)
        return pair.difference if pair else None
    
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse movement for hover effects."""
        pos = event.position()
        
        for rect, diff in self._degree_hitboxes:
            if rect.contains(pos):
                self._hovered_degree = diff
                
                # Show tooltip with pair info
                pair = self._service.get_pair_by_difference(diff)
                if pair:
                    if pair.is_prime_ditrune:
                        tooltip = f"⚡ Prime Ditrune Gate\n{pair.gregorian_date}\nDitrune: {pair.ditrune} | Contrune: {pair.contrune}"
                    else:
                        # Convert letter to sign info
                        sign_letter = pair.sign_letter
                        sign_info = ZODIAC_SIGNS.get(sign_letter, ("Unknown", 0)) if sign_letter else ("Unknown", 0)
                        sign_name = sign_info[0]
                        # Unicode zodiac symbols
                        unicode_symbols = {
                            'A': '♈', 'B': '♉', 'C': '♊', 'D': '♋',
                            'E': '♌', 'F': '♍', 'G': '♎', 'H': '♏',
                            'I': '♐', 'J': '♑', 'K': '♒', 'L': '♓'
                        }
                        symbol = unicode_symbols.get(sign_letter, "") if sign_letter else ""
                        day = pair.sign_day if pair.sign_day is not None else 0
                        zodiac_display = f"{day}° {symbol} {sign_name}"
                        tooltip = f"{zodiac_display} ({pair.gregorian_date})\nDitrune: {pair.ditrune} | Contrune: {pair.contrune}"
                    QToolTip.showText(event.globalPosition().toPoint(), tooltip, self)
                
                self.update()
                return
        
        self._hovered_degree = None
        QToolTip.hideText()
        self.update()
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse click to select a degree."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        
        pos = event.position()
        
        for rect, diff in self._degree_hitboxes:
            if rect.contains(pos):
                self._selected_degree = diff
                pair = self._service.get_pair_by_difference(diff)
                self.degree_clicked.emit(pair)
                self.update()
                return
    
    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Clear hitboxes for rebuild
        self._degree_hitboxes = []
        
        # Get dimensions
        w, h = self.width(), self.height()
        size = min(w, h) - 40
        cx, cy = w / 2, h / 2
        radius = size / 2
        
        # Draw background gradient
        gradient = QRadialGradient(cx, cy, radius)
        gradient.setColorAt(0, self.c_background_start)
        gradient.setColorAt(1, self.c_background_end)
        p.setBrush(QBrush(gradient))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), radius, radius)
        
        # Draw rings
        r_outer = radius * 0.95
        r_zodiac_inner = radius * 0.82
        r_degree_inner = radius * 0.70
        r_center = radius * 0.25
        
        # Outer ring
        p.setPen(QPen(self.c_zodiac_ring, 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r_outer, r_outer)
        p.drawEllipse(QPointF(cx, cy), r_zodiac_inner, r_zodiac_inner)
        p.drawEllipse(QPointF(cx, cy), r_degree_inner, r_degree_inner)
        
        # Draw zodiac signs with Astronomicon font
        self._draw_zodiac_signs(p, cx, cy, r_outer, r_zodiac_inner)
        
        # Draw degree ticks and hitboxes
        self._draw_degree_marks(p, cx, cy, r_zodiac_inner, r_degree_inner)
        
        # Draw Prime Ditrune Gates
        self._draw_prime_gates(p, cx, cy, r_outer)
        
        # Draw divisor relationship lines (if any divisors active and point selected)
        if self._selected_degree and self._active_divisors:
            if self._center_perspective:
                self._draw_center_perspective_lines(p, cx, cy, r_degree_inner * 0.95)
            else:
                self._draw_relationship_lines(p, cx, cy, r_degree_inner * 0.95)
        
        # Draw reversal pair line if enabled
        if self._selected_degree and self._show_reversal:
            self._draw_reversal_line(p, cx, cy, r_degree_inner * 0.95)
        
        # Draw center info
        self._draw_center(p, cx, cy, r_center)
        
        p.end()
    
    def _draw_zodiac_signs(self, p: QPainter, cx: float, cy: float,
                           r_outer: float, r_inner: float) -> None:
        """Draw the 12 zodiac signs."""
        r_sign = (r_outer + r_inner) / 2
        
        # Use Astronomicon font
        astro_font = QFont(self._astro_font_family, 18)
        p.setFont(astro_font)
        
        for letter, (name, idx) in ZODIAC_SIGNS.items():
            # Each sign spans 30 degrees, center at 15 degrees offset
            angle_deg = idx * 30 + 15
            angle_rad = math.radians(-angle_deg + 90)  # Aries at top
            
            sx = cx + math.cos(angle_rad) * r_sign
            sy = cy + math.sin(angle_rad) * r_sign
            
            # Get Astronomicon character
            char = ASTRONOMICON_CHARS.get(letter, letter)
            
            p.setPen(self.c_gold)
            p.drawText(QRectF(sx - 12, sy - 12, 24, 24),
                       Qt.AlignmentFlag.AlignCenter, char)
            
            # Draw division line at sign boundary
            boundary_angle = math.radians(-idx * 30 + 90)
            x1 = cx + math.cos(boundary_angle) * r_inner
            y1 = cy + math.sin(boundary_angle) * r_inner
            x2 = cx + math.cos(boundary_angle) * r_outer
            y2 = cy + math.sin(boundary_angle) * r_outer
            p.setPen(QPen(self.c_zodiac_ring, 1))
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    
    def _draw_degree_marks(self, p: QPainter, cx: float, cy: float,
                           r_outer: float, r_inner: float) -> None:
        """Draw 360 degree marks with clickable hitboxes."""
        r_tick_outer = r_outer - 2
        r_tick_inner = r_inner + 2
        r_hitbox = (r_tick_outer + r_tick_inner) / 2
        
        p.setPen(QPen(self.c_degree_marks, 1))
        
        for deg in range(360):
            angle_rad = math.radians(-deg + 90)
            
            # Find corresponding difference value
            # Map degree to difference: degrees are based on zodiacal position
            diff = self._degree_to_difference(deg)
            
            # Determine tick length
            if deg % 30 == 0:
                # Sign boundary - longest tick
                tick_len = r_tick_outer - r_tick_inner
            elif deg % 10 == 0:
                # 10-degree mark
                tick_len = (r_tick_outer - r_tick_inner) * 0.6
            else:
                # Regular degree
                tick_len = (r_tick_outer - r_tick_inner) * 0.3
            
            r_start = r_tick_outer
            r_end = r_tick_outer - tick_len
            
            x1 = cx + math.cos(angle_rad) * r_start
            y1 = cy + math.sin(angle_rad) * r_start
            x2 = cx + math.cos(angle_rad) * r_end
            y2 = cy + math.sin(angle_rad) * r_end
            
            # Color based on state
            if diff == self._selected_degree:
                p.setPen(QPen(self.c_selected, 2))
            elif diff == self._hovered_degree:
                p.setPen(QPen(self.c_gold, 2))
            elif diff == self._today_difference:
                p.setPen(QPen(self.c_current_day, 2))
            else:
                p.setPen(QPen(self.c_degree_marks, 1))
            
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Create hitbox
            hx = cx + math.cos(angle_rad) * r_hitbox
            hy = cy + math.sin(angle_rad) * r_hitbox
            hitbox = QRectF(hx - 8, hy - 8, 16, 16)
            
            if diff is not None:
                self._degree_hitboxes.append((hitbox, diff))
    
    def _draw_prime_gates(self, p: QPainter, cx: float, cy: float,
                          r_outer: float) -> None:
        """Draw the 4 Prime Ditrune Gates at cardinal points."""
        # The 4 gates at solstices/equinoxes
        gates = [
            (91, 90, "☀️"),    # Summer Solstice
            (182, 180, "🍂"),  # Autumn Equinox
            (273, 270, "❄️"),  # Winter Solstice
            (364, 0, "🌱"),    # Spring Equinox
        ]
        
        r_gate = r_outer + 15
        
        for diff, angle_deg, symbol in gates:
            angle_rad = math.radians(-angle_deg + 90)
            
            gx = cx + math.cos(angle_rad) * r_gate
            gy = cy + math.sin(angle_rad) * r_gate
            
            # Draw gate marker
            if diff == self._selected_degree:
                p.setBrush(QBrush(self.c_selected))
            elif diff == self._hovered_degree:
                p.setBrush(QBrush(self.c_gold))
            else:
                p.setBrush(QBrush(self.c_prime_gate))
            
            p.setPen(QPen(self.c_gold, 2))
            
            # Diamond shape for gates
            diamond_size = 12
            diamond = [
                QPointF(gx, gy - diamond_size),
                QPointF(gx + diamond_size, gy),
                QPointF(gx, gy + diamond_size),
                QPointF(gx - diamond_size, gy),
            ]
            p.drawPolygon(diamond)
            
            # Add hitbox for gate
            hitbox = QRectF(gx - 15, gy - 15, 30, 30)
            self._degree_hitboxes.append((hitbox, diff))
    
    def _draw_center(self, p: QPainter, cx: float, cy: float,
                     r_center: float) -> None:
        """Draw center area with title."""
        # Central circle
        gradient = QRadialGradient(cx, cy, r_center)
        gradient.setColorAt(0, QColor("#2a2a4e"))
        gradient.setColorAt(1, self.c_background_end)
        p.setBrush(QBrush(gradient))
        p.setPen(QPen(self.c_gold, 2))
        p.drawEllipse(QPointF(cx, cy), r_center, r_center)
        
        # Title
        p.setPen(self.c_gold)
        font = QFont("Arial", 12, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(QRectF(cx - 50, cy - 20, 100, 20),
                   Qt.AlignmentFlag.AlignCenter, "Zodiacal")
        p.drawText(QRectF(cx - 50, cy, 100, 20),
                   Qt.AlignmentFlag.AlignCenter, "Circle")
    
    def _degree_to_difference(self, degree: int) -> Optional[int]:
        """Map a zodiacal degree (0-359) to a Difference value (1-364)."""
        # Each sign has 30 degrees, each degree maps to ~1 day
        # Sign 0 (Aries) starts at degree 0
        sign_idx = degree // 30
        day_in_sign = degree % 30
        
        # Find the pair with this zodiacal position
        sign_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        target_sign = sign_letters[sign_idx]
        
        for pair in self._all_pairs:
            if pair.sign_letter == target_sign and pair.sign_day == day_in_sign:
                return pair.difference
        
        return None
    
    def set_selected_difference(self, diff: int) -> None:
        """Programmatically select a difference value."""
        self._selected_degree = diff
        self.update()
    
    def set_active_divisors(self, divisors: List[int]) -> None:
        """Set which divisors to show relationship lines for."""
        self._active_divisors = [d for d in divisors if d in self.DIVISORS_360]
        self.update()
    
    def get_divisors(self) -> dict:
        """Return all available divisors with their info."""
        return self.DIVISORS_360.copy()
    
    def _difference_to_degree(self, diff: int) -> Optional[float]:
        """Convert a Difference value to zodiacal degrees (0-360)."""
        pair = self._service.get_pair_by_difference(diff)
        if pair is None:
            return None
        
        if pair.is_prime_ditrune:
            # Prime Ditrunes at cardinal points
            if diff == 91:
                return 90.0
            elif diff == 182:
                return 180.0
            elif diff == 273:
                return 270.0
            elif diff == 364:
                return 0.0
        
        # Regular days: map sign + day to degrees
        sign_letter = pair.sign_letter
        if sign_letter and sign_letter in ZODIAC_SIGNS:
            _, sign_idx = ZODIAC_SIGNS[sign_letter]
            day_in_sign = pair.sign_day or 0
            return (sign_idx * 30 + day_in_sign) % 360
        
        return None
    
    def _draw_relationship_lines(self, p: QPainter, cx: float, cy: float,
                                  r_line: float) -> None:
        """Draw lines from selected point to related points based on active divisors."""
        if not self._selected_degree:
            return
        
        # Get the degree of the selected point
        selected_deg = self._difference_to_degree(self._selected_degree)
        if selected_deg is None:
            return
        
        # Calculate selected point position
        selected_rad = math.radians(-selected_deg + 90)
        sel_x = cx + math.cos(selected_rad) * r_line
        sel_y = cy + math.sin(selected_rad) * r_line
        
        # Draw lines for each active divisor
        for divisor in self._active_divisors:
            if divisor not in self.DIVISORS_360:
                continue
            
            color_hex, name, angle = self.DIVISORS_360[divisor]
            color = QColor(color_hex)
            pen = QPen(color, 2)
            pen.setStyle(Qt.PenStyle.SolidLine)
            p.setPen(pen)
            
            # Draw lines to all related points
            num_points = divisor
            for i in range(1, num_points):
                # Calculate related degree
                related_deg = (selected_deg + i * angle) % 360
                related_rad = math.radians(-related_deg + 90)
                
                rel_x = cx + math.cos(related_rad) * r_line
                rel_y = cy + math.sin(related_rad) * r_line
                
                # Draw line from selected to related
                p.drawLine(QPointF(sel_x, sel_y), QPointF(rel_x, rel_y))
                
                # Draw small marker at related point
                p.setBrush(QBrush(color))
                p.drawEllipse(QPointF(rel_x, rel_y), 5, 5)
                p.setBrush(Qt.BrushStyle.NoBrush)
    
    def set_show_reversal(self, show: bool) -> None:
        """Toggle showing the reversal pair line."""
        self._show_reversal = show
        self.update()
    
    def _draw_reversal_line(self, p: QPainter, cx: float, cy: float,
                            r_line: float) -> None:
        """Draw line from selected point to its reversal pair."""
        if not self._selected_degree:
            return
        
        # Get selected pair
        selected_pair = self._service.get_pair_by_difference(self._selected_degree)
        if selected_pair is None:
            return
        
        # Get reversal pair
        reversal_pair = self._service.get_reversal_pair(selected_pair)
        if reversal_pair is None:
            return
        
        # Get degrees for both
        selected_deg = self._difference_to_degree(self._selected_degree)
        reversal_deg = self._difference_to_degree(reversal_pair.difference)
        
        if selected_deg is None or reversal_deg is None:
            return
        
        # Calculate positions
        selected_rad = math.radians(-selected_deg + 90)
        reversal_rad = math.radians(-reversal_deg + 90)
        
        sel_x = cx + math.cos(selected_rad) * r_line
        sel_y = cy + math.sin(selected_rad) * r_line
        rev_x = cx + math.cos(reversal_rad) * r_line
        rev_y = cy + math.sin(reversal_rad) * r_line
        
        # Draw the reversal line (dashed, hot pink)
        pen = QPen(self.c_reversal, 3)
        pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        p.drawLine(QPointF(sel_x, sel_y), QPointF(rev_x, rev_y))
        
        # Draw marker at reversal point
        p.setPen(QPen(self.c_reversal, 2))
        p.setBrush(QBrush(self.c_reversal))
        p.drawEllipse(QPointF(rev_x, rev_y), 4, 4)
        p.setBrush(Qt.BrushStyle.NoBrush)
    
    def set_center_perspective(self, enabled: bool) -> None:
        """Toggle center perspective mode."""
        self._center_perspective = enabled
        self.update()
    
    def _draw_center_perspective_lines(self, p: QPainter, cx: float, cy: float,
                                        r_line: float) -> None:
        """Draw lines from center: gold to selected point, silver to divisor points."""
        if not self._selected_degree:
            return
        
        # Get the degree of the selected point
        selected_deg = self._difference_to_degree(self._selected_degree)
        if selected_deg is None:
            return
        
        # Calculate selected point position
        selected_rad = math.radians(-selected_deg + 90)
        sel_x = cx + math.cos(selected_rad) * r_line
        sel_y = cy + math.sin(selected_rad) * r_line
        
        # Draw GOLD line from center to selected point
        gold_pen = QPen(self.c_gold, 3)
        p.setPen(gold_pen)
        p.drawLine(QPointF(cx, cy), QPointF(sel_x, sel_y))
        
        # Draw gold marker at selected point
        p.setBrush(QBrush(self.c_gold))
        p.drawEllipse(QPointF(sel_x, sel_y), 8, 8)
        p.setBrush(Qt.BrushStyle.NoBrush)           
        
        # Draw SILVER lines from center to all divisor-related points
        silver_pen = QPen(self.c_silver, 2)
        p.setPen(silver_pen)
        
        divisors = self.DIVISORS_360
        for divisor in self._active_divisors:
            if divisor not in divisors:
                continue
            
            _, _, angle = divisors[divisor]
            
            for i in range(1, divisor):
                related_deg = (selected_deg + i * angle) % 360
                related_rad = math.radians(-related_deg + 90)
                
                rel_x = cx + math.cos(related_rad) * r_line
                rel_y = cy + math.sin(related_rad) * r_line
                
                # Silver line from center
                p.drawLine(QPointF(cx, cy), QPointF(rel_x, rel_y))
                
                # Silver marker at point
                p.setBrush(QBrush(self.c_silver))
                p.drawEllipse(QPointF(rel_x, rel_y), 5, 5)
                p.setBrush(Qt.BrushStyle.NoBrush)

