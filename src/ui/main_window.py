"""Main window for the Gematria Calculator application."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict, List
from calculators.base import GematriaCalculator


class MainWindow(QMainWindow):
    """Main application window for gematria calculations."""
    
    def __init__(self, calculators: List[GematriaCalculator]):
        """
        Initialize the main window.
        
        Args:
            calculators: List of available gematria calculator instances
        """
        super().__init__()
        self.calculators: Dict[str, GematriaCalculator] = {
            calc.name: calc for calc in calculators
        }
        self.current_calculator: GematriaCalculator = calculators[0]
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface components."""
        self.setWindowTitle("Gematria Calculator")
        self.setMinimumSize(600, 500)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Gematria Calculator")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # System selector
        selector_layout = QHBoxLayout()
        selector_label = QLabel("System:")
        self.system_combo = QComboBox()
        self.system_combo.addItems(list(self.calculators.keys()))
        self.system_combo.currentTextChanged.connect(self._on_system_changed)
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.system_combo)
        selector_layout.addStretch()
        main_layout.addLayout(selector_layout)
        
        # Input section
        input_label = QLabel("Enter text:")
        main_layout.addWidget(input_label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type Hebrew text here...")
        input_font = QFont()
        input_font.setPointSize(14)
        self.input_field.setFont(input_font)
        self.input_field.textChanged.connect(self._on_text_changed)
        self.input_field.returnPressed.connect(self._calculate)
        main_layout.addWidget(self.input_field)
        
        # Calculate button
        self.calc_button = QPushButton("Calculate")
        self.calc_button.clicked.connect(self._calculate)
        button_font = QFont()
        button_font.setPointSize(12)
        self.calc_button.setFont(button_font)
        self.calc_button.setMinimumHeight(40)
        main_layout.addWidget(self.calc_button)
        
        # Results section
        results_label = QLabel("Results:")
        main_layout.addWidget(results_label)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        results_font = QFont("Monospace")
        results_font.setPointSize(11)
        self.results_display.setFont(results_font)
        main_layout.addWidget(self.results_display)
        
        # Set focus to input field
        self.input_field.setFocus()
    
    def _on_system_changed(self, system_name: str):
        """
        Handle calculator system change.
        
        Args:
            system_name: Name of the selected system
        """
        self.current_calculator = self.calculators[system_name]
        # Recalculate if there's text
        if self.input_field.text():
            self._calculate()
    
    def _on_text_changed(self, text: str):
        """
        Handle input text changes for real-time calculation.
        
        Args:
            text: Current input text
        """
        if text:
            self._calculate()
        else:
            self.results_display.clear()
    
    def _calculate(self):
        """Calculate and display gematria value for current input."""
        text = self.input_field.text()
        
        if not text:
            self.results_display.clear()
            return
        
        # Calculate total value
        total = self.current_calculator.calculate(text)
        
        # Get breakdown
        breakdown = self.current_calculator.get_breakdown(text)
        
        # Format results
        results = []
        results.append(f"System: {self.current_calculator.name}")
        results.append(f"\nTotal Value: {total}")
        results.append("\n" + "="*50)
        results.append("\nBreakdown:")
        results.append("-"*50)
        
        if breakdown:
            for char, value in breakdown.items():
                results.append(f"  {char}  =  {value}")
        else:
            results.append("  (No recognized characters)")
        
        results.append("-"*50)
        results.append(f"\nCharacters counted: {len(breakdown)}")
        
        self.results_display.setPlainText("\n".join(results))
