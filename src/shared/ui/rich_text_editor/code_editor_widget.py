"""
Code Editor Widget with Line Numbers.
A QPlainTextEdit subclass that displays line numbers in a sidebar.
"""
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QColor, QPainter, QTextFormat, QFont, QPaintEvent, QResizeEvent
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit

from shared.ui.theme import COLORS


class LineNumberArea(QWidget):
    """Widget for displaying line numbers alongside a code editor."""
    
    def __init__(self, editor: 'CodeEditorWidget'):
        super().__init__(editor)
        self.code_editor = editor
    
    def sizeHint(self) -> QSize:
        return QSize(self.code_editor.line_number_area_width(), 0)
    
    def paintEvent(self, event: QPaintEvent):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditorWidget(QPlainTextEdit):
    """
    A code editor with line numbers and enhanced editing features.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.line_number_area = LineNumberArea(self)
        
        # Connect signals
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        
        self._update_line_number_area_width(0)
        self._highlight_current_line()
        
        # Set monospace font
        font = QFont("Fira Code", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Tab settings
        self.setTabStopDistance(32)  # ~4 spaces
    
    def line_number_area_width(self) -> int:
        """Calculate the width needed for the line number area."""
        digits = 1
        max_block = max(1, self.blockCount())
        while max_block >= 10:
            max_block //= 10
            digits += 1
        
        # Minimum 3 digits, plus padding
        digits = max(3, digits)
        space = 16 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def _update_line_number_area_width(self, _):
        """Update the left margin to accommodate line numbers."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def _update_line_number_area(self, rect: QRect, dy: int):
        """Scroll or repaint the line number area as needed."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize to update line number area geometry."""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def _highlight_current_line(self):
        """Highlight the line where the cursor is."""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#fef9c3")  # Light yellow
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def line_number_area_paint_event(self, event: QPaintEvent):
        """Paint the line numbers."""
        painter = QPainter(self.line_number_area)
        
        # Background
        painter.fillRect(event.rect(), QColor(COLORS["background_alt"]))
        
        # Draw line numbers
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        # Text color
        painter.setPen(QColor(COLORS["text_secondary"]))
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 8, self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
        
        painter.end()
    
    def keyPressEvent(self, event):
        """Handle special key presses for auto-indentation."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Auto-indent: copy leading whitespace from current line
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Extract leading whitespace
            indent = ""
            for char in text:
                if char in (' ', '\t'):
                    indent += char
                else:
                    break
            
            # Check if line ends with ':' or '{' for extra indent
            stripped = text.rstrip()
            if stripped.endswith(':') or stripped.endswith('{'):
                indent += "    "
            
            # Insert newline + indent
            super().keyPressEvent(event)
            self.insertPlainText(indent)
        else:
            super().keyPressEvent(event)
