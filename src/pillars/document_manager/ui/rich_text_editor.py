"""Reusable Rich Text Editor widget with Ribbon UI."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QComboBox, QFontComboBox, QSpinBox,
    QColorDialog, QMenu, QToolButton, QDialog,
    QLabel, QDialogButtonBox, QFormLayout, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QMimeData
from PyQt6.QtGui import (
    QFont, QAction, QIcon, QColor, QTextCharFormat,
    QTextCursor, QTextListFormat, QTextBlockFormat,
    QActionGroup, QBrush
)
from .table_features import TableFeature
from .image_features import ImageFeature
from .list_features import ListFeature
from .search_features import SearchReplaceFeature
from .ribbon_widget import RibbonWidget
from shared.ui import VirtualKeyboard, get_shared_virtual_keyboard

class SafeTextEdit(QTextEdit):
    """
    A hardened QTextEdit that protects against 'Paste Attacks' (Mars Seal).
    """
    def insertFromMimeData(self, source: QMimeData):
        """
        Override paste behavior to protect against freezing.
        """
        # Threshold: 100,000 chars (approx 20-30 pages of text)
        WARN_THRESHOLD = 100000
        
        if source.hasText():
            text = source.text()
            if len(text) > WARN_THRESHOLD:
                # Mars Warning: Chaos detected
                reply = QMessageBox.warning(
                    self, 
                    "Large Paste Detected",
                    f"You are attempting to paste {len(text):,} characters.\n"
                    "This may temporarily freeze the application.\n\n"
                    "Do you wish to proceed?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        
        super().insertFromMimeData(source)

class RichTextEditor(QWidget):
    """
    A comprehensive rich text editor widget with a Ribbon interface.
    """
    
    # Signal emitted when text changes
    text_changed = pyqtSignal()
    
    # Signal emitted when [[ is typed
    wiki_link_requested = pyqtSignal()
    
    def __init__(self, parent=None, placeholder_text="Start typing..."):
        super().__init__(parent)
        self.virtual_keyboard: VirtualKeyboard | None = None
        
        # Styles Definition
        self.styles = {
            "Normal": {"size": 12, "weight": QFont.Weight.Normal, "family": "Arial"},
            "Title": {"size": 28, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 1": {"size": 24, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 2": {"size": 18, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Heading 3": {"size": 14, "weight": QFont.Weight.Bold, "family": "Arial"},
            "Code": {"size": 10, "weight": QFont.Weight.Normal, "family": "Courier New"},
        }
        
        # Features
        self.search_feature = None # Lazy or init later? better init in setup
        
        self._setup_ui(placeholder_text)
        
    def _setup_ui(self, placeholder_text):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- Ribbon ---
        self.ribbon = RibbonWidget()
        layout.addWidget(self.ribbon)
        
        # --- Editor ---
        self.editor = SafeTextEdit()
        self.editor.setPlaceholderText(placeholder_text)
        self.editor.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 40px; /* More padding like a real doc */
                background-color: white;
                selection-background-color: #bfdbfe;
                selection-color: black;
            }
        """)
        self.editor.textChanged.connect(self.text_changed.emit)
        self.editor.textChanged.connect(self._check_wiki_link_trigger)
        self.editor.currentCharFormatChanged.connect(self._update_format_widgets)
        
        # Initialize features that depend on editor
        self.search_feature = SearchReplaceFeature(self.editor, self)
        
        # Context Menu
        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.editor)
        
        # Keybindings
        self.action_find = QAction("Find", self)
        self.action_find.setShortcut("Ctrl+F")
        self.action_find.triggered.connect(self.search_feature.show_search_dialog)
        self.addAction(self.action_find)
        
        # Initialize Ribbon Content
        self._init_ribbon()

    def insertFromMimeData(self, source):
        """
        Override paste behavior to protect against 'Paste Attacks' (Mars Seal).
        Warns user if pasting massive content that could freeze the UI.
        """
        # Threshold: 100,000 chars (approx 20-30 pages of text)
        WARN_THRESHOLD = 100000
        
        if source.hasText():
            text = source.text()
            if len(text) > WARN_THRESHOLD:
                # Mars Warning: Chaos detected
                reply = QMessageBox.warning(
                    self, 
                    "Large Paste Detected",
                    f"You are attempting to paste {len(text):,} characters.\n"
                    "This may temporarily freeze the application.\n\n"
                    "Do you wish to proceed?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        
        # Standard Qt behavior if safe or approved
        super().insertFromMimeData(source) # type: ignore

    def _check_wiki_link_trigger(self):
        """Check if the user just typed '[['."""
        cursor = self.editor.textCursor()
        position = cursor.position()
        
        if position < 2:
            return
            
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 2)
        text = cursor.selectedText()
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, 2)
        
        if text == "[[":
            self.wiki_link_requested.emit()

    def _show_context_menu(self, pos):
        """Show context menu with table options if applicable."""
        cursor = self.editor.cursorForPosition(pos)
        self.editor.setTextCursor(cursor)
        
        menu = self.editor.createStandardContextMenu()
        
        if menu is not None:
            if hasattr(self, 'table_feature'):
                self.table_feature.extend_context_menu(menu)
            if hasattr(self, 'image_feature'):
                self.image_feature.extend_context_menu(menu)
            menu.exec(self.editor.mapToGlobal(pos))

    def _init_ribbon(self):
        """Populate the ribbon with tabs and groups."""
        
        # === TAB: HOME ===
        tab_home = self.ribbon.add_ribbon_tab("Home")
        
        # Group: Clipboard
        grp_clip = tab_home.add_group("Clipboard")
        
        self.action_undo = QAction("Undo", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.triggered.connect(self.editor.undo)
        grp_clip.add_action(self.action_undo)
        
        self.action_redo = QAction("Redo", self)
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.triggered.connect(self.editor.redo)
        grp_clip.add_action(self.action_redo)

        # Group: Styles (New)
        grp_style = tab_home.add_group("Styles")
        self.style_combo = QComboBox()
        self.style_combo.addItems(list(self.styles.keys()))
        self.style_combo.currentTextChanged.connect(self._apply_style)
        self.style_combo.setMinimumWidth(120)
        grp_style.add_widget(self.style_combo)

        # Group: Font
        grp_font = tab_home.add_group("Font")
        
        # Font Row 1: Combo boxes
        font_box = QWidget()
        font_layout = QHBoxLayout(font_box)
        font_layout.setContentsMargins(0,0,0,0)
        
        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(150)
        self.font_combo.currentFontChanged.connect(self.editor.setCurrentFont)
        font_layout.addWidget(self.font_combo)
        
        self.size_combo = QComboBox()
        self.size_combo.setEditable(True)
        self.size_combo.setMaximumWidth(60)
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        self.size_combo.addItems([str(s) for s in sizes])
        self.size_combo.setCurrentText("12")
        self.size_combo.textActivated.connect(self._set_font_size)
        font_layout.addWidget(self.size_combo)
        
        grp_font.add_widget(font_box)
        
        # Font Row 2: Buttons (Bold, Italic, Underline)
        self.action_bold = QAction("B", self)
        self.action_bold.setCheckable(True)
        self.action_bold.setShortcut("Ctrl+B")
        self.action_bold.triggered.connect(self._toggle_bold)
        self.action_bold.setFont(QFont("serif", weight=QFont.Weight.Bold))
        grp_font.add_action(self.action_bold, Qt.ToolButtonStyle.ToolButtonTextOnly) # Compact
        
        self.action_italic = QAction("I", self)
        self.action_italic.setCheckable(True)
        self.action_italic.setShortcut("Ctrl+I")
        self.action_italic.triggered.connect(self.editor.setFontItalic)
        self.action_italic.setFont(QFont("serif", italic=True))
        grp_font.add_action(self.action_italic, Qt.ToolButtonStyle.ToolButtonTextOnly)

        self.action_underline = QAction("U", self)
        self.action_underline.setCheckable(True)
        self.action_underline.setShortcut("Ctrl+U")
        self.action_underline.triggered.connect(self.editor.setFontUnderline)
        grp_font.add_action(self.action_underline, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # Strikethrough
        self.action_strike = QAction("S", self)
        self.action_strike.setCheckable(True)
        self.action_strike.setToolTip("Strikethrough")
        self.action_strike.triggered.connect(self._toggle_strikethrough)
        # Fallback icon or text if theme icon missing? Text S with strike is hard in plain text
        # Using theme icon
        self.action_strike.setIcon(QIcon.fromTheme("format-text-strikethrough"))
        if self.action_strike.icon().isNull():
            self.action_strike.setText("S̶") 
        grp_font.add_action(self.action_strike)

        # Subscript
        self.action_sub = QAction("Sub", self)
        self.action_sub.setCheckable(True)
        self.action_sub.setToolTip("Subscript")
        self.action_sub.triggered.connect(self._toggle_subscript)
        self.action_sub.setIcon(QIcon.fromTheme("format-text-subscript"))
        if self.action_sub.icon().isNull():
             self.action_sub.setText("X₂")
        grp_font.add_action(self.action_sub)

        # Superscript
        self.action_super = QAction("Sup", self)
        self.action_super.setCheckable(True)
        self.action_super.setToolTip("Superscript")
        self.action_super.triggered.connect(self._toggle_superscript)
        self.action_super.setIcon(QIcon.fromTheme("format-text-superscript"))
        if self.action_super.icon().isNull():
             self.action_super.setText("X²")
        grp_font.add_action(self.action_super)
        
        # Clear Formatting
        self.action_clear = QAction("Clear", self)
        self.action_clear.setToolTip("Clear Formatting")
        self.action_clear.triggered.connect(self._clear_formatting)
        self.action_clear.setIcon(QIcon.fromTheme("format-text-clear")) # or edit-clear
        if self.action_clear.icon().isNull():
             self.action_clear.setText("oslash")
        grp_font.add_action(self.action_clear)
        
        # Colors
        btn_color = QToolButton()
        btn_color.setIcon(QIcon()) # Placeholder for now or text
        btn_color.setText("Color")
        btn_color.setToolTip("Text Color")
        btn_color.clicked.connect(self._pick_color)
        grp_font.add_widget(btn_color)
        
        btn_highlight = QToolButton()
        btn_highlight.setText("High")
        btn_highlight.setToolTip("Highlight")
        btn_highlight.clicked.connect(self._pick_highlight)
        grp_font.add_widget(btn_highlight)
        
        btn_clear = QToolButton()
        btn_clear.setText("No Color")
        btn_clear.setToolTip("Clear Highlight")
        btn_clear.clicked.connect(self._clear_highlight)
        grp_font.add_widget(btn_clear)
        
        # Group: Paragraph
        grp_para = tab_home.add_group("Paragraph")
        
        # Alignment Group (Exclusive)
        align_group = QActionGroup(self)
        
        self.action_align_left = QAction("Left", self)
        self.action_align_left.setCheckable(True)
        self.action_align_left.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        align_group.addAction(self.action_align_left)
        grp_para.add_action(self.action_align_left, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_align_center = QAction("Center", self)
        self.action_align_center.setCheckable(True)
        self.action_align_center.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        align_group.addAction(self.action_align_center)
        grp_para.add_action(self.action_align_center, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_align_right = QAction("Right", self)
        self.action_align_right.setCheckable(True)
        self.action_align_right.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        align_group.addAction(self.action_align_right)
        grp_para.add_action(self.action_align_right, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_align_justify = QAction("Justify", self)
        self.action_align_justify.setCheckable(True)
        self.action_align_justify.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        align_group.addAction(self.action_align_justify)
        grp_para.add_action(self.action_align_justify, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        
        grp_para.add_separator()
        
        # Lists & Indentation
        self.list_feature = ListFeature(self.editor, self)
        
        self.action_list_bullet = QAction("• List", self)
        self.action_list_bullet.triggered.connect(lambda: self.list_feature.toggle_list(QTextListFormat.Style.ListDisc))
        grp_para.add_action(self.action_list_bullet, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_list_number = QAction("1. List", self)
        self.action_list_number.triggered.connect(lambda: self.list_feature.toggle_list(QTextListFormat.Style.ListDecimal))
        grp_para.add_action(self.action_list_number, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        grp_para.add_separator()
        
        self.action_outdent = QAction("<< Out", self)
        self.action_outdent.setToolTip("Decrease Indent")
        self.action_outdent.triggered.connect(self.list_feature.outdent)
        grp_para.add_action(self.action_outdent, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        self.action_indent = QAction("In >>", self)
        self.action_indent.setToolTip("Increase Indent")
        self.action_indent.triggered.connect(self.list_feature.indent)
        grp_para.add_action(self.action_indent, Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # Group: Edit
        grp_edit = tab_home.add_group("Edit")
        # Reuse the action defined in setup_ui which has the shortcut
        grp_edit.add_action(self.action_find, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        # === TAB: INSERT ===
        tab_insert = self.ribbon.add_ribbon_tab("Insert")
        
        # Group: Tables
        grp_tables = tab_insert.add_group("Tables")
        self.table_feature = TableFeature(self.editor, self)
        # Adding the toolbar button from the feature
        # We need to extract the action or just add the widget
        grp_tables.add_widget(self.table_feature.create_toolbar_button())
        
        # Group: Illustrations
        grp_illus = tab_insert.add_group("Illustrations")
        self.image_feature = ImageFeature(self.editor, self)
        grp_illus.add_action(self.image_feature.create_toolbar_action(), Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
        # Group: Symbols
        grp_sym = tab_insert.add_group("Symbols")
        
        action_kb = QAction("Keyboard", self)
        action_kb.setToolTip("Open Virtual Keyboard (Hebrew, Greek, Esoteric)")
        action_kb.triggered.connect(self._show_virtual_keyboard)
        grp_sym.add_action(action_kb, Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

    def _set_font_size(self, size_str):
        try:
            size = float(size_str)
            self.editor.setFontPointSize(size)
        except ValueError:
            pass

    def _toggle_bold(self):
        font_weight = self.editor.fontWeight()
        if font_weight == QFont.Weight.Bold:
            self.editor.setFontWeight(QFont.Weight.Normal)
        else:
            self.editor.setFontWeight(QFont.Weight.Bold)

    def _toggle_strikethrough(self):
        """Toggle strikethrough formatting."""
        fmt = self.editor.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_subscript(self):
        """Toggle subscript, exclusive with superscript."""
        fmt = self.editor.currentCharFormat()
        if fmt.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSubScript:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
        self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_superscript(self):
        """Toggle superscript, exclusive with subscript."""
        fmt = self.editor.currentCharFormat()
        if fmt.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSuperScript:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
        else:
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
        self.editor.mergeCurrentCharFormat(fmt)

    def _clear_formatting(self):
        """
        Reset character formatting to default for the current selection, 
        preserves block formatting.
        """
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            # Create a clean format
            fmt = QTextCharFormat()
            # We can't just use empty fmt because merge won't unset properties.
            # We have to explicitly set default properties.
            
            # Reset Font
            default_font = QFont("Arial", 12)
            fmt.setFont(default_font)
            fmt.setFontWeight(QFont.Weight.Normal)
            fmt.setFontItalic(False)
            fmt.setFontUnderline(False)
            fmt.setFontStrikeOut(False)
            
            # Reset Color
            fmt.setForeground(Qt.GlobalColor.black)
            fmt.setBackground(QBrush(Qt.BrushStyle.NoBrush))
            
            # Reset Alignment
            fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
            
            # Apply
            # setCharFormat applied to selection replaces all char properties
            cursor.setCharFormat(fmt)
            self.editor.setFocus()


    def _pick_color(self):
        """
        Open a color picker to set the text color.
        Uses non-native dialog to avoid linux platform integration issues.
        """
        cursor = self.editor.textCursor()
        # Get current color
        fmt = cursor.charFormat()
        current_color = fmt.foreground().color()
        if not current_color.isValid():
            current_color = Qt.GlobalColor.black
        
        # UX Improvement: If color is Black (Value 0), the picker opens in "The Abyss" (Slider at bottom).
        # We default to Red to force the Value Slider to Max, allowing immediate color selection.
        initial_color = current_color
        if current_color.lightness() == 0:
            initial_color = Qt.GlobalColor.red
            
        dialog = QColorDialog(initial_color, self)
        dialog.setWindowTitle("Select Text Color")
        dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel | 
                          QColorDialog.ColorDialogOption.DontUseNativeDialog)
        
        if dialog.exec():
            color = dialog.currentColor()
            if color.isValid():
                # Apply using mergeCharFormat for robustness
                new_fmt = QTextCharFormat()
                new_fmt.setForeground(color)
                self.editor.mergeCurrentCharFormat(new_fmt)
                self.editor.setFocus()

    def _apply_style(self, style_name):
        """Apply a semantic style to the current selection/block."""
        if style_name not in self.styles:
            return
            
        style = self.styles[style_name]
        cursor = self.editor.textCursor()
        
        # If no selection, apply to the entire block (paragraph)
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        
        
        
        # Fallback to HTML insertion for robust styling if direct formatting fails
        # This is a bit heavier but guarantees the style is applied by the engine parser
        
        
        selected_text = cursor.selectedText()
        # Replace Paragraph Separator with space or nothing, as we are wrapping in block tag
        selected_text = selected_text.replace('\u2029', '')
            
        # Determine tag
        tag = "p"
        if style_name == "Heading 1": tag = "h1"
        elif style_name == "Heading 2": tag = "h2"
        elif style_name == "Heading 3": tag = "h3"
        elif style_name == "Title": tag = "h1" # Title as h1 for now
        elif style_name == "Code": tag = "pre"
        
        # Build HTML with inline style to enforce our specific look (font, size)
        # Note: h1 in Qt might have default margins, we can override if needed
        pt_size = style["size"]
        family = style["family"]
        # font-weight is handled by h1 usually, but we enforce specific
        weight_css = "bold" if style["weight"] == QFont.Weight.Bold else "normal"
        
        # We need to ensure the styling applies. 
        # Using a span inside the block tag often helps Qt parser.
        html = f'<{tag} style="margin-top: 10px; margin-bottom: 5px;"><span style="font-family: {family}; font-size: {pt_size}pt; font-weight: {weight_css};">{selected_text}</span></{tag}>'
        
        self.editor.blockSignals(True)
        cursor.insertHtml(html)
        self.editor.blockSignals(False)
        
        # Update combo boxes manually to reflect the change visually in toolbar
        self.size_combo.setCurrentText(str(style["size"]))
        self.font_combo.setCurrentFont(QFont(style["family"]))

    def _pick_highlight(self):
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()
        current_bg = fmt.background().color()
        if not current_bg.isValid():
            current_bg = Qt.GlobalColor.white

        dialog = QColorDialog(current_bg, self)
        dialog.setWindowTitle("Select Highlight Color")
        dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel | 
                          QColorDialog.ColorDialogOption.DontUseNativeDialog)
                          
        if dialog.exec():
            color = dialog.currentColor()
            if color.isValid():
                new_fmt = QTextCharFormat()
                new_fmt.setBackground(color)
                self.editor.mergeCurrentCharFormat(new_fmt)
                self.editor.setFocus()

    def _clear_highlight(self):
        """Clear the background highlight."""
        self.editor.setTextBackgroundColor(QColor(Qt.GlobalColor.transparent))



    def _show_virtual_keyboard(self):
        self.virtual_keyboard = get_shared_virtual_keyboard(self)
        self.virtual_keyboard.set_target_editor(self.editor)
        self.virtual_keyboard.show()
        self.virtual_keyboard.raise_()
        self.virtual_keyboard.activateWindow()

    def _update_format_widgets(self, fmt):
        """Update the ribbon widgets based on the current text format."""
        # Block signals to prevent triggering changes while updating UI
        self.font_combo.blockSignals(True)
        self.size_combo.blockSignals(True)
        self.action_bold.blockSignals(True)
        self.action_italic.blockSignals(True)
        self.action_underline.blockSignals(True)
        self.action_strike.blockSignals(True)
        self.action_sub.blockSignals(True)
        self.action_super.blockSignals(True)
        self.action_align_left.blockSignals(True)
        self.action_align_center.blockSignals(True)
        self.action_align_right.blockSignals(True)
        self.action_align_justify.blockSignals(True)
        
        self.font_combo.setCurrentFont(fmt.font())
        self.size_combo.setCurrentText(str(int(fmt.fontPointSize())))
        
        self.action_bold.setChecked(fmt.fontWeight() == QFont.Weight.Bold)
        self.action_italic.setChecked(fmt.fontItalic())
        self.action_underline.setChecked(fmt.fontUnderline())
        self.action_strike.setChecked(fmt.fontStrikeOut())
        
        v_align = fmt.verticalAlignment()
        self.action_sub.setChecked(v_align == QTextCharFormat.VerticalAlignment.AlignSubScript)
        self.action_super.setChecked(v_align == QTextCharFormat.VerticalAlignment.AlignSuperScript)
        
        # Alignment
        align = self.editor.alignment()
        if align & Qt.AlignmentFlag.AlignLeft:
            self.action_align_left.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignHCenter:
            self.action_align_center.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignRight:
            self.action_align_right.setChecked(True)
        elif align & Qt.AlignmentFlag.AlignJustify:
            self.action_align_justify.setChecked(True)
        
        self.font_combo.blockSignals(False)
        self.size_combo.blockSignals(False)
        self.action_bold.blockSignals(False)
        self.action_italic.blockSignals(False)
        self.action_underline.blockSignals(False)
        self.action_strike.blockSignals(False)
        self.action_sub.blockSignals(False)
        self.action_super.blockSignals(False)
        self.action_align_left.blockSignals(False)
        self.action_align_center.blockSignals(False)
        self.action_align_right.blockSignals(False)
        self.action_align_justify.blockSignals(False)
        
    # --- Public API ---
    def get_html(self) -> str:
        return self.editor.toHtml()
        
    def set_html(self, html: str):
        self.editor.setHtml(html)
        
    def get_text(self) -> str:
        return self.editor.toPlainText()
        
    def set_text(self, text: str):
        self.editor.setPlainText(text)
        
    def clear(self):
        self.editor.clear()

    def find_text(self, text: str) -> bool:
        if not text:
            return False
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        found = self.editor.find(text)
        if found:
            self.editor.setFocus()
            return True
        return False
