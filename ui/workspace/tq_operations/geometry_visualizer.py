from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QPainter, QBrush
import math

class GeometryVisualizerDialog(QDialog):
    def __init__(self, number_type, n_points, position, parent=None):
        """
        number_type: 'star' or 'centered_polygon'
        n_points: number of points in the shape
        position: position in the sequence
        """
        super().__init__(parent)
        
        # Validate inputs
        if n_points < 3:
            raise ValueError("Number of points must be at least 3")
        if position < 1:
            raise ValueError("Position must be positive")
            
        self.number_type = number_type
        self.n_points = n_points
        self.position = position
        
        # Set window flags to stay on top
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        self.init_ui()

    def init_ui(self):
        try:
            self.setWindowTitle(f"{self.n_points}-pointed {self.number_type.replace('_', ' ')} - Position {self.position}")
            self.setMinimumSize(400, 400)
            
            layout = QVBoxLayout(self)
            
            # Create graphics view and scene
            self.scene = QGraphicsScene()
            self.view = QGraphicsView(self.scene)
            self.view.setRenderHint(QPainter.Antialiasing)
            self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
            self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            layout.addWidget(self.view)
            
            # Draw the shape
            if self.number_type == 'star':
                self.draw_star()
            else:
                self.draw_centered_polygon()
                
        except Exception as e:
            print(f"Error initializing geometry visualizer: {str(e)}")

    def draw_star(self):
        # Calculate radius based on position
        radius = 150  # Base radius for visualization
        center = QPointF(0, 0)
        
        # Calculate points for outer vertices
        outer_points = []
        for i in range(self.n_points):
            angle = i * (2 * math.pi / self.n_points) - math.pi/2
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)
            outer_points.append(QPointF(x, y))
        
        # Draw the star
        pen = QPen(QColor(255, 215, 0))  # Gold color
        pen.setWidth(2)
        
        # Draw lines connecting alternate points
        for i in range(self.n_points):
            for step in range(2, (self.n_points + 1) // 2 + 1):
                next_point = (i + step) % self.n_points
                self.scene.addLine(
                    outer_points[i].x(), outer_points[i].y(),
                    outer_points[next_point].x(), outer_points[next_point].y(),
                    pen
                )
        
        # Center the view
        self.view.setSceneRect(-200, -200, 400, 400)
        self.view.centerOn(0, 0)

    def draw_centered_polygon(self):
        radius = 150  # Base radius for visualization
        center = QPointF(0, 0)
        
        # Draw the centered polygon
        pen = QPen(QColor(0, 191, 255))  # Deep sky blue
        pen.setWidth(2)
        
        # Start with center point (1)
        current_number = 1
        center_point = self.scene.addEllipse(-3, -3, 6, 6, 
                                           pen, QBrush(QColor(0, 191, 255)))
        # Add number 1 above center point
        text = self.scene.addText(str(current_number))
        text.setDefaultTextColor(QColor(0, 191, 255))
        text.setPos(-5, -20)  # Position above the point
        
        # Draw concentric polygons based on position
        for p in range(1, self.position + 1):
            current_points = []
            current_radius = radius * (p / self.position)
            
            # Calculate and draw points for this layer
            for i in range(self.n_points):
                angle = i * (2 * math.pi / self.n_points) - math.pi/2
                x = center.x() + current_radius * math.cos(angle)
                y = center.y() + current_radius * math.sin(angle)
                current_points.append(QPointF(x, y))
                
                # Add point marker
                self.scene.addEllipse(x-2, y-2, 4, 4, pen, QBrush(QColor(0, 191, 255)))
                
                # Add number above point
                current_number += 1
                text = self.scene.addText(str(current_number))
                text.setDefaultTextColor(QColor(0, 191, 255))
                # Position text above the point, adjust for text width
                text_width = text.boundingRect().width()
                text.setPos(x - text_width/2, y - 20)
            
            # Draw the polygon lines
            for i in range(self.n_points):
                next_i = (i + 1) % self.n_points
                self.scene.addLine(
                    current_points[i].x(), current_points[i].y(),
                    current_points[next_i].x(), current_points[next_i].y(),
                    pen
                )
        
        # Center the view
        self.view.setSceneRect(-200, -200, 400, 400)
        self.view.centerOn(0, 0) 