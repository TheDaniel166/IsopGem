"""Visualizer for Generalized (Experimental) Star Numbers."""
from __future__ import annotations

from typing import List, Optional, Tuple

from PyQt6.QtWidgets import (
    QCheckBox, QDoubleSpinBox, QFrame, QLabel, QPushButton,
    QSpinBox, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt, QRunnable
from shared.ui import WindowManager
from ..services import (
    generalized_star_number_value,
    generalized_star_number_points,
)
from .base_figurate_window import BaseFigurateWindow, RenderSignals
from .primitives import Bounds, CirclePrimitive, GeometryScenePayload, LabelPrimitive, PenStyle, BrushStyle


class ExperimentalStarWindow(BaseFigurateWindow):
    """Interactive viewer for Generalized Star Numbers (P-grams).
    
    Allows creating stars with any number of points (P >= 3).
    """

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(window_manager, parent)
        self.setWindowTitle("Experimental Star Number Visualizer")

        self.points_spin: Optional[QSpinBox] = None
        self.index_spin: Optional[QSpinBox] = None
        self.spacing_spin: Optional[QDoubleSpinBox] = None
        self.labels_toggle: Optional[QCheckBox] = None
        self.count_label: Optional[QLabel] = None
        self.value_label: Optional[QLabel] = None

        self._current_points = []

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

        title = QLabel("Stellar Matrix")
        title.setStyleSheet("font-family: 'Inter'; font-size: 20pt; font-weight: 800; color: #0f172a;")
        layout.addWidget(title)

        subtitle = QLabel("Summon star figures with arbitrary points (P-grams).")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #334155; font-size: 11pt;")
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        # Star Points (P)
        p_label = QLabel("Star Points (P)")
        p_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        layout.addWidget(p_label)

        self.points_spin = QSpinBox()
        self.points_spin.setRange(3, 30)
        self.points_spin.setValue(5) # Default to Pentagram
        self.points_spin.setStyleSheet(self._spin_style())
        self.points_spin.valueChanged.connect(self._render)
        layout.addWidget(self.points_spin)

        # Index (N)
        n_label = QLabel("Iteration (N)")
        n_label.setStyleSheet("color: #334155; font-weight: 700; font-size: 11pt;")
        layout.addWidget(n_label)

        self.index_spin = QSpinBox()
        self.index_spin.setRange(1, 30)
        self.index_spin.setValue(3)
        self.index_spin.setStyleSheet(self._spin_style())
        self.index_spin.valueChanged.connect(self._render)
        layout.addWidget(self.index_spin)

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

        layout.addSpacing(16)
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #0f172a; font-weight: 800; font-size: 14pt;")
        layout.addWidget(self.count_label)

        self.value_label = QLabel("")
        self.value_label.setStyleSheet("color: #334155; font-size: 11pt; font-style: italic;")
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)

        # Action button
        render_btn = QPushButton("Manifest Star")
        render_btn.setObjectName("MagusButton")
        render_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        render_btn.setStyleSheet(self._primary_button_style())
        render_btn.clicked.connect(self._render)
        self._render_button = render_btn
        layout.addWidget(render_btn)

        layout.addStretch(1)
        return frame

    def _render(self):
        points_count = self.points_spin.value() if self.points_spin else 5
        index = self.index_spin.value() if self.index_spin else 1
        spacing = self.spacing_spin.value() if self.spacing_spin else 1.0

        value = generalized_star_number_value(points_count, index)

        if value >= self.HEAVY_THRESHOLD:
            self._start_async_render(points_count, index, spacing)
            return

        points = generalized_star_number_points(points_count, index, spacing=spacing)
        payload = self._build_payload_static(points, points_count, spacing, index)
        self._apply_render_result(payload, points, value)

    def _start_async_render(self, points_count: int, index: int, spacing: float):
        if self._rendering:
            return
        self._set_busy(True)
        worker = _StarRenderRunnable(points_count, index, spacing)
        worker.signals.finished.connect(self._on_async_finished)
        self.thread_pool.start(worker)

    def _on_async_finished(self, payload_points_value_error):
        payload, points, value, error = payload_points_value_error
        self._apply_render_result(payload, points, value, error)
        self._set_busy(False)

    def _apply_render_result(self, payload: GeometryScenePayload, points: List[Tuple[float, float]], value: int, error: Optional[str] = None):
        if error:
            if self.value_label:
                self.value_label.setText(f"Error: {error}")
            return

        self._current_points = points
        self._update_summary(value, self.points_spin.value() if self.points_spin else 0)
        self.scene.set_payload(payload)
        self.view.fit_scene()
        self._refresh_highlights()

    @staticmethod
    def _build_payload_static(points: List[Tuple[float, float]], sides: int, spacing: float, index: int) -> GeometryScenePayload:
        dot_radius = max(0.06, spacing * 0.18)
        pen = PenStyle(color=(147, 51, 234, 255), width=1.2) # Purple for Experimental
        brush = BrushStyle(color=(216, 180, 254, 220), enabled=True)

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

    def _update_summary(self, value: int, points_count: int):
        if self.count_label:
            self.count_label.setText(f"{value} dots")
        if self.value_label:
            name_map = {3: "Triangle", 4: "Square", 5: "Pentagram", 6: "Hexagram", 7: "Heptagram", 8: "Octagram"}
            shape_name = name_map.get(points_count, f"{points_count}-gram")
            self.value_label.setText(f"Shape: {shape_name} Star  •  Total: {value}")
        if self.labels_toggle:
            self.scene.set_labels_visible(self.labels_toggle.isChecked())


class _StarRenderRunnable(QRunnable):
    def __init__(self, points_count: int, index: int, spacing: float):
        """
          init   logic.
        
        Args:
            points_count: Description of points_count.
            index: Description of index.
            spacing: Description of spacing.
        
        """
        super().__init__()
        self.points_count = points_count
        self.index = index
        self.spacing = spacing
        self.signals = RenderSignals()

    def run(self):
        """
        Execute logic.
        
        """
        try:
            value = generalized_star_number_value(self.points_count, self.index)
            points = generalized_star_number_points(self.points_count, self.index, spacing=self.spacing)
            payload = ExperimentalStarWindow._build_payload_static(points, self.points_count, self.spacing, self.index)
            self.signals.finished.emit((payload, points, value, None))
        except Exception as exc:
            self.signals.finished.emit((None, [], 0, str(exc)))


def _bounds_from_points(points: List[Tuple[float, float]], margin: float) -> Optional[Bounds]:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Bounds(min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin)


__all__ = ["ExperimentalStarWindow"]