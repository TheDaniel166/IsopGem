"""Methods Reference Window - lists all gematria calculation systems with descriptions."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QWidget, QSplitter, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import List, Dict, Optional
from ..services.base_calculator import GematriaCalculator

class MethodsReferenceWindow(QDialog):
    """Window displaying all available gematria calculation methods with their documentation."""

    def __init__(self, calculators: List[GematriaCalculator], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gemetria Methods Reference")
        self.setMinimumSize(1000, 750)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setModal(False)

        # Build a mapping of name -> calculator instance
        self.calculators: Dict[str, GematriaCalculator] = {c.name: c for c in calculators}
        self.filtered_names: List[str] = []

        self._setup_ui()
        self._populate_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📚 Gemetria Methods")
        title.setStyleSheet("font-size: 26pt; font-weight: 700; color: #1e293b;")
        layout.addWidget(title)

        subtitle = QLabel("Reference for all implemented Hebrew, Greek, and English/TQ gematria calculation systems.")
        subtitle.setStyleSheet("color: #475569; font-size: 11pt;")
        layout.addWidget(subtitle)

        # Filter row
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search name or description...")
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.search_input)

        self.language_filter = QComboBox()
        self.language_filter.addItems(["All", "Hebrew", "Greek", "English", "TQ"])
        self.language_filter.setMinimumHeight(36)
        self.language_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.language_filter)

        clear_btn = QPushButton("Clear")
        clear_btn.setMinimumHeight(36)
        clear_btn.clicked.connect(self._clear_filters)
        filter_layout.addWidget(clear_btn)

        layout.addLayout(filter_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QLabel("Methods")
        list_label.setStyleSheet("font-weight: 600; font-size: 12pt;")
        left_layout.addWidget(list_label)

        self.methods_list = QListWidget()
        self.methods_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e2e8f0; border-radius: 6px; background: #ffffff;
                font-size: 11pt;
            }
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background: #dbeafe; color: #1e40af; }
            QListWidget::item:hover { background: #f1f5f9; }
        """)
        self.methods_list.currentItemChanged.connect(self._on_method_selected)
        left_layout.addWidget(self.methods_list)

        splitter.addWidget(left_widget)

        # Right detail pane
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        detail_label = QLabel("Details")
        detail_label.setStyleSheet("font-weight: 600; font-size: 12pt;")
        right_layout.addWidget(detail_label)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet("""
            QTextEdit { border: 1px solid #e2e8f0; border-radius: 6px; background: #f8fafc; font-size: 11pt; padding: 12px; }
        """)
        right_layout.addWidget(self.detail_text)

        # Example input row
        example_layout = QHBoxLayout()
        self.example_input = QLineEdit()
        self.example_input.setPlaceholderText("Try an example word/phrase (optional)...")
        self.example_input.setMinimumHeight(32)
        example_layout.addWidget(self.example_input)

        example_btn = QPushButton("Calculate Example")
        example_btn.setMinimumHeight(32)
        example_btn.clicked.connect(self._calculate_example)
        example_layout.addWidget(example_btn)

        right_layout.addLayout(example_layout)

        splitter.addWidget(right_widget)
        splitter.setSizes([320, 660])
        layout.addWidget(splitter)

        self.status_label = QLabel("Loaded methods reference")
        self.status_label.setStyleSheet("color: #64748b; font-size: 10pt;")
        layout.addWidget(self.status_label)

    def _populate_list(self):
        self.methods_list.clear()
        self.filtered_names = sorted(self.calculators.keys())
        for name in self.filtered_names:
            item = QListWidgetItem(name)
            self.methods_list.addItem(item)
        if self.methods_list.count() > 0:
            self.methods_list.setCurrentRow(0)

    def _on_filter_changed(self):
        term = self.search_input.text().strip().lower()
        lang_filter = self.language_filter.currentText()

        self.methods_list.clear()
        self.filtered_names = []
        for name, calc in self.calculators.items():
            if lang_filter != "All":
                # Language detection by prefix inside name
                if lang_filter == "English":
                    if not ("English" in name or "TQ" in name):
                        continue
                else:
                    if lang_filter not in name:
                        continue
            # Get docstring
            doc = (calc.__class__.__doc__ or "").lower()
            if term and term not in name.lower() and term not in doc:
                continue
            self.filtered_names.append(name)
            self.methods_list.addItem(QListWidgetItem(name))
        self.status_label.setText(f"Filtered: {len(self.filtered_names)} methods")
        if self.methods_list.count() > 0:
            self.methods_list.setCurrentRow(0)
        else:
            self.detail_text.clear()

    def _clear_filters(self):
        self.search_input.clear()
        self.language_filter.setCurrentIndex(0)
        self._populate_list()

    def _on_method_selected(self, current: QListWidgetItem, previous: Optional[QListWidgetItem]):
        if not current:
            self.detail_text.clear()
            return
        name = current.text()
        calc = self.calculators.get(name)
        if not calc:
            self.detail_text.clear()
            return
        doc = calc.__class__.__doc__ or "No description available."
        # Build detail text
        lines = [f"Name: {name}", "", doc.strip(), "", "Example:"]
        sample_word = self.example_input.text().strip() or self._default_sample_for(calc)
        try:
            value = calc.calculate(sample_word)
            lines.append(f"  {sample_word} = {value}")
        except Exception:
            lines.append("  (Failed to calculate example)")
        self.detail_text.setPlainText("\n".join(lines))

    def _calculate_example(self):
        item = self.methods_list.currentItem()
        if not item:
            QMessageBox.information(self, "No Method Selected", "Select a method first.")
            return
        self._on_method_selected(item, None)

    def _default_sample_for(self, calc: GematriaCalculator) -> str:
        name = calc.name
        if "Hebrew" in name:
            return "אהבה"  # Love
        if "Greek" in name:
            return "λογος"  # logos
        if "English" in name or "TQ" in name:
            return "LIGHT"
        return "TEST"

    def closeEvent(self, event):  # type: ignore
        self.deleteLater()
        event.accept()
