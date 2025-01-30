from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPen, QColor
import math
from .items import GeometryPoint, GeometryLine

class GeometryScene(QGraphicsScene):
    """Scene for managing geometric items and their interactions."""
    
    def __init__(self):
        super().__init__()
        # Drawing state
        self.last_clicked_point = None
        self.drawing_mode = True
        self.preview_line = None
        
        # Selection settings
        self.selection_distance = 20
        
    def create_star_number(self, points: int, position: int):
        """Create a star number visualization.
        
        Args:
            points: Number of points in the star
            position: Which star number to show
        """
        # Create center point
        center = GeometryPoint(0, 0, 1)
        self.addItem(center)
        
        # Calculate radius based on position
        radius = 50 * position  # Base radius
        
        # Create outer points
        star_points = []
        for i in range(points):
            angle = 2 * math.pi * i / points - math.pi/2  # Start from top
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            point = GeometryPoint(x, y, i + 2)
            self.addItem(point)
            star_points.append(point)
            
            # Connect to center
            line = GeometryLine(center, point, GeometryLine.Type.BASE)
            self.addItem(line)
        
        # Connect points to form star (skip points based on star pattern)
        skip = (points - 1) // 2  # This creates the proper star pattern
        for i in range(points):
            next_point = star_points[(i + skip) % points]
            line = GeometryLine(star_points[i], next_point, GeometryLine.Type.BASE)
            self.addItem(line)
        
        return [center] + star_points

    def create_centered_polygon(self, sides: int, layers: int, layer_distance: float = 50):
        """Create a centered polygonal number visualization.
        
        Args:
            sides: Number of sides (k)
            layers: Number of layers including center (n)
            layer_distance: Distance between layers
        """
        # Create center point
        center = GeometryPoint(0, 0, 1)
        self.addItem(center)
        points = [center]
        
        point_number = 2
        
        # Create each layer
        for layer in range(1, layers):
            layer_points = []
            points_in_layer = layer * sides
            
            # Create points for this layer
            for i in range(points_in_layer):
                angle = 2 * math.pi * i / points_in_layer
                x = layer * layer_distance * math.cos(angle)
                y = layer * layer_distance * math.sin(angle)
                
                point = GeometryPoint(x, y, point_number)
                self.addItem(point)
                layer_points.append(point)
                points.append(point)
                point_number += 1
            
            # Connect points in this layer
            for i in range(points_in_layer):
                line = GeometryLine(
                    layer_points[i],
                    layer_points[(i + 1) % points_in_layer],
                    GeometryLine.Type.BASE
                )
                self.addItem(line)
                
        return points

    def create_polygonal_number(self, sides: int, n: int, spacing: float = 50):
        """Create a polygonal number visualization.
        Builds from a corner vertex outward in layers, maintaining n-gon symmetry.
        
        Args:
            sides: Number of sides (k-gonal)
            n: Which polygonal number to show
            spacing: Distance between points
        """
        points = []
        point_number = 1
        
        # Start with corner vertex (red)
        corner = GeometryPoint(0, 0, point_number)
        self.addItem(corner)
        points.append(corner)
        point_number += 1
        
        if n == 1:
            return points
            
        # For each layer
        for layer in range(1, n):
            layer_points = []
            
            # Calculate points for this layer
            for side in range(sides - 1):  # -1 because we start from corner
                # Calculate points along this side
                points_on_side = layer + 1  # Number of points on this side
                
                for i in range(points_on_side):
                    # Calculate position along the side
                    fraction = i / layer if layer > 0 else 0
                    
                    # Calculate angles for this side
                    start_angle = 2 * math.pi * side / sides
                    end_angle = 2 * math.pi * (side + 1) / sides
                    
                    # Interpolate between angles
                    angle = start_angle * (1 - fraction) + end_angle * fraction
                    
                    # Calculate point position
                    x = layer * spacing * math.cos(angle)
                    y = layer * spacing * math.sin(angle)
                    
                    # Create point
                    point = GeometryPoint(x, y, point_number)
                    self.addItem(point)
                    layer_points.append(point)
                    points.append(point)
                    point_number += 1
            
            # Connect points within this layer
            for i in range(len(layer_points) - 1):
                line = GeometryLine(layer_points[i], layer_points[i + 1], GeometryLine.Type.BASE)
                self.addItem(line)
            
            # Connect back to corner for first layer
            if layer == 1:
                for point in layer_points:
                    line = GeometryLine(corner, point, GeometryLine.Type.BASE)
                    self.addItem(line)
            else:
                # Connect to previous layer
                prev_layer_start = len(points) - len(layer_points) - (layer * (sides - 1))
                for i in range(len(layer_points)):
                    if i < len(points) - len(layer_points):
                        prev_point = points[prev_layer_start + i]
                        line = GeometryLine(prev_point, layer_points[i], GeometryLine.Type.BASE)
                        self.addItem(line)
        
        return points
        
    def points_too_close(self, x, y, other_point, threshold=1):
        """Check if a potential point would be too close to an existing point."""
        dx = x - other_point.scenePos().x()
        dy = y - other_point.scenePos().y()
        return (dx * dx + dy * dy) < threshold
        
    def get_nearest_point(self, pos: QPointF) -> GeometryPoint:
        """Find the nearest point to the given position."""
        items = self.items(QRectF(
            pos.x() - self.selection_distance,
            pos.y() - self.selection_distance,
            self.selection_distance * 2,
            self.selection_distance * 2
        ))
        
        nearest = None
        min_dist = float('inf')
        
        for item in items:
            if isinstance(item, GeometryPoint):
                dist = (item.scenePos() - pos).manhattanLength()
                if dist < min_dist and dist <= self.selection_distance:
                    min_dist = dist
                    nearest = item
                    
        return nearest
        
    def get_nearest_line(self, pos: QPointF) -> GeometryLine:
        """Find the nearest line to the given position."""
        items = self.items(QRectF(
            pos.x() - self.selection_distance,
            pos.y() - self.selection_distance,
            self.selection_distance * 2,
            self.selection_distance * 2
        ))
        
        nearest = None
        min_dist = float('inf')
        
        for item in items:
            if isinstance(item, GeometryLine):
                dist = self.distance_to_line_segment(
                    pos,
                    item.line().p1(),
                    item.line().p2()
                )
                if dist < min_dist and dist <= self.selection_distance:
                    min_dist = dist
                    nearest = item
                    
        return nearest
        
    def distance_to_line_segment(self, point: QPointF, start: QPointF, end: QPointF) -> float:
        """Calculate the perpendicular distance from a point to a line segment."""
        line_vec = QPointF(end.x() - start.x(), end.y() - start.y())
        point_vec = QPointF(point.x() - start.x(), point.y() - start.y())
        
        line_length = line_vec.x()**2 + line_vec.y()**2
        if line_length == 0:  # Start and end are the same point
            return math.hypot(point.x() - start.x(), point.y() - start.y())
        
        # Project point onto the line, clamped to the segment
        t = max(0, min(1, (point_vec.x() * line_vec.x() + point_vec.y() * line_vec.y()) / line_length))
        projection = QPointF(
            start.x() + t * line_vec.x(),
            start.y() + t * line_vec.y()
        )
        
        return math.hypot(point.x() - projection.x(), point.y() - projection.y()) 