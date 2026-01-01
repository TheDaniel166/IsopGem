from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

class FormulaBarWidget(QWidget):
    """
    A sovereign component for formula input and display.
    Handles user input and signal emission, but leaves orchestration to the Window.
    """
    
    # Signals to the Conductor (Window)
    text_changed = pyqtSignal(str)     # Emitted when user types
    return_pressed = pyqtSignal()      # Emitted on Enter
    focus_received = pyqtSignal()      # Emitted when bar gets focus (if needed)
    fx_clicked = pyqtSignal()          # Emitted when fx button is clicked (Formula Wizard)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # fx Button - Portal to the Formula Wizard
        self.btn_fx = QPushButton("fx")
        self.btn_fx.setFixedWidth(32)
        self.btn_fx.setToolTip("Insert Function (Formula Wizard)")
        self.btn_fx.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-style: italic;
                color: #64748b;
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                background: #f1f5f9;
                color: #3b82f6;
                border-color: #3b82f6;
            }
            QPushButton:pressed {
                background: #e2e8f0;
            }
        """)
        self.btn_fx.clicked.connect(self.fx_clicked.emit)
        layout.addWidget(self.btn_fx)
        
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

    def hasFocus(self) -> bool:
        """Check if the internal editor has focus."""
        return self.editor.hasFocus()
    
    def is_formula_text(self) -> bool:
        """Returns True if current text starts with '=' (formula mode)."""
        text = self.editor.text()
        return text.startswith("=") if text else False
    
    def set_composition_mode(self, active: bool) -> None:
        """Apply visual indication when in formula composition mode."""
        if active:
            # Subtle golden glow effect
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(15)
            effect.setColor(QColor(255, 193, 7, 180))  # Amber glow
            effect.setOffset(0, 0)
            self.editor.setGraphicsEffect(effect)
            self.editor.setStyleSheet(
                "border: 2px solid #f59e0b; border-radius: 4px; padding: 2px;"
            )
        else:
            # Remove glow
            self.editor.setGraphicsEffect(None)
            self.editor.setStyleSheet("")
