"""Hyperlink insertion dialog for Rich Text Editor."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
    QLabel, QDialogButtonBox
)


class HyperlinkDialog(QDialog):
    """Dialog for inserting or editing a hyperlink."""
    
    def __init__(self, selected_text: str = "", parent=None):
        """
          init   logic.
        
        Args:
            selected_text: Description of selected_text.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Insert Hyperlink")
        self.setMinimumWidth(400)
        self._setup_ui(selected_text)
    
    def _setup_ui(self, selected_text: str):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.text_input = QLineEdit()
        self.text_input.setText(selected_text)
        self.text_input.setPlaceholderText("Display text (optional)")
        form.addRow("Text to display:", self.text_input)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        form.addRow("URL:", self.url_input)
        
        layout.addLayout(form)
        
        # Hint label
        hint = QLabel("Tip: Select text first to use it as the display text.")
        hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(hint)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Focus on URL input
        self.url_input.setFocus()