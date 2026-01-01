
"""
Formula Wizard - The Scribe's Grimoire.
Two-stage dialog for selecting and configuring spreadsheet formulas with live preview.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QListWidget,
    QDialogButtonBox, QHBoxLayout, QWidget, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QScrollArea, QFormLayout, QPushButton, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from ..services.formula_helper import FormulaHelperService
from ..services.formula_engine import FormulaMetadata, FormulaEngine, FormulaRegistry

class CipherSelectorWidget(QWidget):
    """
    Nested dropdown for selecting Gematria Ciphers.
    Language (English, Hebrew, Greek) -> Method (TQ, Standard, etc.)
    """
    valueChanged = pyqtSignal(str) # Emits "Language (Method)" string
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.combo_lang = QComboBox()
        self.combo_method = QComboBox()
        
        self.layout.addWidget(self.combo_lang, stretch=1)
        self.layout.addWidget(self.combo_method, stretch=2)
        
        # Data Structure: { "English": ["TQ", "Simple"], "Hebrew": ["Standard", ...] }
        self.cipher_map = {}
        self._parse_ciphers()
        
        # Populate Languages
        self.combo_lang.addItems(sorted(self.cipher_map.keys()))
        
        # Connect
        self.combo_lang.currentTextChanged.connect(self._on_lang_changed)
        self.combo_method.currentTextChanged.connect(self._emit_change)
        
        # Init Defaults (Prefer English default)
        if "ENGLISH" in self.cipher_map:
            self.combo_lang.setCurrentText("ENGLISH")
        
        self._on_lang_changed(self.combo_lang.currentText())

    def _parse_ciphers(self):
        """Parse 'LANGUAGE (METHOD)' strings into map."""
        raw_names = FormulaRegistry.get_cipher_names() # e.g. "ENGLISH (TQ)"
        
        for full_name in raw_names:
            # Expected format: "LANG (METHOD)" or just "NAME"
            if "(" in full_name and full_name.endswith(")"):
                parts = full_name.split("(", 1)
                lang = parts[0].strip().upper()
                method = parts[1][:-1].strip() # Remove trailing )
            else:
                # Fallback
                lang = "OTHER"
                method = full_name
            
            if lang not in self.cipher_map:
                self.cipher_map[lang] = []
            self.cipher_map[lang].append(method)

    def _on_lang_changed(self, lang):
        self.combo_method.blockSignals(True)
        self.combo_method.clear()
        if lang in self.cipher_map:
            methods = sorted(self.cipher_map[lang])
            self.combo_method.addItems(methods)
            
            # Smart Default: TQ for English
            if lang == "ENGLISH" and "TQ" in methods:
                self.combo_method.setCurrentText("TQ")
            # Standard for Hebrew/Greek
            elif "STANDARD" in methods:
                self.combo_method.setCurrentText("STANDARD")
                
        self.combo_method.blockSignals(False)
        self._emit_change()

    def _emit_change(self):
        self.valueChanged.emit(self.text())

    def text(self) -> str:
        """Returns the formatted cipher string."""
        lang = self.combo_lang.currentText()
        method = self.combo_method.currentText()
        if not lang or not method: 
            return ""
        
        # Reconstruct exactly as registry expects: "LANG (METHOD)"
        # Capitalization usually handled by registry being case insensitive or UPPER keys
        # We constructed map from registry keys, so we match them.
        # But wait, registry keys are UPPER.
        # Let's ensure we return something that matches exact registry key if possible, 
        # or at least follows the convention.
        return f"{lang} ({method})"

    def setText(self, text):
        # Optional: Implement if we needed to load existing value
        """
        Settext logic.
        
        Args:
            text: Description of text.
        
        """
        pass


class AstroPropertySelectorWidget(QWidget):
    """
    Nested dropdown for selecting ASTRO function properties.
    Category (Names, Glyphs, Technical) -> Property
    """
    valueChanged = pyqtSignal(str)
    
    # Property definitions with categories and descriptions
    PROPERTY_MAP = {
        "Names & Text": [
            ("Sign", "Zodiac sign name (e.g., Capricorn)"),
            ("ZodiacalDegree", "Full notation (e.g., 10° Capricorn 23')"),
        ],
        "Glyphs (Astronomicon)": [
            ("SignGlyph", "Zodiac glyph (e.g., J for Capricorn)"),
            ("BodyGlyph", "Planet glyph (e.g., Q for Sun)"),
            ("GlyphString", "Full with glyphs (e.g., 10^J23)"),
        ],
        "Technical": [
            ("Degree", "Degree within sign (0-29)"),
            ("Longitude", "Absolute ecliptic longitude (0-360)"),
            ("Retrograde", "Is planet retrograde? (Yes/No)"),
        ]
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self.combo_category = QComboBox()
        self.combo_property = QComboBox()
        
        self._layout.addWidget(self.combo_category, stretch=1)
        self._layout.addWidget(self.combo_property, stretch=2)
        
        # Populate categories
        self.combo_category.addItems(list(self.PROPERTY_MAP.keys()))
        
        # Connect
        self.combo_category.currentTextChanged.connect(self._on_category_changed)
        self.combo_property.currentTextChanged.connect(self._emit_change)
        
        # Initialize with first category
        self._on_category_changed(self.combo_category.currentText())
    
    def _on_category_changed(self, category):
        self.combo_property.blockSignals(True)
        self.combo_property.clear()
        
        if category in self.PROPERTY_MAP:
            for prop_name, prop_desc in self.PROPERTY_MAP[category]:
                self.combo_property.addItem(f"{prop_name} - {prop_desc}", prop_name)
        
        self.combo_property.blockSignals(False)
        self._emit_change()
    
    def _emit_change(self):
        self.valueChanged.emit(self.text())
    
    def text(self) -> str:
        """Returns just the property name for formula construction."""
        idx = self.combo_property.currentIndex()
        if idx >= 0:
            return self.combo_property.itemData(idx) or ""
        return ""
    
    def setText(self, text):
        """Set value by property name."""
        for i in range(self.combo_property.count()):
            if self.combo_property.itemData(i) == text:
                self.combo_property.setCurrentIndex(i)
                return


class FormulaArgumentDialog(QDialog):
    """
    Stage 2: The Formula Palette.
    Dynamic form for entering function arguments with live preview.
    """
    def __init__(self, metadata: FormulaMetadata, engine: FormulaEngine = None, parent=None):
        """
          init   logic.
        
        Args:
            metadata: Description of metadata.
            engine: Description of engine.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.metadata = metadata
        self.engine = engine
        self.setWindowTitle("Function Arguments")
        self.resize(500, 400)
        
        self.arg_inputs = {} # name -> QLineEdit
        self.extra_args = [] # List of QLineEdits for variadic args
        self.active_input = None # Track focused input for click-to-select
        
        self._setup_ui()

    def update_active_input(self, text: str):
        """Called by parent window when grid selection changes."""
        if self.active_input:
            self.active_input.setText(text)
            # self.active_input.setFocus() # Do NOT steal focus back, breaks drag selection on grid
            # But textChanged will trigger recalculate.
            self._recalculate()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 1. Header
        header = QLabel(f"<b>{self.metadata.name}</b>")
        header.setStyleSheet("font-size: 14px;")
        layout.addWidget(header)
        
        desc = QLabel(self.metadata.description)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #555; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # 2. Form Area (Scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Generate inputs for fixed arguments
        for arg in self.metadata.arguments:
            self._add_argument_row(arg.name, arg.description, arg.is_optional, arg.type_hint)
            
        scroll.setWidget(self.form_widget)
        layout.addWidget(scroll, stretch=1)
        
        # Variadic Support
        if self.metadata.is_variadic:
            btn_add = QPushButton("+ Add Argument")
            btn_add.clicked.connect(self._add_variadic_arg)
            layout.addWidget(btn_add)
            
        # 3. Guidance & Result
        self.guidance_label = QLabel("Select an argument for help.")
        self.guidance_label.setStyleSheet("color: #0066cc; font-style: italic;")
        layout.addWidget(self.guidance_label)
        
        result_box = QHBoxLayout()
        result_box.addWidget(QLabel("<b>Result:</b>"))
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        result_box.addWidget(self.result_label)
        layout.addLayout(result_box)
        
        # 4. Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Initial calculation
        self._recalculate()

    def _add_argument_row(self, name: str, description: str, is_optional: bool, type_hint: str = "str") -> QWidget:
        """Adds a single row to the form layout."""
        # Label
        label_text = name if not is_optional else f"{name} (opt)"
        label = QLabel(label_text)
        if not is_optional:
            label.setStyleSheet("font-weight: bold;")
            
        if type_hint == "gematria_cipher":
            inp = CipherSelectorWidget()
            inp.valueChanged.connect(self._recalculate)
        elif type_hint == "astro_property":
            inp = AstroPropertySelectorWidget()
            inp.valueChanged.connect(self._recalculate)
        else:
            inp = QLineEdit()
            inp.setPlaceholderText(description)
            inp.textChanged.connect(self._recalculate)
        
        # Help text event
        original_focus_in = inp.focusInEvent if hasattr(inp, 'focusInEvent') else None
        # Widget wrapper might not have focusInEvent easily for composite, 
        # but we can try attaching to child or just generic enterEvent
        
        def on_focus(event):
            """
            Handle focus logic.
            
            Args:
                event: Description of event.
            
            """
            self.guidance_label.setText(f"{name}: {description}")
            
            # Track active input for grid selection
            if isinstance(inp, QLineEdit):
                self.active_input = inp
                
            if original_focus_in:
                original_focus_in(event)
        
        # Attach focus listener
        if isinstance(inp, QLineEdit):
            inp.focusInEvent = on_focus
        else:
            # For composite/other types (like CipherSelector), 
            # we might want to disable grid selection affecting it, or map it differently.
            # For now, only QLineEdit supports range injection.
            pass 
        
        self.form_layout.addRow(label, inp)
        self.arg_inputs[str(id(inp))] = inp
        
        return inp
        
    def _add_variadic_arg(self):
        """Adds a generic variadic argument row."""
        count = len(self.arg_inputs) + 1
        name = f"arg{count}"
        inp = self._add_argument_row(name, "Optional argument", True)
        self.extra_args.append(inp) # specific tracking if needed

    def _recalculate(self):
        """Constructs formula and evaluates preview."""
        code = self.get_formula_text()
        self.result_label.setText("Calculating...")
        
        if self.engine:
            # We need to strip the '=' for evaluation in some contexts, but engine expects it or handles it.
            # Engine.evaluate expects content starting with '='
            try:
                # We construct a fake call. 
                # Note: Evaluation might fail if arguments are empty/invalid.
                result = self.engine.evaluate(code)
                self.result_label.setText(str(result))
            except Exception as e:
                self.result_label.setText("Error")
        else:
            self.result_label.setText("No Engine")

    def get_formula_text(self):
        """Reconstructs =NAME(Arg1, Arg2, ...)"""
        # We need to grab inputs IN ORDER of appearance in layout
        # Since we just appended them to layout, we can iterate layout?
        # Or better, we iterate metadata + extra_args
        
        parts = []
        
        # 1. Fixed Args
        row = 0
        for arg in self.metadata.arguments:
            # Get the widget at (row, 1) in FormLayout (0 is label)
            item = self.form_layout.itemAt(row, QFormLayout.ItemRole.FieldRole)
            if item and item.widget():
                val = item.widget().text().strip()
                if val:
                    parts.append(val)
                elif not arg.is_optional:
                    # Required arg is missing
                    pass 
            row += 1
            
        # 2. Extra/Variadic Args
        # They continue after fixed rows. 
        # But wait, self.arg_inputs is dict, unsafe order.
        # We should rely on layout order or explicit list.
        # Let's iterate layout rows from len(self.metadata.arguments) to end
        
        total_rows = self.form_layout.rowCount()
        for r in range(len(self.metadata.arguments), total_rows):
            item = self.form_layout.itemAt(r, QFormLayout.ItemRole.FieldRole)
            if item and item.widget():
                val = item.widget().text().strip()
                if val:
                    parts.append(val)
                    
        args_str = ", ".join(parts)
        return f"={self.metadata.name}({args_str})"


