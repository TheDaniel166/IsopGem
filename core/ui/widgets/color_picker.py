"""
Color picker widget
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QColorDialog,
                           QLineEdit)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSignal

class ColorPicker(QWidget):
    """Widget for picking colors"""
    
    # Signal emitted when color changes
    color_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = "#000000"
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the picker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Color preview button
        self.preview_btn = QPushButton()
        self.preview_btn.setFixedSize(30, 30)
        self.preview_btn.clicked.connect(self._show_color_dialog)
        layout.addWidget(self.preview_btn)
        
        # Color hex input
        self.hex_input = QLineEdit()
        self.hex_input.setFixedWidth(80)
        self.hex_input.setPlaceholderText("#RRGGBB")
        self.hex_input.textChanged.connect(self._on_hex_changed)
        layout.addWidget(self.hex_input)
        
        # Update color display
        self._update_color_display()
    
    def _update_color_display(self):
        """Update the color preview and hex input"""
        # Update preview button
        self.preview_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 1px solid #888;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 1px solid #000;
            }}
        """)
        
        # Update hex input if it doesn't match
        if self.hex_input.text() != self._color:
            self.hex_input.setText(self._color)
    
    def _show_color_dialog(self):
        """Show the color picker dialog"""
        color = QColorDialog.getColor(QColor(self._color), self)
        if color.isValid():
            self.set_color(color.name())
    
    def _on_hex_changed(self, text: str):
        """Handle hex input changes"""
        # Validate hex color
        if len(text) == 7 and text.startswith("#"):
            try:
                QColor(text)
                self.set_color(text)
            except:
                pass
    
    def set_color(self, color: str):
        """Set the current color"""
        # Ensure color starts with #
        if not color.startswith("#"):
            color = f"#{color}"
            
        # Only update if it's a valid color
        try:
            QColor(color)  # Validate color
            if color != self._color:
                self._color = color
                self._update_color_display()
                self.color_changed.emit(color)
        except:
            pass
    
    def get_color(self) -> str:
        """Get the current color"""
        return self._color
