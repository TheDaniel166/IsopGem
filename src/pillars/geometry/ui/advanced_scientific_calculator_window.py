"""Advanced scientific calculator window for quick math operations."""
from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QComboBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


MEASURE_UNITS: List[Dict[str, object]] = [
    # Length (meters)
    {"name": "Meter", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 1.0},
    {"name": "Kilometer", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 1000.0},
    {"name": "Centimeter", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 0.01},
    {"name": "Egyptian Royal Cubit", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235, "note": "Royal cubit (7 palms)"},
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
    {"name": "Hebrew Seah", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 7.3},
    {"name": "Hebrew Omer", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 2.2},
    {"name": "Roman Modius", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 8.62},
    {"name": "Greek Chous", "system": "Greek", "category": "volume", "si_unit": "L", "to_si": 3.27}
]


class AdvancedScientificCalculatorWindow(QMainWindow):
    """Lightweight scientific calculator with common functions.

    The evaluator is intentionally constrained to a safe set of math functions
    and constants. All trigonometric inputs expect radians.
    """

    def __init__(self, window_manager: Optional[object] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Advanced Scientific Calculator")
        self.setMinimumSize(520, 560)
        self.setStyleSheet("background-color: #0f172a; color: #e2e8f0;")

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        calc_tab = self._build_calculator_tab()
        measures_tab = self._build_measures_tab()

        self.tab_widget.addTab(calc_tab, "Calculator")
        self.tab_widget.addTab(measures_tab, "Ancient Measures")

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.tab_widget)

        self.setCentralWidget(central)

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

        layout.addLayout(self._build_function_row())
        layout.addLayout(self._build_keypad())

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
            return

        raw_value = self.value_input.text().strip()
        if not raw_value:
            self.result_label.setText("Enter a value to convert.")
            self.base_label.setText("")
            self.note_label.setText("")
            return

        try:
            value = float(raw_value)
        except ValueError:
            self.result_label.setText("Invalid number.")
            self.base_label.setText("")
            self.note_label.setText("")
            return

        from_factor = float(from_unit.get("to_si", 1.0) or 1.0)
        to_factor = float(to_unit.get("to_si", 1.0) or 1.0)
        si_unit = str(from_unit.get("si_unit", ""))

        si_value = value * from_factor
        converted = si_value / to_factor if to_factor else 0

        self.result_label.setText(
            f"{value:g} {from_unit.get('name')} = {converted:.6g} {to_unit.get('name')}"
        )
        base_text = f"Base: {si_value:.6g} {si_unit}"
        self.base_label.setText(base_text)

        note = from_unit.get("note") or to_unit.get("note")
        self.note_label.setText(str(note) if note else "")

    def _build_function_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        buttons = [
            ("AC", self._clear, "#ef4444"),
            ("Back", self._backspace, "#334155"),
            ("(", lambda: self._append("("), "#1f2937"),
            (")", lambda: self._append(")"), "#1f2937"),
        ]
        for label, handler, color in buttons:
            row.addWidget(self._make_button(label, handler, color))
        return row

    def _build_keypad(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(8)

        keys = [
            ("sin", 0, 0, lambda: self._append("sin(")),
            ("cos", 0, 1, lambda: self._append("cos(")),
            ("tan", 0, 2, lambda: self._append("tan(")),
            ("ln", 0, 3, lambda: self._append("log(")),
            ("log10", 0, 4, lambda: self._append("log10(")),
            ("pi", 1, 0, lambda: self._append("pi")),
            ("e", 1, 1, lambda: self._append("e")),
            ("tau", 1, 2, lambda: self._append("tau")),
            ("x^2", 1, 3, lambda: self._append("**2")),
            ("sqrt", 1, 4, lambda: self._append("sqrt(")),
            ("7", 2, 0, lambda: self._append("7")),
            ("8", 2, 1, lambda: self._append("8")),
            ("9", 2, 2, lambda: self._append("9")),
            ("/", 2, 3, lambda: self._append("/")),
            ("^", 2, 4, lambda: self._append("**")),
            ("4", 3, 0, lambda: self._append("4")),
            ("5", 3, 1, lambda: self._append("5")),
            ("6", 3, 2, lambda: self._append("6")),
            ("*", 3, 3, lambda: self._append("*")),
            ("!", 3, 4, lambda: self._append("factorial(")),
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
        self.display.setText(current[:-1])

    def _toggle_sign(self):
        text = self.display.text()
        if not text:
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
        except Exception:
            self.display.setText("Error")

    def _safe_eval(self, expression: str):
        allowed_funcs: Dict[str, Callable] = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "pow": math.pow,
            "factorial": math.factorial,
            "abs": abs,
            "round": round,
        }
        allowed_consts = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
        }
        safe_locals = {**allowed_funcs, **allowed_consts}
        return eval(expression, {"__builtins__": {}}, safe_locals)


__all__ = ["AdvancedScientificCalculatorWindow"]
