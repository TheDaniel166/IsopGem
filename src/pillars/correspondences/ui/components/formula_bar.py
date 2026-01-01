from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import pyqtSignal

class FormulaBarWidget(QWidget):
    """
    A sovereign component for formula input and display.
    Handles user input and signal emission, but leaves orchestration to the Window.
    """
    
    # Signals to the Conductor (Window)
    text_changed = pyqtSignal(str)     # Emitted when user types
    return_pressed = pyqtSignal()      # Emitted on Enter
    focus_received = pyqtSignal()      # Emitted when bar gets focus (if needed)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # fx Label
        self.lbl_fx = QLabel("fx")
        self.lbl_fx.setStyleSheet("font-weight: bold; color: #64748b; margin-right: 5px;")
        layout.addWidget(self.lbl_fx)
        
        # The Input Field
        self.editor = QLineEdit()
        self.editor.setClearButtonEnabled(True)
        self.editor.textEdited.connect(self.text_changed.emit)
        self.editor.returnPressed.connect(self.return_pressed.emit)
        
        layout.addWidget(self.editor)
        
    def text(self) -> str:
        return self.editor.text()
        
    def set_text(self, text: str):
        self.editor.setText(text)
        
    def set_cursor_position(self, pos: int):
        self.editor.setCursorPosition(pos)
        
    def cursor_position(self) -> int:
        return self.editor.cursorPosition()
        
    def set_focus(self):
        self.editor.setFocus()
        
    def blockSignals(self, block: bool):
        return self.editor.blockSignals(block)
        
    # Compatibility Aliases for QLineEdit interface
    def setText(self, text: str):
        self.editor.setText(text)
        
    def setCursorPosition(self, pos: int):
        self.editor.setCursorPosition(pos)
        
    def cursorPosition(self) -> int:
        return self.editor.cursorPosition()
        
    def setPlaceholderText(self, text: str):
        self.editor.setPlaceholderText(text)
        
    def setFocus(self):
        """Override to focus the internal editor, not the container."""
        self.editor.setFocus()
