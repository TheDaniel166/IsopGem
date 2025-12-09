"""3D Figurate Numbers Visualization Window.

Displays tetrahedral, pyramidal, octahedral, and cubic numbers using isometric projection.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QComboBox, QCheckBox, QFrame, QDoubleSpinBox, QGraphicsView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QColor

from ..services.figurate_3d import (
    tetrahedral_number, tetrahedral_points,
    square_pyramidal_number, square_pyramidal_points,
    octahedral_number, octahedral_points,
    cubic_number, cubic_points,
    centered_cubic_number, centered_cubic_points,
    stellated_octahedron_number, stellated_octahedron_points,
    icosahedral_number, icosahedral_points,
    dodecahedral_number, dodecahedral_points,
    project_points_isometric, get_layer_for_point, project_dynamic
)
from .geometry_scene import GeometryScene, GeometryScenePayload
from .geometry_view import GeometryView
from .primitives import CirclePrimitive, LabelPrimitive, Bounds, PenStyle, BrushStyle
from .geometry_interaction import GeometryInteractionManager, GroupManagementPanel, ConnectionToolBar


# Layer color palette (for z-depth visualization)
LAYER_COLORS = [
    (59, 130, 246),   # Blue
    (34, 197, 94),    # Green
    (249, 115, 22),   # Orange
    (168, 85, 247),   # Purple
    (236, 72, 153),   # Pink
    (20, 184, 166),   # Teal
    (245, 158, 11),   # Amber
    (99, 102, 241),   # Indigo
]


def _bounds_from_points(points: List[Tuple[float, float]], margin: float = 0.5) -> Bounds:
    if not points:
        return Bounds(-5, -5, 10, 10)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Bounds(
        min_x=min(xs) - margin,
        max_x=max(xs) + margin,
        min_y=min(ys) - margin,
        max_y=max(ys) + margin
    )


class Figurate3DWindow(QWidget):
    """Window for visualizing 3D figurate numbers."""

    SHAPE_TYPES = [
        ("Tetrahedral", "tetrahedral"),
        ("Square Pyramidal", "pyramidal"),
        ("Octahedral", "octahedral"),
        ("Cubic", "cubic"),
        ("Centered Cubic", "centered_cubic"),
        ("Stellated Octahedron", "stellated_octahedron"),
        ("Centered Icosahedral", "icosahedral"),
        ("Centered Dodecahedral", "dodecahedral"),
    ]

    def __init__(self, window_manager=None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("3D Figurate Numbers")
        self.setMinimumSize(900, 700)

        # Scene and view
        self.scene = GeometryScene()
        self.scene.grid_visible = False
        self.scene.axes_visible = False
        self.view = GeometryView(self.scene, self)

        # State
        self._current_points_3d: List[Tuple[float, float, float]] = []
        self._current_points_2d: List[Tuple[float, float]] = []
        self._refreshing: bool = False
        
        # Camera State
        self.camera_yaw: float = 45.0
        self.camera_pitch: float = 35.264  # Standard isometric pitch
        self._last_mouse_pos: Optional[QPoint] = None
        self._rotating: bool = False
        
        # Interaction Manager
        self.interaction_manager = GeometryInteractionManager(self)

        # Widgets
        self.shape_combo: Optional[QComboBox] = None
        self.index_spin: Optional[QSpinBox] = None
        self.spacing_spin: Optional[QDoubleSpinBox] = None
        self.labels_toggle: Optional[QCheckBox] = None
        self.layer_colors_toggle: Optional[QCheckBox] = None
        self.count_label: Optional[QLabel] = None
        self.value_label: Optional[QLabel] = None

        # Interaction
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
        
        # Install event filter for 3D rotation
        self.view.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if source is self.view.viewport():
            if event.type() == event.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.RightButton:
                    self._rotating = True
                    self._last_mouse_pos = event.pos()
                    self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
                    return True  # Consume event
            elif event.type() == event.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.RightButton:
                    self._rotating = False
                    self._last_mouse_pos = None
                    self.view.setCursor(Qt.CursorShape.ArrowCursor)
                    return True
            elif event.type() == event.Type.MouseMove:
                if self._rotating and self._last_mouse_pos:
                    delta = event.pos() - self._last_mouse_pos
                    self._last_mouse_pos = event.pos()
                    
                    # Update angles
                    self.camera_yaw += delta.x() * 0.5
                    self.camera_pitch += delta.y() * 0.5
                    self.camera_pitch = max(-90.0, min(90.0, self.camera_pitch))
                    
                    self._update_positions()
                    return True

        return super().eventFilter(source, event)

    def _update_positions(self):
        """Re-project 3D points using current camera angles and update scene."""
        if not self._current_points_3d:
            return
            
        # Project using current angles
        self._current_points_2d = project_dynamic(
            self._current_points_3d, self.camera_yaw, self.camera_pitch
        )
        
        # We need to rebuild the payload efficiently or just update positions?
        # Rebuilding is safer to ensure Z-order is correct (if we sorted by depth)
        
        shape_type = self.SHAPE_TYPES[self.shape_combo.currentIndex()][1] if self.shape_combo else "tetrahedral"
        spacing = self.spacing_spin.value() if self.spacing_spin else 1.0
        use_layer_colors = self.layer_colors_toggle.isChecked() if self.layer_colors_toggle else True
        
        payload = self._build_payload(
            self._current_points_3d, 
            self._current_points_2d,
            spacing,
            use_layer_colors
        )
        self.scene.set_payload(payload)
        self._refresh_highlights()

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
        """Handle rubber-band selection - batch add to avoid signal spam."""
        self._refreshing = True
        try:
            for idx in indices:
                self.interaction_manager.toggle_dot_in_group(idx)
        finally:
            self._refreshing = False
        self._refresh_highlights()

    def _refresh_highlights(self, _=None):
        # Disconnect signals to prevent recursion
        try:
            self.interaction_manager.groups_changed.disconnect(self._refresh_highlights)
        except TypeError:
            pass
        try:
            self.interaction_manager.draw_start_changed.disconnect(self._refresh_highlights)
        except TypeError:
            pass

        try:
            self._render_interactions()
        finally:
            self.interaction_manager.groups_changed.connect(self._refresh_highlights)
            self.interaction_manager.draw_start_changed.connect(self._refresh_highlights)

    def _refresh_connections(self):
        self._render()

    def _on_connection_added(self, conn):
        points = self._current_points_2d
        if not points or conn.start_index > len(points) or conn.end_index > len(points):
            return
        
        p1 = points[conn.start_index - 1]
        p2 = points[conn.end_index - 1]
        qt_pen = QPen(conn.color, conn.width)
        qt_pen.setCosmetic(True)
        self.scene.add_connection_line(p1, p2, qt_pen)

    def _handle_dot_click(self, index: int, modifiers, button):
        print(f"[DEBUG] 3D Window: Dot clicked: {index}, Button: {button}, DrawMode: {self.interaction_manager.drawing_active}")
        
        if button == Qt.MouseButton.RightButton:
            print(f"[DEBUG] 3D Window: Toggling group membership for {index}")
            self.interaction_manager.toggle_dot_in_group(index)
            self._refresh_highlights()
            return
        
        if button == Qt.MouseButton.LeftButton and self.interaction_manager.drawing_active:
            conn = self.interaction_manager.process_draw_click(index)
            if conn:
                self._on_connection_added(conn)
            self._refresh_highlights()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left: Controls
        controls = QFrame()
        controls.setFixedWidth(240)
        controls.setStyleSheet("background-color: #f8fafc; border-right: 1px solid #e2e8f0;")
        ctrl_layout = QVBoxLayout(controls)
        ctrl_layout.setContentsMargins(16, 16, 16, 16)
        ctrl_layout.setSpacing(8)

        # Title
        title = QLabel("3D Figurate Numbers")
        title.setStyleSheet("font-size: 14pt; font-weight: 700; color: #0f172a;")
        ctrl_layout.addWidget(title)
        ctrl_layout.addSpacing(8)

        # Shape selector
        shape_label = QLabel("Shape Type")
        shape_label.setStyleSheet("color: #475569; font-weight: 600;")
        ctrl_layout.addWidget(shape_label)

        self.shape_combo = QComboBox()
        for display_name, _ in self.SHAPE_TYPES:
            self.shape_combo.addItem(display_name)
        self.shape_combo.setStyleSheet(self._combo_style())
        self.shape_combo.currentIndexChanged.connect(self._render)
        ctrl_layout.addWidget(self.shape_combo)

        ctrl_layout.addSpacing(6)

        # Index
        index_label = QLabel("Index (n)")
        index_label.setStyleSheet("color: #475569; font-weight: 600;")
        ctrl_layout.addWidget(index_label)

        self.index_spin = QSpinBox()
        self.index_spin.setRange(1, 10)
        self.index_spin.setValue(4)
        self.index_spin.setStyleSheet(self._spin_style())
        self.index_spin.valueChanged.connect(self._render)
        ctrl_layout.addWidget(self.index_spin)

        ctrl_layout.addSpacing(6)

        # Spacing
        spacing_label = QLabel("Dot spacing")
        spacing_label.setStyleSheet("color: #475569; font-weight: 600;")
        ctrl_layout.addWidget(spacing_label)

        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.5, 3.0)
        self.spacing_spin.setSingleStep(0.1)
        self.spacing_spin.setValue(1.0)
        self.spacing_spin.setDecimals(2)
        self.spacing_spin.setStyleSheet(self._spin_style())
        self.spacing_spin.valueChanged.connect(self._render)
        ctrl_layout.addWidget(self.spacing_spin)

        ctrl_layout.addSpacing(6)

        # Toggles
        self.labels_toggle = QCheckBox("Show numbered labels")
        self.labels_toggle.setChecked(True)
        self.labels_toggle.stateChanged.connect(self._toggle_labels)
        ctrl_layout.addWidget(self.labels_toggle)

        self.layer_colors_toggle = QCheckBox("Color by layer (depth)")
        self.layer_colors_toggle.setChecked(True)
        self.layer_colors_toggle.stateChanged.connect(self._render)
        ctrl_layout.addWidget(self.layer_colors_toggle)

        # Summary
        ctrl_layout.addSpacing(10)
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #0f172a; font-weight: 700; font-size: 12pt;")
        ctrl_layout.addWidget(self.count_label)

        self.value_label = QLabel("")
        self.value_label.setStyleSheet("color: #475569; font-size: 10pt;")
        ctrl_layout.addWidget(self.value_label)

        ctrl_layout.addStretch()
        main_layout.addWidget(controls)

        # Center: Viewport with toolbar
        viewport_frame = QFrame()
        viewport_layout = QVBoxLayout(viewport_frame)
        viewport_layout.setContentsMargins(0, 0, 0, 0)
        viewport_layout.setSpacing(0)

        # Toolbar
        self.conn_bar = ConnectionToolBar(self.interaction_manager, self)
        self.conn_bar.dot_color_changed.connect(self.scene.set_dot_color)
        self.conn_bar.text_color_changed.connect(self.scene.set_text_color)
        viewport_layout.addWidget(self.conn_bar)
        viewport_layout.addWidget(self.view)
        main_layout.addWidget(viewport_frame)

        # Right: Group panel
        right_panel = QWidget()
        right_panel.setFixedWidth(200)
        right_panel.setStyleSheet("background-color: #f8fafc; border-left: 1px solid #e2e8f0;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)

        self.group_panel = GroupManagementPanel(self.interaction_manager, self)
        right_layout.addWidget(self.group_panel)
        right_layout.addStretch()

        main_layout.addWidget(right_panel)

    def _render(self, _=None):
        # Clear interaction state without triggering re-render
        self.interaction_manager.blockSignals(True)
        self.interaction_manager.clear()
        self.interaction_manager.blockSignals(False)
        
        shape_type = self.SHAPE_TYPES[self.shape_combo.currentIndex()][1] if self.shape_combo else "tetrahedral"
        n = self.index_spin.value() if self.index_spin else 4
        spacing = self.spacing_spin.value() if self.spacing_spin else 1.0
        use_layer_colors = self.layer_colors_toggle.isChecked() if self.layer_colors_toggle else True

        # Generate 3D points
        if shape_type == "tetrahedral":
            self._current_points_3d = tetrahedral_points(n, spacing)
            value = tetrahedral_number(n)
        elif shape_type == "pyramidal":
            self._current_points_3d = square_pyramidal_points(n, spacing)
            value = square_pyramidal_number(n)
        elif shape_type == "octahedral":
            self._current_points_3d = octahedral_points(n, spacing)
            value = octahedral_number(n)
        elif shape_type == "cubic":
            self._current_points_3d = cubic_points(n, spacing)
            value = cubic_number(n)
        elif shape_type == "centered_cubic":
            self._current_points_3d = centered_cubic_points(n, spacing)
            value = centered_cubic_number(n)
        elif shape_type == "stellated_octahedron":
            self._current_points_3d = stellated_octahedron_points(n, spacing)
            value = stellated_octahedron_number(n)
        elif shape_type == "icosahedral":
            self._current_points_3d = icosahedral_points(n, spacing)
            value = icosahedral_number(n)
        elif shape_type == "dodecahedral":
            self._current_points_3d = dodecahedral_points(n, spacing)
            value = dodecahedral_number(n)
        else:
            self._current_points_3d = []
            value = 0

        # Project to 2D
        self._current_points_2d = project_dynamic(
            self._current_points_3d, self.camera_yaw, self.camera_pitch
        )

        # Build payload
        payload = self._build_payload(
            self._current_points_3d,
            self._current_points_2d,
            spacing,
            use_layer_colors
        )
        self.scene.set_payload(payload)
        self.view.fit_scene()

        # Update summary
        self._update_summary(value, len(self._current_points_2d), shape_type)

        if self.labels_toggle:
            self.scene.set_labels_visible(self.labels_toggle.isChecked())

    def _build_payload(
        self,
        points_3d: List[Tuple[float, float, float]],
        points_2d: List[Tuple[float, float]],
        spacing: float,
        use_layer_colors: bool
    ) -> GeometryScenePayload:
        dot_radius = max(0.08, spacing * 0.15)
        
        primitives = []
        labels = []

        # Determine z-range for layer coloring
        if points_3d:
            z_values = sorted(set(round(p[2] / spacing) for p in points_3d))
            z_to_layer = {z: i for i, z in enumerate(z_values)}
        else:
            z_to_layer = {}

        for idx, ((x2d, y2d), (x3d, y3d, z3d)) in enumerate(zip(points_2d, points_3d), start=1):
            layer_idx = z_to_layer.get(round(z3d / spacing), 0)
            
            if use_layer_colors:
                color = LAYER_COLORS[layer_idx % len(LAYER_COLORS)]
                pen = PenStyle(color=(*color, 255), width=1.2)
                brush = BrushStyle(color=(*color, 180), enabled=True)
            else:
                pen = PenStyle(color=(59, 130, 246, 255), width=1.2)
                brush = BrushStyle(color=(191, 219, 254, 220), enabled=True)

            primitives.append(CirclePrimitive(
                center=(x2d, y2d),
                radius=dot_radius,
                pen=pen,
                brush=brush,
                metadata={"index": idx, "style": "sphere"}
            ))
            labels.append(LabelPrimitive(
                text=str(idx),
                position=(x2d, y2d),
                align_center=True,
                metadata={"index": idx}
            ))

        bounds = _bounds_from_points(points_2d, margin=dot_radius * 3)
        return GeometryScenePayload(primitives=primitives, labels=labels, bounds=bounds)

    def _update_summary(self, value: int, count: int, shape_type: str):
        if self.count_label:
            self.count_label.setText(f"{count} dots")
        if self.value_label:
            names = {
                "tetrahedral": "Tetrahedral",
                "pyramidal": "Square Pyramidal",
                "octahedral": "Octahedral",
                "cubic": "Cubic",
                "centered_cubic": "Centered Cubic",
                "stellated_octahedron": "Stellated Octahedron",
                "icosahedral": "Centered Icosahedral",
                "dodecahedral": "Centered Dodecahedral"
            }
            self.value_label.setText(f"{names.get(shape_type, 'Figurate')} Number: {value}")

    def _toggle_labels(self, state: int):
        self.scene.set_labels_visible(state == 2)

    def _render_interactions(self):
        """Update highlight colors for groups without full re-render."""
        for name, group in self.interaction_manager.groups.items():
            self.scene.highlight_dots(list(group.indices), group.color)
        
        # Highlight active draw start
        start = self.interaction_manager.current_draw_start
        if start is not None:
            self.scene.highlight_dots([start], self.interaction_manager.pen_color)

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


__all__ = ["Figurate3DWindow"]
