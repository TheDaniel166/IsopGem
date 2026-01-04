"""Visualizer for polygonal and centered polygonal numbers."""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFrame, QLabel, QPushButton,
    QSpinBox, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt, QRunnable
from shared.ui import WindowManager
from ..services import (
    centered_polygonal_value,
    polygonal_number_points,
    polygonal_number_value,
    star_number_points,
    star_number_value,
)
from .base_figurate_window import BaseFigurateWindow, RenderSignals
from .primitives import Bounds, CirclePrimitive, GeometryScenePayload, LabelPrimitive, PenStyle, BrushStyle


class PolygonalNumberWindow(BaseFigurateWindow):
    """Interactive viewer for figurate numbers built from dots."""

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(window_manager, parent)
        self.setWindowTitle("Polygonal Number Visualizer")

        # Controls specific to this window
        self.sides_spin: Optional[QSpinBox] = None
        self.index_spin: Optional[QSpinBox] = None
        self.spacing_spin: Optional[QDoubleSpinBox] = None
        self.mode_combo: Optional[QComboBox] = None
        self.labels_toggle: Optional[QCheckBox] = None
        self.count_label: Optional[QLabel] = None
        self.value_label: Optional[QLabel] = None

        self._current_points = [] # 2D points storage for connections

        self._setup_ui()
        self._render()

    def _setup_ui(self):
        controls = self._build_controls()
        self._setup_ui_skeleton(controls)

    def _build_controls(self) -> QWidget:
        frame = QFrame()
        self._controls_frame = frame
        frame.setObjectName("FloatingPanel")
        frame.setFixedWidth(320)
        frame.setStyleSheet("""
            QFrame#FloatingPanel {
                background-color: #f1f5f9; 
                border-right: 1px solid #cbd5e1;
                border: 1px solid #cbd5e1; 
                border-radius: 24px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 32, 24, 32)
        layout.setSpacing(16)

        title = QLabel("Polygonal Matrix")
        title.setStyleSheet("font-family: 'Inter'; font-size: 20pt; font-weight: 800; color: #0f172a;")
        layout.addWidget(title)

        subtitle = QLabel("Select the polygon family and observe the gnomonic growth.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #334155; font-size: 11pt;")
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        # Polygon sides
        sides_label = QLabel("Polygon (n)")
        sides_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        layout.addWidget(sides_label)

        self.sides_spin = QSpinBox()
        self.sides_spin.setRange(3, 20)
        self.sides_spin.setValue(5)
        self.sides_spin.setStyleSheet(self._spin_style())
        self.sides_spin.valueChanged.connect(self._render)
        layout.addWidget(self.sides_spin)

        # Index
        index_label = QLabel("Iteration (k)")
        index_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        layout.addWidget(index_label)

        self.index_spin = QSpinBox()
        self.index_spin.setRange(1, 30)
        self.index_spin.setValue(5)
        self.index_spin.setStyleSheet(self._spin_style())
        self.index_spin.valueChanged.connect(self._render)
        layout.addWidget(self.index_spin)

        # Mode
        mode_label = QLabel("Archetype")
        mode_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        layout.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Polygonal (gnomon growth)", userData="polygonal")
        self.mode_combo.addItem("Centered polygonal", userData="centered")
        self.mode_combo.addItem("Star number (hexagram)", userData="star")
        self.mode_combo.setStyleSheet(self._combo_style())
        self.mode_combo.currentIndexChanged.connect(self._render)
        layout.addWidget(self.mode_combo)

        # Spacing
        spacing_label = QLabel("Grid Lattice")
        spacing_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        layout.addWidget(spacing_label)

        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.2, 5.0)
        self.spacing_spin.setSingleStep(0.1)
        self.spacing_spin.setValue(1.0)
        self.spacing_spin.setDecimals(2)
        self.spacing_spin.setStyleSheet(self._spin_style())
        self.spacing_spin.valueChanged.connect(self._render)
        layout.addWidget(self.spacing_spin)

        layout.addSpacing(8)

        # Toggles
        self.labels_toggle = QCheckBox("Show Sigils")
        self.labels_toggle.setStyleSheet("QCheckBox { color: #334155; font-size: 11pt; }")
        self.labels_toggle.setChecked(True)
        self.labels_toggle.stateChanged.connect(self._toggle_labels)
        layout.addWidget(self.labels_toggle)

        # Summary labels
        layout.addSpacing(16)
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #0f172a; font-weight: 800; font-size: 14pt;")
        layout.addWidget(self.count_label)

        self.value_label = QLabel("")
        self.value_label.setStyleSheet("color: #334155; font-size: 11pt; font-style: italic;")
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)

        # Action button
        render_btn = QPushButton("Manifest Pattern")
        render_btn.setObjectName("MagusButton")
        render_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        render_btn.setStyleSheet(self._primary_button_style())
        render_btn.clicked.connect(self._render)
        self._render_button = render_btn
        layout.addWidget(render_btn)

        layout.addStretch(1)
        return frame

    def _render(self):
        sides = self.sides_spin.value() if self.sides_spin else 3
        index = self.index_spin.value() if self.index_spin else 1
        spacing = self.spacing_spin.value() if self.spacing_spin else 1.0
        
        mode = self.mode_combo.currentData() if self.mode_combo else "polygonal"
        centered = (mode == "centered")
        is_star = (mode == "star")

        if self.sides_spin:
            self.sides_spin.setEnabled(not is_star)

        if is_star:
            value = star_number_value(index)
        else:
            value = centered_polygonal_value(sides, index) if centered else polygonal_number_value(sides, index)

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
        payload, points, value, mode, error = payload_points_value_mode_error  # type: ignore[reportUnknownVariableType]
        self._apply_render_result(payload, points, value, mode, error)  # type: ignore[reportUnknownArgumentType]
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
        self._refresh_highlights() # Re-apply highlights after new load

    @staticmethod
    def _build_payload_static(points: List[Tuple[float, float]], sides: int, spacing: float, index: int, centered: bool) -> GeometryScenePayload:
        dot_radius = max(0.06, spacing * 0.18)
        pen = PenStyle(color=(37, 99, 235, 255), width=1.2)
        brush = BrushStyle(color=(191, 219, 254, 220), enabled=True)

        primitives: List = []
        labels: List[LabelPrimitive] = []

        for idx, (x, y) in enumerate(points, start=1):
            primitives.append(CirclePrimitive(
                center=(x, y), 
                radius=dot_radius, 
                pen=pen, 
                brush=brush,
                metadata={"index": idx}
            ))
            labels.append(LabelPrimitive(text=str(idx), position=(x, y), align_center=True, metadata={"index": idx}))

        bounds = _bounds_from_points(points, margin=dot_radius * 3)
        return GeometryScenePayload(
            primitives=primitives,
            labels=labels,
            bounds=bounds,
        )

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


class _FigurateRenderRunnable(QRunnable):
    def __init__(self, sides: int, index: int, spacing: float, mode: str):
        """
          init   logic.
        
        Args:
            sides: Description of sides.
            index: Description of index.
            spacing: Description of spacing.
            mode: Description of mode.
        
        """
        super().__init__()
        self.sides = sides
        self.index = index
        self.spacing = spacing
        self.mode = mode
        self.signals = RenderSignals()

    def run(self):
        """
        Execute logic.
        
        """
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
        except Exception as exc:
            self.signals.finished.emit((None, [], 0, self.mode, str(exc)))

def _bounds_from_points(points: List[Tuple[float, float]], margin: float) -> Optional[Bounds]:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Bounds(min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin)