from PyQt6.QtWidgets import (
    QGraphicsProxyWidget, QTextEdit, QWidget, QVBoxLayout, QFrame, QLabel, QStyleOptionGraphicsItem, QSizeGrip
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class ResizeGripWidget(QWidget):
    """A small resize grip that appears in the corner."""
    
    resize_delta = pyqtSignal(float, float)  # width delta, height delta
    resize_started = pyqtSignal()
    resize_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self._dragging = False
        self._start_pos = None
        self.setStyleSheet("background-color: transparent;")
    
    def paintEvent(self, event):
        """Draw resize grip lines."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#aaaaaa"), 1)
        painter.setPen(pen)
        
        # Draw diagonal grip lines
        for i in range(3):
            offset = 4 + i * 4
            painter.drawLine(self.width() - offset, self.height(), 
                           self.width(), self.height() - offset)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_pos = event.globalPosition().toPoint()
            self.resize_started.emit()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self._dragging and self._start_pos:
            current = event.globalPosition().toPoint()
            delta_x = current.x() - self._start_pos.x()
            delta_y = current.y() - self._start_pos.y()
            self._start_pos = current
            self.resize_delta.emit(delta_x, delta_y)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self._start_pos = None
            self.resize_finished.emit()
            event.accept()


class NoteContainerWidget(QWidget):
    """
    The internal widget for the container.
    Wraps a RichTextEditor (headless) and a drag handle.
    """
    resize_requested = pyqtSignal(float, float)  # width delta, height delta
    
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
        
        # Resize grip in corner
        self.resize_grip = ResizeGripWidget(self)
        self.resize_grip.resize_delta.connect(self._on_resize_delta)
        
    def _on_resize_delta(self, dx: float, dy: float):
        """Forward resize request to parent."""
        self.resize_requested.emit(dx, dy)
    
    def resizeEvent(self, event):
        """Keep resize grip in bottom-right corner."""
        super().resizeEvent(event)
        grip_size = self.resize_grip.size()
        self.resize_grip.move(
            self.width() - grip_size.width(),
            self.height() - grip_size.height()
        )
        
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
    
    RESIZE_MARGIN = 8  # Pixels from edge to detect resize

    def __init__(self, x=0, y=0, w=400, content=""):
        super().__init__()
        self.widget_inner = NoteContainerWidget()
        self.setWidget(self.widget_inner)
        
        self.setPos(x, y)
        self.resize(w, 100) # Height auto-adjusts
        
        self.widget_inner.set_html(content)
        self.widget_inner.editor.textChanged.connect(self._on_text_changed)
        self.widget_inner.resize_requested.connect(self._on_resize_grip)
        
        # Flags
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsFocusable) # CRITICAL for Scene Focus
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemSendsGeometryChanges)
        # Note: We do NOT set ItemIsMovable because we only want to move via handle
        
        self._dragging = False
        self._drag_start_pos = None
        
        # Resize state
        self._resizing = False
        self._resize_edge = None  # 'right', 'bottom', 'corner'
        self._resize_start_size = None
        self._resize_start_pos = None
        self._auto_height = True  # Auto-adjust height to content
        
        # State properties for context menu features
        self._header_name = ""
        self._header_color = "#dddddd"
        self._background_color = "#ffffff"
        self._is_minimized = False
        self._is_locked = False
        self._minimized_height = 20  # Just the header
        self._expanded_height = 100
        
        # Enable context menu
        self.setAcceptHoverEvents(True)

    def _on_resize_grip(self, dx: float, dy: float):
        """Handle resize grip drag."""
        if self._is_locked or self._is_minimized:
            return
        new_w = max(150, self.size().width() + dx)
        new_h = max(50, self.size().height() + dy)
        self.resize(new_w, new_h)
        self._expanded_height = new_h
        self._auto_height = False  # Disable auto-height when manually resizing

    def _on_text_changed(self):
        self.content_changed.emit()
        if not self._is_minimized and self._auto_height:
            self._auto_resize()
    
    def _auto_resize(self):
        doc_h = self.widget_inner.editor.document().size().height()
        new_h = max(50, doc_h + 30)
        self._expanded_height = new_h
        if not self._is_minimized:
            self.resize(self.size().width(), new_h)
    
    def _get_resize_edge(self, pos: QPointF) -> str:
        """Determine which resize edge (if any) the position is near."""
        w, h = self.size().width(), self.size().height()
        margin = self.RESIZE_MARGIN
        
        near_right = pos.x() >= w - margin
        near_bottom = pos.y() >= h - margin and pos.y() > 20  # Not in header
        
        if near_right and near_bottom:
            return 'corner'
        elif near_right:
            return 'right'
        elif near_bottom:
            return 'bottom'
        return None

    def mousePressEvent(self, event):
        pos = event.pos()
        
        # Check for resize first
        resize_edge = self._get_resize_edge(pos)
        if resize_edge and not self._is_locked and not self._is_minimized:
            self._resizing = True
            self._resize_edge = resize_edge
            self._resize_start_size = self.size()
            self._resize_start_pos = event.scenePos()
            self._auto_height = False  # Disable auto-height when manually resizing
            event.accept()
            return
        
        # Check if click is in handle area (top 20px)
        if pos.y() <= 20 and not self._is_locked:
            self._dragging = True
            self._drag_start_pos = pos
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            self._dragging = False
            if not self._is_minimized:
                self.setCursor(Qt.CursorShape.IBeamCursor)
                self.widget_inner.editor.setFocus() # FORCE FOCUS
            super().mousePressEvent(event) # Pass to editor

    def mouseMoveEvent(self, event):
        if self._resizing and self._resize_start_size and self._resize_start_pos:
            delta = event.scenePos() - self._resize_start_pos
            new_w = self._resize_start_size.width()
            new_h = self._resize_start_size.height()
            
            if self._resize_edge in ('right', 'corner'):
                new_w = max(150, self._resize_start_size.width() + delta.x())
            if self._resize_edge in ('bottom', 'corner'):
                new_h = max(50, self._resize_start_size.height() + delta.y())
            
            self.resize(new_w, new_h)
            self._expanded_height = new_h
            event.accept()
            return
        
        if self._dragging:
            # Calculate delta
            delta = event.pos() - self._drag_start_pos
            self.moveBy(delta.x(), delta.y())
            event.accept()
        else:
            # Update cursor based on position
            resize_edge = self._get_resize_edge(event.pos())
            if resize_edge == 'corner':
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif resize_edge == 'right':
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif resize_edge == 'bottom':
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif event.pos().y() <= 20:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.IBeamCursor)
            super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Double-click on header to toggle minimize
        if event.pos().y() <= 20:
            self._toggle_minimize()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resizing:
            self._resizing = False
            self._resize_edge = None
            self._resize_start_size = None
            self._resize_start_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        
        if self._dragging:
            self._dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            
    def hoverEnterEvent(self, event):
        pass

    def contextMenuEvent(self, event):
        """Show right-click context menu."""
        from PyQt6.QtWidgets import QMenu, QColorDialog, QInputDialog
        
        menu = QMenu()
        
        # Header Name
        name_action = menu.addAction(f"Rename: '{self._header_name or 'Untitled'}'")
        name_action.triggered.connect(self._edit_header_name)
        
        menu.addSeparator()
        
        # Colors submenu
        colors_menu = menu.addMenu("Colors")
        
        # Header Color
        header_color_menu = colors_menu.addMenu("Header Color")
        header_colors = [
            ("Gray", "#dddddd"), ("Blue", "#bfdbfe"), ("Green", "#bbf7d0"),
            ("Yellow", "#fef08a"), ("Red", "#fecaca"), ("Purple", "#e9d5ff"),
            ("Dark", "#6b7280"),
        ]
        for name, color in header_colors:
            action = header_color_menu.addAction(name)
            action.triggered.connect(lambda checked, c=color: self._set_header_color(c))
        header_color_menu.addSeparator()
        header_color_menu.addAction("Custom...").triggered.connect(self._choose_header_color)
        
        # Background Color
        bg_color_menu = colors_menu.addMenu("Background Color")
        bg_colors = [
            ("White", "#ffffff"), ("Light Gray", "#f9fafb"), ("Light Blue", "#eff6ff"),
            ("Light Green", "#f0fdf4"), ("Light Yellow", "#fefce8"), ("Light Red", "#fef2f2"),
            ("Light Purple", "#faf5ff"),
        ]
        for name, color in bg_colors:
            action = bg_color_menu.addAction(name)
            action.triggered.connect(lambda checked, c=color: self._set_background_color(c))
        bg_color_menu.addSeparator()
        bg_color_menu.addAction("Custom...").triggered.connect(self._choose_background_color)
        
        menu.addSeparator()
        
        # Minimize/Expand
        if self._is_minimized:
            expand_action = menu.addAction("Expand")
            expand_action.triggered.connect(self._toggle_minimize)
        else:
            minimize_action = menu.addAction("Minimize")
            minimize_action.triggered.connect(self._toggle_minimize)
        
        # Auto-Height toggle
        if self._auto_height:
            auto_action = menu.addAction("✓ Auto-Height Enabled")
            auto_action.triggered.connect(self._toggle_auto_height)
        else:
            auto_action = menu.addAction("Auto-Height (disabled)")
            auto_action.triggered.connect(self._toggle_auto_height)
        
        # Lock/Unlock
        if self._is_locked:
            unlock_action = menu.addAction("🔓 Unlock Position")
            unlock_action.triggered.connect(self._toggle_lock)
        else:
            lock_action = menu.addAction("🔒 Lock Position")
            lock_action.triggered.connect(self._toggle_lock)
        
        menu.addSeparator()
        
        # Z-Order
        menu.addAction("Bring to Front").triggered.connect(self._bring_to_front)
        menu.addAction("Send to Back").triggered.connect(self._send_to_back)
        
        menu.addSeparator()
        
        # Duplicate
        menu.addAction("Duplicate").triggered.connect(self._duplicate)
        
        # Delete
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(self._delete)
        
        menu.exec(event.screenPos())
    
    def _edit_header_name(self):
        """Edit the header name."""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(None, "Container Name", "Enter name:", 
                                         text=self._header_name)
        if ok:
            self._header_name = name
            self._update_header_display()
    
    def _update_header_display(self):
        """Update the header visual with name and color."""
        name_display = self._header_name if self._header_name else ""
        lock_icon = "🔒 " if self._is_locked else ""
        
        self.widget_inner.handle.setStyleSheet(
            f"background-color: {self._header_color}; "
            f"border-top-left-radius: 4px; border-top-right-radius: 4px; "
            f"color: #333;"
        )
        
        # Add a label for the name if not already present
        if not hasattr(self.widget_inner, 'header_label'):
            from PyQt6.QtWidgets import QHBoxLayout
            layout = QHBoxLayout(self.widget_inner.handle)
            layout.setContentsMargins(8, 0, 8, 0)
            self.widget_inner.header_label = QLabel()
            self.widget_inner.header_label.setStyleSheet("font-size: 11px; color: #333;")
            layout.addWidget(self.widget_inner.header_label)
        
        self.widget_inner.header_label.setText(f"{lock_icon}{name_display}")
    
    def _set_header_color(self, color: str):
        self._header_color = color
        self._update_header_display()
    
    def _choose_header_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(QColor(self._header_color), None, "Header Color")
        if color.isValid():
            self._set_header_color(color.name())
    
    def _set_background_color(self, color: str):
        self._background_color = color
        self.widget_inner.editor.setStyleSheet(
            f"background-color: {color}; border: 1px solid #eeeeee;"
        )
    
    def _choose_background_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(QColor(self._background_color), None, "Background Color")
        if color.isValid():
            self._set_background_color(color.name())
    
    def _toggle_minimize(self):
        self._is_minimized = not self._is_minimized
        if self._is_minimized:
            self._expanded_height = self.size().height()
            self.resize(self.size().width(), self._minimized_height)
            self.widget_inner.rt_editor.hide()
        else:
            self.widget_inner.rt_editor.show()
            self.resize(self.size().width(), self._expanded_height)
    
    def _toggle_lock(self):
        self._is_locked = not self._is_locked
        self._update_header_display()
        if self._is_locked:
            self.widget_inner.handle.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.widget_inner.handle.setCursor(Qt.CursorShape.SizeAllCursor)
    
    def _toggle_auto_height(self):
        """Toggle auto-height mode."""
        self._auto_height = not self._auto_height
        if self._auto_height:
            # Immediately adjust height to content
            self._auto_resize()
    
    def _bring_to_front(self):
        if self.scene():
            max_z = max((item.zValue() for item in self.scene().items()), default=0)
            self.setZValue(max_z + 1)
    
    def _send_to_back(self):
        if self.scene():
            min_z = min((item.zValue() for item in self.scene().items()), default=0)
            self.setZValue(min_z - 1)
    
    def _duplicate(self):
        """Create a copy of this container."""
        if self.scene():
            new_item = NoteContainerItemMovable(
                x=self.pos().x() + 30,
                y=self.pos().y() + 30,
                w=self.size().width(),
                content=self.widget_inner.get_html()
            )
            new_item._header_name = self._header_name
            new_item._header_color = self._header_color
            new_item._background_color = self._background_color
            new_item._update_header_display()
            new_item._set_background_color(self._background_color)
            self.scene().addItem(new_item)
    
    def _delete(self):
        """Remove this container from the scene."""
        if self.scene():
            self.scene().removeItem(self)
    
    def to_dict(self) -> dict:
        """Serialize container for saving."""
        return {
            "x": self.pos().x(),
            "y": self.pos().y(),
            "w": self.size().width(),
            "content": self.widget_inner.get_html(),
            "header_name": self._header_name,
            "header_color": self._header_color,
            "background_color": self._background_color,
            "is_minimized": self._is_minimized,
            "is_locked": self._is_locked,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NoteContainerItemMovable":
        """Create container from saved data."""
        item = cls(
            x=data.get("x", 0),
            y=data.get("y", 0),
            w=data.get("w", 400),
            content=data.get("content", "")
        )
        item._header_name = data.get("header_name", "")
        item._header_color = data.get("header_color", "#dddddd")
        item._background_color = data.get("background_color", "#ffffff")
        item._is_minimized = data.get("is_minimized", False)
        item._is_locked = data.get("is_locked", False)
        
        item._update_header_display()
        item._set_background_color(item._background_color)
        
        if item._is_minimized:
            item.resize(item.size().width(), item._minimized_height)
            item.widget_inner.rt_editor.hide()
        
        return item
