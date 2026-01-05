
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui import QPainterPath, QPen, QColor, QPainter
from PyQt6.QtCore import QPointF, Qt
import math

class DataStream(QGraphicsPathItem):
    """A stream of pure light connecting two nodes."""
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.phase = 0.0
        
        # Connection Path
        self._update_path()
        
        # Visuals
        self.base_color = QColor("#ffaa00")
        
    def _update_path(self):
        path = QPainterPath()
        p1 = self.start_node.pos()
        p2 = self.end_node.pos()
        
        # Handle curve? For now straight line
        path.moveTo(p1)
        path.lineTo(p2)
        self.setPath(path)

    def advance(self, phase):
        self.phase = phase
        self.update()

    def paint(self, painter: QPainter, option, widget):
        path = self.path()
        
        # Draw Base Line
        painter.setPen(QPen(QColor(255, 170, 0, 50), 2))
        painter.drawPath(path)
        
        # Draw Pulse
        # Calculate position along line based on phase
        # Linear interpolation
        p1 = self.start_node.pos()
        p2 = self.end_node.pos()
        
        # A simple pulse moving from p1 to p2
        # Phase 0.0 to 1.0
        t = self.phase
        x = p1.x() + (p2.x() - p1.x()) * t
        y = p1.y() + (p2.y() - p1.y()) * t
        
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(x, y), 3, 3)
