
from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPainter, QBrush, QColor, QRadialGradient
from PyQt6.QtCore import QRectF, QPointF, Qt
import random

class GalaxyBackground(QGraphicsRectItem):
    def __init__(self, rect: QRectF, star_count: int = 200):
        super().__init__(rect)
        self.setZValue(-100)  # Keep it at the back
        self.rect_area = rect
        self.stars = []
        self._generate_stars(star_count)

    def _generate_stars(self, count):
        for _ in range(count):
            x = random.uniform(self.rect_area.left(), self.rect_area.right())
            y = random.uniform(self.rect_area.top(), self.rect_area.bottom())
            size = random.uniform(1.0, 3.0)
            brightness = random.randint(150, 255)
            self.stars.append((QPointF(x, y), size, brightness))

    def paint(self, painter: QPainter, option, widget):
        # Draw Deep Void
        painter.fillRect(self.rect_area, QColor("#050510"))
        
        # Draw Stars
        painter.setPen(Qt.PenStyle.NoPen)
        for (pos, size, brightness) in self.stars:
            color = QColor(255, 255, 255, brightness)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(pos, size, size)
