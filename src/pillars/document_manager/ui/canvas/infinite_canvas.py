from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QBrush, QColor, QMouseEvent

from .note_container import NoteContainerItemMovable
from ..shape_item import (
    BaseShapeItem, RectShapeItem, EllipseShapeItem,
    TriangleShapeItem, LineShapeItem, ArrowShapeItem,
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
        super().__init__(parent)
        # Start large
        self.setSceneRect(0, 0, 5000, 5000)
        self.setBackgroundBrush(QBrush(QColor("white")))

class InfiniteCanvasView(QGraphicsView):
    """
    OneNote-style Click-to-Type Canvas.
    """
    content_changed = pyqtSignal()
    
    def __init__(self, parent=None):
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

    def add_note_container(self, x, y, content="", width=400):
        container = NoteContainerItemMovable(x, y, width, content)
        self._scene.addItem(container)
        container.content_changed.connect(self.content_changed.emit)
        container.setFocus()
        
        # Ensure scene rect grows
        self._ensure_visible(x, y)
        self.content_changed.emit()

    def _ensure_visible(self, x, y):
        rect = self._scene.sceneRect()
        if x > rect.right() - 500:
            rect.setWidth(rect.width() + 1000)
        if y > rect.bottom() - 500:
            rect.setHeight(rect.height() + 1000)
        self._scene.setSceneRect(rect)

    def clear_canvas(self):
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
                sides, skip = self._polygon_config
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

    def load_json_data(self, json_str: str):
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

