"""Geometric transitions analysis window."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QAction, QFont, QPainter, QPen, QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QMainWindow,
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
)

from ..services.geometric_transition_service import (
    GeometricTransitionService,
    Transition,
    Vertex,
)
from .quadset_analysis_window import SubstrateWidget
from shared.ui.theme import COLORS
from shared.signals.navigation_bus import navigation_bus


class GeometricCanvas(QWidget):
    """Simple polygon renderer with optional highlighted transitions."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(320, 320)
        self.vertices: List[Vertex] = []
        self.highlight_skip: Optional[int] = None
        self.highlight_pair: Optional[Transition] = None
        self.special_segments: List[tuple[int, int]] = []

    def set_vertices(self, vertices: List[Vertex]):
        self.vertices = vertices
        self.update()

    def set_highlight(self, skip: Optional[int], transition: Optional[Transition]):
        self.highlight_skip = skip
        self.highlight_pair = transition
        self.update()

    def set_special_segments(self, segments: Optional[List[tuple[int, int]]]):
        self.special_segments = segments or []
        self.update()

    def paintEvent(self, a0):  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#ffffff"))

        if not self.vertices:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data")
            return

        points = [self._map_to_widget(v.x, v.y) for v in self.vertices]

        # Draw polygon perimeter
        pen = QPen(QColor("#9ca3af"), 2)
        painter.setPen(pen)
        painter.drawPolygon(*points)

        # Draw special pattern first so other highlights can sit atop
        if self.special_segments:
            special_pen = QPen(QColor("#10b981"), 3, Qt.PenStyle.DashLine)
            painter.setPen(special_pen)
            for start_idx, end_idx in self.special_segments:
                if 0 <= start_idx < len(points) and 0 <= end_idx < len(points):
                    painter.drawLine(points[start_idx], points[end_idx])

        # Highlight skip group edges
        if self.highlight_skip:
            group_pen = QPen(QColor("#2563eb"), 3)
            painter.setPen(group_pen)
            sides = len(self.vertices)
            for idx, point in enumerate(points):
                target_idx = (idx + self.highlight_skip) % sides
                target_point = points[target_idx]
                painter.drawLine(point, target_point)

        # Highlight single transition on top
        if self.highlight_pair:
            strong_pen = QPen(QColor("#ef4444"), 4)
            painter.setPen(strong_pen)
            start = points[self.highlight_pair.from_index]
            end = points[self.highlight_pair.to_index]
            painter.drawLine(start, end)

        # Draw vertex labels after everything else
        label_pen = QPen(QColor("#111827"))
        painter.setPen(label_pen)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        for vertex, point in zip(self.vertices, points):
            painter.drawEllipse(point, 6, 6)
            painter.drawText(
                point + QPointF(8, -8),
                str(vertex.value),
            )

    def _map_to_widget(self, x: float, y: float) -> QPointF:
        """Map unit circle coordinates to widget coordinates."""
        w = self.width()
        h = self.height()
        margin = 30
        scale = min((w - margin * 2) / 2, (h - margin * 2) / 2)
        cx = w / 2
        cy = h / 2
        return QPointF(cx + x * scale, cy - y * scale)


