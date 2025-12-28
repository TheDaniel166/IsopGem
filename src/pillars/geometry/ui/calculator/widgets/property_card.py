"""
Property Card - The Liturgical Input Tile.
Styled card widget for displaying and editing a single geometric property.
"""
from typing import Optional, Callable
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QLineEdit, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QDoubleValidator

from ....services.base_shape import ShapeProperty
from ...liturgy_styles import LiturgyInputs, LiturgyColors, LiturgyMenus


class PropertyCard(QFrame):
    """
    A liturgy-compliant card for displaying and editing a single geometric property.
    Encapsulates label, input field, unit display, and context actions.
    """
    
    value_changed = pyqtSignal(str, float)  # key, new_value
    input_cleared = pyqtSignal(str)         # key
    quadset_analysis_requested = pyqtSignal(float) # value

    
    def __init__(self, property_data: ShapeProperty, parent=None):
        """
          init   logic.
        
        Args:
            property_data: Description of property_data.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.property_key = property_data.key
        self.property_name = property_data.name
        self.unit = property_data.unit
        self.is_readonly = property_data.readonly
        self.precision = property_data.precision
        
        self._setup_ui()
        self.update_state(property_data.value)

    def _setup_ui(self):
        """Build the internal UI of the card."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(4)
        
        # Header (Name + Unit)
        self.header_label = QLabel(f"{self.property_name} ({self.unit})" if self.unit else self.property_name)
        self.header_label.setStyleSheet(f"color: {LiturgyColors.VOID_SLATE}; font-size: 10pt; font-weight: 600;")
        self.layout.addWidget(self.header_label)
        
        # Input Field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("—")
        if self.is_readonly:
            self.input_field.setReadOnly(True)
            self.input_field.setStyleSheet(LiturgyInputs.vessel_readonly())
        else:
            self.input_field.setStyleSheet(LiturgyInputs.vessel())
            self.input_field.setValidator(QDoubleValidator())
            self.input_field.textChanged.connect(self._on_text_changed)
            
        # Context Menu
        self.input_field.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.input_field.customContextMenuRequested.connect(self._show_context_menu)
            
        self.layout.addWidget(self.input_field)
        
        # Default styling
        self.setStyleSheet(LiturgyInputs.property_card_readonly() if self.is_readonly else LiturgyInputs.property_card_editable())

    def update_state(self, value: Optional[float], is_solved: bool = False):
        """Update the card's visual state based on value."""
        self.blockSignals(True)
        if value is not None:
            fmt = f"{{:.{self.precision}f}}"
            text = fmt.format(value).rstrip('0').rstrip('.')
            self.input_field.setText(text)
            
            if is_solved:
                self.setStyleSheet(LiturgyInputs.property_card_solved())
            elif not self.is_readonly:
                 # Revert to editable style if not solved but has value (e.g. user input)
                 # Actually, "solved" usually means calculated from others. 
                 # If it's user input, it's also "solved" in a way.
                 # For now, let's stick to simple logic:
                 self.setStyleSheet(LiturgyInputs.property_card_solved()) 
        else:
            self.input_field.clear()
            if not self.is_readonly:
                self.setStyleSheet(LiturgyInputs.property_card_editable())
            else:
                 self.setStyleSheet(LiturgyInputs.property_card_readonly())
                 
        self.blockSignals(False)

    def _on_text_changed(self, text: str):
        """Handle text input."""
        if not text:
            self.input_cleared.emit(self.property_key)
            return

        try:
            # Handle comma/dot
            clean_text = text.replace(',', '.')
            val = float(clean_text)
            self.value_changed.emit(self.property_key, val)
        except ValueError:
            pass # Ignore invalid typing

    def _show_context_menu(self, pos):
        """Show extended context menu."""
        menu = self.input_field.createStandardContextMenu()
        menu.setStyleSheet(LiturgyMenus.standard())
        
        # Add separator and integration actions
        menu.addSeparator()
        
        action_quadset = QAction("Send rounded to Quadset Analysis", self)
        action_quadset.triggered.connect(self._request_quadset_analysis)
        menu.addAction(action_quadset)
        
        menu.exec(self.input_field.mapToGlobal(pos))

    def _request_quadset_analysis(self):
        """Handle request to send value to TQ."""
        text = self.input_field.text()
        if not text:
            return
            
        try:
            # Clean text (remove '—' or whatever)
            val = float(text.replace(',', '.'))
            # Round to nearest integer as requested (or just pass float? User said "Rounded Number")
            # TQ Quadset Engine usually expects integers for the main analysis, though it can handle float input?
            # QuadsetEngine usually takes an input decimal. Let's round it to be safe for "Quadset Analysis" which implies integer sequences usually.
            # But the UI has "Input Decimal", so maybe float is fine?
            # User specific request: "Send the Rounded Number" -> implying he wants the INT.
            val_int = round(val)
            self.quadset_analysis_requested.emit(val_int)
        except ValueError:
            pass
