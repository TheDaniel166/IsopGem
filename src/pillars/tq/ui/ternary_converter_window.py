"""Ternary converter tool window."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QGroupBox, QPushButton, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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
        self.setMinimumSize(500, 300)
        
        # Main layout on central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Ternary Converter")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Decimal Section
        decimal_group = QGroupBox("Decimal (Base 10)")
        decimal_layout = QVBoxLayout()
        
        self.decimal_input = QLineEdit()
        self.decimal_input.setPlaceholderText("Enter decimal number...")
        self.decimal_input.setStyleSheet("font-size: 14pt; padding: 8px;")
        self.decimal_input.textChanged.connect(self._on_decimal_changed)
        
        decimal_layout.addWidget(self.decimal_input)
        decimal_group.setLayout(decimal_layout)
        layout.addWidget(decimal_group)
        
        # Arrow indicator
        arrow_label = QLabel("⇅")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_font = QFont()
        arrow_font.setPointSize(24)
        arrow_label.setFont(arrow_font)
        layout.addWidget(arrow_label)
        
        # Ternary Section
        ternary_group = QGroupBox("Ternary (Base 3)")
        ternary_layout = QVBoxLayout()
        
        self.ternary_input = QLineEdit()
        self.ternary_input.setPlaceholderText("Enter ternary number (0, 1, 2)...")
        self.ternary_input.setStyleSheet("font-size: 14pt; padding: 8px;")
        self.ternary_input.textChanged.connect(self._on_ternary_changed)
        
        ternary_layout.addWidget(self.ternary_input)
        ternary_group.setLayout(ternary_layout)
        layout.addWidget(ternary_group)
        
        # Status/Error Label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Clear Button
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        layout.addWidget(clear_btn)
        
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
            # Handle negative sign at start
            if text == "-":
                return
                
            value = self.ternary_service.ternary_to_decimal(text)
            
            self.decimal_input.blockSignals(True)
            self.decimal_input.setText(str(value))
            self.decimal_input.blockSignals(False)
            
        except ValueError:
            self.status_label.setText("Invalid ternary number (use only 0, 1, 2)")
            
    def _clear_all(self):
        """Clear all inputs."""
        self.decimal_input.clear()
        self.ternary_input.clear()
        self.status_label.clear()
