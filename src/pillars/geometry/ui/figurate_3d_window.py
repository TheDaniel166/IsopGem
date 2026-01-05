"""3D Figurate Numbers Visualization Window.

Displays tetrahedral, pyramidal, octahedral, and cubic numbers using isometric projection.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFrame, QLabel, QSpinBox, 
    QVBoxLayout, QWidget, QGraphicsView
)
from PyQt6.QtCore import Qt
from shared.ui import WindowManager
from ..services.figurate_3d import (
    tetrahedral_number, tetrahedral_points,
    square_pyramidal_number, square_pyramidal_points,
    octahedral_number, octahedral_points,
    cubic_number, cubic_points,
    centered_cubic_number, centered_cubic_points,
    stellated_octahedron_number, stellated_octahedron_points,
    icosahedral_number, icosahedral_points,
    dodecahedral_number, dodecahedral_points,
    project_dynamic
)
from .base_figurate_window import BaseFigurateWindow
from .geometry_scene import GeometryScenePayload
from .primitives import CirclePrimitive, LabelPrimitive, Bounds, PenStyle, BrushStyle


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


class Figurate3DWindow(BaseFigurateWindow):
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

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(window_manager, parent)
        self.setWindowTitle("3D Figurate Numbers")
        self.setMinimumSize(900, 700)

        # State specific to 3D
        self._current_points_3d: List[Tuple[float, float, float]] = []
        self._current_points_2d: List[Tuple[float, float]] = []
        self._current_points = [] # Alias for base class
        
        # Camera State
        self.camera_yaw: float = 45.0
        self.camera_pitch: float = 35.264
        self._last_mouse_pos = None
        self._rotating: bool = False
        
        # Controls
        self.shape_combo: Optional[QComboBox] = None
        self.index_spin: Optional[QSpinBox] = None
        self.spacing_spin: Optional[QDoubleSpinBox] = None
        self.labels_toggle: Optional[QCheckBox] = None
        self.layer_colors_toggle: Optional[QCheckBox] = None
        self.count_label: Optional[QLabel] = None
        self.value_label: Optional[QLabel] = None

        self._setup_ui()
        self._render()
        
        # Install event filter for 3D rotation on the viewport
        self.view.viewport().installEventFilter(self)

    def _setup_ui(self):
        controls = self._build_controls()
        self._setup_ui_skeleton(controls)

    def _build_controls(self) -> QWidget:
        controls = QFrame()
        controls.setObjectName("FloatingPanel")
        controls.setFixedWidth(280)
        controls.setStyleSheet("""
            QFrame#FloatingPanel {
                background-color: #f1f5f9; 
                border-right: 1px solid #cbd5e1;
                border-top-right-radius: 24px;
                border-bottom-right-radius: 24px;
            }
        """)
        ctrl_layout = QVBoxLayout(controls)
        ctrl_layout.setContentsMargins(24, 32, 24, 32)
        ctrl_layout.setSpacing(16)

        # Title
        title = QLabel("Figurate 3D")
        title.setStyleSheet("font-family: 'Inter'; font-size: 22pt; font-weight: 800; color: #0f172a;")
        ctrl_layout.addWidget(title)
        ctrl_layout.addSpacing(16)

        # Shape selector
        shape_label = QLabel("Shape Manifestation")
        shape_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        ctrl_layout.addWidget(shape_label)

        self.shape_combo = QComboBox()
        for display_name, _ in self.SHAPE_TYPES:
            self.shape_combo.addItem(display_name)
        self.shape_combo.setStyleSheet(self._combo_style())
        self.shape_combo.currentIndexChanged.connect(self._render)
        ctrl_layout.addWidget(self.shape_combo)

        ctrl_layout.addSpacing(8)

        # Index
        index_label = QLabel("Iteration (n)")
        index_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        ctrl_layout.addWidget(index_label)

        self.index_spin = QSpinBox()
        self.index_spin.setRange(1, 10)
        self.index_spin.setValue(4)
        self.index_spin.setStyleSheet(self._spin_style())
        self.index_spin.valueChanged.connect(self._render)
        ctrl_layout.addWidget(self.index_spin)

        ctrl_layout.addSpacing(8)

        # Spacing
        spacing_label = QLabel("Grid Lattice")
        spacing_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        ctrl_layout.addWidget(spacing_label)

        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.5, 3.0)
        self.spacing_spin.setSingleStep(0.1)
        self.spacing_spin.setValue(1.0)
        self.spacing_spin.setDecimals(2)
        self.spacing_spin.setStyleSheet(self._spin_style())
        self.spacing_spin.valueChanged.connect(self._render)
        ctrl_layout.addWidget(self.spacing_spin)

        # Toggles
        ctrl_layout.addSpacing(16)
        
        self.labels_toggle = QCheckBox("Show Sigils (Labels)")
        self.labels_toggle.setStyleSheet("QCheckBox { color: #334155; font-size: 11pt; }")
        self.labels_toggle.setChecked(True)
        self.labels_toggle.stateChanged.connect(self._toggle_labels)
        ctrl_layout.addWidget(self.labels_toggle)

        self.layer_colors_toggle = QCheckBox("Depth Spectra")
        self.layer_colors_toggle.setStyleSheet("QCheckBox { color: #334155; font-size: 11pt; }")
        self.layer_colors_toggle.setChecked(True)
        self.layer_colors_toggle.stateChanged.connect(self._render)
        ctrl_layout.addWidget(self.layer_colors_toggle)

        # Summary
        ctrl_layout.addSpacing(24)
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #0f172a; font-weight: 800; font-size: 14pt;")
        ctrl_layout.addWidget(self.count_label)

        self.value_label = QLabel("")
        self.value_label.setStyleSheet("color: #334155; font-size: 11pt; font-style: italic;")
        ctrl_layout.addWidget(self.value_label)

        ctrl_layout.addStretch()
        return controls

    def eventFilter(self, source, event):  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType, reportUnknownParameterType]
        """
        Eventfilter logic.
        
        Args:
            source: Description of source.
            event: Description of event.
        
        """
        if source is self.view.viewport():
            if event.type() == event.Type.MouseButtonPress:  # type: ignore[reportUnknownMemberType]
                if event.button() == Qt.MouseButton.RightButton:
                    self._rotating = True
                    self._last_mouse_pos = event.pos()
                    self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
                    return True
            elif event.type() == event.Type.MouseButtonRelease:  # type: ignore[reportUnknownMemberType]
                if event.button() == Qt.MouseButton.RightButton:
                    self._rotating = False
                    self._last_mouse_pos = None
                    self.view.setCursor(Qt.CursorShape.ArrowCursor)
                    return True
            elif event.type() == event.Type.MouseMove:  # type: ignore[reportUnknownMemberType]
                if self._rotating and self._last_mouse_pos:
                    delta = event.pos() - self._last_mouse_pos  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                    self._last_mouse_pos = event.pos()
                    
                    self.camera_yaw += delta.x() * 0.5
                    self.camera_pitch += delta.y() * 0.5
                    self.camera_pitch = max(-90.0, min(90.0, self.camera_pitch))
                    
                    self._update_positions()
                    return True
        return super().eventFilter(source, event)

    def _render(self, _=None):
        shape_type = self.SHAPE_TYPES[self.shape_combo.currentIndex()][1] if self.shape_combo else "tetrahedral"
        n = self.index_spin.value() if self.index_spin else 4
        spacing = self.spacing_spin.value() if self.spacing_spin else 1.0

        # Note: 3D generation is fast enough to do on main thread for reasonable N
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

        self._update_summary(value, len(self._current_points_3d), shape_type)
        self._update_positions()

    def _update_positions(self):
        """Re-project 3D points using current camera angles and update scene."""
        if not self._current_points_3d:
            return
            
        self._current_points_2d = project_dynamic(
            self._current_points_3d, self.camera_yaw, self.camera_pitch
        )
        self._current_points = self._current_points_2d # Sync for base class interactions
        
        spacing = self.spacing_spin.value() if self.spacing_spin else 1.0
        use_layer_colors = self.layer_colors_toggle.isChecked() if self.layer_colors_toggle else True
        
        payload = self._build_payload(
            self._current_points_3d, 
            self._current_points_2d,
            spacing,
            use_layer_colors
        )
        self.scene.set_payload(payload)
        
        # We manually call highlight refresh because scene payload reset clears standard highlights,
        # but interaction manager still holds state.
        self._refresh_highlights()

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

        if points_3d:
            z_values = sorted(set(round(p[2] / spacing) for p in points_3d))
            z_to_layer = {z: i for i, z in enumerate(z_values)}
        else:
            z_to_layer = {}

        for idx, ((x2d, y2d), (_x3d, _y3d, z3d)) in enumerate(zip(points_2d, points_3d), start=1):  # type: ignore[unknown]
            layer_idx = z_to_layer.get(round(z3d / spacing), 0)  # type: ignore[reportUndefinedVariable, reportUnknownArgumentType, unknown]
            
            if use_layer_colors:
                color = LAYER_COLORS[layer_idx % len(LAYER_COLORS)]
                pen = PenStyle(color=(*color, 255), width=1.2)
                brush = BrushStyle(color=(*color, 180), enabled=True)
            else:
                pen = PenStyle(color=(59, 130, 246, 255), width=1.2)
                brush = BrushStyle(color=(191, 219, 254, 220), enabled=True)

            primitives.append(CirclePrimitive(
                center=(x2d, y2d),  # type: ignore[reportUndefinedVariable, reportUnknownArgumentType]
                radius=dot_radius,
                pen=pen,
                brush=brush,
                metadata={"index": idx, "style": "sphere"}
            ))
            labels.append(LabelPrimitive(
                text=str(idx),
                position=(x2d, y2d),  # type: ignore[reportUndefinedVariable, reportUnknownArgumentType]
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


__all__ = ["Figurate3DWindow"]