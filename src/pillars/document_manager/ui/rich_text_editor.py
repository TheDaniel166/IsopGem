"""Reusable Rich Text Editor widget."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QToolBar, QComboBox, QFontComboBox, QSpinBox,
    QColorDialog, QMenu, QToolButton, QDialog,
    QLabel, QDialogButtonBox, QFormLayout, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import (
    QFont, QAction, QIcon, QColor, QTextCharFormat,
    QTextCursor, QTextListFormat, QTextBlockFormat
)
from .table_features import TableFeature
from .image_features import ImageFeature

class RichTextEditor(QWidget):
    """
    A comprehensive rich text editor widget with a toolbar for formatting.
    """
    
    # Signal emitted when text changes
    text_changed = pyqtSignal()
    
    # Signal emitted when [[ is typed
    wiki_link_requested = pyqtSignal()
    
    def __init__(self, parent=None, placeholder_text="Start typing..."):
        super().__init__(parent)
        self._setup_ui(placeholder_text)
        
    def _setup_ui(self, placeholder_text):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setStyleSheet("""
            QToolBar {
                border-bottom: 1px solid #e5e7eb;
                background: #f9fafb;
                padding: 5px;
            }
            QToolButton {
                padding: 4px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #e5e7eb;
            }
            QToolButton:checked {
                background-color: #d1d5db;
            }
        """)
        layout.addWidget(self.toolbar)
        
        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(placeholder_text)
        self.editor.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 20px;
                font-size: 12pt;
                background-color: white;
                selection-background-color: #bfdbfe;
                selection-color: black;
            }
        """)
        self.editor.textChanged.connect(self.text_changed.emit)
        self.editor.textChanged.connect(self._check_wiki_link_trigger)
        self.editor.currentCharFormatChanged.connect(self._update_format_widgets)
        
        # Context Menu
        self.editor.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.editor)
        
        self._init_toolbar()

    def _check_wiki_link_trigger(self):
        """Check if the user just typed '[['."""
        cursor = self.editor.textCursor()
        position = cursor.position()
        
        # Get text before cursor
        # We need at least 2 chars
        if position < 2:
            return
            
        # Read last 2 chars
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 2)
        text = cursor.selectedText()
        
        # Restore cursor position (move back right)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, 2)
        
        if text == "[[":
            self.wiki_link_requested.emit()

        
    def _show_context_menu(self, pos):
        """Show context menu with table options if applicable."""
        # Ensure cursor is at the click position so context operations work on the clicked item
        cursor = self.editor.cursorForPosition(pos)
        self.editor.setTextCursor(cursor)
        
        menu = self.editor.createStandardContextMenu()
        
        if menu is not None:
            if hasattr(self, 'table_feature'):
                self.table_feature.extend_context_menu(menu)
                
            if hasattr(self, 'image_feature'):
                self.image_feature.extend_context_menu(menu)
                
            menu.exec(self.editor.mapToGlobal(pos))

    def _init_toolbar(self):
        """Populate the toolbar with actions."""
        # --- Font Family ---
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.editor.setCurrentFont)
        self.toolbar.addWidget(self.font_combo)
        
        # --- Font Size ---
        self.size_combo = QComboBox()
        self.size_combo.setEditable(True)
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        self.size_combo.addItems([str(s) for s in sizes])
        self.size_combo.setCurrentText("12")
        self.size_combo.textActivated.connect(self._set_font_size)
        self.toolbar.addWidget(self.size_combo)
        
        self.toolbar.addSeparator()
        
        # --- Bold ---
        self.action_bold = QAction("B", self)
        self.action_bold.setCheckable(True)
        self.action_bold.setShortcut("Ctrl+B")
        self.action_bold.setToolTip("Bold (Ctrl+B)")
        self.action_bold.triggered.connect(self._toggle_bold)
        self.action_bold.setFont(QFont("serif", weight=QFont.Weight.Bold))
        self.toolbar.addAction(self.action_bold)
        
        # --- Italic ---
        self.action_italic = QAction("I", self)
        self.action_italic.setCheckable(True)
        self.action_italic.setShortcut("Ctrl+I")
        self.action_italic.setToolTip("Italic (Ctrl+I)")
        self.action_italic.triggered.connect(self.editor.setFontItalic)
        self.action_italic.setFont(QFont("serif", italic=True))
        self.toolbar.addAction(self.action_italic)
        
        # --- Underline ---
        self.action_underline = QAction("U", self)
        self.action_underline.setCheckable(True)
        self.action_underline.setShortcut("Ctrl+U")
        self.action_underline.setToolTip("Underline (Ctrl+U)")
        self.action_underline.triggered.connect(self.editor.setFontUnderline)
        self.action_underline.setFont(QFont("serif")) 
        self.toolbar.addAction(self.action_underline)
        
        self.toolbar.addSeparator()
        
        # --- Color ---
        btn_color = QToolButton()
        btn_color.setText("Color")
        btn_color.setToolTip("Text Color")
        btn_color.clicked.connect(self._pick_color)
        self.toolbar.addWidget(btn_color)
        
        # --- Highlight ---
        btn_highlight = QToolButton()
        btn_highlight.setText("Highlight")
        btn_highlight.setToolTip("Background Color")
        btn_highlight.clicked.connect(self._pick_highlight)
        self.toolbar.addWidget(btn_highlight)
        
        self.toolbar.addSeparator()
        
        # --- Alignment ---
        self.action_align_left = QAction("Left", self)
        self.action_align_left.setCheckable(True)
        self.action_align_left.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignLeft))
        self.toolbar.addAction(self.action_align_left)
        
        self.action_align_center = QAction("Center", self)
        self.action_align_center.setCheckable(True)
        self.action_align_center.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter))
        self.toolbar.addAction(self.action_align_center)
        
        self.action_align_right = QAction("Right", self)
        self.action_align_right.setCheckable(True)
        self.action_align_right.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignRight))
        self.toolbar.addAction(self.action_align_right)
        
        self.action_align_justify = QAction("Justify", self)
        self.action_align_justify.setCheckable(True)
        self.action_align_justify.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignmentFlag.AlignJustify))
        self.toolbar.addAction(self.action_align_justify)
        
        self.toolbar.addSeparator()
        
        # --- Lists ---
        self.action_list_bullet = QAction("• List", self)
        self.action_list_bullet.setToolTip("Bullet List")
        self.action_list_bullet.triggered.connect(lambda: self._toggle_list(QTextListFormat.Style.ListDisc))
        self.toolbar.addAction(self.action_list_bullet)
        
        self.action_list_number = QAction("1. List", self)
        self.action_list_number.setToolTip("Numbered List")
        self.action_list_number.triggered.connect(lambda: self._toggle_list(QTextListFormat.Style.ListDecimal))
        self.toolbar.addAction(self.action_list_number)
        
        self.toolbar.addSeparator()
        
        # --- Table (Modular) ---
        self.table_feature = TableFeature(self.editor, self)
        self.toolbar.addWidget(self.table_feature.create_toolbar_button())
        
        # --- Image (Modular) ---
        self.image_feature = ImageFeature(self.editor, self)
        self.toolbar.addAction(self.image_feature.create_toolbar_action())
        
        self.toolbar.addSeparator()
        
        # --- Undo/Redo ---
        self.action_undo = QAction("Undo", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.triggered.connect(self.editor.undo)
        self.toolbar.addAction(self.action_undo)
        
        self.action_redo = QAction("Redo", self)
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.triggered.connect(self.editor.redo)
        self.toolbar.addAction(self.action_redo)

    def _set_font_size(self, size_str):
        """Set the font size."""
        try:
            size = float(size_str)
            self.editor.setFontPointSize(size)
        except ValueError:
            pass

    def _toggle_bold(self):
        """Toggle bold on the current selection."""
        fmt = QTextCharFormat()
        weight = self.editor.fontWeight()
        if weight == QFont.Weight.Bold:
            self.editor.setFontWeight(QFont.Weight.Normal)
        else:
            self.editor.setFontWeight(QFont.Weight.Bold)

    def _pick_color(self):
        """Pick a text color."""
        color = QColorDialog.getColor(self.editor.textColor(), self)
        if color.isValid():
            self.editor.setTextColor(color)

    def _pick_highlight(self):
        """Pick a background highlight color."""
        color = QColorDialog.getColor(self.editor.textBackgroundColor(), self)
        if color.isValid():
            self.editor.setTextBackgroundColor(color)

    def _toggle_list(self, style):
        """Toggle list formatting."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        current_list = cursor.currentList()
        
        if current_list:
            # If already in a list, check if it's the same type
            fmt = current_list.format()
            if fmt.style() == style:
                # Same style, remove list (convert to block)
                block_fmt = QTextBlockFormat()
                block_fmt.setObjectIndex(-1) # Remove list association
                cursor.setBlockFormat(block_fmt)
            else:
                # Different style, change it
                list_fmt = QTextListFormat()
                list_fmt.setStyle(style)
                current_list.setFormat(list_fmt)
        else:
            # Not in a list, create one
            list_fmt = QTextListFormat()
            list_fmt.setStyle(style)
            cursor.createList(list_fmt)
            
        cursor.endEditBlock()

    def _update_format_widgets(self, fmt):
        """Update toolbar state based on current cursor format."""
        # Update Bold
        self.action_bold.setChecked(self.editor.fontWeight() == QFont.Weight.Bold)
        
        # Update Italic
        self.action_italic.setChecked(self.editor.fontItalic())
        
        # Update Underline
        self.action_underline.setChecked(self.editor.fontUnderline())
        
        # Update Font Family
        self.font_combo.setCurrentFont(self.editor.currentFont())
        
        # Update Font Size
        size = self.editor.fontPointSize()
        if size > 0:
            self.size_combo.setCurrentText(str(int(size)))
            
        # Update Alignment
        align = self.editor.alignment()
        self.action_align_left.setChecked(bool(align & Qt.AlignmentFlag.AlignLeft))
        self.action_align_center.setChecked(bool(align & Qt.AlignmentFlag.AlignCenter))
        self.action_align_right.setChecked(bool(align & Qt.AlignmentFlag.AlignRight))
        self.action_align_justify.setChecked(bool(align & Qt.AlignmentFlag.AlignJustify))

    # --- Public API ---
    
    def get_html(self) -> str:
        """Get the content as HTML."""
        return self.editor.toHtml()
        
    def set_html(self, html: str):
        """Set the content as HTML."""
        self.editor.setHtml(html)
        
    def get_text(self) -> str:
        """Get the content as plain text."""
        return self.editor.toPlainText()
        
    def set_text(self, text: str):
        """Set the content as plain text."""
        self.editor.setPlainText(text)
        
    def clear(self):
        """Clear the editor."""
        self.editor.clear()

    def find_text(self, text: str) -> bool:
        """
        Find and select the first occurrence of text.
        Returns True if found.
        """
        if not text:
            return False
            
        # Move to start to search from beginning
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        
        # Find (this selects and scrolls to the text)
        found = self.editor.find(text)
        
        if found:
            # Ensure it's visible and focused
            self.editor.setFocus()
            return True
            
        return False
