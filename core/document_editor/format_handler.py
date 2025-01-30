from PyQt5.QtWidgets import (QFontComboBox, QSpinBox, QPushButton, QMenu, QAction,
                            QColorDialog, QComboBox, QApplication)
from PyQt5.QtGui import (QTextCharFormat, QColor, QTextBlockFormat, QFont,
                        QTextListFormat)
from PyQt5.QtCore import Qt

class FormatHandler:
    def __init__(self, editor):
        self.editor = editor
        self.copied_format = None
        
    def setup_format_actions(self):
        """Create formatting-related actions and widgets"""
        # Font family
        self.font_family = QFontComboBox()
        self.font_family.setMinimumWidth(150)
        self.font_family.currentFontChanged.connect(self.font_family_changed)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setMinimum(6)
        self.font_size.setMaximum(72)
        self.font_size.setValue(11)
        self.font_size.valueChanged.connect(self.font_size_changed)
        
        # Text formatting actions
        bold_action = self.create_action("Bold", self.toggle_bold, "Ctrl+B", checkable=True)
        italic_action = self.create_action("Italic", self.toggle_italic, "Ctrl+I", checkable=True)
        underline_action = self.create_action("Underline", self.toggle_underline, "Ctrl+U", checkable=True)
        
        # Text alignment actions
        align_left = self.create_action("Left", lambda: self.align_text('left'))
        align_center = self.create_action("Center", lambda: self.align_text('center'))
        align_right = self.create_action("Right", lambda: self.align_text('right'))
        align_justify = self.create_action("Justify", lambda: self.align_text('justify'))
        
        # Color actions
        text_color_action = self.create_action("Text Color", self.text_color)
        highlight_action = self.create_action("Highlight", self.highlight_color)
        
        # Text styles combo
        self.style_combo = QComboBox()
        self.style_combo.setMinimumWidth(120)
        self.style_combo.addItems([
            "Normal",
            "Heading 1",
            "Heading 2",
            "Heading 3",
            "Heading 4",
            "Title",
            "Subtitle"
        ])
        self.style_combo.currentTextChanged.connect(self.apply_text_style)
        
        # Format painter
        self.format_painter = self.create_action(
            "Format Painter",
            self.toggle_format_painter,
            checkable=True
        )
        
        # Add list formatting actions
        bullet_list = self.create_action("Bullet List", self.toggle_bullet_list, checkable=True)
        numbered_list = self.create_action("Numbered List", self.toggle_numbered_list, checkable=True)
        
        # Add to format items
        format_items = {
            'font_family': self.font_family,
            'font_size': self.font_size,
            'bold': bold_action,
            'italic': italic_action,
            'underline': underline_action,
            'align_left': align_left,
            'align_center': align_center,
            'align_right': align_right,
            'align_justify': align_justify,
            'text_color': text_color_action,
            'highlight': highlight_action,
            'style_combo': self.style_combo,
            'format_painter': self.format_painter,
            'bullet_list': bullet_list,
            'numbered_list': numbered_list
        }
        
        return format_items

    def create_action(self, text, slot, shortcut=None, checkable=False):
        """Helper to create an action"""
        action = QAction(text, self.editor)
        action.triggered.connect(slot)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)
        return action

    def font_family_changed(self, font):
        """Change font family of selected text"""
        format = QTextCharFormat()
        format.setFont(font)
        self.merge_format(format)

    def font_size_changed(self, size):
        """Change font size of selected text"""
        format = QTextCharFormat()
        format.setFontPointSize(size)
        self.merge_format(format)

    def toggle_bold(self, checked):
        """Toggle bold formatting"""
        format = QTextCharFormat()
        weight = QFont.Bold if checked else QFont.Normal
        format.setFontWeight(weight)
        self.merge_format(format)

    def toggle_italic(self, checked):
        """Toggle italic formatting"""
        format = QTextCharFormat()
        format.setFontItalic(checked)
        self.merge_format(format)

    def toggle_underline(self, checked):
        """Toggle underline formatting"""
        format = QTextCharFormat()
        format.setFontUnderline(checked)
        self.merge_format(format)

    def text_color(self):
        """Change text color"""
        # Get current text color from editor widget
        cursor = self.editor.editor.textCursor()
        current_format = cursor.charFormat()
        current_color = current_format.foreground().color()
        
        # Show color dialog
        color = QColorDialog.getColor(current_color, self.editor)
        if color.isValid():
            # Create new format with color
            format = QTextCharFormat()
            format.setForeground(color)
            
            # Apply to selection or current position
            cursor = self.editor.editor.textCursor()
            if cursor.hasSelection():
                cursor.mergeCharFormat(format)
            else:
                self.editor.editor.mergeCurrentCharFormat(format)
            
            # Update editor state
            self.editor.editor.setTextCursor(cursor)
            QApplication.processEvents()

    def highlight_color(self):
        """Change text background color"""
        # Get current background color from editor widget
        cursor = self.editor.editor.textCursor()
        current_format = cursor.charFormat()
        current_color = current_format.background().color()
        
        # Show color dialog
        color = QColorDialog.getColor(current_color, self.editor)
        if color.isValid():
            # Create new format with color
            format = QTextCharFormat()
            format.setBackground(color)
            
            # Apply to selection or current position
            cursor = self.editor.editor.textCursor()
            if cursor.hasSelection():
                cursor.mergeCharFormat(format)
            else:
                self.editor.editor.mergeCurrentCharFormat(format)
            
            # Update editor state
            self.editor.editor.setTextCursor(cursor)
            QApplication.processEvents()

    def align_text(self, alignment):
        """Align text in the editor"""
        cursor = self.editor.editor.textCursor()
        block_format = cursor.blockFormat()
        
        if alignment == 'left':
            block_format.setAlignment(Qt.AlignLeft)
        elif alignment == 'center':
            block_format.setAlignment(Qt.AlignCenter)
        elif alignment == 'right':
            block_format.setAlignment(Qt.AlignRight)
        else:  # justify
            block_format.setAlignment(Qt.AlignJustify)
            
        cursor.mergeBlockFormat(block_format)
        self.editor.editor.setTextCursor(cursor)

    def apply_text_style(self, style):
        """Apply predefined text style"""
        cursor = self.editor.editor.textCursor()
        format = QTextCharFormat()
        block_format = QTextBlockFormat()
        
        if style == "Normal":
            format.setFontPointSize(11)
            format.setFontWeight(QFont.Normal)
        elif style == "Title":
            format.setFontPointSize(24)
            format.setFontWeight(QFont.Bold)
            block_format.setAlignment(Qt.AlignCenter)
        elif style == "Subtitle":
            format.setFontPointSize(18)
            format.setFontWeight(QFont.DemiBold)
            block_format.setAlignment(Qt.AlignCenter)
        elif style.startswith("Heading"):
            level = int(style[-1])
            format.setFontPointSize(18 - (level * 2))
            format.setFontWeight(QFont.Bold)
        
        cursor.mergeCharFormat(format)
        cursor.mergeBlockFormat(block_format)
        self.editor.editor.setTextCursor(cursor)

    def toggle_format_painter(self, checked):
        """Toggle format painter tool"""
        if checked:
            cursor = self.editor.textCursor()
            self.copied_format = {
                'char': cursor.charFormat(),
                'block': cursor.blockFormat()
            }
            self.editor.viewport().setCursor(Qt.CrossCursor)
        else:
            self.copied_format = None
            self.editor.viewport().setCursor(Qt.IBeamCursor)

    def merge_format(self, format):
        """Helper to merge format with current cursor selection"""
        cursor = self.editor.editor.textCursor()
        cursor.mergeCharFormat(format)
        self.editor.editor.mergeCurrentCharFormat(format)

    def toggle_bullet_list(self):
        """Toggle bullet list formatting"""
        cursor = self.editor.editor.textCursor()
        list_format = QTextListFormat()
        
        # Check if current block is already a list
        current_list = cursor.currentList()
        if current_list and current_list.format().style() == QTextListFormat.ListDisc:
            # Remove list
            cursor.beginEditBlock()
            for i in range(current_list.count()):
                current_list.item(i).setFormat(QTextBlockFormat())
            cursor.endEditBlock()
        else:
            # Create bullet list
            list_format.setStyle(QTextListFormat.ListDisc)
            cursor.createList(list_format)
        
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()

    def toggle_numbered_list(self):
        """Toggle numbered list formatting"""
        cursor = self.editor.editor.textCursor()
        list_format = QTextListFormat()
        
        # Check if current block is already a list
        current_list = cursor.currentList()
        if current_list and current_list.format().style() == QTextListFormat.ListDecimal:
            # Remove list
            cursor.beginEditBlock()
            for i in range(current_list.count()):
                current_list.item(i).setFormat(QTextBlockFormat())
            cursor.endEditBlock()
        else:
            # Create numbered list
            list_format.setStyle(QTextListFormat.ListDecimal)
            cursor.createList(list_format)
        
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents() 