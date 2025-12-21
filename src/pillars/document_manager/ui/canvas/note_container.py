from PyQt6.QtWidgets import (
    QGraphicsProxyWidget, QTextEdit, QWidget, QVBoxLayout, QFrame, QLabel, QStyleOptionGraphicsItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

class NoteContainerWidget(QWidget):
    """
    The internal widget for the container.
    Wraps a RichTextEditor (headless) and a drag handle.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Drag Handle (Top Bar)
        self.handle = QFrame()
        self.handle.setFixedHeight(20)
        self.handle.setStyleSheet("background-color: #dddddd; border-top-left-radius: 4px; border-top-right-radius: 4px;")
        self.handle.setCursor(Qt.CursorShape.SizeAllCursor)
        self.layout.addWidget(self.handle)
        
        # Content Editor (RichTextEditor headless)
        from pillars.document_manager.ui.rich_text_editor import RichTextEditor
        self.rt_editor = RichTextEditor(show_ui=False)
        self.editor = self.rt_editor.editor # Expose inner SafeTextEdit for direct access
        
        # Override styles for container look
        self.editor.setStyleSheet("background-color: white; border: 1px solid #eeeeee;")
        self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Auto-expand
        
        self.layout.addWidget(self.rt_editor)
        
    def get_html(self):
        return self.editor.toHtml()
        
    def set_html(self, html):
        self.editor.setHtml(html)
        
    def set_text(self, text):
        self.editor.setHtml(text) # Fallback if text passed but it expects HTML container logic usually

class NoteContainerItem(QGraphicsProxyWidget):
    """
    The Graphics Item representation of a Note Container.
    """
    content_changed = pyqtSignal()
    
    def __init__(self, width=400, height=200):
        super().__init__()
        self.widget_inner = NoteContainerWidget()
        self.setWidget(self.widget_inner)
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        self.resize(width, height)
        
        # Hook up signals
        self.widget_inner.editor.textChanged.connect(self._on_text_changed)
        
        # We handle movement slightly differently if we want the "Handle" to be the only drag area.
        # But QGraphicsProxyWidget with ItemIsMovable makes the whole thing movable usually.
        # To restrict to handle, we might need to override mousePressEvent.
        
    def _on_text_changed(self):
        self.content_changed.emit()
        self._auto_resize()
        
    def _auto_resize(self):
        # Adjust height based on content
        doc_height = self.widget_inner.editor.document().size().height()
        new_height = max(100, doc_height + 30) # +30 for handle/padding
        self.resize(self.size().width(), new_height)

    def mousePressEvent(self, event):
        # Only allow drag if clicking on the handle
        # Map pos to widget coordinates
        local_pos = event.pos()
        if local_pos.y() <= 20: # Handle height
             super().mousePressEvent(event) # Allow drag
        else:
             # Pass to widget (Text Edit needs focus/click)
             super().mousePressEvent(event)
             # If we are Movable, super() starts drag. We typically want to DISABLE drag if not on handle.
             # But QGraphicsProxyWidget passes events to widget if not accepted by item.
             # ItemIsMovable consumes mouse press.
             # We should probably UNSET ItemIsMovable and handle moving manually or
             # only accept mouse press for move in the handle area.
             pass

    # Actually simpler: logic to forward events.
    # If ItemIsMovable is set, QGraphicsItem handles the move.
    # We want to conditionally filter it.
    
    # Better approach: 
    # Don't use ItemIsMovable.
    # Implement mouse press/move/release manually.
    
    # Let's simple it:
    # Set ItemIsMovable = True
    # But checking OneNote, you can drag by the handle. Clicking text edits text.
    pass

class NoteContainerItemMovable(QGraphicsProxyWidget):
    """
    Refined implementation with distinct drag handle.
    """
    content_changed = pyqtSignal()

    def __init__(self, x=0, y=0, w=400, content=""):
        super().__init__()
        self.widget_inner = NoteContainerWidget()
        self.setWidget(self.widget_inner)
        
        self.setPos(x, y)
        self.resize(w, 100) # Height auto-adjusts
        
        self.widget_inner.set_html(content)
        self.widget_inner.editor.textChanged.connect(self._on_text_changed)
        
        # Flags
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsFocusable) # CRITICAL for Scene Focus
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemSendsGeometryChanges)
        # Note: We do NOT set ItemIsMovable because we only want to move via handle
        
        self._dragging = False
        self._drag_start_pos = None
        
        # Styling
        # self.setWindowFrameMargins(0, 0, 0, 0) # Remove proxy native frame if any

    def _on_text_changed(self):
        self.content_changed.emit()
        self._auto_resize()
    
    def _auto_resize(self):
        doc_h = self.widget_inner.editor.document().size().height()
        new_h = max(50, doc_h + 30)
        self.resize(self.size().width(), new_h)

    def mousePressEvent(self, event):
        # Check if click is in handle area (top 20px)
        if event.pos().y() <= 20:
            self._dragging = True
            self._drag_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            self._dragging = False
            self.setCursor(Qt.CursorShape.IBeamCursor)
            self.widget_inner.editor.setFocus() # FORCE FOCUS
            super().mousePressEvent(event) # Pass to editor

    def mouseMoveEvent(self, event):
        if self._dragging:
            # Calculate delta
            delta = event.pos() - self._drag_start_pos
            self.moveBy(delta.x(), delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        print("[Item] Double Click")
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            
    def hoverEnterEvent(self, event):
        # Show handle?
        # OneNote shows handle on hover.
        # implementation detail: styled widget
        pass

