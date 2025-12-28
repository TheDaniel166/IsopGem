"""
Document Viewer - The Sacred Text Display.
Read-only text widget with highlighting, selection, and context menu support.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QMenu
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QAction

class DocumentViewer(QWidget):
    """
    Widget for displaying read-only text with highlighting capabilities.
    """
    text_selected = pyqtSignal()  # Emitted when user selects text
    save_requested = pyqtSignal(str)
    calculate_requested = pyqtSignal(str)
    send_to_quadset_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        # Styling extracted from original
        self.text_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 13pt;
                background-color: #ffffff;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                padding: 16px;
                line-height: 1.6;
            }
        """)
        self.text_edit.selectionChanged.connect(self.text_selected.emit)
        # Enable custom context menu
        self.text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.text_edit)

    def _show_context_menu(self, pos):
        menu = self.text_edit.createStandardContextMenu()
        
        selected_text = self.get_selected_text()
        if selected_text:
            menu.addSeparator()
            
            calc_action = QAction("Calculate Selection", self)
            calc_action.triggered.connect(lambda: self.calculate_requested.emit(selected_text))
            menu.addAction(calc_action)
            
            save_action = QAction("Save Selection", self)
            save_action.triggered.connect(lambda: self.save_requested.emit(selected_text))
            menu.addAction(save_action)
            
            quad_action = QAction("Send Total to Quadset Analysis", self)
            quad_action.triggered.connect(lambda: self.send_to_quadset_requested.emit(selected_text))
            menu.addAction(quad_action)
            
        menu.exec(self.text_edit.mapToGlobal(pos))
        
    def set_text(self, text: str):
        """
        Configure text logic.
        
        Args:
            text: Description of text.
        
        """
        self.text_edit.setPlainText(text)
        
    def get_text(self) -> str:
        """
        Retrieve text logic.
        
        Returns:
            Result of get_text operation.
        """
        return self.text_edit.toPlainText()
        
    def get_selected_text(self) -> str:
        """
        Retrieve selected text logic.
        
        Returns:
            Result of get_selected_text operation.
        """
        return self.text_edit.textCursor().selectedText()
        
    def select_range(self, start: int, end: int):
        """
        Select range logic.
        
        Args:
            start: Description of start.
            end: Description of end.
        
        """
        cursor = self.text_edit.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.setFocus()
        
    def highlight_ranges(self, ranges: list):
        """
        Highlight list of (start, end) ranges.
        """
        # Create highlight format
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#fef3c7"))  # Yellow
        fmt.setForeground(QColor("#000000"))
        
        # Save cursor
        original_cursor = self.text_edit.textCursor()
        original_pos = original_cursor.position()
        
        cursor = self.text_edit.textCursor()
        for start, end in ranges:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(fmt)
            
        # Restore cursor
        original_cursor.setPosition(original_pos)
        self.text_edit.setTextCursor(original_cursor)
        
    def clear_highlights(self):
        """
        Clear highlights logic.
        
        """
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#ffffff"))
        fmt.setForeground(QColor("#000000"))
        cursor.setCharFormat(fmt)
        
        cursor.setPosition(0)
        self.text_edit.setTextCursor(cursor)