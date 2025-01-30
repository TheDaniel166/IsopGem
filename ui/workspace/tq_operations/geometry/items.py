from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor

class GeometryPoint(QGraphicsEllipseItem):
    """A point in the geometry visualization system."""
    
    def __init__(self, x: float, y: float, number: int, radius: float = 5):
        """Create a point at (x,y) with given number identifier.
        
        Args:
            x: X coordinate
            y: Y coordinate
            number: Unique identifier for this point
            radius: Visual radius of the point
        """
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.number = number
        self.setPos(x, y)
        self.setup_appearance()
        self.setup_interaction()
        self.label = None  # Initialize label reference
        
    def setup_appearance(self):
        """Configure the visual appearance of the point."""
        self.setZValue(10)  # Keep points above lines
        self.setBrush(QBrush(QColor("dodgerblue")))
        self.setPen(QPen(QColor("dodgerblue")))
        
    def setup_interaction(self):
        """Configure interaction flags and behavior."""
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        
    def highlight(self, active: bool = True):
        """Highlight the point when selected/hovered."""
        color = QColor("red") if active else QColor("dodgerblue")
        self.setBrush(QBrush(color))
        self.setPen(QPen(color))

    def create_label(self):
        """Create and position the number label."""
        if self.scene() and not self.label:
            self.label = self.scene().addText(str(self.number))
            self.label.setDefaultTextColor(QColor("black"))
            # Make label slightly smaller and bold
            font = self.label.font()
            font.setPointSize(8)
            font.setBold(True)
            self.label.setFont(font)
            # Set label to be above points in z-order
            self.label.setZValue(11)
            self.update_label_position()
            
    def update_label_position(self):
        """Update label position when point moves."""
        if self.label:
            pos = self.scenePos()
            # Calculate offset based on number of digits
            num_digits = len(str(self.number))
            x_offset = 4 + (num_digits - 1) * 2
            # Position label centered above point
            self.label.setPos(pos.x() - x_offset, pos.y() - 20)
            
    def itemChange(self, change, value):
        """Handle changes to the item."""
        if change == QGraphicsItem.ItemSceneHasChanged:
            # Create label when added to scene
            self.create_label()
        elif change == QGraphicsItem.ItemScenePositionHasChanged:
            # Update label position when point moves
            self.update_label_position()
        return super().itemChange(change, value)

    def set_size(self, radius):
        """Set point size."""
        self.setRect(-radius, -radius, radius * 2, radius * 2)
        self.update_label_position()

    def set_color(self, color):
        """Set point color."""
        self.setBrush(QBrush(color))
        self.setPen(QPen(color))

    def set_label_size(self, size):
        """Set label font size."""
        if self.label:
            font = self.label.font()
            font.setPointSize(size)
            self.label.setFont(font)
            self.update_label_position()

    def set_label_color(self, color):
        """Set label color."""
        if self.label:
            self.label.setDefaultTextColor(color)

class GeometryLine(QGraphicsLineItem):
    """A line connecting two points in the geometry system."""
    
    class Type:
        """Enumeration of line types."""
        BASE = 1    # Structural lines (polygon edges)
        PATTERN = 2 # Pattern lines (radial connections)
        CUSTOM = 3  # User-drawn lines
        
    def __init__(self, start_point: GeometryPoint, end_point: GeometryPoint, line_type: int):
        """Create a line between two points.
        
        Args:
            start_point: Starting GeometryPoint
            end_point: Ending GeometryPoint
            line_type: Type of line (BASE, PATTERN, or CUSTOM)
        """
        p1 = start_point.scenePos()
        p2 = end_point.scenePos()
        super().__init__(p1.x(), p1.y(), p2.x(), p2.y())
        
        self.start_point = start_point
        self.end_point = end_point
        self.line_type = line_type
        
        self.setup_appearance()
        self.setup_interaction()
        
    def setup_appearance(self):
        """Configure the visual appearance based on line type."""
        self.setZValue(5)  # Above background, below points
        
        if self.line_type == self.Type.BASE:
            self.setPen(QPen(QColor(70, 130, 180), 2))  # Steel blue
        elif self.line_type == self.Type.PATTERN:
            self.setPen(QPen(QColor(255, 165, 0), 2))   # Orange
        else:  # CUSTOM
            self.setPen(QPen(QColor(255, 165, 0), 4))   # Thicker orange
            
    def setup_interaction(self):
        """Configure interaction flags and behavior."""
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        
    def highlight(self, active: bool = True):
        """Highlight the line when selected/hovered."""
        current_pen = self.pen()
        current_pen.setWidth(6 if active else 2)
        self.setPen(current_pen)
        
    @classmethod
    def from_points(cls, start_point: GeometryPoint, end_point: GeometryPoint, 
                   line_type: int) -> 'GeometryLine':
        """Factory method to create a line from two points."""
        return cls(start_point, end_point, line_type)

    def mousePressEvent(self, event):
        """Let the view handle selection."""
        event.ignore()  # Pass event up to view
        
    def hoverEnterEvent(self, event):
        """Highlight on hover."""
        if not self.isSelected():
            self.highlight(True)
            
    def hoverLeaveEvent(self, event):
        """Remove highlight when not hovering."""
        if not self.isSelected():
            self.highlight(False)

    def set_width(self, width):
        """Set line width."""
        pen = self.pen()
        pen.setWidth(width)
        self.setPen(pen)

    def set_color(self, color):
        """Set line color."""
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)