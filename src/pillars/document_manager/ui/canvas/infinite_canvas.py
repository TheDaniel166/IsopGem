from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QBrush, QColor, QMouseEvent

from .note_container import NoteContainerItemMovable
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

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

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

    def get_json_data(self) -> str:
        """Serialize all items to JSON."""
        items_data = []
        for item in self._scene.items():
            if isinstance(item, NoteContainerItemMovable):
                data = {
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "width": item.size().width(),
                    "content": item.widget_inner.get_html()
                }
                items_data.append(data)
        
        payload = {
            "version": 1,
            "items": items_data
        }
        return json.dumps(payload)

    def load_json_data(self, json_str: str):
        """Load items from JSON."""
        self.clear_canvas()
        if not json_str:
            return
            
        try:
            data = json.loads(json_str)
            if data.get("version") == 1:
                for item_data in data.get("items", []):
                    self.add_note_container(
                        item_data["x"],
                        item_data["y"],
                        item_data["content"],
                        item_data.get("width", 400)
                    )
            else:
                 # Legacy or unknown format
                 pass
        except json.JSONDecodeError:
            # Fallback: Treat as raw HTML and create single container
            self.add_note_container(50, 50, json_str)
            logger.info("Converted legacy HTML to Note Container")
