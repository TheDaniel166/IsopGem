"""Gematria calculator tool window."""
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QMessageBox, QInputDialog, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction
from typing import Dict, List, Optional
from ..services.base_calculator import GematriaCalculator
from ..services import CalculationService
from shared.ui import VirtualKeyboard


class GematriaCalculatorWindow(QDialog):
    """Standalone Gematria Calculator window (using QDialog for Wayland stability)."""
    
    def __init__(self, calculators: List[GematriaCalculator], parent=None):
        """
        Initialize the calculator window.
        
        Args:
            calculators: List of available gematria calculator instances
            parent: Optional parent widget
        """
        # Initialize as QDialog for better Wayland compatibility
        super().__init__(parent)
        self.calculators: Dict[str, GematriaCalculator] = {
            calc.name: calc for calc in calculators
        }
        self.current_calculator: GematriaCalculator = calculators[0]
        self.calculation_service = CalculationService()
        
        # Store current calculation
        self.current_text: str = ""
        self.current_value: int = 0
        self.current_breakdown: List[tuple] = []
        
        # Virtual keyboard
        self.virtual_keyboard: Optional[VirtualKeyboard] = None
        self.keyboard_visible: bool = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the calculator interface."""
        self.setWindowTitle("Gematria Calculator")
        self.setMinimumSize(700, 600)
        
        # Prevent this window from closing the entire application
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        # Make it modeless so it doesn't block the main window
        self.setModal(False)
        
        # Main layout (QDialog doesn't have setCentralWidget)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("📖 Gematria Calculator")
        title_label.setStyleSheet("""
            color: #111827;
            font-size: 22pt;
            font-weight: 700;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # System selector with nested menus
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Calculation Method:")
        selector_label.setStyleSheet("font-size: 11pt; font-weight: 500; color: #374151;")
        
        # Create a button that shows a menu
        self.system_button = QPushButton()
        self.system_button.setMinimumHeight(44)
        self.system_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                text-align: left;
                padding: 8px 12px;
                font-size: 11pt;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton::menu-indicator {
                width: 12px;
                subcontrol-position: right center;
                subcontrol-origin: padding;
                left: -4px;
            }
        """)
        
        # Create the menu with nested structure
        self.system_menu = QMenu(self)
        self.system_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                color: #111827;
            }
            QMenu::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e5e7eb;
                margin: 4px 8px;
            }
        """)
        
        # Hebrew submenu
        hebrew_menu = self.system_menu.addMenu("📖 Hebrew")
        # Add "All Methods" option at the top
        all_hebrew_action = hebrew_menu.addAction("✨ All Methods")
        all_hebrew_action.setData("Hebrew_ALL")
        all_hebrew_action.triggered.connect(lambda: self._select_calculator("Hebrew_ALL"))
        hebrew_menu.addSeparator()
        for name in list(self.calculators.keys()):
            if "Hebrew" in name:
                action = hebrew_menu.addAction(name.replace("Hebrew ", ""))
                action.setData(name)
                action.triggered.connect(lambda checked, n=name: self._select_calculator(n))
        
        # Greek submenu
        greek_menu = self.system_menu.addMenu("🔤 Greek")
        # Add "All Methods" option at the top
        all_greek_action = greek_menu.addAction("✨ All Methods")
        all_greek_action.setData("Greek_ALL")
        all_greek_action.triggered.connect(lambda: self._select_calculator("Greek_ALL"))
        greek_menu.addSeparator()
        for name in list(self.calculators.keys()):
            if "Greek" in name:
                action = greek_menu.addAction(name.replace("Greek ", ""))
                action.setData(name)
                action.triggered.connect(lambda checked, n=name: self._select_calculator(n))
        
        # English submenu
        english_menu = self.system_menu.addMenu("🔡 English")
        # Add "All Methods" option at the top
        all_english_action = english_menu.addAction("✨ All Methods")
        all_english_action.setData("English_ALL")
        all_english_action.triggered.connect(lambda: self._select_calculator("English_ALL"))
        english_menu.addSeparator()
        for name in list(self.calculators.keys()):
            if "English" in name or "TQ" in name:
                action = english_menu.addAction(name.replace("English ", ""))
                action.setData(name)
                action.triggered.connect(lambda checked, n=name: self._select_calculator(n))
        
        self.system_button.setMenu(self.system_menu)
        
        # Set first calculator as default
        first_calc = list(self.calculators.keys())[0]
        # Display only the method name without language prefix
        display_name = first_calc.replace("Hebrew ", "").replace("Greek ", "").replace("English ", "")
        self.system_button.setText(display_name)
        self.current_calculator = self.calculators[first_calc]
        
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.system_button, 1)
        main_layout.addLayout(selector_layout)
        
        # Input section
        input_label = QLabel("Input Text:")
        input_label.setStyleSheet("font-size: 11pt; font-weight: 500; color: #374151;")
        main_layout.addWidget(input_label)
        
        # Input field with keyboard toggle
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type text and press Enter or Calculate...")
        self.input_field.setStyleSheet("font-size: 14pt; min-height: 44px;")
        # Only calculate on Enter key press, not on every text change
        self.input_field.returnPressed.connect(self._calculate)
        input_layout.addWidget(self.input_field)
        
        # Keyboard toggle button
        self.keyboard_toggle = QPushButton("⌨️")
        self.keyboard_toggle.setToolTip("Open virtual keyboard")
        self.keyboard_toggle.setMaximumWidth(50)
        self.keyboard_toggle.setMinimumHeight(44)
        self.keyboard_toggle.clicked.connect(self._toggle_keyboard)
        input_layout.addWidget(self.keyboard_toggle)
        
        main_layout.addLayout(input_layout)
        
        # Virtual keyboard (popup window)
        self.virtual_keyboard = VirtualKeyboard(self)
        self.virtual_keyboard.set_target_input(self.input_field)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Calculate button
        self.calc_button = QPushButton("Calculate")
        self.calc_button.clicked.connect(self._calculate)
        self.calc_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                font-size: 12pt;
                font-weight: 600;
                min-height: 44px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        button_layout.addWidget(self.calc_button)
        
        # Save button (initially disabled)
        self.save_button = QPushButton("💾 Save")
        self.save_button.clicked.connect(self._save_calculation)
        self.save_button.setMinimumHeight(44)
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet("""
            QPushButton:enabled {
                background-color: #10b981;
                font-size: 12pt;
                font-weight: 600;
            }
            QPushButton:enabled:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #e5e7eb;
                color: #9ca3af;
            }
        """)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # Results section
        results_label = QLabel("Results:")
        results_label.setStyleSheet("font-size: 11pt; font-weight: 500; color: #374151; margin-top: 8px;")
        main_layout.addWidget(results_label)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 11pt;
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        main_layout.addWidget(self.results_display)
        
        # Set focus to input field
        self.input_field.setFocus()
    
    def _select_calculator(self, system_name: str):
        """
        Select a calculator system from the menu.
        
        Args:
            system_name: Name of the selected system
        """
        # Handle "All Methods" selections
        if system_name.endswith("_ALL"):
            language = system_name.replace("_ALL", "")
            display_name = f"{language} - All Methods"
            self.system_button.setText("All Methods")
            self.current_calculator = None  # Flag for multi-method mode
            self._current_language = language
            
            # Update keyboard layout
            if self.virtual_keyboard:
                if language == 'Hebrew':
                    self.virtual_keyboard.set_layout('hebrew')
                elif language == 'Greek':
                    self.virtual_keyboard.set_layout('greek_lower')
        else:
            # Display only the method name without language prefix
            display_name = system_name.replace("Hebrew ", "").replace("Greek ", "").replace("English ", "")
            self.system_button.setText(display_name)
            self.current_calculator = self.calculators[system_name]
            self._current_language = None
            
            # Update keyboard layout based on calculator language
            if self.virtual_keyboard:
                if 'Hebrew' in system_name:
                    self.virtual_keyboard.set_layout('hebrew')
                elif 'Greek' in system_name:
                    self.virtual_keyboard.set_layout('greek_lower')
        
        # Clear results when switching systems
        self.results_display.clear()
    
    def _toggle_keyboard(self):
        """Toggle virtual keyboard visibility."""
        if self.virtual_keyboard:
            if self.virtual_keyboard.isVisible():
                self.virtual_keyboard.hide()
            else:
                self.virtual_keyboard.show()
                self.virtual_keyboard.raise_()
                self.virtual_keyboard.activateWindow()
    
    def _calculate(self):
        """Calculate and display gematria value for current input."""
        text = self.input_field.text()
        
        if not text:
            self.results_display.clear()
            self.save_button.setEnabled(False)
            return
        
        # Check if in "All Methods" mode
        if self.current_calculator is None and hasattr(self, '_current_language'):
            self._calculate_all_methods(text, self._current_language)
            return
        
        # Calculate total value
        total = self.current_calculator.calculate(text)
        
        # Get breakdown
        breakdown = self.current_calculator.get_breakdown(text)
        
        # Store current calculation
        self.current_text = text
        self.current_value = total
        self.current_breakdown = breakdown
        
        # Enable save button
        self.save_button.setEnabled(True)
        
        # Format results
        results = []
        results.append(f"System: {self.current_calculator.name}")
        results.append(f"\nTotal Value: {total}")
        results.append("\n" + "="*50)
        results.append("\nBreakdown:")
        results.append("-"*50)
        
        if breakdown:
            for char, value in breakdown:
                results.append(f"  {char}  =  {value}")
        else:
            results.append("  (No recognized characters)")
        
        results.append("-"*50)
        results.append(f"\nCharacters counted: {len(breakdown)}")
        
        self.results_display.setPlainText("\n".join(results))
    
    def _calculate_all_methods(self, text: str, language: str):
        """Calculate using all methods for a given language.
        
        Args:
            text: The text to calculate
            language: 'Hebrew', 'Greek', or 'English'
        """
        # Get all calculators for this language
        lang_calculators = [
            (name, calc) for name, calc in self.calculators.items()
            if language in name
        ]
        
        if not lang_calculators:
            return
        
        # Calculate with all methods
        results = []
        results.append(f"Text: {text}")
        results.append(f"Language: {language}")
        results.append("\n" + "="*60)
        results.append("\nAll Methods - Values Only:")
        results.append("-"*60)
        
        # Create table header
        results.append(f"{'Method':<35} {'Value':>20}")
        results.append("-"*60)
        
        for name, calc in lang_calculators:
            try:
                value = calc.calculate(text)
                method_name = name.replace(f"{language} ", "")
                results.append(f"{method_name:<35} {value:>20,}")
            except Exception as e:
                method_name = name.replace(f"{language} ", "")
                results.append(f"{method_name:<35} {'Error':>20}")
        
        results.append("-"*60)
        results.append(f"\nTotal methods calculated: {len(lang_calculators)}")
        
        self.results_display.setPlainText("\n".join(results))
        
        # Store for potential saving
        self.current_text = text
        self.current_value = 0  # No single value in multi-method mode
        self.current_breakdown = []
        
        # Disable save button in all methods mode
        self.save_button.setEnabled(False)
    
    def _save_calculation(self):
        """Save the current calculation to the database."""
        if not self.current_text:
            return
        
        # Create a simple dialog to get notes and tags
        notes, ok = QInputDialog.getMultiLineText(
            self,
            "Save Calculation",
            f"Saving: {self.current_text} = {self.current_value}\n\nNotes (optional):",
            ""
        )
        
        if not ok:
            return
        
        # Get tags
        tags_str, ok = QInputDialog.getText(
            self,
            "Add Tags",
            "Tags (comma-separated, optional):",
            QLineEdit.EchoMode.Normal,
            ""
        )
        
        if not ok:
            tags_str = ""
        
        # Parse tags
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Save to database
        try:
            record = self.calculation_service.save_calculation(
                text=self.current_text,
                value=self.current_value,
                calculator=self.current_calculator,
                breakdown=self.current_breakdown,
                notes=notes,
                tags=tags
            )
            
            QMessageBox.information(
                self,
                "Saved",
                f"Calculation saved successfully!\n\n{record.text} = {record.value}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save calculation:\n{str(e)}"
            )
