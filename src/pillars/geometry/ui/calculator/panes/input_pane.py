"""
Input Pane - The Properties Panel.
Left panel displaying shape properties as editable cards with calculation controls.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal


from ..view_model import GeometryViewModel
from ..widgets.property_card import PropertyCard
from ...liturgy_styles import LiturgyColors, LiturgyPanels, LiturgyButtons, LiturgyScrollArea

class InputPane(QWidget):
    """
    Left panel: Displays shape properties and calculation controls.
    """
    
    def __init__(self, view_model: GeometryViewModel, parent=None):
        """
          init   logic.
        
        Args:
            view_model: Description of view_model.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.view_model = view_model
        self.cards = {} # Map key -> PropertyCard
        
        self._setup_ui()
        self._connect_signals()


    quadset_analysis_requested = pyqtSignal(float) # bubble up to main window


    def _setup_ui(self):
        """Build the pane UI."""
        # Main container style
        self.setStyleSheet(LiturgyPanels.calculation_pane())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(24, 24, 24, 16)
        
        title = QLabel(self.view_model.shape_name)
        title.setStyleSheet(f"font-size: 22pt; font-weight: 300; color: {LiturgyColors.VOID};")
        header_layout.addWidget(title)
        layout.addWidget(header_container)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(LiturgyScrollArea.standard())
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(24, 0, 24, 24)
        self.content_layout.setSpacing(16)
        
        # Help Text
        help_lbl = QLabel(self.view_model.shape_description)
        help_lbl.setWordWrap(True)
        help_lbl.setStyleSheet(f"color: {LiturgyColors.VOID_SLATE}; font-size: 10pt; margin-bottom: 8px;")
        self.content_layout.addWidget(help_lbl)
        
        # Create Cards
        self._create_property_cards()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Footer (Actions)
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 16, 24, 24)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setStyleSheet(LiturgyButtons.destroyer())
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.view_model.clear_all)
        
        footer_layout.addWidget(self.clear_btn)
        layout.addWidget(footer)

    def _create_property_cards(self):
        """Generate cards for all properties."""
        for prop in self.view_model.get_properties():
            card = PropertyCard(prop)
            card.value_changed.connect(self.view_model.set_property)
            card.quadset_analysis_requested.connect(self.quadset_analysis_requested.emit)
            self.content_layout.addWidget(card)

            self.cards[prop.key] = card
            
        self.content_layout.addStretch()

    def _connect_signals(self):
        """Listen to View Model updates."""
        self.view_model.calculation_completed.connect(self._on_calculation_update)
        # self.view_model.shape_cleared.connect(self._on_calculation_update)

    def _on_calculation_update(self):
        """Update all cards with new values from the model."""
        shape = self.view_model.get_shape()
        for key, card in self.cards.items():  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            prop = shape.properties.get(key)
            if prop:
                # Check if this property is 'solved' (has value and not readonly input?)
                # For visual feedback, we can assume non-None derived values are solved.
                _is_solved = prop.value is not None and not prop.readonly 
                # Actually, strictly following previous logic:
                # Solved = Green if it has a value.
                # Required = Amber if None (and not readonly).
                
                # Let's pass the raw value and let card decide style, or pass style hint?
                # Card.update_state handles basic logic.
                # Just pass value.
                card.update_state(prop.value)