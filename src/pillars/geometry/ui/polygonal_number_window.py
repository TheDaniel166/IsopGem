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
)
from PyQt6.QtCore import Qt

from shared.ui import WindowManager
from ..services import (
    centered_polygonal_value,
    max_radius,
    polygonal_number_points,
    polygonal_number_value,
    polygonal_outline_points,
)
from .geometry_scene import GeometryScene
from .geometry_view import GeometryView
from .primitives import Bounds, CirclePrimitive, GeometryScenePayload, LabelPrimitive, PenStyle, BrushStyle, PolygonPrimitive


Color = Tuple[int, int, int, int]


class PolygonalNumberWindow(QMainWindow):
    """Interactive viewer for figurate numbers built from dots."""

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager

        self.scene = GeometryScene()
        self.view = GeometryView(self.scene)

        self.setWindowTitle("Polygonal Number Visualizer")
        self.setMinimumSize(1100, 720)
        self.setStyleSheet("background-color: #f8fafc;")

        self.sides_spin: Optional[QSpinBox] = None
        self.index_spin: Optional[QSpinBox] = None
        self.spacing_spin: Optional[QDoubleSpinBox] = None
        self.mode_combo: Optional[QComboBox] = None
        self.labels_toggle: Optional[QCheckBox] = None
        self.grid_toggle: Optional[QCheckBox] = None
        self.axes_toggle: Optional[QCheckBox] = None
        self.count_label: Optional[QLabel] = None
        self.value_label: Optional[QLabel] = None

        self._setup_ui()
        self._render()

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

        toolbar = self._build_view_toolbar()
        viewport_layout.addWidget(toolbar)
        viewport_layout.addWidget(self.view, 1)

        layout.addWidget(viewport_frame, 1)

    def _build_controls(self) -> QWidget:
        frame = QFrame()
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

        self.grid_toggle = QCheckBox("Show grid")
        self.grid_toggle.setChecked(True)
        self.grid_toggle.stateChanged.connect(lambda state: self.scene.set_grid_visible(state == Qt.CheckState.Checked))
        layout.addWidget(self.grid_toggle)

        self.axes_toggle = QCheckBox("Show axes")
        self.axes_toggle.setChecked(True)
        self.axes_toggle.stateChanged.connect(lambda state: self.scene.set_axes_visible(state == Qt.CheckState.Checked))
        layout.addWidget(self.axes_toggle)

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

        reset_btn = QPushButton("Reset zoom")
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
        centered = (self.mode_combo.currentData() == "centered") if self.mode_combo else False

        value = centered_polygonal_value(sides, index) if centered else polygonal_number_value(sides, index)
        points = polygonal_number_points(sides, index, spacing=spacing, centered=centered)

        self._update_summary(value, centered)
        payload = self._build_payload(points, sides, spacing, index, centered)
        self.scene.set_payload(payload)
        self.view.fit_scene()

    def _build_payload(self, points: List[Tuple[float, float]], sides: int, spacing: float, index: int, centered: bool) -> GeometryScenePayload:
        dot_radius = max(0.06, spacing * 0.18)
        pen = PenStyle(color=(37, 99, 235, 255), width=1.2)
        brush = BrushStyle(color=(191, 219, 254, 220), enabled=True)

        primitives: List = []
        labels: List[LabelPrimitive] = []

        show_labels = self.labels_toggle.isChecked() if self.labels_toggle else True

        if points:
            max_r = max(math.hypot(x, y) for x, y in points)
        else:
            max_r = spacing

        if centered:
            outline_radius = max(max_radius(spacing, index), max_r + spacing * 0.5)
            outline = _regular_polygon_points(sides, outline_radius)
        else:
            outline = polygonal_outline_points(sides, index, spacing)
        primitives.append(PolygonPrimitive(points=outline, pen=PenStyle(color=(79, 70, 229, 255), width=2.0), brush=BrushStyle(enabled=False), closed=False))

        for idx, (x, y) in enumerate(points, start=1):
            primitives.append(CirclePrimitive(center=(x, y), radius=dot_radius, pen=pen, brush=brush))
            if show_labels:
                labels.append(LabelPrimitive(text=str(idx), position=(x, y), align_center=True))

        bounds = _bounds_from_points(points, margin=dot_radius * 3)
        payload = GeometryScenePayload(
            primitives=primitives,
            labels=labels,
            bounds=bounds,
        )
        payload.suggest_grid_span = max(bounds.width, bounds.height) * 1.2 if bounds else None
        return payload

    def _update_summary(self, value: int, centered: bool):
        if self.count_label:
            self.count_label.setText(f"{value} dots")
        if self.value_label:
            family = "Centered" if centered else "Polygonal"
            self.value_label.setText(f"Family: {family}  •  Total: {value}")

        if self.labels_toggle:
            self.scene.set_labels_visible(self.labels_toggle.isChecked())

    def _toggle_labels(self, state: int):
        self.scene.set_labels_visible(state == Qt.CheckState.Checked)

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
