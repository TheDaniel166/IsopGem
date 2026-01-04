"""
Amun Visualizer - The Sacred Geometry Mandala.
A real-time animated widget that renders concentric polygons based on Amun Sound parameters.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QPainterPath
import math
import logging

logger = logging.getLogger(__name__)

class AmunVisualizer(QWidget):
    """
    Real-time geometric visualizer for Amun Sound System.
    Advanced 'Sacred Geometry' Mandala.
    """
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.setStyleSheet("background-color: #000000; border-radius: 8px;")
        
        # State
        self.active = False
        self.active = False
        self.params = {}
        
        # Default State
        self.family_color = QColor("#2a2a2a")
        self.layers = 1
        self.sides = 3 # Triangle default
        self.attack = 0.5
        
        # Animation State
        self.base_rotation = 0.0
        self.star_rotation = 0.0
        self.pulse_phase = 0.0
        
        # Animation Loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) # ~60 FPS
        
    def update_parameters(self, params: dict):
        """Update visualization target parameters from Symphony data."""
        self.active = True
        self.params = params
        
        # Color (Soul)
        hex_color = params.get('color_hex', '#2a2a2a')
        self.family_color = QColor(hex_color)
        
        # Geometry (Body - Red Channel)
        # Map Red Key '00'-'22' to Sides 3-11
        # '00' -> 0, '22' -> 8. +3 = 3..11
        # Need to parse bigram key from params if available, or infer
        red_key = params.get('red_val', '00') 
        # Convert base-3 string to int? '00'=0, '01'=1... '22'=8
        try:
            val = int(red_key, 3)
        except (TypeError, ValueError) as e:
            logger.debug(
                "AmunVisualizer: invalid red_val %r (%s): %s",
                red_key,
                type(e).__name__,
                e,
            )
            val = 0
        self.sides = val + 3
        
        # Layers (Density - Blue Channel)
        self.layers = params.get('layers', 1)
        
        # Dynamics (Breath - Green Channel)
        self.attack = params.get('attack', 0.5)
        
    def stop(self):
        """
        Stop logic.
        
        """
        self.active = False
        self.update()

    def update_animation(self):
        """
        Update animation logic.
        
        """
        if not self.active:
            # Slow idle breath
            self.pulse_phase += 0.05
            self.base_rotation += 0.2
        else:
            # Rotation speed based on Attack (Breath)
            # Short attack = Fast spin
            speed = 2.0 * (1.1 - min(1.0, self.attack))
            self.base_rotation += speed
            self.star_rotation -= (speed * 1.5) # Counter-rotate faster
            
            # Pulse logic: 
            # Breathe based on attack/release rhythm
            # Use fixed rate for now to show life
            rate = 1.0 / (self.attack + 0.1)
            self.pulse_phase += (2 * math.pi * rate * 0.1)
            
        self.update()

    def paintEvent(self, event):  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType, reportUnknownParameterType]
        """
        Paintevent logic.
        
        Args:
            event: Description of event.
        
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        center = QPointF(w/2, h/2)
        radius_max = min(w, h) * 0.45
        
        # 1. Background Gradient (Soul / Family Color)
        # Use Family Color
        c = self.family_color
        grad = QRadialGradient(center, radius_max * 1.5)
        grad.setColorAt(0.0, c.lighter(150))   # Center glow
        grad.setColorAt(0.6, c)                # Mid
        grad.setColorAt(1.0, QColor("#000000")) # Black edge
        painter.fillRect(self.rect(), QBrush(grad))
        
        # 2. Variable Radius (Breath)
        pulse = (math.sin(self.pulse_phase) + 1.0) / 2.0
        base_scale = 0.6 + (pulse * 0.1) # Breathe +/- 10%
        
        painter.translate(center)
        
        # 3. Draw Concentric Rings (Layers / Density)
        # Each layer is a polygon with 'sides' (Red Channel)
        
        # Loop backwards so outer rings don't cover inner ones?
        # Actually draw outlines.
        
        layer_step = radius_max * base_scale / (self.layers + 1)
        
        for i in range(self.layers, 0, -1):
            r = i * layer_step
            
            # Alternating Rotation
            rot = self.base_rotation if i % 2 == 0 else -self.base_rotation
            rot += (i * 15) # Offset
            
            painter.save()
            painter.rotate(rot)
            
            # Opacity based on layer depth
            alpha = 255 - (i * 10)
            color = QColor(c)
            color.setAlpha(max(50, alpha))
            
            # Line width
            width = max(1, 4 - (i // 3))
            
            if self.sides < 3:
                # Circle/Void (fallback) -> Draw as Polygon with many sides or Ellipse
                self._draw_void_spheres(painter, color, r)
            else:
                self._draw_polygon(painter, self.sides, r, color, width)
                
            painter.restore()

    def _draw_void_spheres(self, painter, color, radius):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Draw concentric circles for the Void state."""
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawEllipse(QPointF(0,0), radius, radius)
        painter.drawEllipse(QPointF(0,0), radius*0.6, radius*0.6)
        painter.drawEllipse(QPointF(0,0), radius*0.3, radius*0.3)

    def _draw_polygon(self, painter, sides, radius, color, width):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        pen = QPen(color, width)
        painter.setPen(pen)
        
        points = []
        step = 2 * math.pi / sides
        for i in range(sides):
            angle = i * step
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            points.append(QPointF(x, y))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            
        painter.drawPolygon(points)

    def _draw_star(self, painter, sides, radius, color, width):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        pen = QPen(color, width)
        painter.setPen(pen)
        
        # Create star path by connecting every 2nd or 3rd vertex
        # Skip = floor((sides-1)/2)
        skip = int((sides - 1) / 2)
        if skip < 2: skip = 2 
        
        points = []
        step = 2 * math.pi / sides
        for i in range(sides):
            angle = i * step
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            points.append(QPointF(x, y))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            
        _path = QPainterPath()
        # Naive star drawing: connect i to (i+skip) % sides
        # Better: stroke multiple lines
        for i in range(sides):
            p1 = points[i]
            p2 = points[(i + skip) % sides]
            painter.drawLine(p1, p2)