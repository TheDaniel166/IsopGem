"""Cymatics detector window for analyzing simulated patterns."""
from __future__ import annotations

from typing import Optional

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QDoubleSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..models import DetectionResult, SimulationResult
from ..services import CymaticsDetectionService, CymaticsSessionStore
from shared.ui import WindowManager


class CymaticsDetectorWindow(QMainWindow):
    """Detector view for cymatics patterns produced by the simulator."""

    def __init__(self, window_manager: Optional[WindowManager] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Cymatics Pattern Detector")
        self.setMinimumSize(980, 720)

        self._detector = CymaticsDetectionService()
        self._last_result: Optional[DetectionResult] = None
        self._last_simulation: Optional[SimulationResult] = None
        self._last_preview: Optional[QImage] = None
        self._last_map: Optional[QImage] = None

        self._build_ui()
        self._analyze()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QLabel("Cymatics Pattern Detector")
        header.setStyleSheet("""
            QLabel {
                font-size: 22pt;
                font-weight: 700;
                color: #0f172a;
            }
        """)
        layout.addWidget(header)

        subheader = QLabel("Analyze nodal structure from the simulator output.")
        subheader.setStyleSheet("color: #475569; font-size: 10pt;")
        layout.addWidget(subheader)

        controls = self._build_controls()
        layout.addWidget(controls)

        content_row = QHBoxLayout()
        content_row.setSpacing(16)

        self._preview_panel = self._build_image_panel("Pattern Preview")
        self._map_panel = self._build_image_panel("Detection Map")

        content_row.addWidget(self._preview_panel, 1)
        content_row.addWidget(self._map_panel, 1)

        layout.addLayout(content_row, 1)

        self._metrics = QTextEdit()
        self._metrics.setReadOnly(True)
        self._metrics.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background: #ffffff;
                padding: 12px;
                font-size: 10pt;
                color: #0f172a;
            }
        """)
        layout.addWidget(self._metrics, 0)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        layout.addWidget(self._status_label)

        self.setCentralWidget(root)

    def _build_controls(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background: #ffffff;
            }
        """)

        layout = QGridLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self._threshold = QDoubleSpinBox()
        self._threshold.setRange(0.01, 0.3)
        self._threshold.setSingleStep(0.01)
        self._threshold.setValue(0.08)
        layout.addWidget(QLabel("Nodal Threshold"), 0, 0)
        layout.addWidget(self._threshold, 0, 1)

        self._view_selector = QComboBox()
        self._view_selector.addItems(["Edges", "Nodal Mask"])
        self._view_selector.currentIndexChanged.connect(self._refresh_map_view)
        layout.addWidget(QLabel("View"), 0, 2)
        layout.addWidget(self._view_selector, 0, 3)

        self._refresh_button = QPushButton("Analyze")
        self._refresh_button.clicked.connect(self._analyze)
        self._refresh_button.setStyleSheet("padding: 8px 16px;")

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self._refresh_button)
        layout.addLayout(button_row, 1, 0, 1, 4)

        return frame

    def _build_image_panel(self, title: str) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background: #0f172a;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        label = QLabel(title)
        label.setStyleSheet("color: #e2e8f0; font-size: 9pt;")
        layout.addWidget(label)

        image = QLabel()
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setStyleSheet("background: transparent;")
        layout.addWidget(image, 1)

        panel._image_label = image  # type: ignore[attr-defined]
        return panel

    def _analyze(self) -> None:
        simulation = CymaticsSessionStore.get_last_simulation()
        if simulation is None:
            self._status_label.setText("No simulation data found. Run the simulator first.")
            self._metrics.setPlainText("Awaiting simulation output.")
            self._clear_images()
            return

        self._last_simulation = simulation
        self._last_result = self._detector.detect(simulation, nodal_threshold=self._threshold.value())
        self._last_preview = self._to_qimage(simulation.normalized)
        self._refresh_map_view()
        self._update_metrics()
        self._status_label.setText("Detection updated from latest simulator output.")

    def _update_metrics(self) -> None:
        if self._last_result is None or self._last_simulation is None:
            return

        params = self._last_simulation.params
        metrics = self._last_result.metrics
        lines = [
            f"Mode: m={params.mode_m}, n={params.mode_n}",
            f"Secondary: m={params.secondary_m}, n={params.secondary_n}",
            f"Mix: {params.mix:.2f} | Damping: {params.damping:.2f}",
            f"Edge density: {metrics.edge_density:.3f}",
            f"Symmetry H/V: {metrics.symmetry_horizontal:.3f} / {metrics.symmetry_vertical:.3f}",
        ]

        if metrics.radial_peaks:
            peaks = ", ".join(f"{p:.2f}" for p in metrics.radial_peaks)
            lines.append(f"Radial peaks (norm): {peaks}")
        else:
            lines.append("Radial peaks (norm): none detected")

        if metrics.dominant_frequencies:
            lines.append("Dominant spatial frequencies:")
            for fx, fy, mag in metrics.dominant_frequencies:
                lines.append(f"  fx={fx:.3f}, fy={fy:.3f}, strength={mag:.1f}")
        else:
            lines.append("Dominant spatial frequencies: none detected")

        self._metrics.setPlainText("\n".join(lines))

    def _refresh_map_view(self) -> None:
        if self._last_result is None:
            return

        view = self._view_selector.currentText()
        if view == "Nodal Mask":
            self._last_map = self._to_qimage(self._last_result.nodal_mask)
        else:
            self._last_map = self._to_qimage(self._last_result.edges)

        self._update_image_panels()

    def _update_image_panels(self) -> None:
        if self._last_preview is None or self._last_map is None:
            return

        preview_label = self._preview_panel._image_label  # type: ignore[attr-defined]
        map_label = self._map_panel._image_label  # type: ignore[attr-defined]

        preview_pixmap = QPixmap.fromImage(self._last_preview)
        map_pixmap = QPixmap.fromImage(self._last_map)

        preview_label.setPixmap(self._scale_pixmap(preview_pixmap, preview_label))
        map_label.setPixmap(self._scale_pixmap(map_pixmap, map_label))

    def _scale_pixmap(self, pixmap: QPixmap, label: QLabel) -> QPixmap:
        target_size = label.size()
        if target_size.width() < 10 or target_size.height() < 10:
            return pixmap
        return pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _to_qimage(self, data: np.ndarray) -> QImage:
        if data.ndim != 2:
            data = data[:, :, 0]
        if data.max() <= 1.5:
            array = np.clip(data * 255.0, 0.0, 255.0).astype(np.uint8)
        else:
            array = np.clip(data, 0.0, 255.0).astype(np.uint8)
        array = np.ascontiguousarray(array)
        height, width = array.shape
        qimage = QImage(array.data, width, height, array.strides[0], QImage.Format.Format_Grayscale8)
        return qimage.copy()

    def _clear_images(self) -> None:
        preview_label = self._preview_panel._image_label  # type: ignore[attr-defined]
        map_label = self._map_panel._image_label  # type: ignore[attr-defined]
        preview_label.clear()
        map_label.clear()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_image_panels()
