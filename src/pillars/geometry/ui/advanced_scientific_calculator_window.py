"""Advanced scientific calculator window for quick math operations."""
from __future__ import annotations

import ast
import math
import re
from typing import Callable, Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QComboBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from shared.utils.calculator_persistence import (
        DEFAULT_MAX_HISTORY,
        CalculatorState,
        get_default_state_path,
        load_state,
        save_state,
    )
except ModuleNotFoundError:
    # Tests load this module by file path; in that context `src/` is not
    # necessarily on sys.path and `shared` may not resolve. Fall back to a
    # package-qualified import used by those tests.
    from src.shared.utils.calculator_persistence import (  # type: ignore
        DEFAULT_MAX_HISTORY,
        CalculatorState,
        get_default_state_path,
        load_state,
        save_state,
    )

try:
    from shared.utils.measure_conversion import convert_between_units, parse_measure_value
except ModuleNotFoundError:
    from src.shared.utils.measure_conversion import convert_between_units, parse_measure_value  # type: ignore


MEASURE_UNITS: List[Dict[str, object]] = [
    # Length (meters)
    {"name": "Meter", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 1.0},
    {"name": "Kilometer", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 1000.0},
    {"name": "Centimeter", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 0.01},
    {"name": "Egyptian Royal Cubit", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235, "note": "Royal cubit (7 palms)"},
    {"name": "Egyptian Palm", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235 / 7.0, "note": "Derived: 1 royal cubit = 7 palms"},
    {"name": "Egyptian Digit", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235 / 28.0, "note": "Derived: 1 palm = 4 digits; 1 royal cubit = 28 digits"},
    {"name": "Egyptian Remen", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235 * 5.0 / 7.0, "note": "Derived: 1 remen = 5 palms (royal-cubit palm)"},
    {"name": "Egyptian Common Cubit", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.45},
    {"name": "Hebrew Cubit", "system": "Hebrew", "category": "length", "si_unit": "m", "to_si": 0.457},
    {"name": "Babylonian Cubit", "system": "Babylonian", "category": "length", "si_unit": "m", "to_si": 0.5},
    {"name": "Greek Foot (pous)", "system": "Greek", "category": "length", "si_unit": "m", "to_si": 0.308},
    {"name": "Greek Stadion", "system": "Greek", "category": "length", "si_unit": "m", "to_si": 185.0},
    {"name": "Greek Cubit (pechys)", "system": "Greek", "category": "length", "si_unit": "m", "to_si": 0.462},
    {"name": "Roman Foot (pes)", "system": "Roman", "category": "length", "si_unit": "m", "to_si": 0.296},
    {"name": "Roman Pace (passus)", "system": "Roman", "category": "length", "si_unit": "m", "to_si": 1.48},
    {"name": "Roman Mile (mille passus)", "system": "Roman", "category": "length", "si_unit": "m", "to_si": 1480.0},
    {"name": "Roman Actus", "system": "Roman", "category": "length", "si_unit": "m", "to_si": 35.5},
    {"name": "Persian Parasang", "system": "Persian", "category": "length", "si_unit": "m", "to_si": 5600.0},
    {"name": "Chinese Chi", "system": "Chinese", "category": "length", "si_unit": "m", "to_si": 0.333},
    {"name": "Chinese Zhang", "system": "Chinese", "category": "length", "si_unit": "m", "to_si": 3.33},
    {"name": "Chinese Li", "system": "Chinese", "category": "length", "si_unit": "m", "to_si": 500.0},
    {"name": "Indian Hasta", "system": "Indian", "category": "length", "si_unit": "m", "to_si": 0.4572},
    {"name": "Indian Yojana", "system": "Indian", "category": "length", "si_unit": "m", "to_si": 13000.0, "note": "Yojana varies; using 13 km"},

    # Mass (kilograms)
    {"name": "Kilogram", "system": "Metric", "category": "mass", "si_unit": "kg", "to_si": 1.0},
    {"name": "Gram", "system": "Metric", "category": "mass", "si_unit": "kg", "to_si": 0.001},
    {"name": "Babylonian Talent", "system": "Babylonian", "category": "mass", "si_unit": "kg", "to_si": 30.3},
    {"name": "Babylonian Mina", "system": "Babylonian", "category": "mass", "si_unit": "kg", "to_si": 0.505},
    {"name": "Babylonian Shekel", "system": "Babylonian", "category": "mass", "si_unit": "kg", "to_si": 0.0084},
    {"name": "Hebrew Talent", "system": "Hebrew", "category": "mass", "si_unit": "kg", "to_si": 34.2},
    {"name": "Hebrew Shekel", "system": "Hebrew", "category": "mass", "si_unit": "kg", "to_si": 0.0114},
    {"name": "Greek Talent", "system": "Greek", "category": "mass", "si_unit": "kg", "to_si": 26.0},
    {"name": "Greek Mina", "system": "Greek", "category": "mass", "si_unit": "kg", "to_si": 0.436},
    {"name": "Greek Drachma", "system": "Greek", "category": "mass", "si_unit": "kg", "to_si": 0.00436},
    {"name": "Roman Libra", "system": "Roman", "category": "mass", "si_unit": "kg", "to_si": 0.327},
    {"name": "Roman Uncia", "system": "Roman", "category": "mass", "si_unit": "kg", "to_si": 0.0273},
    {"name": "Egyptian Deben", "system": "Egyptian", "category": "mass", "si_unit": "kg", "to_si": 0.091},
    {"name": "Egyptian Kite (Qedet)", "system": "Egyptian", "category": "mass", "si_unit": "kg", "to_si": 0.091 / 10.0, "note": "Derived: 1 deben = 10 kites (common scholarly convention; varies by period)"},
    {"name": "Chinese Jin", "system": "Chinese", "category": "mass", "si_unit": "kg", "to_si": 0.596},
    {"name": "Chinese Liang", "system": "Chinese", "category": "mass", "si_unit": "kg", "to_si": 0.0373},

    # Volume (liters)
    {"name": "Liter", "system": "Metric", "category": "volume", "si_unit": "L", "to_si": 1.0},
    {"name": "Milliliter", "system": "Metric", "category": "volume", "si_unit": "L", "to_si": 0.001},
    {"name": "Roman Sextarius", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 0.546},
    {"name": "Roman Congius", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 3.25},
    {"name": "Roman Amphora", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 26.2},
    {"name": "Greek Kotyle", "system": "Greek", "category": "volume", "si_unit": "L", "to_si": 0.273},
    {"name": "Greek Metretes", "system": "Greek", "category": "volume", "si_unit": "L", "to_si": 39.4},
    {"name": "Hebrew Bath", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 22.0},
    {"name": "Hebrew Hin", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 3.7},
    {"name": "Egyptian Hekat", "system": "Egyptian", "category": "volume", "si_unit": "L", "to_si": 4.8},
    {"name": "Egyptian Hinu", "system": "Egyptian", "category": "volume", "si_unit": "L", "to_si": 4.8 / 10.0, "note": "Derived: 1 hekat = 10 hinu (approx; historical definitions vary)"},
    {"name": "Hebrew Seah", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 7.3},
    {"name": "Hebrew Omer", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 2.2},
    {"name": "Roman Modius", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 8.62},
    {"name": "Greek Chous", "system": "Greek", "category": "volume", "si_unit": "L", "to_si": 3.27}
]


