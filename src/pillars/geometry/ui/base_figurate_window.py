"""Base class for interactivity and layout of figurate number windows."""
from __future__ import annotations

from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
    QPushButton, QLabel, QGraphicsView
)
from PyQt6.QtCore import Qt, QThreadPool, QObject, pyqtSignal, QRunnable, QPointF
from PyQt6.QtGui import QPen, QColor

from shared.ui import WindowManager
from .geometry_scene import GeometryScene, GeometryScenePayload
from .geometry_view import GeometryView
from .geometry_interaction import GeometryInteractionManager, GroupManagementPanel, ConnectionToolBar

class BaseFigurateWindow(QMainWindow):
    """
    Base class for specific figurate number visualizations.
    
    Handles:
    - Scene/View setup
    - Interaction Manager (Drawing, Grouping, Selection)
    - ThreadPool for async rendering
    - Common UI Layout (Viewport, Right Panel, Toolbar)
    - Shared Styles
    """

    HEAVY_THRESHOLD = 2000

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager

        # Core Components
        self.scene = GeometryScene()
        self.view = GeometryView(self.scene)
        self.thread_pool = QThreadPool.globalInstance()
        self.interaction_manager = GeometryInteractionManager(self)
        
        # State
        self._rendering = False
        self._controls_frame: Optional[QFrame] = None
        self._render_button: Optional[QPushButton] = None
        
        # Base UI setup
        self.setMinimumSize(1100, 720)
        self.setStyleSheet("background-color: #f8fafc;")
        
        # Signals
        self._connect_interaction_signals()
        
    def _connect_interaction_signals(self):
        self.interaction_manager.groups_changed.connect(self._refresh_highlights)
        self.interaction_manager.connection_added.connect(self._on_connection_added)
        self.interaction_manager.connections_cleared.connect(self._refresh_connections)
        self.interaction_manager.mode_changed.connect(self._update_view_mode)
        self.interaction_manager.draw_start_changed.connect(self._refresh_highlights)
        self.scene.dot_clicked.connect(self._handle_dot_click)
        self.scene.mouse_moved.connect(self._on_scene_mouse_move)
        self.scene.dot_hovered.connect(self._on_dot_hover_enter)
        self.scene.dot_hover_leave.connect(self._on_dot_hover_leave)
        self.scene.canvas_clicked.connect(self.interaction_manager.cancel_drawing_chain)
        self.view.dots_selected.connect(self._on_dots_selected)

    def _setup_ui_skeleton(self, controls_widget: QWidget):
        """Builds the main layout using the provided controls widget."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Left: Controls (Provided by subclass)
        layout.addWidget(controls_widget)

        # Center: Viewport
        viewport_frame = QFrame()
        viewport_frame.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 14px;")
        viewport_layout = QVBoxLayout(viewport_frame)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        viewport_layout.setSpacing(0)

        # Connection Toolbar at Top of Viewport
        conn_bar = ConnectionToolBar(self.interaction_manager)
        conn_bar.dot_color_changed.connect(self.scene.set_dot_color)
        conn_bar.text_color_changed.connect(self.scene.set_text_color)
        viewport_layout.addWidget(conn_bar)

        # View Toolbar
        toolbar = self._build_view_toolbar()
        viewport_layout.addWidget(toolbar)
        
        # The Graphics View
        viewport_layout.addWidget(self.view, 1)

        layout.addWidget(viewport_frame, 1)

        # Right: Group panel (The Tablet)
        group_panel = GroupManagementPanel(self.interaction_manager)
        group_panel.setObjectName("FloatingPanelRight")
        group_panel.setFixedWidth(260)
        group_panel.setStyleSheet("""
            QWidget#FloatingPanelRight {
                background-color: #f1f5f9; 
                border-left: 1px solid #cbd5e1;
            }
        """)
        layout.addWidget(group_panel)

    def _build_view_toolbar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet("background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        title = QLabel("Dot layout")
        title.setStyleSheet("color: #0f172a; font-weight: 700;")
        layout.addWidget(title)
        layout.addStretch(1)

        fit_btn = QPushButton("Fit to view")
        fit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fit_btn.setStyleSheet(self._ghost_button_style())
        fit_btn.clicked.connect(self.view.fit_scene)
        layout.addWidget(fit_btn)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        zoom_in_btn.setStyleSheet(self._ghost_button_style())
        zoom_in_btn.setToolTip("Zoom In")
        zoom_in_btn.clicked.connect(lambda: self.view.zoom(1.2))
        layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        zoom_out_btn.setStyleSheet(self._ghost_button_style())
        zoom_out_btn.setToolTip("Zoom Out")
        zoom_out_btn.clicked.connect(lambda: self.view.zoom(1/1.2))
        layout.addWidget(zoom_out_btn)

        reset_btn = QPushButton("Reset view")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(self._ghost_button_style())
        reset_btn.clicked.connect(self.view.reset_view)
        layout.addWidget(reset_btn)

        return bar

    # ------------------------------------------------------------------
    # Interaction Handling
    # ------------------------------------------------------------------
    def _update_view_mode(self, mode: str):
        if mode == "draw":
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.view.setCursor(Qt.CursorShape.CrossCursor)
            self.view.set_selection_mode(False)
        elif mode == "select":
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.view.set_selection_mode(True)
        else:
            self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self.view.set_selection_mode(False)

    def _handle_dot_click(self, index: int, modifiers, button):
        """Handle clicks for both drawing and grouping."""
        is_drawing = self.interaction_manager.drawing_active
        if is_drawing and button == Qt.MouseButton.LeftButton:
            self.scene.clearSelection() # Fix for sticking selection box
            conn = self.interaction_manager.process_draw_click(index)
            if conn:
                self._on_connection_added(conn)
            self._refresh_highlights()
        elif button == Qt.MouseButton.RightButton:
            self.interaction_manager.toggle_dot_in_group(index)
            self._refresh_highlights()

    def _on_connection_added(self, conn):
        # NOTE: Subclasses must maintain self._current_points or override this
        if not hasattr(self, '_current_points') or not self._current_points:
            return
            
        # Handle 1-based indexing
        if conn.start_index > len(self._current_points) or conn.end_index > len(self._current_points):
            return
            
        p1 = self._current_points[conn.start_index - 1]
        p2 = self._current_points[conn.end_index - 1]
        
        # For 3D window, points might be different structure? 
        # Actually 3D window has separate logic for projection.
        # But this base logic assumes 2D points are available.
        # We will make sure 3D window overrides if needed or stores 2D points in _current_points.
        
        qt_pen = QPen(conn.color, conn.width)
        qt_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        qt_pen.setCosmetic(True)
        self.scene.add_connection_line(p1, p2, qt_pen)

    def _on_dots_selected(self, indices: list):
        for idx in indices:
            self.interaction_manager.toggle_dot_in_group(idx)
        self._refresh_highlights()

    def _on_scene_mouse_move(self, pos):
        """Handle mouse movement for drawing previews."""
        if not self.interaction_manager.drawing_active:
             # Ensure preview is cleared if we exited mode but moved mouse
            if self.scene._preview_line_item:
                self.scene.set_preview_line(None, None, visible=False)
            return

        start_index = self.interaction_manager.current_draw_start
        if start_index is not None and hasattr(self, '_current_points'):
            # Check range
            if 1 <= start_index <= len(self._current_points):
                pt = self._current_points[start_index - 1]
                start_pos = QPointF(pt[0], pt[1])
                
                # If hovering over a dot, snap to it?
                # The visual snap 'glow' is handled by _on_dot_hover_enter.
                # The line should follow mouse for fluid feel, OR snap to dot center if hover is active.
                # Let's snap if we know usage.
                # Scene stores _hovered_dot_index. We can query it?
                # For now, just follow mouse. simpler and standard.
                
                # Use the pen color from manager
                self.scene.set_preview_line(start_pos, pos, visible=True, color=self.interaction_manager.pen_color)

    def _on_dot_hover_enter(self, index: int):
        """Highlight dot under cursor."""
        if self.interaction_manager.drawing_active:
            self.scene.set_hover_target(index)
            # If we are dragging a line, maybe snap the end to this dot?
            # Implemented via visual snap (hover target) + mouse cursor position.
    
    def _on_dot_hover_leave(self, index: int):
        self.scene.set_hover_target(None)
    
    def _refresh_highlights(self, _=None):
        """Re-apply visual highlights for groups and active tools."""
        # 1. Groups
        for name, group in self.interaction_manager.groups.items():
            self.scene.highlight_dots(list(group.indices), group.color)
            
        # 2. Active Draw Start (Pen Color)
        start = self.interaction_manager.current_draw_start
        if start is not None:
             self.scene.set_start_dot_highlight(start, self.interaction_manager.pen_color)
        else:
             # Ensure preview and highlight are cleared
             self.scene.set_start_dot_highlight(None)
             self.scene.set_preview_line(None, None, visible=False)

    def _refresh_connections(self):
        # Trigger full re-render to clear lines effectively
        # Subclasses should implement _render()
        if hasattr(self, '_render'):
            self._render()

    # ------------------------------------------------------------------
    # Rendering Helpers
    # ------------------------------------------------------------------
    def _set_busy(self, busy: bool):
        self._rendering = busy
        self.setCursor(Qt.CursorShape.BusyCursor if busy else Qt.CursorShape.ArrowCursor)
        if self._controls_frame:
            self._controls_frame.setDisabled(busy)
        if self._render_button:
            self._render_button.setText("Rendering..." if busy else self._render_button.text().replace("Rendering...", ""))
            self._render_button.setDisabled(busy)

    def _toggle_labels(self, state: int):
        self.scene.set_labels_visible(state == 2)

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------
    def _spin_style(self) -> str:
        return (
            "QSpinBox, QDoubleSpinBox {"
            "    min-height: 54px;"
            "    padding: 0px 16px;"
            "    font-size: 15pt;"
            "    border: 2px solid #e2e8f0;"
            "    border-radius: 12px;"
            "    background-color: #ffffff;"
            "    color: #0f172a;"
            "}"
            "QSpinBox:focus, QDoubleSpinBox:focus { border: 2px solid #3b82f6; }"
        )

    def _combo_style(self) -> str:
        return (
            "QComboBox {"
            "    min-height: 54px;"
            "    padding: 0px 16px;"
            "    font-size: 15pt;"
            "    border: 2px solid #e2e8f0;"
            "    border-radius: 12px;"
            "    background-color: #ffffff;"
            "    color: #0f172a;"
            "}"
            "QComboBox::drop-down { border: none; }"
            "QComboBox:focus { border: 2px solid #3b82f6; }"
        )

    def _primary_button_style(self) -> str:
        return """
        QPushButton#MagusButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
            border: 1px solid #6d28d9;
            color: white;
            border-radius: 12px;
            padding: 10px;
            font-weight: 600;
            font-size: 11pt;
        }
        QPushButton#MagusButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a78bfa, stop:1 #8b5cf6);
            border: 1px solid #7c3aed;
        }
        QPushButton#MagusButton:pressed {
            background: #7c3aed;
            padding-top: 12px;
            padding-left: 12px;
        }
        """

    def _ghost_button_style(self) -> str:
        return (
            "QPushButton {background-color: #e2e8f0; color: #0f172a; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 600;}"
            "QPushButton:hover {background-color: #cbd5e1;}"
        )


class RenderSignals(QObject):
    """Shared signals for async rendering."""
    finished = pyqtSignal(object)  # payload
