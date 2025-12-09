from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QPainterPath
import math

class AmunVisualizer(QWidget):
    """
    Real-time geometric visualizer for Amun Sound System.
    Advanced 'Sacred Geometry' Mandala.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.setStyleSheet("background-color: #000000; border-radius: 8px;")
        
        # State
        self.active = False
        self.freq = 0.0
        self.amp = 0.5
        self.mod_rate = 0.0
        self.bigram = 0
        
        # Animation State
        self.base_rotation = 0.0
        self.star_rotation = 0.0
        self.pulse_phase = 0.0
        
        # Animation Loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) # ~60 FPS
        
    def update_parameters(self, freq: float, amp: float, bigram_val: int, mod_rate: float = 0.0):
        """Update visualization target parameters."""
        self.active = True
        self.freq = freq
        self.amp = max(0.2, min(1.0, amp))
        self.bigram = bigram_val
        self.mod_rate = mod_rate
        
    def stop(self):
        self.active = False
        self.update()

    def update_animation(self):
        if not self.active:
            # Slow idle breath
            self.pulse_phase += 0.05
            self.base_rotation += 0.2
        else:
            # Rotation speed based on Freq
            # Higher freq = faster spin
            speed = min(5.0, self.freq / 80.0)
            self.base_rotation += speed
            self.star_rotation -= (speed * 1.5) # Counter-rotate faster
            
            # Pulse logic: 
            # If mod_rate > 0, pulse at that HZ rate.
            # Else pulse slowly
            rate = self.mod_rate if self.mod_rate > 0 else 0.5
            # Convert Hz to Phase Increment (assuming 60fps)
            # Phase = 2*pi * rate * t
            # Phase step = (2*pi * rate) / 60
            self.pulse_phase += (2 * math.pi * rate) / 60.0
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        center = QPointF(w/2, h/2)
        radius_max = min(w, h) * 0.45
        
        # 1. Background Gradient (Octave Atmosphere)
        # Hue based on Freq (Logarithmic mapping ideally, but linear for now)
        hue = int((self.freq / 1000.0) * 360) % 360
        grad = QRadialGradient(center, radius_max * 1.5)
        grad.setColorAt(0.0, QColor.fromHsv(hue, 100, 40, 255))   # Center glow
        grad.setColorAt(0.8, QColor.fromHsv(hue, 150, 20, 100))  # Mid fade
        grad.setColorAt(1.0, QColor.fromHsv(hue, 0, 0, 255))     # Black edge
        painter.fillRect(self.rect(), QBrush(grad))
        
        # 2. Pulse Calculation
        # Pulse affects Scale
        pulse_val = (math.sin(self.pulse_phase) + 1.0) / 2.0 # 0.0 to 1.0
        # Intensity of pulse depends on Amp
        current_scale = self.amp * (0.8 + (pulse_val * 0.2)) 
        
        current_radius = radius_max * current_scale
        
        painter.translate(center)
        
        # 3. Draw Geometry
        sides = self.bigram + 3 # Map Bigram 0->Triangle (3), 1->Square (4)...
        if self.bigram == 0: sides = 0 # Bigram 0 = Circle
        
        # Color Palettes
        base_color = QColor.fromHsv(hue, 200, 255, 200)
        star_color = QColor.fromHsv((hue + 180) % 360, 255, 255, 180) # Compl
        
        if sides == 0:
            # Draw Spheres (Bigram 0 / Void)
            self._draw_void_spheres(painter, base_color, current_radius)
        else:
            # Layer 1: Base Polygon (Rotating CW)
            painter.save()
            painter.rotate(self.base_rotation)
            self._draw_polygon(painter, sides, current_radius, base_color, 3)
            painter.restore()
            
            # Layer 2: Star / Stellation (Rotating CCW)
            # Only stellate if sides >= 5
            if sides >= 5:
                painter.save()
                painter.rotate(self.star_rotation)
                self._draw_star(painter, sides, current_radius * 0.7, star_color, 2)
                painter.restore()
            else:
                # For Triangle/Square, draw inner inverted polygon
                painter.save()
                painter.rotate(self.star_rotation)
                self._draw_polygon(painter, sides, current_radius * 0.5, star_color, 2)
                painter.restore()

    def _draw_void_spheres(self, painter, color, radius):
        """Draw concentric circles for the Void state."""
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawEllipse(QPointF(0,0), radius, radius)
        painter.drawEllipse(QPointF(0,0), radius*0.6, radius*0.6)
        painter.drawEllipse(QPointF(0,0), radius*0.3, radius*0.3)

    def _draw_polygon(self, painter, sides, radius, color, width):
        pen = QPen(color, width)
        painter.setPen(pen)
        
        points = []
        step = 2 * math.pi / sides
        for i in range(sides):
            angle = i * step
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            points.append(QPointF(x, y))
            
        painter.drawPolygon(points)

    def _draw_star(self, painter, sides, radius, color, width):
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
            points.append(QPointF(x, y))
            
        path = QPainterPath()
        # Naive star drawing: connect i to (i+skip) % sides
        # Better: stroke multiple lines
        for i in range(sides):
            p1 = points[i]
            p2 = points[(i + skip) % sides]
            painter.drawLine(p1, p2)