TIME_UNITS: List[Dict[str, object]] = [
    # Time (seconds)
    {"name": "Second", "system": "SI", "category": "time", "si_unit": "s", "to_si": 1.0},
    {"name": "Minute", "system": "SI", "category": "time", "si_unit": "s", "to_si": 60.0},
    {"name": "Hour", "system": "SI", "category": "time", "si_unit": "s", "to_si": 3600.0},
    {"name": "Day", "system": "SI", "category": "time", "si_unit": "s", "to_si": 86400.0},
    {"name": "Week", "system": "Common", "category": "time", "si_unit": "s", "to_si": 7.0 * 86400.0},

    # Ancient/Historical (explicitly approximate)
    {
        "name": "Seasonal Hour (Ancient Egypt/Antiquity)",
        "system": "Historical",
        "category": "time",
        "si_unit": "s",
        "to_si": 3600.0,
        "note": "Unequal hour: daylight/night divided into 12 parts; duration varies by season/latitude. Using 3600s as a mean placeholder.",
    },

    # Astronomical/civil definitions (exact vs mean)
    {
        "name": "Julian Year (astronomy)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.25 * 86400.0,
        "note": "Exact by definition: 365.25 days of 86400 SI seconds.",
    },
    {
        "name": "Tropical Year (mean)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.24219 * 86400.0,
        "note": "Mean value; varies slightly over time.",
    },
]


