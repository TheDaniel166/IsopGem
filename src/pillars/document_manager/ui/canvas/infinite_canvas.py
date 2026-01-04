"""
Infinite Canvas - The Boundless Workspace.
OneNote-style expandable canvas with click-to-type note containers, shape support, and zoom controls.
"""
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QBrush, QColor, QMouseEvent

from .note_container import NoteContainerItemMovable
from ..shape_item import (
    BaseShapeItem, RectShapeItem, EllipseShapeItem,
    TriangleShapeItem, LineShapeItem, ArrowShapeItem,  # type: ignore[reportUnusedImport]
    create_shape_from_dict
)
import json
import logging

logger = logging.getLogger(__name__)

class InfiniteCanvasScene(QGraphicsScene):
    """
    Infinite scene that expands as items move.
    """
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        # Start large
        self.setSceneRect(0, 0, 5000, 5000)
        self.setBackgroundBrush(QBrush(QColor("white")))

class InfiniteCanvasView(QGraphicsView):
    """
    OneNote-style Click-to-Type Canvas with zoom and grid support.
    """
    content_changed = pyqtSignal()
    zoom_changed = pyqtSignal(float)  # Emits zoom percentage
    
    # Zoom limits
    MIN_ZOOM = 0.1  # 10%
    MAX_ZOOM = 4.0  # 400%
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self._scene = InfiniteCanvasScene(self)
        self.setScene(self._scene)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.NoDrag) # We handle dragging manually or via items
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Scrollbars always on for infinite feel?
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Shape insert mode
        self._insert_mode = False
        self._insert_shape_type = None
        
        # Zoom state
        self._zoom_factor = 1.0
        
        # Grid settings
        self._show_grid = False
        self._grid_size = 20
    
    # --- Zoom Methods ---
    
    def get_zoom(self) -> float:
        """Get current zoom factor (1.0 = 100%)."""
        return self._zoom_factor
    
    def set_zoom(self, factor: float):
        """Set absolute zoom factor."""
        factor = max(self.MIN_ZOOM, min(self.MAX_ZOOM, factor))
        self.resetTransform()
        self.scale(factor, factor)
        self._zoom_factor = factor
        self.zoom_changed.emit(factor * 100)
    
    def zoom_in(self):
        """Zoom in by 25%."""
        self.set_zoom(self._zoom_factor * 1.25)
    
    def zoom_out(self):
        """Zoom out by 25%."""
        self.set_zoom(self._zoom_factor / 1.25)
    
    def zoom_reset(self):
        """Reset to 100% zoom."""
        self.set_zoom(1.0)
    
    def zoom_fit(self):
        """Fit all content in view."""
        items_rect = self._scene.itemsBoundingRect()
        if items_rect.isEmpty():
            self.zoom_reset()
            return
        # Add padding
        items_rect.adjust(-50, -50, 50, 50)
        self.fitInView(items_rect, Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_factor = self.transform().m11()
        self.zoom_changed.emit(self._zoom_factor * 100)
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming (with Ctrl) or scrolling."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            # Normal scrolling
            super().wheelEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Create new note container on double click."""
        logger.info(f"Canvas Double Click at {event.pos()}")
        # Convert view point to scene point
        scene_pos = self.mapToScene(event.pos())
        
        # check if item exists there
        item = self._scene.itemAt(scene_pos, self.transform())
        if not item:
            self.add_note_container(scene_pos.x(), scene_pos.y())
        else:
            super().mouseDoubleClickEvent(event)

    def add_note_container(self, x, y, content="", width=400):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
        Add note container logic.
        
        Args:
            x: Description of x.
            y: Description of y.
            content: Description of content.
            width: Description of width.
        
        """
        container = NoteContainerItemMovable(x, y, width, content)
        self._scene.addItem(container)
        # Connect to handler that updates scene rect
        container.content_changed.connect(self._on_item_changed)
        container.setFocus()
        
        # Initial check
        self._update_scene_rect()
        self.content_changed.emit()

    def _on_item_changed(self):
        """Handle item content changes."""
        self._update_scene_rect()
        self.content_changed.emit()

    def _update_scene_rect(self):
        """Dynamically expand scene rect to fit all items."""
        items_rect = self._scene.itemsBoundingRect()
        scene_rect = self._scene.sceneRect()
        
        # Check if we need to grow
        # Default size is 5000x5000, we never shrink below that generally
        # Logic: If items go beyond current rect - 500 margin, grow by 2000
        
        new_w = scene_rect.width()
        new_h = scene_rect.height()
        changed = False
        
        if items_rect.right() > scene_rect.right() - 500:
            new_w = max(new_w, items_rect.right() + 1000)
            changed = True
            
        if items_rect.bottom() > scene_rect.bottom() - 500:
            new_h = max(new_h, items_rect.bottom() + 1000)
            changed = True
            
        if changed:
            # Save current center point to prevent view jump
            current_center = self.mapToScene(self.viewport().rect().center())
            
            self._scene.setSceneRect(0, 0, new_w, new_h)
            
            # Restore center (re-center on the same point)
            self.centerOn(current_center)

    def clear_canvas(self):
        """
        Clear canvas logic.
        
        """
        self._scene.clear()
        self._scene.setSceneRect(0, 0, 5000, 5000)
        self._insert_mode = False
        self._insert_shape_type = None

    # --- Shape Support ---
    
    def add_shape(self, shape: BaseShapeItem):
        """Add a shape to the canvas."""
        self._scene.addItem(shape)
        self.content_changed.emit()
    
    def start_shape_insert(self, shape_type: type):
        """Enter insert mode for shapes."""
        self._insert_mode = True
        self._insert_shape_type = shape_type
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    def cancel_shape_insert(self):
        """Cancel shape insert mode."""
        self._insert_mode = False
        self._insert_shape_type = None
        self._polygon_config = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        """Handle mouse press - check for shape insert mode."""
        if self._insert_mode and self._insert_shape_type:
            scene_pos = self.mapToScene(event.pos())
            
            # Check for polygon with custom config
            if self._insert_shape_type.__name__ == "PolygonShapeItem" and hasattr(self, '_polygon_config') and self._polygon_config:
                from ..shape_item import PolygonShapeItem
                sides, skip = self._polygon_config  # type: ignore[reportGeneralTypeIssues, reportUnknownVariableType]
                shape = PolygonShapeItem(scene_pos.x(), scene_pos.y(), 100, 100, sides, skip)
                self._polygon_config = None
            else:
                shape = self._insert_shape_type(scene_pos.x(), scene_pos.y())
            
            self.add_shape(shape)
            shape.setSelected(True)
            self._insert_mode = False
            self._insert_shape_type = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """Handle delete key for shapes."""
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            for item in self._scene.selectedItems():
                if isinstance(item, BaseShapeItem):
                    self._scene.removeItem(item)
                    self.content_changed.emit()
            event.accept()
            return
        
        if event.key() == Qt.Key.Key_Escape and self._insert_mode:
            self.cancel_shape_insert()
            event.accept()
            return
        
        super().keyPressEvent(event)

    def get_json_data(self) -> str:
        """Serialize all items to JSON."""
        items_data = []
        shapes_data = []
        
        for item in self._scene.items():
            if isinstance(item, NoteContainerItemMovable):
                data = {
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "width": item.size().width(),
                    "content": item.widget_inner.get_html()
                }
                items_data.append(data)
            elif isinstance(item, BaseShapeItem):
                shapes_data.append(item.to_dict())
        
        payload = {
            "version": 2,  # Updated version for shape support
            "items": items_data,
            "shapes": shapes_data
        }
        return json.dumps(payload)

    def get_searchable_text(self) -> str:
        """Extract plain text from all note containers for indexing."""
        texts = []
        for item in self._scene.items():
            if isinstance(item, NoteContainerItemMovable):
                # We need extracted plain text
                # We can use item.widget_inner.editor.toPlainText()
                # But widget_inner might not be exposed directly if we didn't import strict type
                # But python is dynamic.
                if hasattr(item.widget_inner, 'editor'):
                     texts.append(item.widget_inner.editor.toPlainText())
        
        return "\n".join(texts)

    def load_json_data(self, json_str: str, reset_scroll: bool = True):
        """Load items from JSON."""
        self.clear_canvas()
        if not json_str:
            return
            
        try:
            data = json.loads(json_str)
            version = data.get("version", 1)
            
            # Load note containers
            for item_data in data.get("items", []):
                self.add_note_container(
                    item_data["x"],
                    item_data["y"],
                    item_data["content"],
                    item_data.get("width", 400)
                )
            
            # Load shapes (v2+)
            if version >= 2:
                for shape_data in data.get("shapes", []):
                    shape = create_shape_from_dict(shape_data)
                    if shape:
                        self._scene.addItem(shape)
                        
        except json.JSONDecodeError:
            # Fallback: Treat as raw HTML and create single container
            self.add_note_container(50, 50, json_str)
            logger.info("Converted legacy HTML to Note Container")
            
        # Ensure view starts at top-left
        if reset_scroll:
            self.horizontalScrollBar().setValue(0)
            self.verticalScrollBar().setValue(0)
