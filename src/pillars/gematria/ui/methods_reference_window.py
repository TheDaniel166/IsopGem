"""Methods Reference Window - lists all gematria calculation systems with descriptions."""
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QWidget, QSplitter, QComboBox, QMessageBox, QFrame, QToolButton
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from typing import List, Dict, Optional
from pathlib import Path
from ..services.base_calculator import GematriaCalculator
from shared.ui.theme import (
    COLORS, get_title_style, get_subtitle_style, set_archetype, 
    get_tablet_style, apply_tablet_shadow, get_exegesis_toolbar_style
)

logger = logging.getLogger(__name__)

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
        self.setWindowTitle("Gematria Methods Reference")
        self.setMinimumSize(1200, 800)  # Larger window for more content space
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        # Build a mapping of name -> calculator instance
        self.calculators: Dict[str, GematriaCalculator] = {c.name: c for c in calculators}
        self.filtered_names: List[str] = []
        self.calculator_visible = False  # Track calculator visibility state - start hidden

        self._setup_ui()
        self._populate_list()

    def _setup_ui(self):
        # 1. Nano Banana Protocol (Textured Substrate)
        # ---------------------------------------------------------
        possible_paths = [
            Path("src/assets/patterns/gematria_bg_pattern.png"),
            Path("assets/patterns/gematria_bg_pattern.png"),
            Path(__file__).parent.parent.parent.parent.parent / "assets/patterns/gematria_bg_pattern.png"
        ]
        
        bg_path = None
        for p in possible_paths:
            if p.exists():
                bg_path = p
                break

        central = QWidget()
        central.setObjectName("CentralContainer")
        self.setCentralWidget(central)

        if bg_path:
            abs_path = bg_path.absolute().as_posix()
            central.setStyleSheet(f"""
                QWidget#CentralContainer {{
                    border-image: url("{abs_path}") 0 0 0 0 stretch stretch;
                    border: none;
                    background-color: {COLORS['surface']};
                }}
            """)
        else:
            central.setStyleSheet(f"QWidget#CentralContainer {{ background-color: {COLORS['cloud']}; }}")

        layout = QVBoxLayout(central)
        layout.setSpacing(6)  # Tighter rhythm
        layout.setContentsMargins(12, 8, 12, 8)  # Absolute minimum margins

        # ---------------------------------------------------------
        # 1. Minimal Header (Sigil + Title)
        # ---------------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # The Sigil: 16pt (Even smaller)
        title = QLabel("📚 Gematria Methods")
        title.setStyleSheet(get_title_style(size=16))
        header_layout.addWidget(title)

        # The Scripture: 9pt
        subtitle = QLabel("Index of known calculation systems.")
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9pt; padding-top: 3px;")
        header_layout.addWidget(subtitle)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        layout.addSpacing(8)  # Minimal spacing

        # ---------------------------------------------------------
        # 2. Compact Floating Toolbar
        # ---------------------------------------------------------
        filter_frame = QFrame()
        filter_frame.setObjectName("FloatingHeader")
        # Don't use get_exegesis_toolbar_style() - it breaks button archetypes!
        # Use specific selector instead
        filter_frame.setStyleSheet(f"""
            QFrame#FloatingHeader {{
                background-color: {COLORS['light']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
            }}
        """)
        apply_tablet_shadow(filter_frame)

        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 6, 10, 6)  # Even tighter margins
        filter_layout.setSpacing(10)

        # The Vessel: More compact height (32px)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setMinimumHeight(32) 
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: 10pt;
                padding: 0px 12px;
                border: 1px solid {COLORS['ash']};
                border-radius: 6px;
                background-color: {COLORS['light']};
                color: {COLORS['void']};
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['focus']};
            }}
        """)
        self.search_input.textChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.search_input, stretch=2)

        self.language_filter = QComboBox()
        self.language_filter.addItems(["All", "Hebrew", "Greek", "English", "TQ"])
        self.language_filter.setMinimumHeight(32)
        self.language_filter.setStyleSheet(f"""
            QComboBox {{
                font-size: 10pt;
                padding: 0px 12px;
                border: 1px solid {COLORS['ash']};
                border-radius: 6px;
                background-color: {COLORS['light']};
                color: {COLORS['void']};
            }}
            QComboBox:hover {{
                border-color: {COLORS['focus']};
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['light']};
                color: {COLORS['void']};
                selection-background-color: {COLORS['seeker_soft']};
                selection-color: {COLORS['seeker_dark']};
            }}
        """)
        self.language_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.language_filter, stretch=1)

        clear_btn = QPushButton("✕")  # X icon instead of "Reset"
        clear_btn.setFixedSize(32, 32)  # Square button
        clear_btn.setToolTip("Clear filters")
        clear_btn.clicked.connect(self._clear_filters)
        set_archetype(clear_btn, "ghost")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        filter_layout.addWidget(clear_btn)

        layout.addWidget(filter_frame)
        layout.addSpacing(8)  # Minimal spacing before splitter

        # ---------------------------------------------------------
        # 3. The Divine Split (Islands)
        # ---------------------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(12) # Reduced gap for more content space
        # Make handle transparent to show background texture between islands
        splitter.setStyleSheet(f"""
            QSplitter::handle {{ background: transparent; }}
        """)
        splitter.setChildrenCollapsible(False)

        # Left Tablet: The Catalog (Question)
        left_tablet = QFrame()  # Use QFrame for visual styling
        left_tablet.setObjectName("LeftTablet")
        left_tablet.setFrameShape(QFrame.Shape.StyledPanel)
        # Apply inline style ONLY to this specific widget using object selector
        # This prevents overriding app stylesheet for children (buttons)
        left_tablet.setStyleSheet(f"""
            QFrame#LeftTablet {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 24px;
            }}
        """)
        apply_tablet_shadow(left_tablet)

        left_layout = QVBoxLayout(left_tablet)
        left_layout.setContentsMargins(12, 8, 12, 12)  # Minimal margins
        left_layout.setSpacing(6)  # Tighter spacing

        # H3 Header - Minimal and subtle
        list_label = QLabel("Sacred Ciphers")
        list_label.setStyleSheet(f"font-weight: 600; font-size: 9pt; color: {COLORS['text_secondary']};")
        left_layout.addWidget(list_label)

        self.methods_list = QListWidget()
        self.methods_list.setFrameShape(QFrame.Shape.NoFrame) # Seamless integration
        self.methods_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                color: {COLORS['void']};
                font-size: 10pt;
                outline: none;
            }}
            QListWidget::item {{ 
                padding: 8px; 
                border-radius: 6px;
                margin-bottom: 4px;
            }}
            QListWidget::item:selected {{
                background: {COLORS['magus_soft']};
                color: {COLORS['magus_dark']};
                font-weight: 600;
            }}
            QListWidget::item:hover:!selected {{ 
                background: {COLORS['marble']}; 
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['ash']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self.methods_list.currentItemChanged.connect(self._on_method_selected)
        left_layout.addWidget(self.methods_list)

        splitter.addWidget(left_tablet)

        # Right Tablet: The Codex (Answer) - Expanded Width
        right_tablet = QFrame()  # Use QFrame for visual styling
        right_tablet.setObjectName("RightTablet")
        right_tablet.setFrameShape(QFrame.Shape.StyledPanel)
        # Apply inline style ONLY to this specific widget using object selector
        right_tablet.setStyleSheet(f"""
            QFrame#RightTablet {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 24px;
            }}
        """)
        apply_tablet_shadow(right_tablet)

        right_layout = QVBoxLayout(right_tablet)
        right_layout.setContentsMargins(12, 8, 12, 12)  # Minimal margins for maximum space
        right_layout.setSpacing(6)  # Tighter spacing

        # Header with toggle button - Minimal
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        # H2 Header - Minimal size
        detail_label = QLabel("Esoteric Archives")
        detail_label.setStyleSheet(f"font-weight: 600; font-size: 9pt; color: {COLORS['text_secondary']};")
        header_layout.addWidget(detail_label)

        header_layout.addStretch()

        # Toggle button for calculator - Smaller and more subtle
        self.toggle_calculator_btn = QToolButton()
        self.toggle_calculator_btn.setText("▲")  # Start with up arrow since hidden by default
        self.toggle_calculator_btn.setToolTip("Show Calculator")
        self.toggle_calculator_btn.setFixedSize(24, 24)
        self.toggle_calculator_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: 1px solid {COLORS['ash']};
                border-radius: 4px;
                color: {COLORS['text_secondary']};
                font-size: 9pt;
                font-weight: bold;
            }}
            QToolButton:hover {{
                background-color: {COLORS['marble']};
                border-color: {COLORS['stone']};
                color: {COLORS['void']};
            }}
        """)
        self.toggle_calculator_btn.clicked.connect(self._toggle_calculator_visibility)
        header_layout.addWidget(self.toggle_calculator_btn)

        right_layout.addLayout(header_layout)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setFrameShape(QFrame.Shape.NoFrame)
        self.detail_text.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                color: {COLORS['void']};
                font-size: 12pt;
                line-height: 1.6;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['stone']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        right_layout.addWidget(self.detail_text)  # Fill all available space

        splitter.addWidget(right_tablet)

        # --- FLOATING CALCULATOR (Separate Island) ---
        # Create as child of right_tablet so it floats on top
        self.calculator_container = QFrame(right_tablet)  # Use QFrame for styling
        self.calculator_container.setObjectName("FloatingCalculator")
        self.calculator_container.setFrameShape(QFrame.Shape.StyledPanel)
        # Use get_tablet_style which doesn't override button styles
        self.calculator_container.setStyleSheet(f"""
            QFrame#FloatingCalculator {{
                background-color: {COLORS['light']};
                border: 2px solid {COLORS['magus_soft']};
                border-radius: 12px;
            }}
        """)
        apply_tablet_shadow(self.calculator_container)

        calculator_layout = QVBoxLayout(self.calculator_container)
        calculator_layout.setContentsMargins(16, 16, 16, 16)  # Even margins for centering
        calculator_layout.setSpacing(0)  # No extra spacing needed

        example_layout = QHBoxLayout()
        example_layout.setSpacing(12)
        example_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center horizontally

        self.example_input = QLineEdit()
        self.example_input.setPlaceholderText("Inscribe word/phrase...")
        self.example_input.setMinimumHeight(42)
        self.example_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: 11pt;
                padding: 0px 16px;
                border: 1px solid {COLORS['ash']};
                border-radius: 8px;
                background-color: {COLORS['cloud']};
                color: {COLORS['void']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['magus_dark']};
            }}
        """)
        example_layout.addWidget(self.example_input, stretch=3)

        example_btn = QPushButton("Invoke")
        example_btn.setMinimumHeight(42)  # Match input height
        example_btn.clicked.connect(self._calculate_example)
        set_archetype(example_btn, "magus")
        example_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        example_layout.addWidget(example_btn, stretch=1)

        calculator_layout.addLayout(example_layout)

        # Position it and hide by default
        self.calculator_container.hide()
        self.calculator_container.setFixedHeight(80)
        # Will be repositioned in resizeEvent

        # Apply The Divine Proportion (Expanded Content): 1:5 for maximum description space
        splitter.setStretchFactor(0, 1)  # List (Very Compact)
        splitter.setStretchFactor(1, 5)  # Details (Maximum Expanded)

        # Set initial sizes - left panel narrower
        splitter.setSizes([200, 1000])

        layout.addWidget(splitter, stretch=1)  # Give splitter all vertical space

    def _toggle_calculator_visibility(self):
        """Toggle the visibility of the calculator input area."""
        self.calculator_visible = not self.calculator_visible

        if self.calculator_visible:
            self._position_calculator()
            self.calculator_container.show()
            self.calculator_container.raise_()  # Bring to front
            self.toggle_calculator_btn.setText("▼")
            self.toggle_calculator_btn.setToolTip("Hide Calculator")
        else:
            self.calculator_container.hide()
            self.toggle_calculator_btn.setText("▲")
            self.toggle_calculator_btn.setToolTip("Show Calculator")

    def _position_calculator(self):
        """Position the floating calculator at the bottom center of the description area."""
        if not hasattr(self, 'calculator_container') or not hasattr(self, 'detail_text'):
            return

        # Get the description area geometry
        parent = self.calculator_container.parent()
        if not parent:
            return

        parent_width = parent.width()
        parent_height = parent.height()

        calc_width = int(parent_width * 0.85)  # 85% of parent width
        calc_height = 80

        # Position at bottom center with some margin
        x = (parent_width - calc_width) // 2
        y = parent_height - calc_height - 20  # 20px from bottom

        self.calculator_container.setGeometry(x, y, calc_width, calc_height)

    def resizeEvent(self, event):
        """Handle window resize to reposition floating calculator."""
        super().resizeEvent(event)
        if self.calculator_visible:
            self._position_calculator()

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
        # Status removed to save space
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
                f"<span style='font-size: 14pt; color: {COLORS['void']}'>{sample_word} = <b>{value}</b></span>"
                f"</div>"
            )
        except Exception:
            html_parts.append("<p>(Failed to calculate example)</p>")

        self.detail_text.setHtml("".join(html_parts))

    def _get_theme_for_calc(self, name: str) -> Dict[str, str]:
        """Return color palette for the calculator language.
        
        Visual Liturgy Exemption: These colors are HTML document content (not UI chrome).
        """
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
        
        # Use theme tokens where possible, or passed theme colors
        raw_lines = doc.strip().split('\n')
        
        # Summary (first paragraph)
        lines.append(f"<p style='font-size: 11pt; color: {COLORS['text_secondary']};'><b>{raw_lines[0]}</b></p>")
        
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
                # Use theme medium for emphasis
                lines.append(f"<h4 style='color: {theme['medium']}; margin-top: 12px; margin-bottom: 4px;'>{line}</h4>")
            elif line.startswith('- '):
                # List item
                if not in_list:
                    # Using text_secondary for list items
                    lines.append(f"<ul style='margin-left: -20px; color: {COLORS['text_secondary']};'>")
                    in_list = True
                content = line[2:]
                lines.append(f"<li>{content}</li>")
            else:
                # Normal text
                if in_list:
                    lines.append("</ul>")
                    in_list = False
                lines.append(f"<p style='color: {COLORS['text_secondary']}; margin-top: 4px;'>{line}</p>")
                
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