class AdvancedScientificCalculatorWindow(QMainWindow):
    """Lightweight scientific calculator with common functions.

    The evaluator is intentionally constrained to a safe set of math functions
    and constants. All trigonometric inputs expect radians.
    """

    def __init__(self, window_manager: Optional[object] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self._last_answer: Optional[float] = None
        self._angle_mode: str = "RAD"  # or "DEG"
        self._memory: float = 0.0
        self._state_path = get_default_state_path("isopgem")
        self._restoring_state = False
        self._last_measure_result: Optional[dict] = None
        self._last_time_result: Optional[dict] = None
        self.setWindowTitle("Advanced Scientific Calculator")
        self.setMinimumSize(520, 560)
        self.setStyleSheet("background-color: #0f172a; color: #e2e8f0;")

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        calc_tab = self._build_calculator_tab()
        measures_tab = self._build_measures_tab()
        time_tab = self._build_time_tab()

        self.tab_widget.addTab(calc_tab, "Calculator")
        self.tab_widget.addTab(measures_tab, "Ancient Measures")
        self.tab_widget.addTab(time_tab, "Time Units")

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.tab_widget)

        self.setCentralWidget(central)

        self._restore_persisted_state()

    def _build_time_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Time Conversion")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Convert between SI time units and historically-attested (approximate) ones.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        layout.addWidget(subtitle)

        from_row = QHBoxLayout()
        from_row.setSpacing(8)
        from_label = QLabel("From:")
        from_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.time_from_unit_combo = QComboBox()
        self.time_from_unit_combo.currentIndexChanged.connect(self._update_time_conversion_result)
        from_row.addWidget(from_label)
        from_row.addWidget(self.time_from_unit_combo, 1)
        layout.addLayout(from_row)

        to_row = QHBoxLayout()
        to_row.setSpacing(8)
        to_label = QLabel("To:")
        to_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.time_to_unit_combo = QComboBox()
        self.time_to_unit_combo.currentIndexChanged.connect(self._update_time_conversion_result)
        to_row.addWidget(to_label)
        to_row.addWidget(self.time_to_unit_combo, 1)

        swap_btn = QPushButton("Swap")
        swap_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        swap_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1f2937;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #334155; }
            QPushButton:pressed { background-color: #0b1729; }
            """
        )
        swap_btn.clicked.connect(self._swap_time_units)
        to_row.addWidget(swap_btn)
        layout.addLayout(to_row)

        value_row = QHBoxLayout()
        value_row.setSpacing(8)
        value_label = QLabel("Value:")
        value_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.time_value_input = QLineEdit()
        self.time_value_input.setPlaceholderText("Enter a number")
        self.time_value_input.textChanged.connect(self._update_time_conversion_result)
        self.time_value_input.setStyleSheet(
            """
            QLineEdit {
                background: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 10px 10px;
                font-size: 12pt;
            }
            """
        )
        value_row.addWidget(value_label)
        value_row.addWidget(self.time_value_input, 1)
        layout.addLayout(value_row)

        self.time_result_label = QLabel("Enter a value to convert.")
        self.time_result_label.setWordWrap(True)
        self.time_result_label.setStyleSheet("color: #cbd5e1; font-size: 11pt;")
        layout.addWidget(self.time_result_label)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)
        actions_row.addStretch(1)

        self.copy_time_result_btn = QPushButton("Copy Result")
        self.copy_time_result_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_time_result_btn.setEnabled(False)
        self.copy_time_result_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton:pressed { background-color: #0b1729; }
            QPushButton:disabled { color: #94a3b8; background-color: #1f2937; }
            """
        )
        self.copy_time_result_btn.clicked.connect(self._copy_time_result)
        actions_row.addWidget(self.copy_time_result_btn)
        layout.addLayout(actions_row)

        self.time_base_label = QLabel("")
        self.time_base_label.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        layout.addWidget(self.time_base_label)

        self.time_note_label = QLabel("")
        self.time_note_label.setWordWrap(True)
        self.time_note_label.setStyleSheet("color: #94a3b8; font-size: 9pt; font-style: italic;")
        layout.addWidget(self.time_note_label)

        layout.addStretch()

        self._refresh_time_unit_combos()
        return container

    def _unit_options_for_time(self) -> List[Dict[str, object]]:
        return [u for u in TIME_UNITS if u.get("category") == "time"]

    def _refresh_time_unit_combos(self, *_):
        units = self._unit_options_for_time()
        units_sorted = sorted(units, key=lambda u: (str(u.get("system")), str(u.get("name"))))

        def populate(combo: QComboBox):
            combo.blockSignals(True)
            combo.clear()
            for unit in units_sorted:
                label = f"{unit.get('system')} - {unit.get('name')}"
                combo.addItem(label, unit)
            combo.blockSignals(False)

        populate(self.time_from_unit_combo)
        populate(self.time_to_unit_combo)

        if self.time_from_unit_combo.count() > 0:
            self.time_from_unit_combo.setCurrentIndex(0)
        if self.time_to_unit_combo.count() > 1:
            self.time_to_unit_combo.setCurrentIndex(1)
        elif self.time_to_unit_combo.count() > 0:
            self.time_to_unit_combo.setCurrentIndex(0)

        self._update_time_conversion_result()

    def _swap_time_units(self) -> None:
        if not hasattr(self, "time_from_unit_combo") or not hasattr(self, "time_to_unit_combo"):
            return
        from_idx = self.time_from_unit_combo.currentIndex()
        to_idx = self.time_to_unit_combo.currentIndex()
        self.time_from_unit_combo.blockSignals(True)
        self.time_to_unit_combo.blockSignals(True)
        self.time_from_unit_combo.setCurrentIndex(to_idx)
        self.time_to_unit_combo.setCurrentIndex(from_idx)
        self.time_from_unit_combo.blockSignals(False)
        self.time_to_unit_combo.blockSignals(False)
        self._update_time_conversion_result()

    def _copy_time_result(self) -> None:
        payload = self._last_time_result
        if not isinstance(payload, dict):
            return
        text = payload.get("copy_text")
        if not isinstance(text, str) or not text:
            return
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

    def _current_time_unit(self, combo: QComboBox) -> Optional[Dict[str, object]]:
        idx = combo.currentIndex()
        if idx < 0:
            return None
        data = combo.currentData()
        if isinstance(data, dict):
            return data
        return None

    def _update_time_conversion_result(self, *_):
        from_unit = self._current_time_unit(self.time_from_unit_combo)
        to_unit = self._current_time_unit(self.time_to_unit_combo)

        if not from_unit or not to_unit:
            self.time_result_label.setText("Select units to convert.")
            self.time_base_label.setText("")
            self.time_note_label.setText("")
            self._last_time_result = None
            if hasattr(self, "copy_time_result_btn"):
                self.copy_time_result_btn.setEnabled(False)
            return

        raw_value = self.time_value_input.text().strip()
        if not raw_value:
            self.time_result_label.setText("Enter a value to convert.")
            self.time_base_label.setText("")
            self.time_note_label.setText("")
            self._last_time_result = None
            if hasattr(self, "copy_time_result_btn"):
                self.copy_time_result_btn.setEnabled(False)
            return

        try:
            value = parse_measure_value(raw_value)
        except ValueError:
            self.time_result_label.setText("Invalid number.")
            self.time_base_label.setText("")
            self.time_note_label.setText("")
            self._last_time_result = None
            if hasattr(self, "copy_time_result_btn"):
                self.copy_time_result_btn.setEnabled(False)
            return

        try:
            result = convert_between_units(value, from_unit, to_unit)
        except ValueError:
            self.time_result_label.setText("Conversion error.")
            self.time_base_label.setText("")
            self.time_note_label.setText("")
            self._last_time_result = None
            if hasattr(self, "copy_time_result_btn"):
                self.copy_time_result_btn.setEnabled(False)
            return

        result_text = f"{result.input_value:g} {result.from_name} = {result.converted_value:.6g} {result.to_name}"
        self.time_result_label.setText(result_text)

        base_text = f"Base: {result.base_value:.6g} {result.base_unit}"
        self.time_base_label.setText(base_text)

        note = from_unit.get("note") or to_unit.get("note")
        self.time_note_label.setText(str(note) if note else "")

        self._last_time_result = {
            "value": result.input_value,
            "from": from_unit,
            "to": to_unit,
            "si_value": result.base_value,
            "converted": result.converted_value,
            "copy_text": f"{result.converted_value:.6g} {result.to_name}",
        }
        if hasattr(self, "copy_time_result_btn"):
            self.copy_time_result_btn.setEnabled(True)

    def _restore_persisted_state(self) -> None:
        self._restoring_state = True
        try:
            state = load_state(self._state_path, max_history=DEFAULT_MAX_HISTORY)
            self._angle_mode = state.angle_mode
            self._memory = float(state.memory)
            if hasattr(self, "angle_mode_label"):
                self.angle_mode_label.setText(f"Mode: {self._angle_mode}")
            if hasattr(self, "history_list"):
                self.history_list.clear()
                for entry in (state.history or []):
                    self.history_list.addItem(QListWidgetItem(entry))
        finally:
            self._restoring_state = False

    def _persist_state(self) -> None:
        if getattr(self, "_restoring_state", False):
            return
        history: List[str] = []
        if hasattr(self, "history_list"):
            for i in range(self.history_list.count()):
                item = self.history_list.item(i)
                if item is not None:
                    history.append(item.text())
        state = CalculatorState(angle_mode=self._angle_mode, memory=self._memory, history=history)
        save_state(state, self._state_path, max_history=DEFAULT_MAX_HISTORY)

    def _build_calculator_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setStyleSheet(
            """
            QLineEdit {
                background: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 14px 12px;
                font-size: 18pt;
                letter-spacing: 0.5px;
            }
            """
        )
        layout.addWidget(self.display)

        self.angle_mode_label = QLabel("Mode: RAD")
        self.angle_mode_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.angle_mode_label.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        layout.addWidget(self.angle_mode_label)

        layout.addLayout(self._build_function_row())

        content_row = QHBoxLayout()
        content_row.setSpacing(12)
        content_row.addLayout(self._build_keypad(), 3)

        self.history_list = QListWidget()
        self.history_list.setMinimumWidth(220)
        self.history_list.setStyleSheet(
            """
            QListWidget {
                background: #0b1220;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 6px;
                color: #e2e8f0;
            }
            QListWidget::item {
                padding: 6px;
            }
            QListWidget::item:selected {
                background: #1f2937;
            }
            """
        )
        self.history_list.itemClicked.connect(self._on_history_item_clicked)
        content_row.addWidget(self.history_list, 1)

        layout.addLayout(content_row)

        layout.addStretch()
        return container

    def _build_measures_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Ancient Measures Conversion")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Convert between ancient systems and modern metric baselines.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        layout.addWidget(subtitle)

        category_row = QHBoxLayout()
        category_row.setSpacing(8)
        category_label = QLabel("Category:")
        category_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.measure_category_combo = QComboBox()
        self.measure_category_combo.addItem("Length (meters)", "length")
        self.measure_category_combo.addItem("Mass (kilograms)", "mass")
        self.measure_category_combo.addItem("Volume (liters)", "volume")
        self.measure_category_combo.currentIndexChanged.connect(self._refresh_unit_combos)
        category_row.addWidget(category_label)
        category_row.addWidget(self.measure_category_combo, 1)
        layout.addLayout(category_row)

        from_row = QHBoxLayout()
        from_row.setSpacing(8)
        from_label = QLabel("From:")
        from_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.from_unit_combo = QComboBox()
        self.from_unit_combo.currentIndexChanged.connect(self._update_conversion_result)
        from_row.addWidget(from_label)
        from_row.addWidget(self.from_unit_combo, 1)
        layout.addLayout(from_row)

        to_row = QHBoxLayout()
        to_row.setSpacing(8)
        to_label = QLabel("To:")
        to_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.to_unit_combo = QComboBox()
        self.to_unit_combo.currentIndexChanged.connect(self._update_conversion_result)
        to_row.addWidget(to_label)
        to_row.addWidget(self.to_unit_combo, 1)

        swap_btn = QPushButton("Swap")
        swap_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        swap_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1f2937;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #334155; }
            QPushButton:pressed { background-color: #0b1729; }
            """
        )
        swap_btn.clicked.connect(self._swap_measures_units)
        to_row.addWidget(swap_btn)
        layout.addLayout(to_row)

        value_row = QHBoxLayout()
        value_row.setSpacing(8)
        value_label = QLabel("Value:")
        value_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter a number")
        self.value_input.textChanged.connect(self._update_conversion_result)
        self.value_input.setStyleSheet(
            """
            QLineEdit {
                background: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 10px 10px;
                font-size: 12pt;
            }
            """
        )
        value_row.addWidget(value_label)
        value_row.addWidget(self.value_input, 1)
        layout.addLayout(value_row)

        self.result_label = QLabel("Enter a value to convert.")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: #cbd5e1; font-size: 11pt;")
        layout.addWidget(self.result_label)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)
        actions_row.addStretch(1)

        self.copy_result_btn = QPushButton("Copy Result")
        self.copy_result_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_result_btn.setEnabled(False)
        self.copy_result_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton:pressed { background-color: #0b1729; }
            QPushButton:disabled { color: #94a3b8; background-color: #1f2937; }
            """
        )
        self.copy_result_btn.clicked.connect(self._copy_measures_result)
        actions_row.addWidget(self.copy_result_btn)
        layout.addLayout(actions_row)

        self.base_label = QLabel("")
        self.base_label.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        layout.addWidget(self.base_label)

        self.note_label = QLabel("")
        self.note_label.setWordWrap(True)
        self.note_label.setStyleSheet("color: #94a3b8; font-size: 9pt; font-style: italic;")
        layout.addWidget(self.note_label)

        layout.addStretch()
        self._refresh_unit_combos()
        return container

    def _swap_measures_units(self) -> None:
        if not hasattr(self, "from_unit_combo") or not hasattr(self, "to_unit_combo"):
            return
        from_idx = self.from_unit_combo.currentIndex()
        to_idx = self.to_unit_combo.currentIndex()
        self.from_unit_combo.blockSignals(True)
        self.to_unit_combo.blockSignals(True)
        self.from_unit_combo.setCurrentIndex(to_idx)
        self.to_unit_combo.setCurrentIndex(from_idx)
        self.from_unit_combo.blockSignals(False)
        self.to_unit_combo.blockSignals(False)
        self._update_conversion_result()

    def _copy_measures_result(self) -> None:
        payload = self._last_measure_result
        if not isinstance(payload, dict):
            return
        text = payload.get("copy_text")
        if not isinstance(text, str) or not text:
            return
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

    def _unit_options_for_category(self, category: str) -> List[Dict[str, object]]:
        if not category:
            return []
        return [u for u in MEASURE_UNITS if u.get("category") == category]

    def _refresh_unit_combos(self, *_):
        category = self.measure_category_combo.currentData()
        units = self._unit_options_for_category(category)
        units_sorted = sorted(
            units,
            key=lambda u: (0 if u.get("system") == "Metric" else 1, str(u.get("system")), str(u.get("name"))),
        )

        def populate(combo: QComboBox):
            combo.blockSignals(True)
            combo.clear()
            for unit in units_sorted:
                label = f"{unit.get('system')} - {unit.get('name')}"
                combo.addItem(label, unit)
            combo.blockSignals(False)

        populate(self.from_unit_combo)
        populate(self.to_unit_combo)

        if self.from_unit_combo.count() > 0:
            self.from_unit_combo.setCurrentIndex(0)
        if self.to_unit_combo.count() > 1:
            self.to_unit_combo.setCurrentIndex(1)
        elif self.to_unit_combo.count() > 0:
            self.to_unit_combo.setCurrentIndex(0)

        self._update_conversion_result()

    def _current_unit(self, combo: QComboBox) -> Optional[Dict[str, object]]:
        idx = combo.currentIndex()
        if idx < 0:
            return None
        data = combo.currentData()
        if isinstance(data, dict):
            return data
        return None

    def _update_conversion_result(self, *_):
        from_unit = self._current_unit(self.from_unit_combo)
        to_unit = self._current_unit(self.to_unit_combo)

        if not from_unit or not to_unit:
            self.result_label.setText("Select units to convert.")
            self.base_label.setText("")
            self.note_label.setText("")
            self._last_measure_result = None
            if hasattr(self, "copy_result_btn"):
                self.copy_result_btn.setEnabled(False)
            return

        raw_value = self.value_input.text().strip()
        if not raw_value:
            self.result_label.setText("Enter a value to convert.")
            self.base_label.setText("")
            self.note_label.setText("")
            self._last_measure_result = None
            if hasattr(self, "copy_result_btn"):
                self.copy_result_btn.setEnabled(False)
            return

        try:
            value = parse_measure_value(raw_value)
        except ValueError:
            self.result_label.setText("Invalid number.")
            self.base_label.setText("")
            self.note_label.setText("")
            self._last_measure_result = None
            if hasattr(self, "copy_result_btn"):
                self.copy_result_btn.setEnabled(False)
            return

        try:
            result = convert_between_units(value, from_unit, to_unit)
        except ValueError:
            self.result_label.setText("Conversion error.")
            self.base_label.setText("")
            self.note_label.setText("")
            self._last_measure_result = None
            if hasattr(self, "copy_result_btn"):
                self.copy_result_btn.setEnabled(False)
            return

        result_text = f"{result.input_value:g} {result.from_name} = {result.converted_value:.6g} {result.to_name}"
        self.result_label.setText(result_text)

        base_text = f"Base: {result.base_value:.6g} {result.base_unit}"
        self.base_label.setText(base_text)

        note = from_unit.get("note") or to_unit.get("note")
        self.note_label.setText(str(note) if note else "")

        self._last_measure_result = {
            "value": result.input_value,
            "from": from_unit,
            "to": to_unit,
            "si_value": result.base_value,
            "converted": result.converted_value,
            "copy_text": f"{result.converted_value:.6g} {result.to_name}",
        }
        if hasattr(self, "copy_result_btn"):
            self.copy_result_btn.setEnabled(True)

    def _build_function_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        buttons = [
            ("AC", self._clear, "#ef4444"),
            ("Back", self._backspace, "#334155"),
            ("DEG/RAD", self._toggle_angle_mode, "#334155"),
            ("MC", self._memory_clear, "#334155"),
            ("MR", self._memory_recall, "#334155"),
            ("M+", self._memory_add, "#334155"),
            ("M-", self._memory_subtract, "#334155"),
            ("(", lambda: self._append("("), "#1f2937"),
            (")", lambda: self._append(")"), "#1f2937"),
        ]
        for label, handler, color in buttons:
            row.addWidget(self._make_button(label, handler, color))
        return row

    def _toggle_angle_mode(self):
        self._angle_mode = "DEG" if self._angle_mode == "RAD" else "RAD"
        if hasattr(self, "angle_mode_label"):
            self.angle_mode_label.setText(f"Mode: {self._angle_mode}")
        self._persist_state()

    def _memory_clear(self):
        self._memory = 0.0
        self._persist_state()

    def _memory_recall(self):
        # Insert as a readable constant rather than pasting the numeric value.
        self._append("mem")

    def _memory_add(self):
        if self._last_answer is not None:
            self._memory += float(self._last_answer)
            self._persist_state()

    def _memory_subtract(self):
        if self._last_answer is not None:
            self._memory -= float(self._last_answer)
            self._persist_state()

    def _build_keypad(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(8)

        keys = [
            ("sin", 0, 0, lambda: self._append("sin(")),
            ("cos", 0, 1, lambda: self._append("cos(")),
            ("tan", 0, 2, lambda: self._append("tan(")),
            ("ln", 0, 3, lambda: self._append("log(")),
            ("log10", 0, 4, lambda: self._append("log10(")),
            ("ANS", 1, 0, lambda: self._append("ans")),
            ("MEM", 1, 5, lambda: self._append("mem")),
            ("deg", 1, 1, lambda: self._append("deg(")),
            ("rad", 1, 2, lambda: self._append("rad(")),
            ("x^2", 1, 3, lambda: self._append("**2")),
            ("sqrt", 1, 4, lambda: self._append("sqrt(")),
            ("7", 2, 0, lambda: self._append("7")),
            ("8", 2, 1, lambda: self._append("8")),
            ("9", 2, 2, lambda: self._append("9")),
            ("/", 2, 3, lambda: self._append("/")),
            ("^", 2, 4, lambda: self._append("^")),
            ("pi", 6, 0, lambda: self._append("pi")),
            ("e", 6, 1, lambda: self._append("e")),
            ("tau", 6, 2, lambda: self._append("tau")),
            ("4", 3, 0, lambda: self._append("4")),
            ("5", 3, 1, lambda: self._append("5")),
            ("6", 3, 2, lambda: self._append("6")),
            ("*", 3, 3, lambda: self._append("*")),
            ("!", 3, 4, self._append_factorial),
            ("1", 4, 0, lambda: self._append("1")),
            ("2", 4, 1, lambda: self._append("2")),
            ("3", 4, 2, lambda: self._append("3")),
            ("-", 4, 3, lambda: self._append("-")),
            ("mod", 4, 4, lambda: self._append("%")),
            ("0", 5, 0, lambda: self._append("0")),
            (".", 5, 1, lambda: self._append(".")),
            ("+/-", 5, 2, self._toggle_sign),
            ("+", 5, 3, lambda: self._append("+")),
            ("=", 5, 4, self._calculate),
        ]

        for label, row, col, handler in keys:
            if label == "=":
                btn = self._make_button(label, handler, "#10b981")
            elif label == "AC":
                btn = self._make_button(label, handler, "#ef4444")
            else:
                btn = self._make_button(label, handler, "#1f2937")
            grid.addWidget(btn, row, col)

        return grid

    def _append_factorial(self):
        text = self.display.text()
        if not text:
            self._append("factorial(")
            return

        idx = len(text) - 1
        while idx >= 0 and text[idx].isspace():
            idx -= 1
        if idx < 0:
            self._append("factorial(")
            return

        last = text[idx]
        if last.isdigit() or last == ")":
            self._append("!")
        else:
            self._append("factorial(")

    def _make_button(self, text: str, handler: Callable, bg_color: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 10px;
                padding: 10px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: #334155;
            }}
            QPushButton:pressed {{
                background-color: #0b1729;
            }}
            """
        )
        btn.clicked.connect(handler)
        return btn

    def _append(self, value: str):
        self.display.setText(self.display.text() + value)

    def _clear(self):
        self.display.clear()

    def _backspace(self):
        current = self.display.text()
        self.display.setText(_smart_backspace(current))

    def _toggle_sign(self):
        text = self.display.text()
        if not text:
            return

        # Toggle sign of the last numeric literal when possible; fall back to whole expression.
        idx = len(text) - 1
        while idx >= 0 and text[idx].isspace():
            idx -= 1
        if idx < 0:
            return

        end = idx + 1
        has_digit = False
        while idx >= 0:
            ch = text[idx]
            if ch.isdigit():
                has_digit = True
                idx -= 1
                continue
            if ch == ".":
                idx -= 1
                continue
            break

        if has_digit:
            start = idx + 1
            if start > 0 and text[start - 1] == "-":
                before = text[start - 2] if start - 2 >= 0 else ""
                if start - 1 == 0 or before in "+-*/%(":
                    self.display.setText(text[: start - 1] + text[start:])
                    return
            self.display.setText(text[:start] + "-" + text[start:])
            return

        if text.startswith("-"):
            self.display.setText(text[1:])
        else:
            self.display.setText(f"-{text}")

    def _calculate(self):
        expression = self.display.text().strip()
        if not expression:
            return
        try:
            result = self._safe_eval(expression)
            # Avoid scientific notation for most results
            if isinstance(result, float):
                display_val = ("{0:.12g}".format(result)).rstrip("0").rstrip(".")
                self.display.setText(display_val)
            else:
                self.display.setText(str(result))
            if isinstance(result, (int, float)):
                self._last_answer = float(result)
            self._append_history(expression, result)
        except ValueError as exc:
            message = str(exc) or "Error"
            if "Invalid expression" in message:
                self.display.setText("Syntax Error")
            elif "Math domain error" in message:
                self.display.setText("Math Error")
            else:
                self.display.setText("Error")
        except Exception:
            self.display.setText("Error")

    def _append_history(self, expression: str, result):
        if not hasattr(self, "history_list"):
            return
        item_text = f"{expression} = {result}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, {"expression": expression, "result": str(result)})
        self.history_list.insertItem(0, item)
        self._persist_state()

    def _on_history_item_clicked(self, item: QListWidgetItem):
        payload = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(payload, dict) and "result" in payload:
            self.display.setText(str(payload["result"]))

    def _safe_eval(self, expression: str):
        expression = _normalize_expression(expression)

        def _angle_to_radians(x: float) -> float:
            return math.radians(x) if self._angle_mode == "DEG" else x

        def sin_wrapped(x: float) -> float:
            return math.sin(_angle_to_radians(x))

        def cos_wrapped(x: float) -> float:
            return math.cos(_angle_to_radians(x))

        def tan_wrapped(x: float) -> float:
            return math.tan(_angle_to_radians(x))

        allowed_funcs: Dict[str, Callable] = {
            "sin": sin_wrapped,
            "cos": cos_wrapped,
            "tan": tan_wrapped,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "floor": math.floor,
            "ceil": math.ceil,
            "pow": math.pow,
            "factorial": math.factorial,
            "gcd": math.gcd,
            "lcm": math.lcm,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "deg": math.degrees,
            "rad": math.radians,
        }
        allowed_consts: Dict[str, float] = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "ans": float(self._last_answer) if self._last_answer is not None else 0.0,
            "mem": float(self._memory),
        }

        return _safe_math_eval(expression, allowed_funcs=allowed_funcs, allowed_consts=allowed_consts)


def _normalize_expression(expression: str) -> str:
    # Support common calculator convention: caret for exponent.
    # The UI already emits '**', but users may type '^' manually.
    normalized = expression.replace("^", "**")
    normalized = _rewrite_unit_suffixes(normalized)
    normalized = _insert_implicit_multiplication(normalized)
    return _rewrite_postfix_factorial(normalized)


def _rewrite_unit_suffixes(expression: str) -> str:
    """Rewrite number+unit suffixes into explicit conversion calls.

    Supported:
    - 30deg  -> rad(30)
    - 0.5rad -> 0.5

    This is intentionally explicit (no guessing). Users can still control
    trig input via the global DEG/RAD mode, but suffixes override by turning
    values into radians directly.
    """

    tokens = _tokenize_expression(expression)
    if not tokens:
        return expression

    out: List[str] = []
    i = 0
    while i < len(tokens):
        kind, val = tokens[i]
        if kind == "number" and i + 1 < len(tokens):
            n_kind, n_val = tokens[i + 1]
            if n_kind == "ident" and n_val.lower() in {"deg", "rad"}:
                if n_val.lower() == "deg":
                    out.append(f"rad({val})")
                else:
                    out.append(val)
                i += 2
                continue
        out.append(val)
        i += 1
    return "".join(out)


_TOKEN_RE = re.compile(
    r"""\s*(?:(\d+(?:\.\d*)?|\.\d+)|(\*\*|[+\-*/%(),!])|([A-Za-z_][A-Za-z_0-9]*))"""
)


def _tokenize_expression(expression: str) -> List[tuple[str, str]]:
    tokens: List[tuple[str, str]] = []
    pos = 0
    while pos < len(expression):
        match = _TOKEN_RE.match(expression, pos)
        if not match:
            # Keep original behavior: let AST parse throw later, but here we
            # surface a clear error for odd characters.
            raise ValueError("Invalid expression")
        number, op, ident = match.groups()
        if number is not None:
            tokens.append(("number", number))
        elif op is not None:
            tokens.append(("op", op))
        elif ident is not None:
            tokens.append(("ident", ident))
        pos = match.end()
    return tokens


def _insert_implicit_multiplication(expression: str) -> str:
    """Insert '*' where calculators typically assume multiplication.

    Examples: 2pi -> 2*pi, 2(3+4) -> 2*(3+4), (1+2)(3+4) -> (1+2)*(3+4),
    2sin(pi/2) -> 2*sin(pi/2)
    """

    tokens = _tokenize_expression(expression)
    if not tokens:
        return expression

    def is_value(tok: tuple[str, str]) -> bool:
        kind, val = tok
        return kind in {"number", "ident"} or (kind == "op" and val == ")")

    def is_value_start(tok: tuple[str, str]) -> bool:
        kind, val = tok
        # NOTE: '(' can start a value expression, but we only want implicit
        # multiplication into '(' (not treating '(' as an argument list).
        return kind in {"number", "ident"} or (kind == "op" and val == "(")

    known_func_names = {
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "sqrt",
        "log",
        "log10",
        "pow",
        "factorial",
        "exp",
        "floor",
        "ceil",
        "gcd",
        "lcm",
        "abs",
        "round",
        "min",
        "max",
        "deg",
        "rad",
    }

    out: List[str] = []
    for i, tok in enumerate(tokens):
        if i > 0:
            prev = tokens[i - 1]
            if is_value(prev) and is_value_start(tok):
                # If we have IDENT '(' it might be a function call. Only insert
                # '*' when the identifier is NOT a known safe function name.
                if prev[0] == "ident" and tok == ("op", "(") and prev[1] in known_func_names:
                    pass
                else:
                    out.append("*")
        out.append(tok[1])
    return "".join(out)


def _rewrite_postfix_factorial(expression: str) -> str:
    """Rewrite postfix factorial to explicit factorial() calls.

    Examples:
    - 5! -> factorial(5)
    - (3+2)! -> factorial((3+2))
    - 3!! -> factorial(factorial(3))

    This stays within the safe evaluation allowlist (factorial is already allowed).
    """

    tokens = _tokenize_expression(expression)
    if not tokens:
        return expression

    out: List[tuple[str, str]] = []

    def pop_atom() -> str:
        if not out:
            raise ValueError("Invalid expression")

        kind, val = out[-1]
        if kind in {"number", "ident"}:
            out.pop()
            return val

        # Parenthesized atom: find matching '('
        if kind == "op" and val == ")":
            depth = 0
            pieces: List[str] = []
            while out:
                k, v = out.pop()
                pieces.append(v)
                if k == "op" and v == ")":
                    depth += 1
                elif k == "op" and v == "(":
                    depth -= 1
                    if depth == 0:
                        break
            if depth != 0:
                raise ValueError("Invalid expression")
            return "".join(reversed(pieces))

        raise ValueError("Invalid expression")

    for kind, val in tokens:
        if kind == "op" and val == "!":
            atom = pop_atom()
            out.append(("ident", f"factorial({atom})"))
        else:
            out.append((kind, val))

    return "".join(v for _, v in out)


def _safe_math_eval(
    expression: str,
    *,
    allowed_funcs: Dict[str, Callable],
    allowed_consts: Dict[str, float],
):
    """Evaluate a constrained math expression.

    Supports numbers, parentheses, binary ops (+, -, *, /, %, **), unary +/-,
    and calls to a strict allowlist of functions.
    """

    def fail(message: str) -> ValueError:
        return ValueError(message)

    expression = _normalize_expression(expression)

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise fail("Invalid expression") from exc

    def eval_node(node):
        if isinstance(node, ast.Expression):
            return eval_node(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise fail("Only numeric literals are allowed")

        if isinstance(node, ast.Name):
            if node.id in allowed_consts:
                return allowed_consts[node.id]
            raise fail(f"Unknown identifier: {node.id}")

        if isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise fail("Unsupported unary operator")

        if isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left ** right
            raise fail("Unsupported operator")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise fail("Only simple function calls are allowed")
            func_name = node.func.id
            func = allowed_funcs.get(func_name)
            if func is None:
                raise fail(f"Function not allowed: {func_name}")
            if node.keywords:
                raise fail("Keyword arguments are not allowed")
            args = [eval_node(arg) for arg in node.args]
            try:
                return func(*args)
            except Exception as exc:
                raise fail("Math domain error") from exc

        raise fail("Unsupported expression")

    # Explicitly forbid nodes even if they might slip through.
    for subnode in ast.walk(tree):
        if isinstance(
            subnode,
            (
                ast.Attribute,
                ast.Subscript,
                ast.Lambda,
                ast.Dict,
                ast.List,
                ast.Set,
                ast.Tuple,
                ast.ListComp,
                ast.SetComp,
                ast.DictComp,
                ast.GeneratorExp,
                ast.Await,
                ast.Yield,
                ast.YieldFrom,
                ast.Compare,
                ast.IfExp,
                ast.BoolOp,
                ast.NamedExpr,
            ),
        ):
            raise fail("Unsupported expression")

    return eval_node(tree)


def _smart_backspace(text: str) -> str:
    """Backspace that removes whole tokens where it improves UX.

    Examples:
    - 'sin(' deletes as a unit
    - 'deg(' / 'rad(' / 'log10(' / 'factorial(' delete as units
    - '**' deletes as a unit
    - postfix '!' deletes as a unit
    """

    if not text:
        return text

    # Trim trailing whitespace first.
    stripped = text.rstrip()
    if not stripped:
        return ""

    token_suffixes = [
        "log10(",
        "factorial(",
        "sqrt(",
        "asin(",
        "acos(",
        "atan(",
        "sin(",
        "cos(",
        "tan(",
        "deg(",
        "rad(",
        "log(",
        "ans",
        "mem",
        "pi",
        "tau",
        "e",
        "**",
        "!",
    ]

    for suffix in token_suffixes:
        if stripped.endswith(suffix):
            return stripped[: -len(suffix)]

    return stripped[:-1]




__all__ = ["AdvancedScientificCalculatorWindow", "_smart_backspace"]
