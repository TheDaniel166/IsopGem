"""
Visual Math Editor Dialog - Comprehensive LaTeX Editing Interface.

**Purpose**:
Provide a rich, visual environment for creating and editing LaTeX mathematical
expressions with live preview, symbol palette, templates, and formula library.

**Architecture**:
3-Pane Layout:
- Left: Symbol Palette + Templates (tabs)
- Center: Code Editor with syntax highlighting
- Right: Live Preview + Rendering Options

**Features**:
- Click-to-insert symbols organized by category
- Template browser with predefined equations
- Formula library for saving/reusing favorites
- Real-time LaTeX preview with debouncing
- Syntax highlighting
- Rendering options (color, size, DPI)
- Export capabilities

**Usage**:
```python
dialog = VisualMathEditorDialog(parent)
dialog.set_latex("E = mc^2")

if dialog.exec() == QDialog.DialogCode.Accepted:
    latex = dialog.get_latex()
    image = dialog.get_rendered_image()
```
"""

import logging
from typing import Optional
import qtawesome as qta

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QTabWidget, QWidget, QSplitter, QMessageBox,
    QListWidget, QListWidgetItem, QLineEdit, QSpinBox,
    QGroupBox, QComboBox, QDialogButtonBox, QScrollArea,
    QGridLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont,
    QImage, QTextDocument, QPixmap
)

from .math_renderer import MathRenderer
from .latex_symbols import LATEX_SYMBOLS
from .latex_templates import LATEX_TEMPLATES, create_template
from .formula_library import FormulaLibrary, seed_default_formulas

logger = logging.getLogger(__name__)


# ============================================================================
# SYNTAX HIGHLIGHTER
# ============================================================================

class LaTeXSyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for LaTeX code.
    
    **Features**:
    - Commands: \\command (blue)
    - Curly braces: {} (red)
    - Square brackets: [] (orange)
    - Superscripts/subscripts: ^_ (purple)
    - Comments: % ... (green)
    """
    
    def __init__(self, parent: Optional[QTextDocument] = None):
        super().__init__(parent)
        
        # Command (\something)
        self.command_format = QTextCharFormat()
        self.command_format.setForeground(QColor("#3B82F6"))  # Blue
        self.command_format.setFontWeight(QFont.Weight.Bold)
        
        # Braces {}
        self.brace_format = QTextCharFormat()
        self.brace_format.setForeground(QColor("#EF4444"))  # Red
        
        # Brackets []
        self.bracket_format = QTextCharFormat()
        self.bracket_format.setForeground(QColor("#F59E0B"))  # Orange
        
        # Super/Subscripts ^_
        self.script_format = QTextCharFormat()
        self.script_format.setForeground(QColor("#A855F7"))  # Purple
        
        # Comments %
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#10B981"))  # Green
        self.comment_format.setFontItalic(True)
    
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text."""
        # Comments (% to end of line)
        if '%' in text:
            idx = text.index('%')
            self.setFormat(idx, len(text) - idx, self.comment_format)
            text = text[:idx]  # Don't highlight inside comments
        
        # Commands (\word)
        i = 0
        while i < len(text):
            if text[i] == '\\':
                j = i + 1
                while j < len(text) and (text[j].isalnum() or text[j] == '*'):
                    j += 1
                self.setFormat(i, j - i, self.command_format)
                i = j
            else:
                i += 1
        
        # Braces
        for i, char in enumerate(text):
            if char in '{}':
                self.setFormat(i, 1, self.brace_format)
        
        # Brackets
        for i, char in enumerate(text):
            if char in '[]':
                self.setFormat(i, 1, self.bracket_format)
        
        # Super/Subscripts
        for i, char in enumerate(text):
            if char in '^_':
                self.setFormat(i, 1, self.script_format)


# ============================================================================
# SYMBOL PALETTE
# ============================================================================

