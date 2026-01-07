"""Ternary converter tool window."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QFrame, QPushButton, QWidget,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from shared.ui.theme import COLORS, get_card_style, get_app_stylesheet
from shared.ui.catalyst_styles import get_navigator_style
from ..services.ternary_service import TernaryService


class TernaryConverterWindow(QMainWindow):
    """Window for converting between decimal and ternary numbers."""
    
    def __init__(self, parent=None):
        """Initialize the converter window."""
        super().__init__(parent)
        self.ternary_service = TernaryService()
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Ternary Converter")
        self.setMinimumSize(600, 450)
        
        # Level 0: The Substrate (Ghost Layer)
        # We use a stylesheet on the central widget to set the background texture
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        bg_path = os.path.join(base_path, "assets", "textures", "substrate_v2.png")
        
        # Fallback if image doesn't exist, though we just created it
        bg_style = f"background-image: url({bg_path}); background-repeat: repeat; background-position: center;"
        
        # Main layout on central widget
        central = QWidget()
        central.setObjectName("Substrate")
        central.setStyleSheet(f"""
            QWidget#Substrate {{
                background-color: {COLORS['background']};
                {bg_style}
            }}
        """)
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel("Ternary Converter")
        title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 24pt;
            font-weight: 700;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Level 1: The Tablet (Marble Slate)
        content_card = QFrame()
        content_card.setStyleSheet(get_card_style())
        
        # Add shadow for depth (Levitation)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 25))
        content_card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(content_card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        # Decimal Section
        decimal_label = QLabel("Decimal (Base 10)")
        decimal_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        card_layout.addWidget(decimal_label)
        
        self.decimal_input = QLineEdit()
        self.decimal_input.setPlaceholderText("Enter decimal number...")
        self.decimal_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: 16pt; 
                padding: 12px;
                background: {COLORS['background_alt']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['focus']};
                background: {COLORS['light']};
            }}
        """)
        self.decimal_input.textChanged.connect(self._on_decimal_changed)
        card_layout.addWidget(self.decimal_input)
        
        # Arrow indicator
        arrow_container = QWidget()
        arrow_layout = QHBoxLayout(arrow_container)
        arrow_layout.setContentsMargins(0, 10, 0, 10)
        
        arrow_label = QLabel("⇅")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_label.setStyleSheet(f"""
            color: {COLORS['primary']}; 
            font-size: 24pt; 
            font-weight: bold;
        """)
        arrow_layout.addWidget(arrow_label)
        card_layout.addWidget(arrow_container)
        
        # Ternary Section
        ternary_label = QLabel("Ternary (Base 3)")
        ternary_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        card_layout.addWidget(ternary_label)
        
        self.ternary_input = QLineEdit()
        self.ternary_input.setPlaceholderText("Enter ternary number (0, 1, 2)...")
        self.ternary_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: 16pt; 
                padding: 12px;
                background: {COLORS['background_alt']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['focus']};
                background: {COLORS['light']};
            }}
        """)
        self.ternary_input.textChanged.connect(self._on_ternary_changed)
        card_layout.addWidget(self.ternary_input)
        
        layout.addWidget(content_card)
        
        # Status/Error Label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {COLORS['error']}; font-weight: 600; font-size: 11pt;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Clear Button (Navigator Archetype)
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        clear_btn.setStyleSheet(get_navigator_style())
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Center the button
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        layout.addWidget(btn_container)
        
        layout.addStretch()
        
    def _on_decimal_changed(self, text: str):
        """Handle changes in decimal input."""
        self.status_label.clear()
        
        if not text:
            self.ternary_input.blockSignals(True)
            self.ternary_input.clear()
            self.ternary_input.blockSignals(False)
            return
            
        try:
            # Handle negative sign at start
            if text == "-":
                return
                
            value = int(text)
            ternary = self.ternary_service.decimal_to_ternary(value)
            self.ternary_input.blockSignals(True)
            self.ternary_input.setText(ternary)
            self.ternary_input.blockSignals(False)
            
        except ValueError:
            self.status_label.setText("Invalid decimal number")
            
    def _on_ternary_changed(self, text: str):
        """Handle changes in ternary input."""
        self.status_label.clear()
        
        if not text:
            self.decimal_input.blockSignals(True)
            self.decimal_input.clear()
            self.decimal_input.blockSignals(False)
            return
            
        try:
            value = self.ternary_service.ternary_to_decimal(text)
            self.decimal_input.blockSignals(True)
            self.decimal_input.setText(str(value))
            self.decimal_input.blockSignals(False)
            
        except ValueError:
            self.status_label.setText("Invalid ternary number")
            
    def _clear_all(self):
        """Clear all inputs."""
        self.decimal_input.clear()
        self.ternary_input.clear()
        self.status_label.clear()
