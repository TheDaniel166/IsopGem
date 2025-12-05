"""3D geometric transitions window built on Platonic solids."""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

from PyQt6.QtCore import QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QMouseEvent, QPaintEvent, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QMainWindow,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..services.platonic_transition_service import (
    PlatonicSolidGeometry,
    PlatonicTransitionService,
    SolidFamilyGroup,
    SolidTransition3D,
    SolidVertex3D,
)


class SolidCanvas3D(QWidget):
    """Simple orthographic projection canvas for Platonic solids."""

    rotation_changed = pyqtSignal(float, float)

    _DEFAULT_YAW = -35.0
    _DEFAULT_PITCH = 22.5
    _MIN_PITCH = -85.0
    _MAX_PITCH = 85.0
    _DRAG_SENSITIVITY = 0.45

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(360, 360)
        self.setMouseTracking(True)
        self.vertices: List[SolidVertex3D] = []
        self.edges: List[tuple[int, int]] = []
        self.family_segments: List[tuple[int, int]] = []
        self.pattern_segments: List[tuple[int, int]] = []
        self.transition_pair: Optional[tuple[int, int]] = None
        self.rotation_y = self._DEFAULT_YAW
        self.rotation_x = self._DEFAULT_PITCH
        self._is_dragging = False
        self._last_drag_pos: Optional[QPointF] = None

    def set_geometry(self, vertices: List[SolidVertex3D], edges: List[tuple[int, int]]):
        self.vertices = vertices or []
        self.edges = edges or []
        self.family_segments = []
        self.pattern_segments = []
        self.transition_pair = None
        self.update()

    def set_family_segments(self, segments: Optional[List[tuple[int, int]]]):
        self.family_segments = segments or []
        self.update()

    def set_pattern_segments(self, segments: Optional[List[tuple[int, int]]]):
        self.pattern_segments = segments or []
        self.update()

    def set_transition(self, transition: Optional[SolidTransition3D]):
        if transition is None:
            self.transition_pair = None
        else:
            self.transition_pair = (transition.from_index, transition.to_index)
        self.update()

    def paintEvent(self, a0: Optional[QPaintEvent]):  # noqa: N802 - Qt override
        del a0
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#ffffff"))

        points = self._project_vertices()
        if not points:
            painter.setPen(QPen(QColor("#94a3b8"), 1, Qt.PenStyle.DashLine))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Select a solid")
            return

        self._draw_segments(painter, self.edges, points, QColor("#cbd5e1"), 2)
        self._draw_segments(painter, self.pattern_segments, points, QColor("#10b981"), 3, dashed=True)
        self._draw_segments(painter, self.family_segments, points, QColor("#2563eb"), 4)
        if self.transition_pair:
            self._draw_segments(
                painter,
                [self.transition_pair],
                points,
                QColor("#ef4444"),
                4,
            )
        self._draw_vertices(painter, points)

    def _project_vertices(self) -> Dict[int, QPointF]:
        if not self.vertices:
            return {}
        angle_y = math.radians(self.rotation_y)
        angle_x = math.radians(self.rotation_x)
        cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
        cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
        raw_points: List[tuple[int, float, float]] = []
        for vertex in self.vertices:
            x, y, z = vertex.position
            xz = x * cos_y + z * sin_y
            zz = -x * sin_y + z * cos_y
            xy = y * cos_x - zz * sin_x
            raw_points.append((vertex.index, xz, xy))
        min_x = min(point[1] for point in raw_points)
        max_x = max(point[1] for point in raw_points)
        min_y = min(point[2] for point in raw_points)
        max_y = max(point[2] for point in raw_points)
        width = max(max_x - min_x, 1e-3)
        height = max(max_y - min_y, 1e-3)
        margin = 32.0
        available_w = max(self.width() - margin * 2.0, 1.0)
        available_h = max(self.height() - margin * 2.0, 1.0)
        scale = min(available_w / width, available_h / height)
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        mid_x = (max_x + min_x) / 2.0
        mid_y = (max_y + min_y) / 2.0
        projected: Dict[int, QPointF] = {}
        for index, px, py in raw_points:
            dx = (px - mid_x) * scale
            dy = (py - mid_y) * scale
            projected[index] = QPointF(center_x + dx, center_y - dy)
        return projected

    def _draw_segments(
        self,
        painter: QPainter,
        segments: Optional[List[tuple[int, int]]],
        points: Dict[int, QPointF],
        color: QColor,
        width: int,
        dashed: bool = False,
    ):
        if not segments:
            return
        pen = QPen(color, width)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        for start, end in segments:
            p1 = points.get(start)
            p2 = points.get(end)
            if p1 is None or p2 is None:
                continue
            painter.drawLine(p1, p2)

    def _draw_vertices(self, painter: QPainter, points: Dict[int, QPointF]):
        pen = QPen(QColor("#0f172a"), 1)
        brush_color = QColor("#f8fafc")
        painter.setPen(pen)
        painter.setBrush(brush_color)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        for vertex in self.vertices:
            point = points.get(vertex.index)
            if point is None:
                continue
            painter.drawEllipse(point, 6, 6)
            painter.drawText(point + QPointF(8, -8), vertex.label)

    def mousePressEvent(self, a0: Optional[QMouseEvent]):
        if a0 is not None and a0.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._last_drag_pos = a0.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            a0.accept()
            return
        super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]):
        if self._is_dragging and self._last_drag_pos is not None and a0 is not None:
            current = a0.position()
            delta_x = current.x() - self._last_drag_pos.x()
            delta_y = current.y() - self._last_drag_pos.y()
            new_yaw = self.rotation_y + delta_x * self._DRAG_SENSITIVITY
            new_pitch = self.rotation_x + delta_y * self._DRAG_SENSITIVITY
            self.set_rotation(yaw=new_yaw, pitch=new_pitch)
            self._last_drag_pos = current
            a0.accept()
            return
        super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: Optional[QMouseEvent]):
        if a0 is not None and a0.button() == Qt.MouseButton.LeftButton and self._is_dragging:
            self._is_dragging = False
            self._last_drag_pos = None
            self.unsetCursor()
            a0.accept()
            return
        super().mouseReleaseEvent(a0)

    def set_rotation(
        self,
        *,
        yaw: Optional[float] = None,
        pitch: Optional[float] = None,
        emit_signal: bool = True,
    ):
        changed = False
        if yaw is not None:
            wrapped = ((yaw + 180.0) % 360.0) - 180.0
            if not math.isclose(wrapped, self.rotation_y, rel_tol=1e-6, abs_tol=1e-3):
                self.rotation_y = wrapped
                changed = True
        if pitch is not None:
            bounded = max(self._MIN_PITCH, min(self._MAX_PITCH, pitch))
            if not math.isclose(bounded, self.rotation_x, rel_tol=1e-6, abs_tol=1e-3):
                self.rotation_x = bounded
                changed = True
        if changed:
            self.update()
            if emit_signal:
                self.rotation_changed.emit(self.rotation_y, self.rotation_x)

    def reset_view(self):
        self.set_rotation(yaw=self._DEFAULT_YAW, pitch=self._DEFAULT_PITCH)