class FormulaWizardDialog(QDialog):
    """
    Stage 1: Function Selection.
    """
    
    def __init__(self, engine: FormulaEngine = None, parent=None):
        """
          init   logic.
        
        Args:
            engine: Description of engine.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("Insert Function")
        self.resize(600, 450)
        
        self.selected_formula = None
        self.final_text = "=" # Result stored here
        
        self._setup_ui()
        self._populate_list(FormulaHelperService.get_all_definitions())

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 0. Instructions
        layout.addWidget(QLabel("Search for a function or select a category:"))
        
        # 1. Search & Filter
        top_bar = QHBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a brief description...")
        self.search_input.textChanged.connect(self._on_search)
        top_bar.addWidget(QLabel("Search:"))
        top_bar.addWidget(self.search_input, stretch=2)
        
        # Category
        top_bar.addWidget(QLabel("  Or select a category:"))
        self.cat_combo = QComboBox()
        self.cat_combo.addItem("All")
        self.cat_combo.addItems(FormulaHelperService.get_categories())
        self.cat_combo.currentTextChanged.connect(self._on_category_changed)
        top_bar.addWidget(self.cat_combo, stretch=1)
        
        layout.addLayout(top_bar)
        
        # 2. Main Content (List + Description)
        # "Select a function:"
        layout.addWidget(QLabel("Select a function:"))
        
        self.func_list = QListWidget()
        self.func_list.currentItemChanged.connect(self._on_selection_changed)
        self.func_list.itemDoubleClicked.connect(self._on_next_stage) # Double click -> Next
        layout.addWidget(self.func_list)
        
        # Description Box
        self.desc_label = QLabel("No function selected")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("padding: 5px; font-style: italic;")
        layout.addWidget(self.desc_label)
        
        self.syntax_label = QLabel("")
        self.syntax_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.syntax_label)

        # 3. Buttons
        # "OK" means "Next Step" really
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self._on_next_stage)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _populate_list(self, items):
        self.func_list.clear()
        for meta in items:
            item = QListWidgetItem(f"{meta.name}")
            item.setData(Qt.ItemDataRole.UserRole, meta)
            # We store the pure name as clean text effectively? 
            # Or just "NAME" and show desc in bubble?
            # Standard excel shows NAME in list.
            item.setText(meta.name) 
            self.func_list.addItem(item)
            
        if self.func_list.count() > 0:
            self.func_list.setCurrentRow(0)

    def _on_search(self, text):
        # If searching, reset category to All usually? 
        # Or filter within category?
        # Let's simple filter on text first.
        results = FormulaHelperService.search(text)
        self._populate_list(results)

    def _on_category_changed(self, category):
        all_items = FormulaHelperService.get_all_definitions()
        if category == "All":
            filtered = all_items
        else:
            filtered = [x for x in all_items if x.category == category]
        self._populate_list(filtered)

    def _on_selection_changed(self, current, previous):
        if not current:
            self.selected_formula = None
            self.desc_label.setText("")
            self.syntax_label.setText("")
            return
            
        meta = current.data(Qt.ItemDataRole.UserRole)
        self.selected_formula = meta
        self.desc_label.setText(meta.description)
        self.syntax_label.setText(f"Syntax: {meta.syntax}")

    def _on_next_stage(self):
        """Transition to Stage 2: Format Palette."""
        if not self.selected_formula:
            return

        # New Flow: Return Success. Caller (SpreadsheetWindow) initiates Stage 2.
        super().accept()

    def get_selected_formula(self):
        """
        Retrieve selected formula logic.
        
        Returns:
            Result of get_selected_formula operation.
        """
        return self.selected_formula

    def get_insertion_text(self):
        """
        Retrieve insertion text logic.
        
        Returns:
            Result of get_insertion_text operation.
        """
        return self.final_text