class GeometricTransitionsWindow(QMainWindow):
    """Main window coordinating polygon transitions."""

    RESULT_COLUMN_INDEX = 5

    def __init__(self, window_manager=None, parent: Optional[QWidget] = None, initial_values: Optional[List[int]] = None, **kwargs):
        super().__init__(parent)
        self.window_manager = window_manager
        self.service = GeometricTransitionService()
        self.vertices: List[Vertex] = []
        self.group_data: Dict[int, Dict[str, object]] = {}
        self.special_patterns: List[Dict[str, object]] = []

        self.shape_combo: QComboBox
        self.max_skip_spin: QSpinBox
        self.value_inputs: List[QLineEdit] = []
        self.canvas = GeometricCanvas()
        # Vertical tab pattern: sidebar + stack
        self.results_sidebar = QListWidget()
        self.results_stack = QStackedWidget()
        self.results_pages: List[QWidget] = []
        self.copy_btn: QPushButton | None = None
        self.special_combo: QComboBox | None = None
        self.special_table: QTableWidget | None = None
        self.special_tab_index: int | None = None
        self.special_summary_label: QLabel | None = None

        self._setup_ui()
        self._refresh_value_inputs()
        
        if initial_values:
            # Auto-select shape based on length using itemData
            count = len(initial_values)
            for i in range(self.shape_combo.count()):
                if self.shape_combo.itemData(i) == count:
                    self.shape_combo.setCurrentIndex(i)
                    break
            
            # Refresh happens via signal, but let's force populate
            # We wait for signal or do it manually? 
            # Signal is synchronous usually.
            
            for i, val in enumerate(initial_values):
                if i < len(self.value_inputs):
                    self.value_inputs[i].setText(str(val))

    # -- UI setup --------------------------------------------------------

    def _setup_ui(self):
        self.setWindowTitle("Geometric Transitions")
        self.setMinimumSize(1200, 700)

        # Level 0: The Substrate
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        bg_path = os.path.join(base_path, "assets", "textures", "quadset_substrate.png")
        
        central = SubstrateWidget(bg_path)
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setSpacing(20)
        root_layout.setContentsMargins(24, 24, 24, 24)

        controls = self._build_left_controls()
        canvas_group = self._build_canvas_section()
        results = self._build_results_section()

        root_layout.addWidget(controls, 2)
        root_layout.addWidget(canvas_group, 3)
        root_layout.addWidget(results, 4)

    def _create_card(self, title: str = "") -> QFrame:
        """Create a styled card container with drop shadow."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        card.setGraphicsEffect(shadow)
        
        return card

    def _build_left_controls(self) -> QWidget:
        card = self._create_card()
        layout = QVBoxLayout(card)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QLabel("CONFIGURATION")
        header.setStyleSheet(f"""
            font-weight: 800; 
            font-size: 11pt; 
            color: {COLORS['text_secondary']}; 
            letter-spacing: 2px;
        """)
        layout.addWidget(header)

        # Shape selector
        shape_label = QLabel("Polygon")
        shape_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_secondary']};")
        layout.addWidget(shape_label)

        self.shape_combo = QComboBox()
        for option in self.service.get_polygon_options():
            self.shape_combo.addItem(
                f"{option['sides']} - {option['name']}",
                option['sides'],
            )
        self.shape_combo.currentIndexChanged.connect(self._refresh_value_inputs)
        layout.addWidget(self.shape_combo)

        # Max skip spinner
        skip_label = QLabel("Max Skip Group")
        skip_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_secondary']};")
        layout.addWidget(skip_label)

        self.max_skip_spin = QSpinBox()
        self.max_skip_spin.setMinimum(1)
        self.max_skip_spin.setMaximum(self.service.MAX_SKIP_GROUPS)
        self.max_skip_spin.setValue(6)
        layout.addWidget(self.max_skip_spin)

        # Values input area inside scroll
        values_label = QLabel("Vertex Values")
        values_label.setStyleSheet(f"font-weight: 600; color: {COLORS['text_secondary']};")
        layout.addWidget(values_label)

        self.values_container = QWidget()
        self.values_layout = QGridLayout(self.values_container)
        self.values_layout.setColumnStretch(1, 1)
        values_scroll = QScrollArea()
        values_scroll.setWidgetResizable(True)
        values_scroll.setWidget(self.values_container)
        values_scroll.setMinimumHeight(200)
        values_scroll.setStyleSheet(f"background-color: {COLORS['background_alt']}; border-radius: 6px;")
        layout.addWidget(values_scroll)

        # Buttons
        buttons_layout = QHBoxLayout()
        generate_btn = QPushButton("Generate")
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['magus']};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['magus_hover']};
            }}
        """)
        generate_btn.clicked.connect(self._handle_generate)
        buttons_layout.addWidget(generate_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['navigator']};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['navigator_hover']};
            }}
        """)
        clear_btn.clicked.connect(self._handle_clear)
        buttons_layout.addWidget(clear_btn)
        layout.addLayout(buttons_layout)

        layout.addStretch(1)
        return card

    def _build_canvas_section(self) -> QWidget:
        # Canvas displayed directly without card wrapper
        self.canvas.setStyleSheet(f"""
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        """)
        return self.canvas

    def _build_results_section(self) -> QWidget:
        card = self._create_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header row with title and copy button
        header_layout = QHBoxLayout()
        header = QLabel("SKIP GROUPS")
        header.setStyleSheet(f"""
            font-weight: 800; 
            font-size: 11pt; 
            color: {COLORS['text_secondary']}; 
            letter-spacing: 2px;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFixedHeight(28)
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['scribe']};
                color: #ffffff;
                font-weight: bold;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {COLORS['scribe_hover']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_disabled']};
            }}
        """)
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._copy_results_to_clipboard)
        header_layout.addWidget(self.copy_btn)
        layout.addLayout(header_layout)
        
        # Horizontal split: sidebar on left, content on right
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        
        # Sidebar
        self.results_sidebar.setFixedWidth(100)
        self.results_sidebar.setFrameShape(QFrame.Shape.NoFrame)
        self.results_sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['background_alt']};
                border: none;
                border-radius: 6px;
                outline: none;
            }}
            QListWidget::item {{
                height: 36px;
                padding: 8px;
                color: {COLORS['text_secondary']};
                border-left: 3px solid transparent;
            }}
            QListWidget::item:selected {{
                color: {COLORS['text_primary']};
                background-color: {COLORS['surface']};
                border-left: 3px solid {COLORS['primary']};
                font-weight: bold;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        self.results_sidebar.currentRowChanged.connect(self._handle_tab_changed)
        content_layout.addWidget(self.results_sidebar)
        
        # Stacked content
        content_layout.addWidget(self.results_stack)
        layout.addLayout(content_layout)

        return card

    # -- Actions ---------------------------------------------------------

    def _refresh_value_inputs(self):
        """Rebuild value inputs based on selected polygon."""
        while self.values_layout.count():
            item = self.values_layout.takeAt(0)
            if not item:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.value_inputs.clear()
        sides = self.shape_combo.currentData(Qt.ItemDataRole.UserRole)
        if sides is None:
            sides = GeometricTransitionService.MIN_SIDES

        for idx in range(int(sides)):
            label = QLabel(str(idx + 1))
            input_field = QLineEdit()
            input_field.setPlaceholderText(str(idx + 1))
            input_field.setMaximumWidth(80)
            self.values_layout.addWidget(label, idx, 0)
            self.values_layout.addWidget(input_field, idx, 1)
            self.value_inputs.append(input_field)

    def _handle_generate(self):
        sides = int(self.shape_combo.currentData(Qt.ItemDataRole.UserRole))
        max_skip = int(self.max_skip_spin.value())

        values = []
        for idx, widget in enumerate(self.value_inputs):
            text = widget.text().strip()
            if text:
                try:
                    values.append(int(text))
                except ValueError:
                    values.append(idx + 1)
            else:
                values.append(idx + 1)

        self.vertices = self.service.build_vertices(sides, values)
        self.canvas.set_vertices(self.vertices)

        groups = self.service.generate_skip_groups(self.vertices, max_skip)
        self.group_data = {}
        for group in groups:
            skip_value = group.get("skip") if isinstance(group, dict) else None
            if isinstance(skip_value, int):
                self.group_data[skip_value] = group
        self._populate_tabs(groups)
        if self.copy_btn:
            self.copy_btn.setEnabled(bool(groups))

        self.special_patterns = self.service.generate_special_sequences(self.vertices)
        self._ensure_special_tab()

    def _handle_clear(self):
        for widget in self.value_inputs:
            widget.clear()
        self.vertices = []
        self.group_data = {}
        # Clear sidebar and stack
        self.results_sidebar.clear()
        while self.results_stack.count() > 0:
            widget = self.results_stack.widget(0)
            self.results_stack.removeWidget(widget)
            widget.deleteLater()
        self.results_pages.clear()
        self.canvas.set_vertices([])
        self.canvas.set_highlight(None, None)
        self.canvas.set_special_segments(None)
        if self.copy_btn:
            self.copy_btn.setEnabled(False)
        self.special_patterns = []
        self._remove_special_tab()

    def _populate_tabs(self, groups: List[Dict[str, object]]):
        self.results_sidebar.blockSignals(True)
        # Clear existing
        self.results_sidebar.clear()
        while self.results_stack.count() > 0:
            widget = self.results_stack.widget(0)
            self.results_stack.removeWidget(widget)
            widget.deleteLater()
        self.results_pages.clear()
        self.special_tab_index = None
        self.special_combo = None
        self.special_table = None
        self.special_summary_label = None
        font = QFont()
        font.setPointSize(10)

        for group in groups:
            if not isinstance(group, dict):
                continue
            skip_value = group.get("skip")
            if not isinstance(skip_value, int):
                continue
            skip = skip_value
            transitions_raw = group.get("transitions", [])
            transitions: List[Transition] = (
                transitions_raw if isinstance(transitions_raw, list) else []
            )
            summary_raw = group.get("summary", {})
            summary: Dict[str, object] = (
                summary_raw if isinstance(summary_raw, dict) else {}
            )

            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            summary_widget = QLabel(self._format_summary_text(summary))
            summary_widget.setObjectName("summary_label")
            summary_widget.setProperty("skip_value", skip)
            summary_widget.setStyleSheet("color: #4b5563; font-style: italic;")
            summary_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            summary_widget.customContextMenuRequested.connect(
                lambda pos, label=summary_widget: self._show_summary_context_menu(label, pos)
            )
            tab_layout.addWidget(summary_widget)

            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(
                [
                    "From",
                    "To",
                    "From Value",
                    "To Value",
                    "Result (Ternary)",
                    "Result (Decimal)",
                ]
            )
            vertical_header = table.verticalHeader()
            if vertical_header is not None:
                vertical_header.setVisible(False)
            table.setRowCount(len(transitions))
            table.setSortingEnabled(False)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setStyleSheet("font-family: 'JetBrains Mono', monospace;")
            table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            table.customContextMenuRequested.connect(
                lambda pos, tbl=table: self._show_result_context_menu(tbl, pos)
            )

            for row, transition in enumerate(transitions):
                table.setItem(row, 0, QTableWidgetItem(str(transition.from_index + 1)))
                table.setItem(row, 1, QTableWidgetItem(str(transition.to_index + 1)))

                from_item = QTableWidgetItem(
                    f"{transition.from_value} ({transition.from_ternary})"
                )
                to_item = QTableWidgetItem(
                    f"{transition.to_value} ({transition.to_ternary})"
                )
                table.setItem(row, 2, from_item)
                table.setItem(row, 3, to_item)

                table.setItem(row, 4, QTableWidgetItem(transition.result_ternary))
                table.setItem(row, 5, QTableWidgetItem(str(transition.result_decimal)))

            table.itemSelectionChanged.connect(
                lambda skip=skip, tbl=table: self._handle_table_selection(skip, tbl)
            )
            table.resizeColumnsToContents()
            tab_layout.addWidget(table)

            # Add to sidebar and stack
            item = QListWidgetItem(f"Skip {skip}")
            self.results_sidebar.addItem(item)
            self.results_stack.addWidget(tab)
            self.results_pages.append(tab)
            tab.setProperty("skip_value", skip)
        self.results_sidebar.blockSignals(False)
        if self.results_sidebar.count() > 0:
            self.results_sidebar.setCurrentRow(0)
        # Special tab added separately after skip tabs

    def _ensure_special_tab(self):
        self._remove_special_tab()
        if not self.special_patterns:
            self.canvas.set_special_segments(None)
            return

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        info_label = QLabel("Predefined star paths and custom diagonals.")
        info_label.setStyleSheet("color: #6b7280; font-style: italic;")
        layout.addWidget(info_label)

        self.special_summary_label = QLabel()
        self.special_summary_label.setStyleSheet("color: #4b5563; font-style: italic;")
        self.special_summary_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.special_summary_label.customContextMenuRequested.connect(
            lambda pos, lbl=self.special_summary_label: self._show_special_summary_context_menu(lbl, pos)
        )
        layout.addWidget(self.special_summary_label)

        self.special_combo = QComboBox()
        for pattern in self.special_patterns:
            self.special_combo.addItem(str(pattern.get("name", "Special")))
        self.special_combo.currentIndexChanged.connect(self._handle_special_changed)
        layout.addWidget(self.special_combo)

        self.special_table = QTableWidget()
        self.special_table.setColumnCount(6)
        self.special_table.setHorizontalHeaderLabels(
            [
                "From",
                "To",
                "From Value",
                "To Value",
                "Result (Ternary)",
                "Result (Decimal)",
            ]
        )
        if self.special_table.verticalHeader() is not None:
            self.special_table.verticalHeader().setVisible(False)
        self.special_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.special_table.setStyleSheet("font-family: 'JetBrains Mono', monospace;")
        layout.addWidget(self.special_table)

        # Add to sidebar and stack
        item = QListWidgetItem("Special")
        self.results_sidebar.addItem(item)
        self.special_tab_index = self.results_stack.addWidget(widget)
        self.results_pages.append(widget)
        self.results_sidebar.setCurrentRow(self.results_sidebar.count() - 1)
        self._populate_special_table(0)

    def _remove_special_tab(self):
        if self.special_tab_index is not None and self.special_tab_index < self.results_stack.count():
            widget = self.results_stack.widget(self.special_tab_index)
            if widget:
                self.results_stack.removeWidget(widget)
                widget.deleteLater()
            # Remove from sidebar
            if self.results_sidebar.count() > 0:
                last_item = self.results_sidebar.takeItem(self.results_sidebar.count() - 1)
                del last_item
            if len(self.results_pages) > self.special_tab_index:
                self.results_pages.pop(self.special_tab_index)
        self.special_tab_index = None
        self.special_combo = None
        self.special_table = None
        self.special_summary_label = None

    def _handle_special_changed(self, index: int):
        self._populate_special_table(index)

    def _populate_special_table(self, index: int):
        if (
            not self.special_patterns
            or not self.special_table
            or index < 0
            or index >= len(self.special_patterns)
        ):
            if self.special_table:
                self.special_table.setRowCount(0)
            self.canvas.set_special_segments(None)
            if self.special_summary_label:
                self.special_summary_label.setText("")
                self.special_summary_label.setProperty("special_sum", None)
            return

        pattern = self.special_patterns[index]
        transitions: List[Transition] = pattern.get("transitions", [])  # type: ignore[arg-type]
        self.special_table.setRowCount(len(transitions))
        for row, transition in enumerate(transitions):
            self.special_table.setItem(row, 0, QTableWidgetItem(str(transition.from_index + 1)))
            self.special_table.setItem(row, 1, QTableWidgetItem(str(transition.to_index + 1)))
            self.special_table.setItem(
                row,
                2,
                QTableWidgetItem(f"{transition.from_value} ({transition.from_ternary})"),
            )
            self.special_table.setItem(
                row,
                3,
                QTableWidgetItem(f"{transition.to_value} ({transition.to_ternary})"),
            )
            self.special_table.setItem(row, 4, QTableWidgetItem(transition.result_ternary))
            self.special_table.setItem(row, 5, QTableWidgetItem(str(transition.result_decimal)))

        segments = [(t.from_index, t.to_index) for t in transitions]
        self.canvas.set_special_segments(segments)

        summary = pattern.get("summary", {}) if isinstance(pattern, dict) else {}
        if self.special_summary_label:
            desc = str(pattern.get("description", "")).strip() if isinstance(pattern, dict) else ""
            summary_text = self._format_summary_text(summary)
            if desc:
                summary_text = f"{desc} — {summary_text}"
            self.special_summary_label.setText(summary_text)
            sum_value = summary.get("sum_result") if isinstance(summary, dict) else None
            self.special_summary_label.setProperty("special_sum", sum_value)

    @staticmethod
    def _format_summary_text(summary: Dict[str, object]) -> str:
        if not isinstance(summary, dict):
            summary = {}
        return (
            "Count: {count} | Sum: {total} | Mean Result: {mean:.2f} | Range: {min_val} – {max_val} | "
            "Unique Results: {unique}"
        ).format(
            count=summary.get('count', 0),
            total=summary.get('sum_result', 0),
            mean=summary.get('mean_result', 0.0) or 0.0,
            min_val=summary.get('min_result', 0),
            max_val=summary.get('max_result', 0),
            unique=summary.get('unique_results', 0),
        )

    def _handle_tab_changed(self, index: int):
        if index < 0:
            return
        # Update stack
        self.results_stack.setCurrentIndex(index)
        
        if self.special_tab_index is not None and index == self.special_tab_index:
            # When viewing special patterns, disable skip highlights and reapply current star
            self.canvas.set_highlight(None, None)
            current = self.special_combo.currentIndex() if self.special_combo else -1
            if current >= 0:
                self._populate_special_table(current)
            return

        # Leaving special tab should hide dashed overlays
        if self.special_tab_index is not None:
            self.canvas.set_special_segments(None)

        # Get the page widget
        if index < len(self.results_pages):
            tab = self.results_pages[index]
            skip = tab.property("skip_value")
            if skip is None:
                self.canvas.set_highlight(None, None)
                return
            self.canvas.set_highlight(skip, None)

    def _handle_table_selection(self, skip: int, table: QTableWidget):
        items = table.selectedItems()
        if not items:
            self.canvas.set_highlight(skip, None)
            return
        row = items[0].row()
        group = self.group_data.get(skip)
        transition: Optional[Transition] = None
        if group:
            transitions_raw = group.get("transitions", [])
            transitions: List[Transition] = (
                transitions_raw if isinstance(transitions_raw, list) else []
            )
            if 0 <= row < len(transitions):
                transition = transitions[row]
        self.canvas.set_highlight(skip, transition)

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
        send_action.triggered.connect(
            lambda _, value=numeric_value: self._send_value_to_quadset(value)
        )

        lookup_action = QAction("Look up in Database", menu)
        lookup_action.triggered.connect(
            lambda _, value=numeric_value: self._lookup_value_in_database(value)
        )

        if not self.window_manager:
            send_action.setEnabled(False)
            lookup_action.setEnabled(False)

        menu.addAction(send_action)
        menu.addAction(lookup_action)
        viewport = table.viewport()
        if viewport:
            menu.exec(viewport.mapToGlobal(position))

    def _show_summary_context_menu(self, label: QLabel, position):
        if not label:
            return
        skip = label.property("skip_value")
        if skip is None:
            return
        group = self.group_data.get(skip)
        if not group:
            return
        summary_obj = group.get("summary")
        if not isinstance(summary_obj, dict):
            return
        numeric_value = summary_obj.get("sum_result")
        if numeric_value is None:
            return
        menu = QMenu(label)
        self._style_result_menu(menu)

        send_action = QAction("Send to Quadset Analysis", menu)
        send_action.triggered.connect(
            lambda _, value=numeric_value: self._send_value_to_quadset(value)
        )

        lookup_action = QAction("Look up in Database", menu)
        lookup_action.triggered.connect(
            lambda _, value=numeric_value: self._lookup_value_in_database(value)
        )

        if not self.window_manager:
            send_action.setEnabled(False)
            lookup_action.setEnabled(False)

        menu.addAction(send_action)
        menu.addAction(lookup_action)
        menu.exec(label.mapToGlobal(position))

    def _show_special_summary_context_menu(self, label: QLabel, position):
        if not label:
            return
        numeric_value = label.property("special_sum")
        if numeric_value is None:
            return

        menu = QMenu(label)
        self._style_result_menu(menu)

        send_action = QAction("Send to Quadset Analysis", menu)
        send_action.triggered.connect(
            lambda _, value=numeric_value: self._send_value_to_quadset(value)
        )

        lookup_action = QAction("Look up in Database", menu)
        lookup_action.triggered.connect(
            lambda _, value=numeric_value: self._lookup_value_in_database(value)
        )

        if not self.window_manager:
            send_action.setEnabled(False)
            lookup_action.setEnabled(False)

        menu.addAction(send_action)
        menu.addAction(lookup_action)
        menu.exec(label.mapToGlobal(position))

    @staticmethod
    def _style_result_menu(menu: QMenu):
        if not menu:
            return
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #ffffff;
                color: #0f172a;
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
            QMenu::separator {
                height: 1px;
                margin: 4px 6px;
                background-color: #e2e8f0;
            }
            """
        )

    @staticmethod
    def _parse_numeric_value(text: str) -> Optional[float]:
        if not text:
            return None
        try:
            return float(text)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _round_cross_pillar_value(value: float) -> int:
        return int(round(value))

    def _send_value_to_quadset(self, value: float):
        rounded_value = self._round_cross_pillar_value(value)
        navigation_bus.request_window.emit(
            "tq_quadset_analysis",
            {
                "window_manager": self.window_manager,
                "initial_value": rounded_value
            }
        )

    def _lookup_value_in_database(self, value: float):
        rounded_value = self._round_cross_pillar_value(value)
        navigation_bus.request_window.emit(
            "gematria_saved_calculations",
            {
                "window_manager": self.window_manager,
                "initial_value": rounded_value,
                "allow_multiple": False 
            }
        )

    def _copy_results_to_clipboard(self):
        if not self.group_data and not self.special_patterns:
            return
        lines = [
            "Skip\tGroup\tFrom\tTo\tFrom Value\tTo Value\tResult (Ternary)\tResult (Decimal)"
        ]
        sorted_skips = sorted(self.group_data.keys())
        for skip in sorted_skips:
            group = self.group_data.get(skip)
            if not group:
                continue
            label = group.get("label", "")
            transitions_raw = group.get("transitions", [])
            transitions: List[Transition] = (
                transitions_raw if isinstance(transitions_raw, list) else []
            )
            summary_raw = group.get("summary", {})
            summary: Dict[str, object] = (
                summary_raw if isinstance(summary_raw, dict) else {}
            )

            for t in transitions:
                lines.append(
                    "\t".join(
                        [
                            str(skip),
                            str(label),
                            str(t.from_index + 1),
                            str(t.to_index + 1),
                            f"{t.from_value} ({t.from_ternary})",
                            f"{t.to_value} ({t.to_ternary})",
                            t.result_ternary,
                            str(t.result_decimal),
                        ]
                    )
                )

            if summary:
                lines.append(
                    "\t".join(
                        [
                            str(skip),
                            "Sum",
                            "",
                            "",
                            "",
                            "",
                            "",
                            str(summary.get("sum_result", "")),
                        ]
                    )
                )

        if self.special_patterns:
            for pattern in self.special_patterns:
                name = str(pattern.get("name", "Special"))
                transitions: List[Transition] = pattern.get("transitions", [])  # type: ignore[arg-type]
                summary: Dict[str, object] = (
                    pattern.get("summary", {})
                    if isinstance(pattern, dict)
                    else {}
                )

                for t in transitions:
                    lines.append(
                        "\t".join(
                            [
                                "Special",
                                name,
                                str(t.from_index + 1),
                                str(t.to_index + 1),
                                f"{t.from_value} ({t.from_ternary})",
                                f"{t.to_value} ({t.to_ternary})",
                                t.result_ternary,
                                str(t.result_decimal),
                            ]
                        )
                    )

                if summary:
                    lines.append(
                        "\t".join(
                            [
                                "Special",
                                f"{name} Sum",
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
