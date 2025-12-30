"""Canvas for visualizing Chariot Axles and Geometry."""
from typing import Optional, List, Dict
import math

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPolygonF, QFont
)
from PyQt6.QtWidgets import QWidget

from shared.services.astro_glyph_service import astro_glyphs
from .chart_canvas import ChartCanvas
from ..models.chariot_models import ChariotReport, AxlePosition


class ChariotCanvas(ChartCanvas):
    """
    Specialized canvas for visualizing Chariot Geometry.
    Displays the 7 Axles as triangles connecting their midpoints.
    Allows highlighting a specific Axle.
    """
    
    def __init__(self, parent: Optional[QWidget] = None, report: Optional[ChariotReport] = None):
        super().__init__(parent)
        self._report: Optional[ChariotReport] = None
        self._highlighted_axle_id: Optional[str] = None
        self._highlighted_point_name: Optional[str] = None
        
        # Colors for Axles (Semantic Mapping?)
        # For now, we use a cycle or map them if they have specific colors.
        # We'll use a standard palette.
        self.axle_colors: Dict[str, QColor] = {}
        
        if report:
            self.set_chariot_data(report)
        
    def set_chariot_data(self, report: ChariotReport) -> None:
        """Set the chariot report data."""
        self._report = report
        self._assign_axle_colors()
        self.update()
        
    def set_highlighted_axle(self, axle_id: Optional[str]) -> None:
        """Set which Axle to highlight (brighten)."""
        self._highlighted_axle_id = axle_id
        self._highlighted_point_name = None # Clear point highlight when axle selected
        self.update()
        
    def set_highlighted_point(self, point_name: Optional[str]) -> None:
        """Set which specific point (Tarot Card) to highlight."""
        self._highlighted_point_name = point_name
        self.update()

    # ... (colors method remains the same) ...

    def _assign_axle_colors(self) -> None:
        """Assign colors to axles."""
        if not self._report:
            return
            
        palette = [
            QColor("#FF5555"), # Red
            QColor("#FFB86C"), # Orange
            QColor("#F1FA8C"), # Yellow
            QColor("#50FA7B"), # Green
            QColor("#8BE9FD"), # Cyan
            QColor("#BD93F9"), # Purple
            QColor("#FF79C6"), # Pink
        ]
        
        self.axle_colors = {}
        for i, axle in enumerate(self._report.axles):
            self.axle_colors[axle.id] = palette[i % len(palette)]

    def paintEvent(self, event) -> None:
        """Draw the Chariot geometry."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cx, cy = w / 2.0, h / 2.0
        
        radius = min(w, h) * 0.45
        inner_radius = radius * 0.75
        
        # 1. Background (The Void)
        self._draw_background(painter, cx, cy, w, h)
        
        def angle_for(deg: float) -> float:
            return math.radians(180.0 - deg)

        # 2. Zodiac Ring
        self._draw_zodiac_ring(painter, cx, cy, angle_for, radius, inner_radius)
        
        # 3. Axle Triangles
        if self._report:
            self._draw_axles(painter, cx, cy, angle_for, inner_radius)
            
            # 4. Axle Points (Calculated Centers)
            self._draw_axle_points(painter, cx, cy, angle_for, inner_radius)
            
            # 5. Chariot Point
            self._draw_chariot_point(painter, cx, cy, angle_for, inner_radius)
            
        painter.end()

    def _draw_axles(self, p: QPainter, cx: float, cy: float, angle_func, radius: float) -> None:
        """Draw triangles for each axle."""
        if not self._report:
            return
            
        # Draw non-highlighted first (dim)
        for axle in self._report.axles:
            if axle.id == self._highlighted_axle_id:
                continue
            self._draw_single_axle(p, cx, cy, angle_func, radius, axle, is_highlighted=False)
            
        # Draw highlighted on top (bright)
        if self._highlighted_axle_id:
            for axle in self._report.axles:
                if axle.id == self._highlighted_axle_id:
                    self._draw_single_axle(p, cx, cy, angle_func, radius, axle, is_highlighted=True)
                    break

    def _draw_axle_points(self, p: QPainter, cx: float, cy: float, angle_func, radius: float) -> None:
        """Draw calculated center points for each Axle."""
        if not self._report:
            return

        for axle in self._report.axles:
            # Calculate Circular Mean of the 3 midpoints
            sin_sum = 0.0
            cos_sum = 0.0
            count = 0
            
            for midpoint in axle.midpoints:
                # Convert zodiac degree to radians (standard math angle)
                # Note: angle_func converts degree to screen angle. 
                # We need true geometric angle for mean calculation.
                # Standard Astro: 0 Aries = 0 deg.
                rad = math.radians(midpoint.longitude)
                sin_sum += math.sin(rad)
                cos_sum += math.cos(rad)
                count += 1
                
            if count == 0:
                continue
                
            avg_sin = sin_sum / count
            avg_cos = cos_sum / count
            avg_rad = math.atan2(avg_sin, avg_cos)
            
            # Convert back to degrees for angle_func
            avg_deg = math.degrees(avg_rad)
            if avg_deg < 0:
                avg_deg += 360.0
                
            # Draw
            angle = angle_func(avg_deg)
            # Position: Inside the triangle, slightly closer to center than vertices
            px = cx + math.cos(angle) * (radius * 0.75)
            py = cy + math.sin(angle) * (radius * 0.75)
            pt = QPointF(px, py)
            
            is_highlighted = (self._highlighted_point_name == "Axle Point" and 
                              self._highlighted_axle_id == axle.id)
            
            if is_highlighted:
                # Bright Silver
                color = QColor("#E0E0E0") 
                glow_color = QColor("#FFFFFF")
                glow_color.setAlpha(150)
                
                # Glow
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(glow_color)
                p.drawEllipse(pt, 10.0, 10.0)
                
                # Core
                p.setBrush(color)
                p.drawEllipse(pt, 5.0, 5.0)
                
            else:
                # Dull Silver
                color = QColor("#808080")
                color.setAlpha(180)
                
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(color)
                p.drawEllipse(pt, 4.0, 4.0)

    def _draw_single_axle(self, p: QPainter, cx: float, cy: float, angle_func, radius: float, axle: AxlePosition, is_highlighted: bool) -> None:
        """Draw a single axle triangle."""
        color = self.axle_colors.get(axle.id, QColor("white"))
        
        if is_highlighted:
            alpha_fill = 60
            alpha_line = 255
            width = 2.0
        else:
            alpha_fill = 10
            alpha_line = 100
            width = 1.0
            
        # Triangle Polygon
        points = []
        point_data = [] # Store (point, name)
        
        for midpoint in axle.midpoints:
            angle = angle_func(midpoint.longitude)
            px = cx + math.cos(angle) * (radius * 0.85) 
            py = cy + math.sin(angle) * (radius * 0.85)
            pt = QPointF(px, py)
            points.append(pt)
            point_data.append((pt, midpoint.name))
            
        if len(points) == 3:
            polygon = QPolygonF(points)
            
            # Fill
            c_fill = QColor(color)
            c_fill.setAlpha(alpha_fill)
            p.setBrush(QBrush(c_fill))
            
            # Stroke
            c_line = QColor(color)
            c_line.setAlpha(alpha_line)
            pen = QPen(c_line)
            pen.setWidthF(width)
            p.setPen(pen)
            
            p.drawPolygon(polygon)
            
            # Draw Points
            for pt, name in point_data:
                # Basic point
                p.setBrush(c_line)
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(pt, 3.0, 3.0)
                
                # Selection Highlight (Reticle)
                if self._highlighted_point_name == name:
                    # Draw reticle
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    
                    # Outer glow ring
                    glow_color = QColor(color)
                    glow_color.setAlpha(150)
                    glow_pen = QPen(glow_color)
                    glow_pen.setWidthF(1.5)
                    p.setPen(glow_pen)
                    p.drawEllipse(pt, 12.0, 12.0)
                    
                    # Inner bright ring
                    bright_color = QColor(color)
                    bright_color.setAlpha(255)
                    bright_pen = QPen(bright_color)
                    bright_pen.setWidthF(2.0)
                    p.setPen(bright_pen)
                    p.drawEllipse(pt, 8.0, 8.0)

    def _draw_chariot_point(self, p: QPainter, cx: float, cy: float, angle_func, radius: float) -> None:
        """Draw the Chariot Point (Singular Important Point)."""
        cp = self._report.chariot_point
        angle = angle_func(cp.longitude)
        
        # Position
        px = cx + math.cos(angle) * (radius * 0.6) # Inside the triangles
        py = cy + math.sin(angle) * (radius * 0.6)
        
        # Style: Gold Star/Diamond
        c_gold = QColor("#FFD700")
        
        # Glow
        p.setPen(Qt.PenStyle.NoPen)
        c_glow = QColor(c_gold)
        c_glow.setAlpha(100)
        p.setBrush(c_glow)
        p.drawEllipse(QPointF(px, py), 15.0, 15.0)
        
        # Core
        p.setBrush(c_gold)
        p.drawEllipse(QPointF(px, py), 6.0, 6.0)