class SymbolPaletteWidget(QWidget):
    """
    Widget displaying categorized LaTeX symbols.
    
    **Signals**:
        symbol_clicked(str): Emitted when a symbol is clicked (LaTeX code)
    """
    
    symbol_clicked = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter symbols...")
        self.search_box.textChanged.connect(self._filter_symbols)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Tab widget for categories
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)  # Vertical tabs on left
        self.tab_widget.setUsesScrollButtons(False)  # Disable arrow buttons
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideNone)  # Don't elide text
        
        # Make tab bar compact with icon-only display
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                min-width: 40px;
                max-width: 40px;
                min-height: 48px;
                padding: 8px;
            }
            QTabBar {
                qproperty-drawBase: 0;
            }
        """)
        
        # Icon mapping for categories (ONLY valid FontAwesome 5 Solid icons)
        category_icons = {
            "Greek Letters (Lowercase)": qta.icon("fa5s.font", color="#3B82F6"),
            "Greek Letters (Uppercase)": qta.icon("fa5s.language", color="#3B82F6"),
            "Operators": qta.icon("fa5s.plus", color="#10B981"),
            "Relations": qta.icon("fa5s.equals", color="#F59E0B"),
            "Arrows": qta.icon("fa5s.arrow-right", color="#EF4444"),
            "Set Theory": qta.icon("fa5s.circle", color="#8B5CF6"),
            "Logic": qta.icon("fa5s.lightbulb", color="#EC4899"),
            "Accents": qta.icon("fa5s.superscript", color="#6366F1"),
            "Miscellaneous": qta.icon("fa5s.star", color="#64748B"),
        }
        
        # Create a tab for each category
        for category, symbols in LATEX_SYMBOLS.items():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            container = QWidget()
            grid = QGridLayout(container)
            grid.setSpacing(5)
            
            for i, symbol in enumerate(symbols):
                btn = QPushButton(symbol.unicode)
                btn.setToolTip(f"{symbol.name}\n{symbol.latex}")
                btn.setFixedSize(QSize(50, 40))
                btn.clicked.connect(lambda checked, s=symbol: self.symbol_clicked.emit(s.latex))
                
                row = i // 4  # 4 columns instead of 5
                col = i % 4
                grid.addWidget(btn, row, col)
            
            grid.setRowStretch(grid.rowCount(), 1)
            scroll.setWidget(container)
            
            # Add tab with icon only (empty text)
            icon = category_icons.get(category, qta.icon("fa5s.star", color="#64748B"))
            self.tab_widget.addTab(scroll, icon, "")
            self.tab_widget.setTabToolTip(self.tab_widget.count() - 1, category)
        
        layout.addWidget(self.tab_widget)
    
    def _filter_symbols(self, query: str):
        """Filter symbols based on search query."""
        # TODO: Implement search filter
        pass


# ============================================================================
# TEMPLATE BROWSER
# ============================================================================

class TemplateBrowserWidget(QWidget):
    """
    Widget displaying categorized LaTeX templates.
    
    **Signals**:
        template_selected(str, str): Emitted when a template is selected (name, latex)
    """
    
    template_selected = pyqtSignal(str, str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Category selector
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(sorted(set(t["category"] for t in LATEX_TEMPLATES.values())))
        self.category_combo.currentTextChanged.connect(self._update_list)
        cat_layout.addWidget(self.category_combo)
        layout.addLayout(cat_layout)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self._on_template_double_clicked)
        layout.addWidget(self.template_list)
        
        # Insert button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        insert_btn = QPushButton("Insert Template")
        insert_btn.clicked.connect(self._on_insert_clicked)
        btn_layout.addWidget(insert_btn)
        layout.addLayout(btn_layout)
        
        # Initial population
        self._update_list()
    
    def _update_list(self):
        """Update template list based on selected category."""
        self.template_list.clear()
        
        selected_category = self.category_combo.currentText()
        
        for name, template in LATEX_TEMPLATES.items():
            if template["category"] == selected_category:
                item = QListWidgetItem(name)
                item.setToolTip(template["description"])
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.template_list.addItem(item)
    
    def _on_template_double_clicked(self, item: QListWidgetItem):
        """Handle template double-click."""
        self._insert_selected()
    
    def _on_insert_clicked(self):
        """Handle insert button click."""
        self._insert_selected()
    
    def _insert_selected(self):
        """Emit signal for selected template."""
        current = self.template_list.currentItem()
        if current:
            name = current.data(Qt.ItemDataRole.UserRole)
            template_ast = create_template(name)
            if template_ast:
                self.template_selected.emit(name, template_ast.latex_code)


# ============================================================================
# FORMULA LIBRARY WIDGET
# ============================================================================

class FormulaLibraryWidget(QWidget):
    """
    Widget for browsing and managing saved formulas.
    
    **Signals**:
        formula_selected(str, str): Emitted when a formula is selected (name, latex)
    """
    
    formula_selected = pyqtSignal(str, str)
    
    def __init__(self, library: FormulaLibrary, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.library = library
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # View mode selector
        view_layout = QHBoxLayout()
        view_layout.addWidget(QLabel("View:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(["All", "By Category", "Recent", "Most Used"])
        self.view_combo.currentTextChanged.connect(self._update_list)
        view_layout.addWidget(self.view_combo)
        layout.addLayout(view_layout)
        
        # Category selector (hidden by default)
        self.category_layout = QHBoxLayout()
        self.category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self._update_list)
        self.category_layout.addWidget(self.category_combo)
        self.category_widget = QWidget()
        self.category_widget.setLayout(self.category_layout)
        self.category_widget.setVisible(False)
        layout.addWidget(self.category_widget)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search formulas...")
        self.search_box.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Formula list
        self.formula_list = QListWidget()
        self.formula_list.itemDoubleClicked.connect(self._on_formula_double_clicked)
        layout.addWidget(self.formula_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        insert_btn = QPushButton("Insert")
        insert_btn.clicked.connect(self._on_insert_clicked)
        btn_layout.addWidget(insert_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._on_delete_clicked)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # Initial population
        self._update_categories()
        self._update_list()
    
    def _update_categories(self):
        """Update category combo box with top-level categories."""
        self.category_combo.clear()
        # Get top-level categories only (e.g., "Physics" not "Physics: Mechanics")
        categories = self.library.get_categories(top_level_only=True)
        self.category_combo.addItems(categories)
    
    def _update_list(self):
        """Update formula list based on view mode."""
        self.formula_list.clear()
        
        view_mode = self.view_combo.currentText()
        
        # Show/hide category selector
        self.category_widget.setVisible(view_mode == "By Category")
        
        # Get formulas
        if view_mode == "All":
            formulas = self.library.get_all()
        elif view_mode == "By Category":
            category = self.category_combo.currentText()
            formulas = self.library.get_by_category(category)
        elif view_mode == "Recent":
            formulas = self.library.get_recent(20)
        elif view_mode == "Most Used":
            formulas = self.library.get_most_used(20)
        else:
            formulas = []
        
        # Populate list
        for formula in formulas:
            display_text = formula.name
            if view_mode != "By Category":
                display_text += f" [{formula.category}]"
            
            item = QListWidgetItem(display_text)
            item.setToolTip(f"{formula.description}\n\nLaTeX: {formula.latex}")
            item.setData(Qt.ItemDataRole.UserRole, formula.name)
            self.formula_list.addItem(item)
    
    def _on_search(self, query: str):
        """Handle search."""
        if not query:
            self._update_list()
            return
        
        self.formula_list.clear()
        results = self.library.search(query)
        
        for formula in results:
            item = QListWidgetItem(f"{formula.name} [{formula.category}]")
            item.setToolTip(f"{formula.description}\n\nLaTeX: {formula.latex}")
            item.setData(Qt.ItemDataRole.UserRole, formula.name)
            self.formula_list.addItem(item)
    
    def _on_formula_double_clicked(self, item: QListWidgetItem):
        """Handle formula double-click."""
        self._insert_selected()
    
    def _on_insert_clicked(self):
        """Handle insert button click."""
        self._insert_selected()
    
    def _insert_selected(self):
        """Emit signal for selected formula."""
        current = self.formula_list.currentItem()
        if current:
            name = current.data(Qt.ItemDataRole.UserRole)
            formula = self.library.get_by_name(name)
            if formula:
                self.library.mark_used(name)
                self.formula_selected.emit(name, formula.latex)
    
    def _on_delete_clicked(self):
        """Handle delete button click."""
        current = self.formula_list.currentItem()
        if not current:
            return
        
        name = current.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Delete Formula",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.library.remove_formula(name)
            self._update_list()
            logger.info(f"Deleted formula: {name}")
    
    def refresh(self):
        """Refresh the list (call after saving new formulas)."""
        self._update_categories()
        self._update_list()


# ============================================================================
# MAIN DIALOG
# ============================================================================

class VisualMathEditorDialog(QDialog):
    """
    Comprehensive visual editor for LaTeX mathematical expressions.
    
    **Layout**:
    ```
    ┌─────────────┬──────────────┬──────────────┐
    │   Palette   │    Editor    │   Preview    │
    │  (Tabs)     │  (Code+HL)   │  (Live)      │
    │             │              │              │
    │ - Symbols   │              │  [Render Opts]│
    │ - Templates │              │              │
    │ - Library   │              │              │
    └─────────────┴──────────────┴──────────────┘
                [Save to Library] [OK] [Cancel]
    ```
    
    **Usage**:
    ```python
    dialog = VisualMathEditorDialog(parent, math_renderer)
    dialog.set_latex("\\int_0^\\infty e^{-x^2} dx")
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        latex = dialog.get_latex()
        image = dialog.get_rendered_image()
    ```
    """
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        math_renderer: Optional[MathRenderer] = None,
        initial_latex: str = ""
    ):
        super().__init__(parent)
        self.math_renderer = math_renderer or MathRenderer()
        self.formula_library = FormulaLibrary()
        seed_default_formulas(self.formula_library)
        
        self.current_image: Optional[QImage] = None
        
        self.setWindowTitle("Visual Math Editor")
        self.resize(1200, 700)
        
        self._init_ui()
        
        if initial_latex:
            self.set_latex(initial_latex)
        
        # Initial render
        self._schedule_preview_update()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        
        # Main 3-pane splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANE: Palette Tabs
        left_tabs = QTabWidget()
        left_tabs.setTabPosition(QTabWidget.TabPosition.West)  # Vertical tabs on left
        
        # Make tabs compact with icon-only display
        left_tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 40px;
                max-width: 40px;
                min-height: 48px;
                padding: 8px;
            }
            QTabBar {
                qproperty-drawBase: 0;
            }
        """)
        
        # Symbols tab
        self.symbol_palette = SymbolPaletteWidget()
        self.symbol_palette.symbol_clicked.connect(self._insert_symbol)
        symbols_icon = qta.icon("fa5s.square-root-alt", color="#3B82F6")
        left_tabs.addTab(self.symbol_palette, symbols_icon, "")
        left_tabs.setTabToolTip(0, "Symbols")
        
        # Templates tab
        self.template_browser = TemplateBrowserWidget()
        self.template_browser.template_selected.connect(self._insert_template)
        templates_icon = qta.icon("fa5s.clipboard", color="#10B981")
        left_tabs.addTab(self.template_browser, templates_icon, "")
        left_tabs.setTabToolTip(1, "Templates")
        
        # Library tab
        self.library_widget = FormulaLibraryWidget(self.formula_library)
        self.library_widget.formula_selected.connect(self._insert_formula)
        library_icon = qta.icon("fa5s.book", color="#F59E0B")
        left_tabs.addTab(self.library_widget, library_icon, "")
        left_tabs.setTabToolTip(2, "Library")
        
        splitter.addWidget(left_tabs)
        
        # CENTER PANE: Code Editor
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.addWidget(QLabel("LaTeX Code:"))
        
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Courier New", 12))
        self.code_editor.textChanged.connect(self._schedule_preview_update)
        
        # Apply syntax highlighting
        self.highlighter = LaTeXSyntaxHighlighter(self.code_editor.document())
        
        center_layout.addWidget(self.code_editor)
        splitter.addWidget(center_widget)
        
        # RIGHT PANE: Preview + Options
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Live Preview:"))
        
        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #ccc; }")
        right_layout.addWidget(self.preview_label, 1)
        
        # Render options
        options_group = QGroupBox("Render Options")
        options_layout = QVBoxLayout()
        
        # High Quality toggle
        self.high_quality_check = QCheckBox("High Quality Rendering")
        self.high_quality_check.setChecked(True)  # Enabled by default
        self.high_quality_check.setToolTip(
            "Enable anti-aliasing and enhanced font rendering for sharper output"
        )
        self.high_quality_check.stateChanged.connect(self._schedule_preview_update)
        options_layout.addWidget(self.high_quality_check)
        
        # DPI
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("DPI:"))
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(200)  # Increased from 150 for better quality
        self.dpi_spin.setToolTip("Resolution (higher = sharper, but slower)")
        self.dpi_spin.valueChanged.connect(self._schedule_preview_update)
        dpi_layout.addWidget(self.dpi_spin)
        dpi_layout.addStretch()
        options_layout.addLayout(dpi_layout)
        
        # Font size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(14)
        self.size_spin.valueChanged.connect(self._schedule_preview_update)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        options_layout.addLayout(size_layout)
        
        # Color - Comprehensive Mathematical Palette
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_combo = QComboBox()
        
        # Comprehensive color palette for mathematical expressions
        # Organized by category for easy selection
        math_colors = [
            # === STANDARD ===
            "Black",
            "White",
            "Gray",
            "DarkGray",
            "LightGray",
            "Silver",
            
            # === PRIMARY COLORS ===
            "Red",
            "Green",
            "Blue",
            "Yellow",
            "Cyan",
            "Magenta",
            
            # === DARK VARIANTS ===
            "DarkRed",
            "DarkGreen",
            "DarkBlue",
            "DarkYellow",
            "DarkCyan",
            "DarkMagenta",
            
            # === EXTENDED SPECTRUM ===
            "Orange",
            "DarkOrange",
            "OrangeRed",
            "Purple",
            "DarkPurple",
            "Violet",
            "DarkViolet",
            "Indigo",
            "Pink",
            "DeepPink",
            "HotPink",
            "Crimson",
            "Brown",
            "SaddleBrown",
            "Maroon",
            "Olive",
            "Teal",
            "Navy",
            
            # === MATHEMATICAL HIGHLIGHTING ===
            "RoyalBlue",      # For primary equations
            "SteelBlue",      # For secondary equations
            "CornflowerBlue", # For definitions
            "DodgerBlue",     # For theorems
            "DeepSkyBlue",    # For proofs
            "SkyBlue",        # For remarks
            
            "ForestGreen",    # For positive terms
            "SeaGreen",       # For convergent series
            "MediumSeaGreen", # For solutions
            "LimeGreen",      # For correct answers
            "SpringGreen",    # For approximations
            
            "Tomato",         # For errors/corrections
            "Coral",          # For warnings
            "Salmon",         # For deprecated
            "LightCoral",     # For notes
            
            "Gold",           # For important formulas
            "Goldenrod",      # For key results
            "Khaki",          # For examples
            
            "Orchid",         # For abstract concepts
            "MediumOrchid",   # For transformations
            "DarkOrchid",     # For operators
            "BlueViolet",     # For eigenvectors
            "MediumPurple",   # For complex numbers
            
            "Chocolate",      # For constants
            "Peru",           # For parameters
            "Sienna",         # For variables
            
            "SlateGray",      # For subscripts
            "DimGray",        # For superscripts
            "DarkSlateGray",  # For indices
            
            # === LIGHT TINTS (for backgrounds/highlights) ===
            "LightBlue",
            "LightGreen",
            "LightYellow",
            "LightCyan",
            "LightPink",
            "Lavender",
            "MintCream",
            "Azure",
            "Ivory",
            "Beige",
        ]
        
        self.color_combo.addItems(math_colors)
        self.color_combo.setCurrentText("Black")  # Default to black
        self.color_combo.currentTextChanged.connect(self._schedule_preview_update)
        color_layout.addWidget(self.color_combo)
        color_layout.addStretch()
        options_layout.addLayout(color_layout)
        
        options_group.setLayout(options_layout)
        right_layout.addWidget(options_group)
        
        splitter.addWidget(right_widget)
        
        # Set splitter sizes (30%, 40%, 30%)
        splitter.setSizes([300, 400, 300])
        
        layout.addWidget(splitter)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        
        save_to_library_btn = QPushButton("Save to Library")
        save_to_library_btn.clicked.connect(self._save_to_library)
        btn_layout.addWidget(save_to_library_btn)
        
        copy_latex_btn = QPushButton("Copy LaTeX")
        copy_latex_btn.setToolTip("Copy LaTeX formula to clipboard")
        copy_latex_btn.clicked.connect(self._copy_latex)
        btn_layout.addWidget(copy_latex_btn)
        
        export_png_btn = QPushButton("Export PNG")
        export_png_btn.setToolTip("Export rendered formula as PNG image")
        export_png_btn.clicked.connect(self._export_png)
        btn_layout.addWidget(export_png_btn)
        
        btn_layout.addStretch()
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        btn_layout.addWidget(button_box)
        
        layout.addLayout(btn_layout)
        
        # Timer for debounced preview
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)
    
    def _schedule_preview_update(self):
        """Schedule a preview update (debounced)."""
        self.preview_timer.stop()
        self.preview_timer.start(500)  # 500ms delay
    
    def _update_preview(self):
        """Update the live preview."""
        latex = self.code_editor.toPlainText().strip()
        
        if not latex:
            self.preview_label.setText("(empty)")
            self.current_image = None
            return
        
        # Get render options
        dpi = self.dpi_spin.value()
        fontsize = self.size_spin.value()
        color = self.color_combo.currentText().lower()
        high_quality = self.high_quality_check.isChecked()
        
        # Render
        try:
            image = self.math_renderer.render_latex(
                latex,
                dpi=dpi,
                fontsize=fontsize,
                color=color,
                use_high_quality=high_quality
            )
            
            if image and not image.isNull():
                self.current_image = image
                # Convert QImage to QPixmap for display
                pixmap = QPixmap.fromImage(image)
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
            else:
                self.preview_label.setText("(render failed)")
                self.current_image = None
        
        except Exception as e:
            logger.error(f"Preview render failed: {e}")
            self.preview_label.setText(f"Error: {e}")
            self.current_image = None
    
    def _insert_symbol(self, latex: str):
        """Insert a symbol at cursor position."""
        cursor = self.code_editor.textCursor()
        cursor.insertText(latex)
        self.code_editor.setFocus()
    
    def _insert_template(self, name: str, latex: str):
        """Insert a template."""
        self.code_editor.setPlainText(latex)
        self.code_editor.setFocus()
    
    def _insert_formula(self, name: str, latex: str):
        """Insert a formula from library."""
        self.code_editor.setPlainText(latex)
        self.code_editor.setFocus()
    
    def _save_to_library(self):
        """Save current equation to library."""
        latex = self.code_editor.toPlainText().strip()
        
        if not latex:
            QMessageBox.warning(self, "No Equation", "Please enter an equation first.")
            return
        
        # Show dialog to get name and category
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self,
            "Save to Library",
            "Formula Name:"
        )
        
        if not ok or not name:
            return
        
        category, ok = QInputDialog.getItem(
            self,
            "Save to Library",
            "Category:",
            self.formula_library.get_categories() + ["New Category..."],
            0,
            True
        )
        
        if not ok or not category:
            return
        
        if category == "New Category...":
            category, ok = QInputDialog.getText(
                self,
                "Save to Library",
                "New Category Name:"
            )
            if not ok or not category:
                return
        
        # Save
        self.formula_library.add_formula(name, latex, category)
        self.library_widget.refresh()
        
        QMessageBox.information(
            self,
            "Saved",
            f"Formula '{name}' saved to library."
        )
    
    def _copy_latex(self):
        """Copy LaTeX formula to clipboard with math delimiters."""
        from PyQt6.QtWidgets import QApplication, QInputDialog
        
        latex = self.get_latex()
        if not latex:
            QMessageBox.warning(
                self,
                "No Formula",
                "There is no LaTeX formula to copy."
            )
            return
        
        # Ask user for format
        formats = [
            "Display Math ($$...$$) - Centered, large",
            "Inline Math ($...$) - In-line with text",
            "Raw LaTeX (no delimiters)"
        ]
        
        choice, ok = QInputDialog.getItem(
            self,
            "Copy Format",
            "Select the format to copy:",
            formats,
            0,  # Default to display math
            False
        )
        
        if not ok:
            return
        
        # Format the LaTeX based on choice
        if "Display Math" in choice:
            # Ensure we don't double-wrap
            latex_stripped = latex.strip()
            if latex_stripped.startswith('$$') and latex_stripped.endswith('$$'):
                formatted_latex = latex_stripped
            elif latex_stripped.startswith('$') and latex_stripped.endswith('$'):
                formatted_latex = f"$${latex_stripped[1:-1]}$$"
            else:
                formatted_latex = f"$${latex}$$"
        elif "Inline Math" in choice:
            # Ensure we don't double-wrap
            latex_stripped = latex.strip()
            if latex_stripped.startswith('$$') and latex_stripped.endswith('$$'):
                formatted_latex = f"${latex_stripped[2:-2]}$"
            elif latex_stripped.startswith('$') and latex_stripped.endswith('$'):
                formatted_latex = latex_stripped
            else:
                formatted_latex = f"${latex}$"
        else:  # Raw LaTeX
            formatted_latex = latex
        
        clipboard = QApplication.clipboard()
        clipboard.setText(formatted_latex)
        
        QMessageBox.information(
            self,
            "Copied",
            f"LaTeX formula copied to clipboard as:\n{formatted_latex[:100]}{'...' if len(formatted_latex) > 100 else ''}"
        )
    
    def _export_png(self):
        """Export rendered formula as PNG image."""
        from PyQt6.QtWidgets import QFileDialog
        
        if not self.current_image or self.current_image.isNull():
            QMessageBox.warning(
                self,
                "No Image",
                "There is no rendered image to export. Please render a formula first."
            )
            return
        
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Formula as PNG",
            "",
            "PNG Image (*.png)"
        )
        
        if not file_path:
            return  # User cancelled
        
        # Ensure .png extension
        if not file_path.lower().endswith('.png'):
            file_path += '.png'
        
        # Save the image
        try:
            success = self.current_image.save(file_path, 'PNG')
            if success:
                QMessageBox.information(
                    self,
                    "Exported",
                    f"Formula exported successfully to:\n{file_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    "Failed to save the image. Please try again."
                )
        except Exception as e:
            logger.error(f"PNG export failed: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export:\n{e}"
            )
    
    def set_latex(self, latex: str):
        """Set the LaTeX code."""
        self.code_editor.setPlainText(latex)
    
    def get_latex(self) -> str:
        """Get the LaTeX code."""
        return self.code_editor.toPlainText().strip()
    
    def get_rendered_image(self) -> Optional[QImage]:
        """Get the rendered image."""
        return self.current_image
