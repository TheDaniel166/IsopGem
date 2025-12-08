"""Visualizer for Generalized (Experimental) Star Numbers."""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QSpinBox, QDoubleSpinBox, QCheckBox, QMainWindow, QSizePolicy, QGraphicsView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QColor
from shared.ui import WindowManager
from ..services import (
    generalized_star_number_value,
    generalized_star_number_points,
)
from .geometry_scene import GeometryScene
from .geometry_view import GeometryView
from .geometry_interaction import GeometryInteractionManager, GroupManagementPanel, ConnectionToolBar
from .primitives import Bounds, CirclePrimitive, GeometryScenePayload, LabelPrimitive, PenStyle, BrushStyle


class ExperimentalStarWindow(QMainWindow):
    """Interactive viewer for Generalized Star Numbers (P-grams).
    
    Allows creating stars with any number of points (P >= 3).
    """

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager

        self.scene = GeometryScene()
        self.view = GeometryView(self.scene)

        self.setWindowTitle("Experimental Star Number Visualizer")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet("background-color: #f8fafc;")

        self.points_spin: Optional[QSpinBox] = None
        self.index_spin: Optional[QSpinBox] = None
        self.spacing_spin: Optional[QDoubleSpinBox] = None
        self.labels_toggle: Optional[QCheckBox] = None
        self.grid_toggle: Optional[QCheckBox] = None
        self.axes_toggle: Optional[QCheckBox] = None
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

        self._current_points = [] # Store for connection line lookups

        self._setup_ui()
        self._render()
        
        # Connect view selection signal
        self.view.dots_selected.connect(self._on_dots_selected)

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
    
    def _on_dots_selected(self, indices: list):
        """Handle rubber-band selection of dots."""
        for idx in indices:
            self.interaction_manager.toggle_dot_in_group(idx)

    def _refresh_highlights(self, _=None):
        self._render_interactions()

    def _refresh_connections(self):
        self._render()

    def _on_connection_added(self, conn):
        points = self._current_points
        if not points or conn.start_index > len(points) or conn.end_index > len(points):
            return
        
        p1 = points[conn.start_index - 1]
        p2 = points[conn.end_index - 1]
        qt_pen = QPen(conn.color, conn.width)
        qt_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.scene.add_connection_line(p1, p2, qt_pen)

    def _handle_dot_click(self, index: int, modifiers: Qt.KeyboardModifier, button: Qt.MouseButton):
        if self.interaction_manager.drawing_active and button == Qt.MouseButton.LeftButton:
            self.interaction_manager.process_draw_click(index)
        elif button == Qt.MouseButton.RightButton:
            self.interaction_manager.toggle_dot_in_group(index)

    def _render_interactions(self):
        for name, group in self.interaction_manager.groups.items():
            self.scene.highlight_dots(list(group.indices), group.color)
        
        start = self.interaction_manager.current_draw_start
        if start is not None:
             self.scene.highlight_dots([start], self.interaction_manager.pen_color)

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

        # Interaction Toolbar
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
        frame.setFixedWidth(320)
        frame.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 14px;")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Experimental Star Numbers")
        title.setStyleSheet("color: #0f172a; font-size: 16pt; font-weight: 800;")
        layout.addWidget(title)

        subtitle = QLabel("Create star figures with any number of points (P-grams).")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #475569; font-size: 10.5pt;")
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        # Star Points (P)
        p_label = QLabel("Star Points (P)")
        p_label.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(p_label)

        self.points_spin = QSpinBox()
        self.points_spin.setRange(3, 30)
        self.points_spin.setValue(5) # Default to Pentagram
        self.points_spin.setStyleSheet(self._spin_style())
        self.points_spin.valueChanged.connect(self._render)
        layout.addWidget(self.points_spin)

        # Index (N)
        n_label = QLabel("Index (N)")
        n_label.setStyleSheet("color: #475569; font-weight: 600;")
        layout.addWidget(n_label)

        self.index_spin = QSpinBox()
        self.index_spin.setRange(1, 30)
        self.index_spin.setValue(3)
        self.index_spin.setStyleSheet(self._spin_style())
        self.index_spin.valueChanged.connect(self._render)
        layout.addWidget(self.index_spin)

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

        layout.addSpacing(10)
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #0f172a; font-weight: 700; font-size: 12pt;")
        layout.addWidget(self.count_label)

        self.value_label = QLabel("")
        self.value_label.setStyleSheet("color: #475569; font-size: 10.5pt;")
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)

        # Action button
        render_btn = QPushButton("Render Star")
        render_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        render_btn.setStyleSheet(self._primary_button_style())
        render_btn.clicked.connect(self._render)
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

    def _render(self):
        points_count = self.points_spin.value() if self.points_spin else 5
        index = self.index_spin.value() if self.index_spin else 1
        spacing = self.spacing_spin.value() if self.spacing_spin else 1.0

        value = generalized_star_number_value(points_count, index)
        points = generalized_star_number_points(points_count, index, spacing=spacing)

        self._update_summary(value, points_count)
        payload = self._build_payload(points, points_count, spacing, index)
        self.scene.set_payload(payload)
        self.view.fit_scene()

    def _build_payload(self, points: List[Tuple[float, float]], sides: int, spacing: float, index: int) -> GeometryScenePayload:
        dot_radius = max(0.06, spacing * 0.18)
        pen = PenStyle(color=(147, 51, 234, 255), width=1.2) # Purple for Experimental
        brush = BrushStyle(color=(216, 180, 254, 220), enabled=True)

        primitives: List = []
        labels: List[LabelPrimitive] = []

        # Store points for interaction
        self._current_points = points

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
        return GeometryScenePayload(
            primitives=primitives,
            labels=labels,
            bounds=bounds,
        )

    def _update_summary(self, value: int, points_count: int):
        if self.count_label:
            self.count_label.setText(f"{value} dots")
        if self.value_label:
            name_map = {3: "Triangle", 4: "Square", 5: "Pentagram", 6: "Hexagram", 7: "Heptagram", 8: "Octagram"}
            shape_name = name_map.get(points_count, f"{points_count}-gram")
            self.value_label.setText(f"Shape: {shape_name} Star  •  Total: {value}")
        if self.labels_toggle:
            self.scene.set_labels_visible(self.labels_toggle.isChecked())

    def _toggle_labels(self, state: int):
        self.scene.set_labels_visible(state == 2)

    def _spin_style(self) -> str:
        return (
            "QSpinBox, QDoubleSpinBox {padding: 8px 10px; font-size: 11pt; border: 1px solid #cbd5e1; border-radius: 8px;}"
            "QSpinBox:focus, QDoubleSpinBox:focus {border-color: #9333ea;}"
        )

    def _primary_button_style(self) -> str:
        return (
            "QPushButton {background-color: #9333ea; color: white; border: none; padding: 10px 14px; border-radius: 10px; font-weight: 700;}"
            "QPushButton:hover {background-color: #7e22ce;}"
            "QPushButton:pressed {background-color: #6b21a8;}"
        )

    def _ghost_button_style(self) -> str:
        return (
            "QPushButton {background-color: #e2e8f0; color: #0f172a; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 600;}"
            "QPushButton:hover {background-color: #cbd5e1;}"
        )


def _bounds_from_points(points: List[Tuple[float, float]], margin: float) -> Optional[Bounds]:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Bounds(min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin)


__all__ = ["ExperimentalStarWindow"]