class GeometricTransitions3DWindow(QMainWindow):
    """Interactive window for Platonic solid ternary transitions."""

    RESULT_COLUMN_INDEX = 5

    def __init__(self, window_manager=None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.current_geometry: Optional[PlatonicSolidGeometry] = None
        self.family_lookup: Dict[str, SolidFamilyGroup] = {}
        self.face_patterns: List[Dict[str, object]] = []
        self.value_inputs: List[QLineEdit] = []
        self.vertex_hints: List[QLabel] = []

        self.solid_combo: QComboBox
        self.vertex_stats_label: QLabel
        self.values_container: QWidget
        self.values_layout: QGridLayout
        self.canvas = SolidCanvas3D()
        self.tabs = QTabWidget()
        self.copy_btn: QPushButton
        self.azimuth_slider: Optional[QSlider] = None
        self.elevation_slider: Optional[QSlider] = None
        self.face_tab_index: Optional[int] = None
        self.face_combo: Optional[QComboBox] = None
        self.face_table: Optional[QTableWidget] = None
        self.face_summary_label: Optional[QLabel] = None

        self.canvas.rotation_changed.connect(self._handle_canvas_rotation_changed)
        self._setup_ui()
        self._refresh_value_inputs()

    # -- UI setup --------------------------------------------------------

    def _setup_ui(self):
        self.setWindowTitle("3D Geometric Transitions")
        self.setMinimumSize(1400, 760)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setSpacing(18)
        root_layout.setContentsMargins(24, 24, 24, 24)

        root_layout.addWidget(self._build_left_panel(), 3)
        root_layout.addWidget(self._build_canvas_panel(), 4)
        root_layout.addWidget(self._build_results_panel(), 5)

    def _build_left_panel(self) -> QWidget:
        group = QGroupBox("Configuration")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        layout.addWidget(self._build_solid_selector())

        self.vertex_stats_label = QLabel("Vertices: 0 • Faces: 0")
        self.vertex_stats_label.setStyleSheet("color: #475569;")
        layout.addWidget(self.vertex_stats_label)

        values_label = QLabel("Vertex Values")
        values_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(values_label)

        self.values_container = QWidget()
        self.values_layout = QGridLayout(self.values_container)
        self.values_layout.setColumnStretch(1, 1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.values_container)
        scroll.setMinimumHeight(260)
        layout.addWidget(scroll)

        buttons = QHBoxLayout()
        generate_btn = QPushButton("Generate")
        generate_btn.setStyleSheet("background-color: #2563eb; color: #ffffff; font-weight: bold;")
        generate_btn.clicked.connect(self._handle_generate)
        buttons.addWidget(generate_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._handle_clear)
        buttons.addWidget(clear_btn)
        layout.addLayout(buttons)

        layout.addStretch(1)
        return group

    def _build_solid_selector(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Platonic Solid")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        self.solid_combo = QComboBox()
        for option in PlatonicTransitionService.get_solid_options():
            display = f"{option['name']} ({option['vertex_count']} vertices)"
            self.solid_combo.addItem(display, option['key'])
        self.solid_combo.currentIndexChanged.connect(self._refresh_value_inputs)
        layout.addWidget(self.solid_combo)
        return container

    def _build_canvas_panel(self) -> QWidget:
        group = QGroupBox("Visualization")
        layout = QVBoxLayout(group)
        layout.addWidget(self.canvas)
        layout.addWidget(self._build_view_controls())
        hint = QLabel("Blue = connection family, Green = face circuit, Red = selected transition")
        hint.setStyleSheet("color: #475569; font-style: italic;")
        layout.addWidget(hint)
        return group

    def _build_view_controls(self) -> QWidget:
        controls = QGroupBox("View Controls")
        layout = QGridLayout(controls)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(8)

        az_label = QLabel("Horizontal")
        az_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(az_label, 0, 0)

        self.azimuth_slider = QSlider(Qt.Orientation.Horizontal)
        self.azimuth_slider.setRange(-180, 180)
        self.azimuth_slider.setSingleStep(1)
        self.azimuth_slider.setPageStep(15)
        self.azimuth_slider.valueChanged.connect(self._handle_azimuth_slider_changed)
        layout.addWidget(self.azimuth_slider, 0, 1)

        el_label = QLabel("Vertical")
        el_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(el_label, 1, 0)

        self.elevation_slider = QSlider(Qt.Orientation.Horizontal)
        self.elevation_slider.setRange(-85, 85)
        self.elevation_slider.setSingleStep(1)
        self.elevation_slider.setPageStep(10)
        self.elevation_slider.valueChanged.connect(self._handle_elevation_slider_changed)
        layout.addWidget(self.elevation_slider, 1, 1)

        reset_btn = QPushButton("Reset View")
        reset_btn.clicked.connect(self._handle_reset_view)
        layout.addWidget(reset_btn, 2, 0, 1, 2)

        self._sync_rotation_controls(self.canvas.rotation_y, self.canvas.rotation_x)

        return controls

    def _sync_rotation_controls(self, yaw: float, pitch: float):
        if self.azimuth_slider is not None:
            self.azimuth_slider.blockSignals(True)
            self.azimuth_slider.setValue(int(round(yaw)))
            self.azimuth_slider.blockSignals(False)
        if self.elevation_slider is not None:
            self.elevation_slider.blockSignals(True)
            self.elevation_slider.setValue(int(round(pitch)))
            self.elevation_slider.blockSignals(False)

    def _handle_canvas_rotation_changed(self, yaw: float, pitch: float):
        self._sync_rotation_controls(yaw, pitch)

    def _handle_azimuth_slider_changed(self, value: int):
        self.canvas.set_rotation(yaw=float(value))

    def _handle_elevation_slider_changed(self, value: int):
        self.canvas.set_rotation(pitch=float(value))

    def _handle_reset_view(self):
        self.canvas.reset_view()

    def _build_results_panel(self) -> QWidget:
        group = QGroupBox("Transition Families")
        layout = QVBoxLayout(group)
        controls = QHBoxLayout()
        self.copy_btn = QPushButton("Copy Tables")
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 6px 12px; border-radius: 6px;")
        self.copy_btn.clicked.connect(self._copy_results_to_clipboard)
        controls.addWidget(self.copy_btn)
        controls.addStretch()
        layout.addLayout(controls)

        self.tabs.currentChanged.connect(self._handle_tab_changed)
        layout.addWidget(self.tabs)
        return group

    # -- Actions ---------------------------------------------------------

    def _refresh_value_inputs(self):
        solid_key = self.solid_combo.currentData(Qt.ItemDataRole.UserRole)
        preview = PlatonicTransitionService.build_geometry(solid_key)
        self._clear_value_inputs()
        self.value_inputs = []
        self.vertex_hints = []
        for row, vertex in enumerate(preview.vertices):
            hint = QLabel(f"{vertex.label}  ({vertex.position[0]:.2f}, {vertex.position[1]:.2f}, {vertex.position[2]:.2f})")
            hint.setStyleSheet("color: #475569;")
            input_field = QLineEdit()
            input_field.setPlaceholderText(str(vertex.value))
            input_field.setMaximumWidth(120)
            self.values_layout.addWidget(hint, row, 0)
            self.values_layout.addWidget(input_field, row, 1)
            self.value_inputs.append(input_field)
            self.vertex_hints.append(hint)
        self.vertex_stats_label.setText(f"Vertices: {len(preview.vertices)} • Faces: {len(preview.faces)}")
        self.canvas.set_geometry(preview.vertices, preview.edges)
        self.family_lookup = {}
        self.face_patterns = []
        self.tabs.clear()
        self.copy_btn.setEnabled(False)

    def _clear_value_inputs(self):
        while self.values_layout.count():
            item = self.values_layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _handle_generate(self):
        solid_key = self.solid_combo.currentData(Qt.ItemDataRole.UserRole)
        values: List[int] = []
        for idx, widget in enumerate(self.value_inputs):
            text = widget.text().strip()
            if text:
                try:
                    values.append(int(text))
                except ValueError:
                    values.append(idx + 1)
            else:
                values.append(idx + 1)
        geometry = PlatonicTransitionService.build_geometry(solid_key, values)
        self.current_geometry = geometry
        self.canvas.set_geometry(geometry.vertices, geometry.edges)

        families = PlatonicTransitionService.generate_families(geometry)
        self.family_lookup = {group.key: group for group in families}
        self._populate_family_tabs(families)

        self.face_patterns = PlatonicTransitionService.generate_face_sequences(geometry)
        self._ensure_face_tab()

        self.copy_btn.setEnabled(bool(families) or bool(self.face_patterns))

    def _handle_clear(self):
        for widget in self.value_inputs:
            widget.clear()
        self.current_geometry = None
        self.family_lookup = {}
        self.face_patterns = []
        self.canvas.set_geometry([], [])
        self.tabs.clear()
        self.copy_btn.setEnabled(False)

    def _populate_family_tabs(self, families: List[SolidFamilyGroup]):
        self.tabs.blockSignals(True)
        self.tabs.clear()
        self.face_tab_index = None
        self.face_combo = None
        self.face_table = None
        self.face_summary_label = None
        font = QFont()
        font.setPointSize(10)
        for group in families:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            summary_label = QLabel(self._format_summary_text(group.summary))
            summary_label.setStyleSheet("color: #475569; font-style: italic;")
            summary_label.setProperty("family_key", group.key)
            summary_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            summary_label.customContextMenuRequested.connect(
                lambda pos, key=group.key, label=summary_label: self._show_family_summary_menu(key, label, pos)
            )
            tab_layout.addWidget(summary_label)

            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels([
                "From",
                "To",
                "From Value",
                "To Value",
                "Result (Ternary)",
                "Result (Decimal)",
            ])
            header = table.verticalHeader()
            if header is not None:
                header.setVisible(False)
            table.setRowCount(len(group.transitions))
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setStyleSheet("font-family: 'JetBrains Mono', monospace;")
            table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            table.customContextMenuRequested.connect(
                lambda pos, tbl=table: self._show_result_context_menu(tbl, pos)
            )

            for row, transition in enumerate(group.transitions):
                table.setItem(row, 0, QTableWidgetItem(str(transition.from_index + 1)))
                table.setItem(row, 1, QTableWidgetItem(str(transition.to_index + 1)))
                table.setItem(row, 2, QTableWidgetItem(f"{transition.from_value} ({transition.from_ternary})"))
                table.setItem(row, 3, QTableWidgetItem(f"{transition.to_value} ({transition.to_ternary})"))
                table.setItem(row, 4, QTableWidgetItem(transition.result_ternary))
                table.setItem(row, 5, QTableWidgetItem(str(transition.result_decimal)))

            table.itemSelectionChanged.connect(
                lambda key=group.key, tbl=table: self._handle_family_selection(key, tbl)
            )
            table.resizeColumnsToContents()
            tab_layout.addWidget(table)
            tab.setProperty("family_key", group.key)
            self.tabs.addTab(tab, group.label)
        self.tabs.blockSignals(False)

    def _ensure_face_tab(self):
        if self.face_tab_index is not None:
            self.tabs.removeTab(self.face_tab_index)
        self.face_tab_index = None
        self.face_combo = None
        self.face_table = None
        self.face_summary_label = None
        if not self.face_patterns:
            self.canvas.set_pattern_segments([])
            return

        widget = QWidget()
        layout = QVBoxLayout(widget)
        info = QLabel("Face-level perimeter traversals")
        info.setStyleSheet("color: #475569; font-style: italic;")
        layout.addWidget(info)

        self.face_summary_label = QLabel()
        self.face_summary_label.setStyleSheet("color: #475569; font-style: italic;")
        self.face_summary_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.face_summary_label.customContextMenuRequested.connect(self._show_face_summary_menu)
        layout.addWidget(self.face_summary_label)

        self.face_combo = QComboBox()
        for pattern in self.face_patterns:
            self.face_combo.addItem(str(pattern.get("name", "Face")))
        self.face_combo.currentIndexChanged.connect(self._handle_face_combo_changed)
        layout.addWidget(self.face_combo)

        self.face_table = QTableWidget()
        self.face_table.setColumnCount(6)
        self.face_table.setHorizontalHeaderLabels([
            "From",
            "To",
            "From Value",
            "To Value",
            "Result (Ternary)",
            "Result (Decimal)",
        ])
        if self.face_table is not None:
            header = self.face_table.verticalHeader()
            if header is not None:
                header.setVisible(False)
        self.face_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.face_table.setStyleSheet("font-family: 'JetBrains Mono', monospace;")
        self.face_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.face_table.customContextMenuRequested.connect(
            lambda pos, tbl=self.face_table: self._show_result_context_menu(tbl, pos)
        )
        self.face_table.itemSelectionChanged.connect(self._handle_face_selection)
        layout.addWidget(self.face_table)

        self.face_tab_index = self.tabs.addTab(widget, "Face Circuits")
        self.tabs.setTabToolTip(self.face_tab_index, "Traverse each face perimeter")
        self._populate_face_table(0)

    def _populate_face_table(self, index: int):
        if not self.face_patterns or not self.face_table:
            return
        if index < 0 or index >= len(self.face_patterns):
            self.face_table.setRowCount(0)
            self.canvas.set_pattern_segments([])
            if self.face_summary_label:
                self.face_summary_label.setText("")
            return
        pattern = self.face_patterns[index]
        transitions: List[SolidTransition3D] = pattern.get("transitions", [])  # type: ignore[arg-type]
        self.face_table.setRowCount(len(transitions))
        for row, transition in enumerate(transitions):
            self.face_table.setItem(row, 0, QTableWidgetItem(str(transition.from_index + 1)))
            self.face_table.setItem(row, 1, QTableWidgetItem(str(transition.to_index + 1)))
            self.face_table.setItem(row, 2, QTableWidgetItem(f"{transition.from_value} ({transition.from_ternary})"))
            self.face_table.setItem(row, 3, QTableWidgetItem(f"{transition.to_value} ({transition.to_ternary})"))
            self.face_table.setItem(row, 4, QTableWidgetItem(transition.result_ternary))
            self.face_table.setItem(row, 5, QTableWidgetItem(str(transition.result_decimal)))
        segments = self._extract_segments(pattern.get("segments"))
        self.canvas.set_pattern_segments(segments)
        summary_obj = pattern.get("summary")
        summary = summary_obj if isinstance(summary_obj, dict) else {}
        if self.face_summary_label:
            self.face_summary_label.setText(self._format_summary_text(summary))
            self.face_summary_label.setProperty("face_index", index)

    # -- Event handlers --------------------------------------------------

    def _handle_tab_changed(self, index: int):
        if index < 0:
            return
        if self.face_tab_index is not None and index == self.face_tab_index:
            current = self.face_combo.currentIndex() if self.face_combo else -1
            self.canvas.set_family_segments([])
            if current >= 0:
                self._populate_face_table(current)
            return
        self.canvas.set_pattern_segments([])
        tab = self.tabs.widget(index)
        if not tab:
            self.canvas.set_family_segments([])
            self.canvas.set_transition(None)
            return
        key = tab.property("family_key")
        if not key:
            self.canvas.set_family_segments([])
            self.canvas.set_transition(None)
            return
        group = self.family_lookup.get(key)
        if not group:
            self.canvas.set_family_segments([])
            self.canvas.set_transition(None)
            return
        self.canvas.set_family_segments(group.segments)
        self.canvas.set_transition(None)

    def _handle_family_selection(self, family_key: str, table: QTableWidget):
        group = self.family_lookup.get(family_key)
        if not group:
            self.canvas.set_transition(None)
            return
        selected = table.selectedItems()
        if not selected:
            self.canvas.set_transition(None)
            self.canvas.set_family_segments(group.segments)
            return
        row = selected[0].row()
        if 0 <= row < len(group.transitions):
            self.canvas.set_transition(group.transitions[row])
        else:
            self.canvas.set_transition(None)

    def _handle_face_combo_changed(self, index: int):
        if self.face_table:
            self.face_table.clearSelection()
        self._populate_face_table(index)

    def _handle_face_selection(self):
        if not self.face_table or not self.face_patterns:
            return
        selected = self.face_table.selectedItems()
        if not selected:
            self.canvas.set_transition(None)
            current = self.face_combo.currentIndex() if self.face_combo else -1
            if current >= 0 and current < len(self.face_patterns):
                segments_obj = self.face_patterns[current].get("segments")
                self.canvas.set_pattern_segments(self._extract_segments(segments_obj))
            return
        row = selected[0].row()
        current = self.face_combo.currentIndex() if self.face_combo else -1
        if current < 0 or current >= len(self.face_patterns):
            return
        transitions: List[SolidTransition3D] = self.face_patterns[current].get("transitions", [])  # type: ignore[arg-type]
        if 0 <= row < len(transitions):
            self.canvas.set_transition(transitions[row])

    # -- Context menu helpers -------------------------------------------

    def _show_result_context_menu(self, table: QTableWidget, position):
        if not table:
            return
        item = table.itemAt(position)
        if not item or item.column() != self.RESULT_COLUMN_INDEX:
            return
        numeric_value = self._parse_numeric_value(item.text())
        if numeric_value is None:
            return
        menu = QMenu(table)
        self._style_result_menu(menu)
        send_action = QAction("Send to Quadset Analysis", menu)
        send_action.triggered.connect(lambda _, value=numeric_value: self._send_value_to_quadset(value))
        lookup_action = QAction("Look up in Database", menu)
        lookup_action.triggered.connect(lambda _, value=numeric_value: self._lookup_value_in_database(value))
        if not self.window_manager:
            send_action.setEnabled(False)
            lookup_action.setEnabled(False)
        menu.addAction(send_action)
        menu.addAction(lookup_action)
        viewport = table.viewport()
        if viewport:
            menu.exec(viewport.mapToGlobal(position))

    def _show_family_summary_menu(self, family_key: str, label: QLabel, position):
        group = self.family_lookup.get(family_key)
        if not group:
            return
        numeric_value = self._coerce_float(group.summary.get("sum_result"))
        if numeric_value is None:
            return
        menu = QMenu(label)
        self._style_result_menu(menu)
        send_action = QAction("Send to Quadset Analysis", menu)
        send_action.triggered.connect(lambda _, value=numeric_value: self._send_value_to_quadset(value))
        lookup_action = QAction("Look up in Database", menu)
        lookup_action.triggered.connect(lambda _, value=numeric_value: self._lookup_value_in_database(value))
        if not self.window_manager:
            send_action.setEnabled(False)
            lookup_action.setEnabled(False)
        menu.addAction(send_action)
        menu.addAction(lookup_action)
        menu.exec(label.mapToGlobal(position))

    def _show_face_summary_menu(self, position):
        if not self.face_summary_label or not self.face_patterns:
            return
        index = self.face_summary_label.property("face_index")
        if index is None:
            return
        try:
            idx = int(index)
        except (TypeError, ValueError):
            return
        if idx < 0 or idx >= len(self.face_patterns):
            return
        pattern = self.face_patterns[idx]
        summary = pattern.get("summary")
        if not isinstance(summary, dict):
            return
        numeric_value = self._coerce_float(summary.get("sum_result"))
        if numeric_value is None:
            return
        menu = QMenu(self.face_summary_label)
        self._style_result_menu(menu)
        send_action = QAction("Send to Quadset Analysis", menu)
        send_action.triggered.connect(lambda _, value=numeric_value: self._send_value_to_quadset(value))
        lookup_action = QAction("Look up in Database", menu)
        lookup_action.triggered.connect(lambda _, value=numeric_value: self._lookup_value_in_database(value))
        if not self.window_manager:
            send_action.setEnabled(False)
            lookup_action.setEnabled(False)
        menu.addAction(send_action)
        menu.addAction(lookup_action)
        menu.exec(self.face_summary_label.mapToGlobal(position))

    @staticmethod
    def _style_result_menu(menu: QMenu):
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 6px 16px;
            }
            QMenu::item:selected {
                background-color: #e0e7ff;
                color: #1d4ed8;
            }
            """
        )

    # -- Utilities -------------------------------------------------------

    @staticmethod
    def _parse_numeric_value(text: str) -> Optional[float]:
        if not text:
            return None
        try:
            return float(text)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_summary_text(summary: Optional[Dict[str, object]]) -> str:
        if not isinstance(summary, dict):
            summary = {}
        mean = summary.get("mean_result") or 0
        return (
            "Count: {count} | Sum: {total} | Mean: {mean:.2f} | Range: {min_val} – {max_val} | Unique: {unique}"
        ).format(
            count=summary.get("count", 0),
            total=summary.get("sum_result", 0),
            mean=mean,
            min_val=summary.get("min_result", 0),
            max_val=summary.get("max_result", 0),
            unique=summary.get("unique_results", 0),
        )

    @staticmethod
    def _coerce_float(value: object) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_segments(value: object) -> List[tuple[int, int]]:
        segments: List[tuple[int, int]] = []
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for entry in value:
                if (
                    isinstance(entry, Sequence)
                    and not isinstance(entry, (str, bytes))
                    and len(entry) == 2
                ):
                    start, end = entry
                    if isinstance(start, int) and isinstance(end, int):
                        segments.append((start, end))
        return segments

    def _copy_results_to_clipboard(self):
        if not self.family_lookup and not self.face_patterns:
            return
        lines = [
            "Family\tFrom\tTo\tFrom Value\tTo Value\tResult (Ternary)\tResult (Decimal)"
        ]
        ordered_groups = sorted(self.family_lookup.values(), key=lambda group: group.distance)
        for group in ordered_groups:
            for transition in group.transitions:
                lines.append(
                    "\t".join(
                        [
                            group.label,
                            str(transition.from_index + 1),
                            str(transition.to_index + 1),
                            f"{transition.from_value} ({transition.from_ternary})",
                            f"{transition.to_value} ({transition.to_ternary})",
                            transition.result_ternary,
                            str(transition.result_decimal),
                        ]
                    )
                )
            if group.summary:
                lines.append(
                    "\t".join(
                        [
                            group.label,
                            "",
                            "",
                            "",
                            "",
                            "",
                            str(group.summary.get("sum_result", "")),
                        ]
                    )
                )
        if self.face_patterns:
            for pattern in self.face_patterns:
                name = str(pattern.get("name", "Face"))
                transitions: List[SolidTransition3D] = pattern.get("transitions", [])  # type: ignore[arg-type]
                for transition in transitions:
                    lines.append(
                        "\t".join(
                            [
                                f"{name} Circuit",
                                str(transition.from_index + 1),
                                str(transition.to_index + 1),
                                f"{transition.from_value} ({transition.from_ternary})",
                                f"{transition.to_value} ({transition.to_ternary})",
                                transition.result_ternary,
                                str(transition.result_decimal),
                            ]
                        )
                    )
                summary_obj = pattern.get("summary")
                summary = summary_obj if isinstance(summary_obj, dict) else {}
                if summary:
                    lines.append(
                        "\t".join(
                            [
                                f"{name} Circuit",
                                "",
                                "",
                                "",
                                "",
                                "",
                                str(summary.get("sum_result", "")),
                            ]
                        )
                    )
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText("\n".join(lines))

    def _send_value_to_quadset(self, value: float):
        if not self.window_manager:
            return
        from .quadset_analysis_window import QuadsetAnalysisWindow

        rounded = int(round(value))
        window = self.window_manager.open_window(
            "quadset_analysis",
            QuadsetAnalysisWindow,
        )
        if not window:
            return
        input_field = getattr(window, "input_field", None)
        if input_field is not None:
            input_field.setText(str(rounded))
            window.raise_()
            window.activateWindow()

    def _lookup_value_in_database(self, value: float):
        if not self.window_manager:
            return
        from pillars.gematria.ui.saved_calculations_window import SavedCalculationsWindow

        rounded = int(round(value))
        window = self.window_manager.open_window(
            "saved_calculations",
            SavedCalculationsWindow,
            allow_multiple=False,
        )
        if not window:
            return
        value_field = getattr(window, "value_input", None)
        if value_field is not None:
            value_field.setText(str(rounded))
        search_method = getattr(window, "_search", None)
        if callable(search_method):
            search_method()
        window.raise_()
        window.activateWindow()


__all__ = ["GeometricTransitions3DWindow"]
