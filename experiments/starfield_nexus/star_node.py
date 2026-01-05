
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsDropShadowEffect
from PyQt6.QtCore import QRectF, Qt, QPointF
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor, QPainterPath

class StarNode(QGraphicsItem):
    def __init__(self, label: str, x: float, y: float, size: float = 100):
        super().__init__()
        self.label = label
        self.size = size
        self.setPos(x, y)
        
        # Enable hover events
        self.setAcceptHoverEvents(True)
        
        # Visual properties
        self.base_color = QColor("#ffaa00")  # Amber
        self.glow_color = QColor("#ffaa00")
        self.pen_width = 2
        
        # State
        self.hovered = False
        
        # Hierarchy
        self.children = []
        self.parent_node = None
        self.is_moon = False


    def boundingRect(self) -> QRectF:
        s = self.size
        return QRectF(-s/2, -s/2, s, s)

    def paint(self, painter: QPainter, option, widget):
        # Setup painter
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create Heptagon Path (7-sided)
        path = QPainterPath()
        s = self.size / 2
        import math
        
        # 7 points
        points = []
        angle_step = (2 * math.pi) / 7
        # Start at top (-90 degrees or -pi/2)
        start_angle = -math.pi / 2
        
        for i in range(7):
            angle = start_angle + (i * angle_step)
            px = s * math.cos(angle)
            py = s * math.sin(angle)
            points.append(QPointF(px, py))
        
        path.moveTo(points[0])
        for p in points[1:]:
            path.lineTo(p)
        path.closeSubpath()
        
        # Draw Glow/Fill
        if self.hovered:
            painter.setPen(QPen(self.base_color, self.pen_width + 2))
            painter.setBrush(QBrush(QColor(self.base_color.red(), self.base_color.green(), self.base_color.blue(), 50)))
        else:
            painter.setPen(QPen(self.base_color, self.pen_width))
            painter.setBrush(QBrush(QColor(0, 0, 0, 200))) # Dark background
            
        painter.drawPath(path)
        
        # Draw Label
        painter.setPen(QPen(self.base_color))
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, self.label)

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)
