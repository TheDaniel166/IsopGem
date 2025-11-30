"""Viewport widget for rendering geometric shapes."""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from typing import Dict, List, Tuple, Optional
import math


class GeometryViewport(QWidget):
    """Widget that renders geometric shapes based on drawing instructions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.drawing_data: Optional[Dict] = None
        self.labels: List[Tuple[str, float, float]] = []
        self.show_labels = True
        self.show_grid = True
        self.show_axes = True
        
        # Styling
        self.setStyleSheet("background-color: white; border: 1px solid #e5e7eb;")
    
    def set_drawing_data(self, drawing_data: Dict, labels: List[Tuple[str, float, float]]):
        """
        Set the data to draw.
        
        Args:
            drawing_data: Dictionary with drawing instructions
            labels: List of (text, x, y) tuples for labels
        """
        self.drawing_data = drawing_data
        self.labels = labels
        self.update()  # Trigger repaint
    
    def clear(self):
        """Clear the viewport."""
        self.drawing_data = None
        self.labels = []
        self.update()
    
    def paintEvent(self, event):
        """Paint the geometric shape."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get viewport dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # Draw background grid
        if self.show_grid:
            self._draw_grid(painter, width, height)
        
        # Draw axes
        if self.show_axes:
            self._draw_axes(painter, width, height, center_x, center_y)
        
        # Draw shape if data exists
        if self.drawing_data and self.drawing_data.get('type') != 'empty':
            # Calculate scale to fit shape in viewport
            scale = self._calculate_scale(width, height)
            
            # Draw the shape
            painter.save()
            painter.translate(center_x, center_y)
            painter.scale(scale, -scale)  # Flip Y axis for math coordinates
            
            self._draw_shape(painter)
            
            painter.restore()
            
            # Draw labels
            if self.show_labels and self.labels:
                self._draw_labels(painter, center_x, center_y, scale)
    
    def _draw_grid(self, painter: QPainter, width: int, height: int):
        """Draw background grid."""
        painter.setPen(QPen(QColor(240, 240, 240), 1))
        
        # Vertical lines
        for x in range(0, width, 40):
            painter.drawLine(x, 0, x, height)
        
        # Horizontal lines
        for y in range(0, height, 40):
            painter.drawLine(0, y, width, y)
    
    def _draw_axes(self, painter: QPainter, width: int, height: int, cx: float, cy: float):
        """Draw X and Y axes."""
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        
        # X axis
        painter.drawLine(0, int(cy), width, int(cy))
        
        # Y axis
        painter.drawLine(int(cx), 0, int(cx), height)
    
    def _calculate_scale(self, width: int, height: int) -> float:
        """Calculate scale factor to fit shape in viewport."""
        if not self.drawing_data:
            return 1.0
        
        # Default scale
        base_scale = min(width, height) * 0.35
        
        shape_type = self.drawing_data.get('type')
        
        if shape_type == 'circle':
            radius = self.drawing_data.get('radius', 1)
            return base_scale / max(radius, 0.1)
        
        elif shape_type == 'polygon':
            points = self.drawing_data.get('points', [])
            if not points:
                return base_scale
            
            # Find bounding box
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            max_extent = max(max(xs) - min(xs), max(ys) - min(ys))
            
            return base_scale / max(max_extent, 0.1)
        
        return base_scale
    
    def _draw_shape(self, painter: QPainter):
        """Draw the geometric shape."""
        shape_type = self.drawing_data.get('type')
        
        # Shape pen and brush
        shape_pen = QPen(QColor(37, 99, 235), 3)  # Blue
        shape_brush = QBrush(QColor(219, 234, 254, 100))  # Light blue transparent
        
        painter.setPen(shape_pen)
        painter.setBrush(shape_brush)
        
        if shape_type == 'circle':
            self._draw_circle(painter)
        elif shape_type == 'polygon':
            self._draw_polygon(painter)
    
    def _draw_circle(self, painter: QPainter):
        """Draw a circle."""
        cx = self.drawing_data.get('center_x', 0)
        cy = self.drawing_data.get('center_y', 0)
        radius = self.drawing_data.get('radius', 1)
        
        # Draw circle
        painter.drawEllipse(QPointF(cx, cy), radius, radius)
        
        # Draw radius line
        if self.drawing_data.get('show_radius_line', False):
            painter.setPen(QPen(QColor(220, 38, 38), 2))  # Red
            painter.drawLine(QPointF(cx, cy), QPointF(cx + radius, cy))
        
        # Draw diameter line
        if self.drawing_data.get('show_diameter_line', False):
            painter.setPen(QPen(QColor(16, 185, 129), 2, Qt.PenStyle.DashLine))  # Green
            painter.drawLine(QPointF(cx - radius, cy), QPointF(cx + radius, cy))
        
        # Draw center point
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(QPointF(cx, cy), 0.05, 0.05)
    
    def _draw_polygon(self, painter: QPainter):
        """Draw a polygon."""
        points = self.drawing_data.get('points', [])
        if not points:
            return
        
        # Convert to QPointF
        qpoints = [QPointF(x, y) for x, y in points]
        
        # Draw polygon or star polygon
        if self.drawing_data.get('star', False) and len(qpoints) >= 3:
            # Draw star by connecting every second vertex (step=2) for hexagram
            painter.save()
            painter.setPen(QPen(QColor(37, 99, 235), 3))
            n = len(qpoints)
            # Draw two overlapped triangles for clarity
            # Triangle 1: vertices 0,2,4
            tri1 = [qpoints[i % n] for i in [0, 2, 4]]
            painter.drawPolygon(tri1)
            # Triangle 2: vertices 1,3,5
            tri2 = [qpoints[i % n] for i in [1, 3, 5]]
            painter.drawPolygon(tri2)
            painter.restore()
        else:
            painter.drawPolygon(qpoints)
        
        # Draw vertices
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(QBrush(QColor(37, 99, 235)))
        for pt in qpoints:
            painter.drawEllipse(pt, 0.1, 0.1)
        
        # Optional features
        if self.drawing_data.get('show_diagonals', False):
            self._draw_diagonals(painter, qpoints)
        
        if self.drawing_data.get('show_diagonal', False):
            self._draw_shortest_diagonal(painter, qpoints)
        
        if self.drawing_data.get('show_circumcircle', False):
            self._draw_circumcircle(painter, qpoints)
        
        if self.drawing_data.get('show_incircle', False):
            self._draw_incircle(painter, qpoints)
    
    def _draw_diagonals(self, painter: QPainter, points: List[QPointF]):
        """Draw diagonals of polygon."""
        painter.setPen(QPen(QColor(156, 163, 175), 1, Qt.PenStyle.DashLine))
        n = len(points)
        for i in range(n):
            for j in range(i + 2, n):
                if not (i == 0 and j == n - 1):  # Skip adjacent sides
                    painter.drawLine(points[i], points[j])
    
    def _draw_shortest_diagonal(self, painter: QPainter, points: List[QPointF]):
        """Draw all shortest diagonals (skipping one vertex) of a regular polygon."""
        if len(points) < 4:
            return  # No diagonals for triangles
        
        # Draw all instances of the shortest diagonal (connecting vertices separated by one vertex)
        painter.setPen(QPen(QColor(220, 38, 38), 2, Qt.PenStyle.DashLine))  # Red dashed
        n = len(points)
        for i in range(n):
            # Connect vertex i to vertex i+2 (skipping one vertex)
            next_vertex = (i + 2) % n
            painter.drawLine(points[i], points[next_vertex])
    
    def _draw_circumcircle(self, painter: QPainter, points: List[QPointF]):
        """Draw circumscribed circle."""
        # Calculate center (centroid for regular polygon)
        cx = sum(p.x() for p in points) / len(points)
        cy = sum(p.y() for p in points) / len(points)
        
        # Radius is distance to first vertex
        radius = math.sqrt((points[0].x() - cx)**2 + (points[0].y() - cy)**2)
        
        painter.setPen(QPen(QColor(124, 58, 237), 2, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)
    
    def _draw_incircle(self, painter: QPainter, points: List[QPointF]):
        """Draw inscribed circle (simplified for regular polygons)."""
        # This is simplified - works well for regular polygons
        cx = sum(p.x() for p in points) / len(points)
        cy = sum(p.y() for p in points) / len(points)
        
        # For regular polygon, inradius is distance to midpoint of side
        if len(points) >= 3:
            mid_x = (points[0].x() + points[1].x()) / 2
            mid_y = (points[0].y() + points[1].y()) / 2
            inradius = math.sqrt((mid_x - cx)**2 + (mid_y - cy)**2)
            
            painter.setPen(QPen(QColor(16, 185, 129), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), inradius, inradius)
    
    def _draw_labels(self, painter: QPainter, cx: float, cy: float, scale: float):
        """Draw labels on the shape."""
        painter.setPen(QPen(QColor(0, 0, 0)))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        for text, x, y in self.labels:
            # Convert shape coordinates to screen coordinates
            screen_x = cx + (x * scale)
            screen_y = cy - (y * scale)  # Flip Y
            
            # Draw text
            painter.drawText(int(screen_x), int(screen_y), text)
