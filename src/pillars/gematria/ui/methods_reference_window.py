"""Methods Reference Window - lists all gematria calculation systems with descriptions."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QWidget, QSplitter, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import List, Dict, Optional
from ..services.base_calculator import GematriaCalculator

class MethodsReferenceWindow(QMainWindow):
    """Window displaying all available gematria calculation methods with their documentation."""

    def __init__(self, calculators: List[GematriaCalculator], parent=None):
        """
          init   logic.
        
        Args:
            calculators: Description of calculators.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Gemetria Methods Reference")
        self.setMinimumSize(1000, 750)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        # Build a mapping of name -> calculator instance
        self.calculators: Dict[str, GematriaCalculator] = {c.name: c for c in calculators}
        self.filtered_names: List[str] = []

        self._setup_ui()
        self._populate_list()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
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
            
        # Determine theme based on language
        theme = self._get_theme_for_calc(name)
        
        # Build HTML content
        html_parts = []
        
        # 1. Title
        html_parts.append(f"<h2 style='color: {theme['dark']}; margin-bottom: 5px;'>{name}</h2>")
        
        # 2. Docstring (formatted)
        doc = calc.__class__.__doc__ or "No description available."
        formatted_doc = self._format_docstring_html(doc, theme)
        html_parts.append(formatted_doc)
        
        # 3. Visual Cipher Chart
        # Only if we have values
        mapping = getattr(calc, "_letter_values", {})
        if mapping:
            chart_html = self._generate_cipher_chart_html(mapping, theme)
            html_parts.append(f"<h3 style='color: {theme['medium']}; margin-top: 20px;'>Cipher Chart</h3>")
            html_parts.append(chart_html)
            
        # 4. Example
        html_parts.append(f"<h3 style='color: {theme['medium']}; margin-top: 20px;'>Example</h3>")
        sample_word = self.example_input.text().strip() or self._default_sample_for(calc)
        try:
            value = calc.calculate(sample_word)
            # Make the value pop
            html_parts.append(
                f"<div style='background-color: {theme['light']}; padding: 10px; border-radius: 6px; border-left: 4px solid {theme['accent']};'>"
                f"<span style='font-size: 14pt;'>{sample_word} = <b>{value}</b></span>"
                f"</div>"
            )
        except Exception:
            html_parts.append("<p>(Failed to calculate example)</p>")

        self.detail_text.setHtml("".join(html_parts))

    def _get_theme_for_calc(self, name: str) -> Dict[str, str]:
        """Return color palette for the calculator language."""
        if "Hebrew" in name:
            return {
                "light": "#e0f2fe",   # Sky 100
                "medium": "#0284c7",  # Sky 600
                "dark": "#0c4a6e",    # Sky 900
                "accent": "#0ea5e9",  # Sky 500
                "border": "#bae6fd"   # Sky 200
            }
        elif "Greek" in name:
            return {
                "light": "#ccfbf1",   # Teal 100
                "medium": "#0d9488",  # Teal 600
                "dark": "#115e59",    # Teal 800
                "accent": "#14b8a6",  # Teal 500
                "border": "#99f6e4"   # Teal 200
            }
        else: # TQ / English
            return {
                "light": "#f3e8ff",   # Purple 100
                "medium": "#9333ea",  # Purple 600
                "dark": "#581c87",    # Purple 900
                "accent": "#a855f7",  # Purple 500
                "border": "#e9d5ff"   # Purple 200
            }

    def _format_docstring_html(self, doc: str, theme: Dict[str, str]) -> str:
        """Convert standard docstring format to styled HTML."""
        lines = []
        # Basic parsing: treating lines ending in ':' as headers
        # and first line as summary
        
        raw_lines = doc.strip().split('\n')
        
        # Summary (first paragraph)
        lines.append(f"<p style='font-size: 11pt; color: #334155;'><b>{raw_lines[0]}</b></p>")
        
        in_list = False
        
        for line in raw_lines[1:]:
            line = line.strip()
            if not line:
                if in_list:
                    lines.append("</ul>")
                    in_list = False
                continue
                
            if line.endswith(':'):
                # Header
                if in_list:
                    lines.append("</ul>")
                    in_list = False
                lines.append(f"<h4 style='color: {theme['medium']}; margin-top: 12px; margin-bottom: 4px;'>{line}</h4>")
            elif line.startswith('- '):
                # List item
                if not in_list:
                    lines.append("<ul style='margin-left: -20px; color: #475569;'>")
                    in_list = True
                content = line[2:]
                lines.append(f"<li>{content}</li>")
            else:
                # Normal text
                if in_list:
                    lines.append("</ul>")
                    in_list = False
                lines.append(f"<p style='color: #475569; margin-top: 4px;'>{line}</p>")
                
        if in_list:
            lines.append("</ul>")
            
        return "".join(lines)

    def _generate_cipher_chart_html(self, mapping: Dict[str, int], theme: Dict[str, str]) -> str:
        """Create a grid of letter-value badges."""
        html = "<div style='width: 100%; display: flex; flex-wrap: wrap; gap: 8px;'>"
        
        # Iterate over mapping. Assuming insertion order preserves alphabet or meaningful order
        # If necessary, we can try to sort if it looks messy, but usually calculators defs are ordered.
        
        style = (
            f"background-color: {theme['light']}; "
            f"border: 1px solid {theme['border']}; "
            f"border-radius: 4px; "
            f"padding: 4px 8px; "
            f"color: {theme['dark']}; "
            f"font-family: monospace; "
            f"font-size: 11pt; "
            f"text-align: center; "
            f"display: inline-block; "
            f"margin: 4px;"
        )
        
        for char, val in mapping.items():
            html += (
                f"<span style='{style}'>"
                f"<b>{char}</b>: {val}"
                f"</span>"
            )
            
        html += "</div>"
        return html

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
        """
        Closeevent logic.
        
        Args:
            event: Description of event.
        
        """
        self.deleteLater()
        event.accept()