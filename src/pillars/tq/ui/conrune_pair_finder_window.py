"""UI for Conrune Pair Finder."""
from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ..services.conrune_pair_finder_service import (
    ConrunePair,
    ConrunePairFinderService,
)


class ConrunePairFinderWindow(QDialog):
    """Find Conrune pairs that match a target difference."""

    DECIMAL_COLUMN = 2

    def __init__(self, window_manager=None, parent: Optional[QDialog] = None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.service = ConrunePairFinderService()
        self.pairs: List[ConrunePair] = []
        self.expected_difference = 0
        self.calculated_difference = 0

        self.input_field: QLineEdit
        self.table: QTableWidget
        self.balanced_label: QLabel
        self.expected_diff_label: QLabel
        self.calculated_diff_label: QLabel
        self.status_label: QLabel
        self.copy_button: QPushButton

        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Conrune Pair Finder")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Conrune Pair Finder")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "Provide a differential value D. The tool converts D to balanced ternary, maps it to the"
            " original ternary pair (A) and its Conrune counterpart (B), then verifies |A - B| = D."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #6b7280;")
        layout.addWidget(desc)

        input_group = QGroupBox("Input")
        input_layout = QHBoxLayout(input_group)
        input_layout.setSpacing(12)

        input_label = QLabel("Decimal:")
        input_label.setStyleSheet("font-weight: bold;")
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter decimal number…")
        self.input_field.setFixedHeight(36)
        self.input_field.textChanged.connect(self._handle_input_change)

        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_field)

        layout.addWidget(input_group)

        balanced_group = QGroupBox("Balanced Ternary (from D)")
        balanced_layout = QVBoxLayout(balanced_group)
        self.balanced_label = QLabel("–")
        self.balanced_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.balanced_label.setStyleSheet("font-family: 'JetBrains Mono', monospace; font-size: 16pt;")
        balanced_layout.addWidget(self.balanced_label)
        layout.addWidget(balanced_group)

        table_group = QGroupBox("Pairs")
        table_layout = QVBoxLayout(table_group)

        self.table = QTableWidget(2, 3)
        self.table.setHorizontalHeaderLabels(["Pair", "Ternary", "Decimal"])
        vertical_header = self.table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        table_layout.addWidget(self.table)

        layout.addWidget(table_group)

        diff_group = QGroupBox("Difference Verification")
        diff_layout = QGridLayout(diff_group)
        diff_layout.setHorizontalSpacing(20)
        diff_layout.setVerticalSpacing(10)

        self.expected_diff_label = self._build_value_label(
            "Target Difference (|A - B|)", diff_layout, 0
        )
        self.calculated_diff_label = self._build_value_label(
            "Calculated |A - B|", diff_layout, 1
        )
        layout.addWidget(diff_group)

        self.status_label = QLabel("Enter a value to begin")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #6b7280; font-style: italic;")
        layout.addWidget(self.status_label)

        button_row = QHBoxLayout()
        self.send_button = QPushButton("Send to Quadset")
        self.send_button.setEnabled(False)
        self.send_button.setStyleSheet(
            """
            QPushButton {
                background-color: #10b981;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
            """
        )
        self.send_button.clicked.connect(self._send_first_pair_to_quadset)
        button_row.addWidget(self.send_button)

        self.copy_button = QPushButton("Copy Results")
        self.copy_button.setEnabled(False)
        self.copy_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
            """
        )
        self.copy_button.clicked.connect(self._copy_results)
        button_row.addWidget(self.copy_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

    def _build_value_label(self, title: str, layout: QGridLayout, row: int) -> QLabel:
        label_title = QLabel(title)
        label_title.setStyleSheet("font-weight: bold;")
        value_label = QLabel("–")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        value_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        value_label.customContextMenuRequested.connect(
            lambda pos, widget=value_label: self._show_diff_context_menu(widget, pos)
        )
        layout.addWidget(label_title, row, 0)
        layout.addWidget(value_label, row, 1)
        return value_label

    # ------------------------------------------------------------------
    def _handle_input_change(self, text: str):
        text = text.strip()
        if not text or text == "-":
            self._clear_results()
            return
        try:
            value = int(text)
        except ValueError:
            self._clear_results()
            return

        data = self.service.analyze(value)
        pairs_data = data.get("pairs")
        self.pairs = pairs_data if isinstance(pairs_data, list) else []
        balanced_value = data.get("balanced", "-")
        self.balanced_label.setText(str(balanced_value))

        expected_value = data.get("expected_difference")
        calculated_value = data.get("calculated_difference")
        self.expected_difference = expected_value if isinstance(expected_value, int) else 0
        self.calculated_difference = (
            calculated_value if isinstance(calculated_value, int) else 0
        )
        verified = bool(data.get("verified"))

        self._populate_table()
        self._populate_differences()

        if verified:
            self.status_label.setText("Verified: |A - B| matches the input difference")
            self.status_label.setStyleSheet("color: #15803d; font-weight: bold;")
        else:
            self.status_label.setText(
                "Warning: Calculated |A - B| does not match the input difference"
            )
            self.status_label.setStyleSheet("color: #dc2626; font-weight: bold;")

        enable_actions = bool(self.pairs)
        self.copy_button.setEnabled(enable_actions)
        self.send_button.setEnabled(enable_actions)

    def _clear_results(self):
        self.pairs = []
        self.expected_difference = 0
        self.calculated_difference = 0
        self.copy_button.setEnabled(False)
        self.send_button.setEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(2)
        self.table.setHorizontalHeaderLabels(["Pair", "Ternary", "Decimal"])
        self.balanced_label.setText("–")
        self.expected_diff_label.setText("–")
        self.calculated_diff_label.setText("–")
        self.status_label.setText("Enter a value to begin")
        self.status_label.setStyleSheet("color: #6b7280; font-style: italic;")

    def _populate_table(self):
        self.table.setRowCount(len(self.pairs))
        for row, pair in enumerate(self.pairs):
            self.table.setItem(row, 0, QTableWidgetItem(pair.label))
            self.table.setItem(row, 1, QTableWidgetItem(pair.ternary))
            self.table.setItem(row, 2, QTableWidgetItem(str(pair.decimal)))

        self.table.resizeColumnsToContents()

    def _populate_differences(self):
        self.expected_diff_label.setText(str(self.expected_difference) or "–")
        self.calculated_diff_label.setText(str(self.calculated_difference) or "–")

    # ------------------------------------------------------------------
    def _show_table_context_menu(self, position):
        item = self.table.itemAt(position)
        if not item or item.column() != self.DECIMAL_COLUMN:
            return
        numeric_value = self._parse_numeric_value(item.text())
        if numeric_value is None:
            return
        menu = QMenu(self.table)
        self._style_menu(menu)
        self._attach_menu_actions(menu, numeric_value)
        viewport = self.table.viewport()
        if viewport:
            menu.exec(viewport.mapToGlobal(position))

    def _show_diff_context_menu(self, label: QLabel, position):
        numeric_value = self._parse_numeric_value(label.text())
        if numeric_value is None:
            return
        menu = QMenu(label)
        self._style_menu(menu)
        self._attach_menu_actions(menu, numeric_value)
        menu.exec(label.mapToGlobal(position))

    def _attach_menu_actions(self, menu: QMenu, value: float):
        send_action = QAction("Send to Quadset Analysis", menu)
        send_action.triggered.connect(
            lambda _, val=value: self._send_value_to_quadset(val)
        )
        lookup_action = QAction("Look up in Database", menu)
        lookup_action.triggered.connect(
            lambda _, val=value: self._lookup_value_in_database(val)
        )
        if not self.window_manager:
            send_action.setEnabled(False)
            lookup_action.setEnabled(False)
        menu.addAction(send_action)
        menu.addAction(lookup_action)

    @staticmethod
    def _style_menu(menu: QMenu):
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
            """
        )

    # ------------------------------------------------------------------
    def _copy_results(self):
        if not self.pairs:
            return
        lines = ["Pair\tTernary\tDecimal"]
        for pair in self.pairs:
            lines.append(f"{pair.label}\t{pair.ternary}\t{pair.decimal}")
        lines.append("")
        lines.append(f"Balanced Ternary (D)\t\t{self.balanced_label.text()}")
        lines.append(f"Target |A-B|\t\t{self.expected_difference}")
        lines.append(f"Calculated |A-B|\t\t{self.calculated_difference}")
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText("\n".join(lines))

    def _send_first_pair_to_quadset(self):
        if not self.pairs:
            return
        first_pair = self.pairs[0]
        self._send_value_to_quadset(first_pair.decimal)

    # ------------------------------------------------------------------
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
        if not self.window_manager:
            return
        from .quadset_analysis_window import QuadsetAnalysisWindow

        rounded = self._round_cross_pillar_value(value)
        window = self.window_manager.open_window(
            "quadset_analysis",
            QuadsetAnalysisWindow,
        )
        if not window:
            return
        input_widget = getattr(window, "input_field", None)
        if input_widget is not None:
            input_widget.setText(str(rounded))
            window.raise_()
            window.activateWindow()

    def _lookup_value_in_database(self, value: float):
        if not self.window_manager:
            return
        from pillars.gematria.ui.saved_calculations_window import SavedCalculationsWindow

        rounded = self._round_cross_pillar_value(value)
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
        search_fn = getattr(window, "_search", None)
        if callable(search_fn):
            search_fn()
        window.raise_()
        window.activateWindow()
