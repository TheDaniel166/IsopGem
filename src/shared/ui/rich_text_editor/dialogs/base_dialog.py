"""
Base dialog class with common utilities for Rich Text Editor dialogs.
Reduces code duplication for color pickers, buttons, and common layouts.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QDialogButtonBox, QColorDialog,
    QPushButton, QFormLayout
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from typing import Optional


class BaseEditorDialog(QDialog):
    """
    Base class for editor dialogs with common utilities.
    Provides standardized color picker, button layouts, and form helpers.
    """
    
    def __init__(self, title: str, parent=None, min_width: int = 350):
        """
          init   logic.
        
        Args:
            title: Description of title.
            parent: Description of parent.
            min_width: Description of min_width.
        
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(min_width)
        
        # Main layout - subclasses add to this
        self._main_layout = QVBoxLayout(self)
        
        # Setup subclass UI first
        self._setup_ui()
        
        # Add standard buttons if subclass didn't
        if not hasattr(self, '_buttons_added') or not self._buttons_added:
            self.add_ok_cancel_buttons()
    
    def _setup_ui(self):
        """
        Override in subclasses to set up the dialog UI.
        Call self.layout to get the main layout.
        """
        pass
    
    @property
    def layout(self) -> QVBoxLayout:
        """Get the main layout for adding widgets."""
        return self._main_layout
    
    def add_ok_cancel_buttons(self, ok_text: str = None, cancel_text: str = None):
        """
        Add standard OK/Cancel buttons to the dialog.
        
        Args:
            ok_text: Custom text for OK button (default: "OK")
            cancel_text: Custom text for Cancel button (default: "Cancel")
        """
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        
        if ok_text:
            buttons.button(QDialogButtonBox.StandardButton.Ok).setText(ok_text)
        if cancel_text:
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(cancel_text)
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._main_layout.addWidget(buttons)
        self._buttons_added = True
        self._button_box = buttons
        return buttons
    
    def pick_color(
        self, 
        current_color: QColor = None, 
        title: str = "Choose Color"
    ) -> Optional[QColor]:
        """
        Show a color picker dialog and return the selected color.
        Uses non-native dialog for consistent appearance.
        
        Args:
            current_color: Initial color to show
            title: Title for the color dialog
        
        Returns:
            Selected QColor, or None if cancelled
        """
        if current_color is None:
            current_color = QColor(Qt.GlobalColor.black)
        
        dialog = QColorDialog(current_color, self)
        dialog.setWindowTitle(title)
        dialog.setOptions(QColorDialog.ColorDialogOption.DontUseNativeDialog)
        
        if dialog.exec():
            return dialog.currentColor()
        return None
    
    def update_color_button(self, button: QPushButton, color: QColor):
        """
        Update a button's style to show the given color.
        
        Args:
            button: Button to update
            color: Color to display as background
        """
        button.setStyleSheet(
            f"background-color: {color.name()}; "
            f"min-width: 80px; min-height: 20px; border: 1px solid #ccc;"
        )
    
    def create_form_layout(self) -> QFormLayout:
        """
        Create and add a form layout to the dialog.
        
        Returns:
            QFormLayout added to the main layout
        """
        form = QFormLayout()
        self._main_layout.addLayout(form)
        return form