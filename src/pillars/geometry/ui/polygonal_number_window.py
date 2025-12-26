"""Visualizer for polygonal and centered polygonal numbers."""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QGraphicsView,
)
from PyQt6.QtCore import Qt, QTimer, QThreadPool, QRunnable, QObject, pyqtSignal
from PyQt6.QtGui import QPen, QColor
from shared.ui import WindowManager
from ..services import (
    centered_polygonal_value,
    max_radius,
    polygonal_number_points,
    polygonal_number_value,
    polygonal_outline_points,
    star_number_points,
    star_number_value,
)
from .geometry_scene import GeometryScene
from .geometry_view import GeometryView
from .geometry_interaction import GeometryInteractionManager, GroupManagementPanel, ConnectionToolBar
from .primitives import Bounds, CirclePrimitive, GeometryScenePayload, LabelPrimitive, PenStyle, BrushStyle, PolygonPrimitive


Color = Tuple[int, int, int, int]


class PolygonalNumberWindow(QMainWindow):
    """Interactive viewer for figurate numbers built from dots."""

    HEAVY_THRESHOLD = 2000  # dot count above which we offload rendering to a worker

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager

        self.scene = GeometryScene()
        self.view = GeometryView(self.scene)
        self.thread_pool = QThreadPool.globalInstance()
        self._rendering = False
        self._controls_frame: Optional[QFrame] = None
        self._render_button: Optional[QPushButton] = None

        self.setWindowTitle("Polygonal Number Visualizer")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet("background-color: #f8fafc;")

        self.sides_spin: Optional[QSpinBox] = None
        self.index_spin: Optional[QSpinBox] = None
        self.spacing_spin: Optional[QDoubleSpinBox] = None
        self.mode_combo: Optional[QComboBox] = None
        self.labels_toggle: Optional[QCheckBox] = None
        self.count_label: Optional[QLabel] = None
        self.value_label: Optional[QLabel] = None

        # Interaction
        self.interaction_manager = GeometryInteractionManager(self)
        self.interaction_manager.groups_changed.connect(self._refresh_highlights)
        self.interaction_manager.connection_added.connect(self._on_connection_added)
        self.interaction_manager.connections_cleared.connect(self._refresh_connections)
        self.interaction_manager.mode_changed.connect(self._update_view_mode)
        self.interaction_manager.draw_start_changed.connect(self._refresh_highlights)
        self.scene.dot_clicked.connect(self._handle_dot_click)

        self._setup_ui()
        self._render()
        
        # Connect view selection signal
        self.view.dots_selected.connect(self._on_dots_selected)

    def _update_view_mode(self, mode: str):
        if mode == "draw":
            print(f"[DEBUG] Window: Switching View to NoDrag (Draw Mode)")
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.view.setCursor(Qt.CursorShape.CrossCursor)
            self.view.set_selection_mode(False)
        elif mode == "select":
            print(f"[DEBUG] Window: Switching View to Selection Mode")
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.view.set_selection_mode(True)
        else:
            print(f"[DEBUG] Window: Switching View to ScrollHandDrag (View Mode)")
            self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
            self.view.set_selection_mode(False)
    
    def _on_dots_selected(self, indices: list):
        """Handle rubber-band selection of dots."""
        print(f"[DEBUG] Window: Rectangle selected dots: {indices}")
        for idx in indices:
            self.interaction_manager.toggle_dot_in_group(idx)

    def _refresh_highlights(self, _=None):
        # Clear existing highlights first? No, scene.highlight_dots overwrites brush.
        # But we need to reset all dots to default first ideally, OR just update the ones in groups.
        # Actually, render loop resets generic brush.
        # But if we just update groups, we might need to "un-highlight" removed ones.
        # Easiest: Re-render connections and highlights on top of existing payload without full re-calc?
        # Or just iterate all dots and reset brush if not in group?
        # For MVP: Iterate groups and apply highlight. Dots not in groups stay default (blue-ish).
        # To handle removal properly, we should probably reset brushes.
        # Let's rely on _render_interactions() helper maybe?
        self._render_interactions()

    def _refresh_connections(self):
        # scene.clear_temporary_items() # Does not clear lines
        # We need to clear lines added by add_connection_line.
        # Since we don't track them easily in scene, we might need to re-render the whole scene
        # which clears everything, then re-apply interactions.
        self._render()

    def _on_connection_added(self, conn):
        points = self._current_points # Need to store points from last render
        if not points or conn.start_index > len(points) or conn.end_index > len(points):
            print(f"[DEBUG] Window: Connection indices out of bounds: {conn.start_index}->{conn.end_index} vs {len(points) if points else 0}")
            return
        
        # indices are 1-based in manager logic (from render loop)
        p1 = points[conn.start_index - 1]
        p2 = points[conn.end_index - 1]
        
        qt_pen = QPen(conn.color, conn.width)
        qt_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        print(f"[DEBUG] Window: Adding connection line graphic.")
        self.scene.add_connection_line(p1, p2, qt_pen)

    def _handle_dot_click(self, index: int, modifiers: Qt.KeyboardModifier, button: Qt.MouseButton):
        is_drawing = self.interaction_manager.drawing_active
        print(f"[DEBUG] Window: Dot clicked: {index}, Modifiers: {modifiers}, Button: {button}, DrawMode: {is_drawing}")
        
        if is_drawing and button == Qt.MouseButton.LeftButton:
            # Drawing logic (Left Click only)
            self.interaction_manager.process_draw_click(index)
        
        # Grouping: Relaxed to allow ANY Right Click for better usability/testing
        elif button == Qt.MouseButton.RightButton:
             # Grouping logic
            print(f"[DEBUG] Window: Toggling group membership for {index} (Right Click detected)")
            self.interaction_manager.toggle_dot_in_group(index)

    def _render_interactions(self):
        # Re-apply group highlights
        for name, group in self.interaction_manager.groups.items():
            self.scene.highlight_dots(list(group.indices), group.color)
            
        # Highlight current drawing start dot
        start = self.interaction_manager.current_draw_start
        if start is not None:
             # Use a distinct color for the active start dot (e.g., Red or complementary to pen)
             # Pen color is manager.pen_color. Let's match it or make it distinct.
             # Actually, let's use the pen color but lighter/darker?
             # manager.pen_color is default Red.
             active_color = self.interaction_manager.pen_color
             self.scene.highlight_dots([start], active_color)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        controls = self._build_controls()
        layout.addWidget(controls)

        viewport_frame = QFrame()
        viewport_frame.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 14px;")
        viewport_layout = QVBoxLayout(viewport_frame)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        viewport_layout.setSpacing(0)

        # Connection Toolbar
        conn_bar = ConnectionToolBar(self.interaction_manager)
        conn_bar.dot_color_changed.connect(self.scene.set_dot_color)
        conn_bar.text_color_changed.connect(self.scene.set_text_color)
        viewport_layout.addWidget(conn_bar)

        toolbar = self._build_view_toolbar()
        viewport_layout.addWidget(toolbar)
        viewport_layout.addWidget(self.view, 1)

        layout.addWidget(viewport_frame, 1)

        # Right sidebar for groups
        group_panel = GroupManagementPanel(self.interaction_manager)
        group_panel.setFixedWidth(260)
        layout.addWidget(group_panel)



    def _build_controls(self) -> QWidget:
        frame = QFrame()
        self._controls_frame = frame
        frame.setFixedWidth(320)
        frame.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 14px;")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Polygonal / Centered Visualizer")
        title.setStyleSheet("color: #0f172a; font-size: 16pt; font-weight: 800;")
        layout.addWidget(title)

        subtitle = QLabel("Pick a polygon, choose the index, and see the dot construction with numbers.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #475569; font-size: 10.5pt;")
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        # Polygon sides
        sides_label = QLabel("Polygon sides (n)")
        sides_label.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(sides_label)

        self.sides_spin = QSpinBox()
        self.sides_spin.setRange(3, 20)
        self.sides_spin.setValue(5)
        self.sides_spin.setStyleSheet(self._spin_style())
        self.sides_spin.valueChanged.connect(self._render)
        layout.addWidget(self.sides_spin)

        # Index
        index_label = QLabel("Index k")
        index_label.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(index_label)

        self.index_spin = QSpinBox()
        self.index_spin.setRange(1, 30)
        self.index_spin.setValue(5)
        self.index_spin.setStyleSheet(self._spin_style())
        self.index_spin.valueChanged.connect(self._render)
        layout.addWidget(self.index_spin)

        # Mode
        mode_label = QLabel("Number family")
        mode_label.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Polygonal (gnomon growth)", userData="polygonal")
        self.mode_combo.addItem("Centered polygonal", userData="centered")
        self.mode_combo.addItem("Star number (hexagram)", userData="star")
        self.mode_combo.setStyleSheet(self._combo_style())
        self.mode_combo.currentIndexChanged.connect(self._render)
        layout.addWidget(self.mode_combo)

        # Spacing
        spacing_label = QLabel("Dot spacing")
        spacing_label.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(spacing_label)

        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.2, 5.0)
        self.spacing_spin.setSingleStep(0.1)
        self.spacing_spin.setValue(1.0)
        self.spacing_spin.setDecimals(2)
        self.spacing_spin.setStyleSheet(self._spin_style())
        self.spacing_spin.valueChanged.connect(self._render)
        layout.addWidget(self.spacing_spin)

        layout.addSpacing(6)

        # Toggles
        self.labels_toggle = QCheckBox("Show numbered labels")
        self.labels_toggle.setChecked(True)
        self.labels_toggle.stateChanged.connect(self._toggle_labels)
        layout.addWidget(self.labels_toggle)

        # Summary labels
        layout.addSpacing(10)
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #0f172a; font-weight: 700; font-size: 12pt;")
        layout.addWidget(self.count_label)

        self.value_label = QLabel("")
        self.value_label.setStyleSheet("color: #475569; font-size: 10.5pt;")
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)

        # Action button
        render_btn = QPushButton("Render pattern")
        render_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        render_btn.setStyleSheet(self._primary_button_style())
        render_btn.clicked.connect(self._render)
        self._render_button = render_btn
        layout.addWidget(render_btn)

        layout.addStretch(1)
        return frame

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
    # Rendering
    # ------------------------------------------------------------------
    def _render(self):
        sides = self.sides_spin.value() if self.sides_spin else 3
        index = self.index_spin.value() if self.index_spin else 1
        spacing = self.spacing_spin.value() if self.spacing_spin else 1.0
        
        mode = self.mode_combo.currentData() if self.mode_combo else "polygonal"
        centered = (mode == "centered")
        is_star = (mode == "star")

        # Disable/Enable sides spin for star mode (fixed to 6/hexagram)
        if self.sides_spin:
            self.sides_spin.setEnabled(not is_star)

        if is_star:
            value = star_number_value(index)
        else:
            value = centered_polygonal_value(sides, index) if centered else polygonal_number_value(sides, index)

        # Offload heavy renders to a worker to keep the UI responsive.
        if value >= self.HEAVY_THRESHOLD:
            self._start_async_render(sides, index, spacing, mode)
            return

        points = star_number_points(index, spacing=spacing) if is_star else polygonal_number_points(sides, index, spacing=spacing, centered=centered)
        payload = self._build_payload_static(points, sides, spacing, index, centered or is_star)
        self._apply_render_result(payload, points, value, mode, None)

    def _start_async_render(self, sides: int, index: int, spacing: float, mode: str):
        if self._rendering:
            return
        self._set_busy(True)
        worker = _FigurateRenderRunnable(sides, index, spacing, mode)
        worker.signals.finished.connect(self._on_async_finished)
        self.thread_pool.start(worker)

    def _on_async_finished(self, payload_points_value_mode_error):
        payload, points, value, mode, error = payload_points_value_mode_error
        self._apply_render_result(payload, points, value, mode, error)
        self._set_busy(False)

    def _apply_render_result(self, payload: GeometryScenePayload, points: List[Tuple[float, float]], value: int, mode: str, error: Optional[str]):
        if error:
            if self.value_label:
                self.value_label.setText(f"Error: {error}")
            return

        self._current_points = points
        self._update_summary(value, mode)
        self.scene.set_payload(payload)
        self.view.fit_scene()

    def _set_busy(self, busy: bool):
        self._rendering = busy
        self.setCursor(Qt.CursorShape.BusyCursor if busy else Qt.CursorShape.ArrowCursor)
        if self._controls_frame:
            self._controls_frame.setDisabled(busy)
        if self._render_button:
            self._render_button.setText("Rendering..." if busy else "Render pattern")
            self._render_button.setDisabled(busy)

    @staticmethod
    def _build_payload_static(points: List[Tuple[float, float]], sides: int, spacing: float, index: int, centered: bool) -> GeometryScenePayload:
        dot_radius = max(0.06, spacing * 0.18)
        pen = PenStyle(color=(37, 99, 235, 255), width=1.2)
        brush = BrushStyle(color=(191, 219, 254, 220), enabled=True)

        primitives: List = []
        labels: List[LabelPrimitive] = []

        if points:
            max_r = max(math.hypot(x, y) for x, y in points)
        else:
            max_r = spacing

        # Outline removed as per user request

        for idx, (x, y) in enumerate(points, start=1):
            primitives.append(CirclePrimitive(
                center=(x, y), 
                radius=dot_radius, 
                pen=pen, 
                brush=brush,
                metadata={"index": idx}
            ))
            # Always include labels in payload - scene controls visibility
            labels.append(LabelPrimitive(text=str(idx), position=(x, y), align_center=True, metadata={"index": idx}))

        bounds = _bounds_from_points(points, margin=dot_radius * 3)
        payload = GeometryScenePayload(
            primitives=primitives,
            labels=labels,
            bounds=bounds,
        )
        payload.suggest_grid_span = max(bounds.width, bounds.height) * 1.2 if bounds else None
        return payload

    def _update_summary(self, value: int, mode: str):
        if self.count_label:
            self.count_label.setText(f"{value} dots")
        if self.value_label:
            family_map = {
                "polygonal": "Polygonal",
                "centered": "Centered",
                "star": "Star Number"
            }
            family = family_map.get(mode, "Polygonal")
            self.value_label.setText(f"Family: {family}  •  Total: {value}")

        if self.labels_toggle:
            self.scene.set_labels_visible(self.labels_toggle.isChecked())

    def _toggle_labels(self, state: int):
        self.scene.set_labels_visible(state == 2)

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------
    def _spin_style(self) -> str:
        return (
            "QSpinBox, QDoubleSpinBox {padding: 8px 10px; font-size: 11pt; border: 1px solid #cbd5e1; border-radius: 8px;}"
            "QSpinBox:focus, QDoubleSpinBox:focus {border-color: #3b82f6;}"
        )

    def _combo_style(self) -> str:
        return (
            "QComboBox {padding: 8px 10px; font-size: 11pt; border: 1px solid #cbd5e1; border-radius: 8px;}"
            "QComboBox:focus {border-color: #3b82f6;}"
        )

    def _primary_button_style(self) -> str:
        return (
            "QPushButton {background-color: #2563eb; color: white; border: none; padding: 10px 14px; border-radius: 10px; font-weight: 700;}"
            "QPushButton:hover {background-color: #1d4ed8;}"
            "QPushButton:pressed {background-color: #1e3a8a;}"
        )

    def _ghost_button_style(self) -> str:
        return (
            "QPushButton {background-color: #e2e8f0; color: #0f172a; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 600;}"
            "QPushButton:hover {background-color: #cbd5e1;}"
        )


    # ----------------------------------------------------------------------
    # Async rendering helpers
    # ----------------------------------------------------------------------


    class _RenderSignals(QObject):
        finished = pyqtSignal(object)  # (payload, points, value, mode, error)


    class _FigurateRenderRunnable(QRunnable):
        def __init__(self, sides: int, index: int, spacing: float, mode: str):
            super().__init__()
            self.sides = sides
            self.index = index
            self.spacing = spacing
            self.mode = mode
            self.signals = _RenderSignals()

        def run(self):  # pragma: no cover - background thread
            try:
                is_star = self.mode == "star"
                centered = self.mode == "centered"
                if is_star:
                    value = star_number_value(self.index)
                    points = star_number_points(self.index, spacing=self.spacing)
                else:
                    value = centered_polygonal_value(self.sides, self.index) if centered else polygonal_number_value(self.sides, self.index)
                    points = polygonal_number_points(self.sides, self.index, spacing=self.spacing, centered=centered)

                payload = PolygonalNumberWindow._build_payload_static(points, self.sides, self.spacing, self.index, centered or is_star)
                self.signals.finished.emit((payload, points, value, self.mode, None))
            except Exception as exc:  # pragma: no cover - defensive
                self.signals.finished.emit((None, [], 0, self.mode, str(exc)))


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _regular_polygon_points(sides: int, radius: float, rotation: float = -math.pi / 2) -> List[Tuple[float, float]]:
    sides = max(3, int(sides))
    radius = max(0.1, float(radius))
    angle_step = (2 * math.pi) / sides
    return [
        (radius * math.cos(rotation + i * angle_step), radius * math.sin(rotation + i * angle_step))
        for i in range(sides)
    ]


def _bounds_from_points(points: List[Tuple[float, float]], margin: float) -> Optional[Bounds]:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Bounds(min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin)


__all__ = ["PolygonalNumberWindow"]
