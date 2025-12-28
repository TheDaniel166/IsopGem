"""Shape overlay for the Rich Text Editor.

This overlay sits on top of the text editor and handles floating shapes.
Mouse events pass through to the editor when not interacting with shapes.
"""
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QWidget, QApplication
)
from PyQt6.QtCore import Qt, QEvent, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QMouseEvent, QColor

from .shape_item import (
    BaseShapeItem, RectShapeItem, EllipseShapeItem, 
    TriangleShapeItem, LineShapeItem, ArrowShapeItem,
    create_shape_from_dict
)
from typing import Optional, List


class ShapeScene(QGraphicsScene):
    """Scene for shape items."""
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setBackgroundBrush(Qt.GlobalColor.transparent)


class ShapeOverlay(QGraphicsView):
    """Transparent overlay for floating shapes.
    
    Key behavior:
    - Transparent background (see through to text editor)
    - Mouse events pass through when not over a shape
    - Shapes can be selected, moved, and resized
    """
    
    # Emitted when a shape is selected/deselected
    shape_selected = pyqtSignal(object)  # BaseShapeItem or None
    
    def __init__(self, parent: QWidget = None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        self._scene = ShapeScene()
        super().__init__(self._scene, parent)
        
        # Transparent appearance
        self.setStyleSheet("background: transparent; border: none;")
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        
        # Make overlay transparent to mouse by default
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setMouseTracking(True)
        
        # Track if we're currently interacting with a shape
        self._interacting = False
        self._insert_mode = False
        self._insert_shape_type: Optional[type] = None
        
        # Install event filter on parent for mouse tracking
        if parent:
            parent.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filter events from parent to detect shape hover."""
        if event.type() == QEvent.Type.MouseMove:
            # Check if mouse is over a shape
            pos = self.mapFromGlobal(event.globalPosition().toPoint())
            scene_pos = self.mapToScene(pos)
            items = self._scene.items(scene_pos)
            shape_items = [i for i in items if isinstance(i, BaseShapeItem)]
            
            if shape_items or self._interacting or self._insert_mode:
                # Enable mouse events on overlay when over a shape
                self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            else:
                # Pass through mouse events when not over a shape
                self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press."""
        if self._insert_mode and self._insert_shape_type:
            # Insert new shape at click position
            scene_pos = self.mapToScene(event.position().toPoint())
            shape = self._insert_shape_type(scene_pos.x(), scene_pos.y())
            self.add_shape(shape)
            shape.setSelected(True)
            self._insert_mode = False
            self._insert_shape_type = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        
        self._interacting = True
        super().mousePressEvent(event)
        
        # Emit selection signal
        selected = self.get_selected_shapes()
        self.shape_selected.emit(selected[0] if selected else None)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        super().mouseReleaseEvent(event)
        self._interacting = False
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move."""
        super().mouseMoveEvent(event)
    
    def keyPressEvent(self, event):
        """Handle key press for shape deletion."""
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for shape in self.get_selected_shapes():
                self._scene.removeItem(shape)
            event.accept()
            return
        
        if event.key() == Qt.Key.Key_Escape:
            if self._insert_mode:
                self._insert_mode = False
                self._insert_shape_type = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                # Deselect all
                for item in self._scene.selectedItems():
                    item.setSelected(False)
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    # --- Shape Management ---
    
    def add_shape(self, shape: BaseShapeItem):
        """Add a shape to the overlay."""
        self._scene.addItem(shape)
    
    def remove_shape(self, shape: BaseShapeItem):
        """Remove a shape from the overlay."""
        self._scene.removeItem(shape)
    
    def get_shapes(self) -> List[BaseShapeItem]:
        """Get all shapes in the overlay."""
        return [i for i in self._scene.items() if isinstance(i, BaseShapeItem)]
    
    def get_selected_shapes(self) -> List[BaseShapeItem]:
        """Get currently selected shapes."""
        return [i for i in self._scene.selectedItems() if isinstance(i, BaseShapeItem)]
    
    def clear_shapes(self):
        """Remove all shapes."""
        for shape in self.get_shapes():
            self._scene.removeItem(shape)
    
    def start_insert_mode(self, shape_type: type):
        """Enter insert mode - next click will create a shape."""
        self._insert_mode = True
        self._insert_shape_type = shape_type
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    def cancel_insert_mode(self):
        """Cancel insert mode."""
        self._insert_mode = False
        self._insert_shape_type = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    # --- Serialization ---
    
    def to_list(self) -> List[dict]:
        """Serialize all shapes to a list of dictionaries."""
        return [shape.to_dict() for shape in self.get_shapes()]
    
    def from_list(self, shapes_data: List[dict]):
        """Load shapes from a list of dictionaries."""
        self.clear_shapes()
        for data in shapes_data:
            shape = create_shape_from_dict(data)
            if shape:
                self.add_shape(shape)
    
    # --- Geometry ---
    
    def resizeEvent(self, event):
        """Handle resize to match parent."""
        super().resizeEvent(event)
        # Update scene rect to match view
        self.setSceneRect(0, 0, self.width(), self.height())