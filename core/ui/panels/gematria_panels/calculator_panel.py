"""
Gematria Calculator Panel implementation
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QComboBox, QGroupBox, 
                            QLineEdit, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QSpinBox, QMessageBox, QFileDialog, QDialog)
from PyQt6.QtCore import Qt
import logging
import csv
import openpyxl
import os

from .base_gematria_panel import BaseGematriaPanel
from core.gematria import GematriaCalculator
from databases.gematria.word_repository import WordRepository
from core.gematria.cipher_manager import CipherManager

logger = logging.getLogger(__name__)

class CalculatorPanel(BaseGematriaPanel):
    """Panel for calculating gematria values"""
    
    def __init__(self, parent=None):
        super().__init__(parent, title="🔢 Gematria Calculator")
        self.calculator = GematriaCalculator()
        
        # Initialize the word repository with the unified database path
        self.word_repository = WordRepository()
        self.cipher_manager = CipherManager()
        
        self.setup_ui()
        self.connect_signals()
        self.load_ciphers()
        
    def setup_ui(self):
        """Set up the calculator panel UI"""
        # Clear any existing content first to prevent duplication
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Recursively clear layouts
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
        
        # Main layout - use a single layout for all content
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Input section with better organization
        input_section = QWidget()
        input_layout = QVBoxLayout(input_section)
        input_layout.setSpacing(10)
        
        # Add header for input section
        input_header = QLabel("Calculate Gematria")
        input_header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #e0e0ff;
            }
        """)
        
        # Improve text input appearance
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to calculate...")
        self.text_input.setMinimumHeight(100)
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid rgba(60, 60, 80, 0.5);
                border-radius: 5px;
                padding: 8px;
                background-color: rgba(30, 30, 40, 0.7);
                color: #e0e0ff;
            }
            QTextEdit:focus {
                border-color: rgba(100, 100, 180, 0.8);
            }
        """)
        
        # Cipher selection with label
        cipher_layout = QHBoxLayout()
        cipher_label = QLabel("Select Cipher:")
        cipher_label.setStyleSheet("color: #e0e0ff;")
        
        self.cipher_select = QComboBox()
        self.cipher_select.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 2px solid rgba(60, 60, 80, 0.5);
                border-radius: 5px;
                min-width: 150px;
                background-color: rgba(40, 40, 60, 0.7);
                color: #e0e0ff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(40, 40, 60, 0.9);
                color: #e0e0ff;
                selection-background-color: rgba(60, 60, 120, 0.8);
            }
        """)
        
        cipher_layout.addWidget(cipher_label)
        cipher_layout.addWidget(self.cipher_select)
        cipher_layout.addStretch()
        
        # Results section with better styling
        results_section = QWidget()
        results_section.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 40, 0.7);
                border-radius: 8px;
                padding: 10px;
                border: 1px solid rgba(60, 60, 80, 0.5);
            }
        """)
        
        results_layout = QHBoxLayout(results_section)
        
        value_section = QVBoxLayout()
        self.value_label = QLabel("Calculated Value")
        self.value_label.setStyleSheet("font-weight: bold; color: #e0e0ff;")
        
        self.value_display = QLabel("0")
        self.value_display.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #a0a0ff;
            padding: 10px;
        """)
        
        value_section.addWidget(self.value_label)
        value_section.addWidget(self.value_display)
        
        # Button styling - using our mystical theme
        button_style = """
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
                background-color: rgba(40, 40, 80, 0.7);
                color: #e0e0ff;
                border: 1px solid rgba(100, 100, 180, 0.4);
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 120, 0.8);
                border: 1px solid rgba(120, 120, 200, 0.6);
            }
        """
        
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setStyleSheet(button_style)
        
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(button_style)
        
        self.import_button = QPushButton("Import")
        self.import_button.setStyleSheet(button_style)
        
        self.refresh_button = QPushButton("Refresh Ciphers")
        self.refresh_button.setStyleSheet(button_style)
        
        # Add everything to layouts
        input_layout.addWidget(input_header)
        input_layout.addWidget(self.text_input)
        input_layout.addLayout(cipher_layout)
        
        results_layout.addLayout(value_section)
        results_layout.addStretch()
        results_layout.addWidget(self.calculate_button)
        results_layout.addWidget(self.save_button)
        results_layout.addWidget(self.import_button)
        results_layout.addWidget(self.refresh_button)
        
        main_layout.addWidget(input_section)
        main_layout.addWidget(results_section)
        main_layout.addStretch()
        
        # Set main layout to content widget
        self.content_layout.addLayout(main_layout)

    def connect_signals(self):
        """Connect UI signals to slots"""
        self.calculate_button.clicked.connect(self.calculate_value)
        self.save_button.clicked.connect(self.save_word)
        self.import_button.clicked.connect(self.import_csv)
        self.refresh_button.clicked.connect(self.refresh_ciphers)

    def load_ciphers(self):
        """Load all available ciphers into the combo box"""
        # Add built-in ciphers
        built_in_ciphers = [
            'TQ English',
            'Hebrew Standard',
            'Hebrew Gadol',
            'Greek'
        ]
        self.cipher_select.addItems(built_in_ciphers)
        
        # Add Hebrew variant methods
        self.cipher_select.insertSeparator(len(built_in_ciphers))
        hebrew_variants = [
            'Hebrew Mispar Katan',
            'Hebrew Mispar Kolel',
            'Hebrew AtBash',
            'Hebrew AlBam',
            'Hebrew Mispar Siduri',
            'Hebrew Mispar Bone\'eh'
        ]
        self.cipher_select.addItems(hebrew_variants)
        
        # Add Greek variant methods
        self.cipher_select.insertSeparator(len(built_in_ciphers) + len(hebrew_variants) + 1)
        greek_variants = [
            'Greek Mikros',
            'Greek Pleon',
            'Greek Antistrophos',
            'Greek Hemisu',
            'Greek Arithmos',
            'Greek Dynamis'
        ]
        self.cipher_select.addItems(greek_variants)
        
        # Add tooltips for the Hebrew variant methods
        tooltips = {
            'Hebrew Mispar Katan': "Reduces each letter value to a single digit by summing its digits (e.g., 100 → 1+0+0 = 1)",
            'Hebrew Mispar Kolel': "Standard Hebrew value plus 1 for the word itself",
            'Hebrew AtBash': "Letter substitution cipher where א becomes ת, ב becomes ש, etc.",
            'Hebrew AlBam': "Letter substitution cipher where the alphabet is split in half and letters are paired",
            'Hebrew Mispar Siduri': "Ordinal value - each letter is assigned its position in the alphabet (א=1, ב=2, etc.)",
            'Hebrew Mispar Bone\'eh': "Building value - the square of each letter's standard value",
            # Greek variant tooltips
            'Greek Mikros': "Small value - reduces each letter value to a single digit by summing its digits",
            'Greek Pleon': "Plus one - standard Greek value plus 1 for the word itself",
            'Greek Antistrophos': "Reversed - letter substitution cipher where α becomes ω, β becomes ψ, etc.",
            'Greek Hemisu': "Half - letter substitution cipher where the alphabet is split in half and letters are paired",
            'Greek Arithmos': "Number - ordinal value where each letter is assigned its position in the alphabet",
            'Greek Dynamis': "Power - the square of each letter's standard value"
        }
        
        # Set tooltips for each item in the combobox
        for i in range(self.cipher_select.count()):
            text = self.cipher_select.itemText(i)
            if text in tooltips:
                self.cipher_select.setItemData(i, tooltips[text], Qt.ItemDataRole.ToolTipRole)
        
        # Add separator and custom ciphers
        # Reload all ciphers to ensure we have the latest
        self.cipher_manager.load_all_ciphers()
        custom_cipher_names = self.cipher_manager.get_cipher_names()
        
        if custom_cipher_names:
            self.cipher_select.insertSeparator(len(built_in_ciphers) + len(hebrew_variants) + len(greek_variants) + 2)
            for cipher_name in custom_cipher_names:
                display_name = f"Custom: {cipher_name}"
                self.cipher_select.addItem(display_name)
                
                # Add tooltip for the custom cipher
                cipher = self.cipher_manager.load_cipher(cipher_name)
                if cipher:
                    tooltip = f"Custom cipher: {cipher_name}"
                    if cipher.description:
                        tooltip += f"\n{cipher.description}"
                    
                    # Add active scripts info to tooltip
                    active_scripts = []
                    if cipher.active_scripts['english']:
                        active_scripts.append("English")
                    if cipher.active_scripts['greek']:
                        active_scripts.append("Greek")
                    if cipher.active_scripts['hebrew']:
                        active_scripts.append("Hebrew")
                    
                    if active_scripts:
                        tooltip += f"\nActive scripts: {', '.join(active_scripts)}"
                    
                    # Add case sensitivity info
                    tooltip += f"\nCase sensitive: {'Yes' if cipher.case_sensitive else 'No'}"
                    
                    index = self.cipher_select.findText(display_name)
                    if index >= 0:
                        self.cipher_select.setItemData(index, tooltip, Qt.ItemDataRole.ToolTipRole)

    def refresh_ciphers(self):
        """Refresh the list of available ciphers"""
        # Remember the current selection
        current_cipher = self.cipher_select.currentText()
        
        # Clear and reload all ciphers
        self.cipher_select.clear()
        
        # Force reload of all ciphers from disk
        self.cipher_manager.load_all_ciphers()
        
        # Reload the combo box
        self.load_ciphers()
        
        # Try to restore the previous selection
        index = self.cipher_select.findText(current_cipher)
        if index >= 0:
            self.cipher_select.setCurrentIndex(index)
        else:
            self.cipher_select.setCurrentIndex(0)
            
        logger.debug("Refreshed cipher list")

    def calculate_value(self):
        """Calculate gematria value for the input text"""
        text = self.text_input.toPlainText()
        cipher = self.cipher_select.currentText()
        
        # Validate inputs
        if not text.strip():
            QMessageBox.warning(self, "Error", "Please enter text to calculate")
            return
            
        if not cipher:
            QMessageBox.warning(self, "Error", "Please select a cipher type")
            return
        
        try:
            # Handle custom ciphers
            if cipher.startswith("Custom: "):
                cipher_name = cipher[8:]  # Remove "Custom: " prefix
                custom_cipher = self.cipher_manager.load_cipher(cipher_name)
                
                if not custom_cipher:
                    raise ValueError(f"Custom cipher '{cipher_name}' not found")
                
                logger.debug(f"Calculating with custom cipher: {cipher_name}")
                value = 0
                
                # Calculate value using the custom cipher
                for char in text:
                    char_value = custom_cipher.get_value(char)
                    value += char_value
                    logger.debug(f"Character '{char}' has value {char_value}")
                
                self.value_display.setText(str(value))
                logger.info(f"Calculated {cipher_name} value for '{text}': {value}")
                
                # Add to calculation history
                if text.strip():
                    self.word_repository.add_to_history(text, cipher, value)
            else:
                # Use the standard calculator for built-in ciphers
                value = self.calculator.calculate(text, cipher)
                self.value_display.setText(str(value))
                logger.info(f"Calculated {cipher} value for '{text}': {value}")
                
                # Add to calculation history
                if text.strip():
                    self.word_repository.add_to_history(text, cipher, value)
                
        except Exception as e:
            logger.error(f"Error calculating gematria: {e}")
            QMessageBox.warning(self, "Calculation Error", f"Error: {str(e)}")

    def save_word(self):
        """Save the current word/phrase to the database"""
        text = self.text_input.toPlainText()
        cipher = self.cipher_select.currentText()
        
        try:
            value = int(self.value_display.text())
        except ValueError:
            value = 0
        
        if not text.strip():
            QMessageBox.warning(self, "Error", "Please enter text to save.")
            return
        
        # Check if word exists
        if self.word_repository.word_exists(text, cipher):
            response = QMessageBox.question(
                self, 
                "Duplicate Entry", 
                f"'{text}' already exists in the database with cipher {cipher}. Do you want to update it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if response == QMessageBox.StandardButton.No:
                return
        
        # Save the word
        success = self.word_repository.save_word(text, cipher, value)
        if success:
            QMessageBox.information(self, "Success", "Word saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save word to database.")

    def import_csv(self):
        """Import words/phrases from CSV or Excel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import File", "", "Files (*.csv *.xlsx *.xls)")
        
        if file_path:
            # Create a dialog with mystical styling
            cipher_dialog = QDialog(self)
            cipher_dialog.setWindowTitle("Select Cipher Type")
            cipher_dialog.setStyleSheet("""
                QDialog {
                    background-color: rgba(30, 30, 40, 0.9);
                }
                QLabel {
                    color: #e0e0ff;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: rgba(40, 40, 80, 0.7);
                    color: #e0e0ff;
                    border: 1px solid rgba(100, 100, 180, 0.4);
                    border-radius: 5px;
                    padding: 8px 15px;
                }
                QPushButton:hover {
                    background-color: rgba(60, 60, 120, 0.8);
                    border: 1px solid rgba(120, 120, 200, 0.6);
                }
                QComboBox {
                    padding: 5px;
                    border: 2px solid rgba(60, 60, 80, 0.5);
                    border-radius: 5px;
                    min-width: 150px;
                    background-color: rgba(40, 40, 60, 0.7);
                    color: #e0e0ff;
                }
            """)
            
            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            cipher_combo = QComboBox()
            
            # Add standard ciphers
            standard_ciphers = [
                'TQ English',
                'Hebrew Standard',
                'Hebrew Gadol',
                'Greek'
            ]
            cipher_combo.addItems(standard_ciphers)
            
            # Add Hebrew variant methods
            cipher_combo.insertSeparator(len(standard_ciphers))
            hebrew_variants = [
                'Hebrew Mispar Katan',
                'Hebrew Mispar Kolel',
                'Hebrew AtBash',
                'Hebrew AlBam',
                'Hebrew Mispar Siduri',
                'Hebrew Mispar Bone\'eh'
            ]
            cipher_combo.addItems(hebrew_variants)
            
            # Add Greek variant methods
            cipher_combo.insertSeparator(len(standard_ciphers) + len(hebrew_variants) + 1)
            greek_variants = [
                'Greek Mikros',
                'Greek Pleon',
                'Greek Antistrophos',
                'Greek Hemisu',
                'Greek Arithmos',
                'Greek Dynamis'
            ]
            cipher_combo.addItems(greek_variants)
            
            # Add custom ciphers
            custom_cipher_names = self.cipher_manager.get_cipher_names()
            if custom_cipher_names:
                cipher_combo.insertSeparator(len(standard_ciphers) + len(hebrew_variants) + len(greek_variants) + 2)
                for cipher_name in custom_cipher_names:
                    cipher_combo.addItem(f"Custom: {cipher_name}")
            
            confirm_button = QPushButton("Import")
            
            layout.addWidget(QLabel("Select cipher type for import:"))
            layout.addWidget(cipher_combo)
            layout.addWidget(confirm_button)
            
            cipher_dialog.setLayout(layout)
            
            def do_import():
                selected_cipher = cipher_combo.currentText()
                if file_path.lower().endswith(('.xlsx', '.xls')):
                    self.import_excel_file(file_path, selected_cipher)
                else:
                    self.import_csv_file(file_path, selected_cipher)
                cipher_dialog.accept()
            
            confirm_button.clicked.connect(do_import)
            cipher_dialog.exec()

    def import_csv_file(self, file_path, cipher_type):
        """Import data from CSV file"""
        try:
            imported_count = 0
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)  # Skip header row
                
                for row in reader:
                    if len(row) >= 2:  # At least text and value
                        text = row[0].strip()
                        try:
                            value = int(row[1].strip())
                            
                            # Save to database
                            if self.word_repository.save_word(text, cipher_type, value):
                                imported_count += 1
                        except ValueError:
                            logger.warning(f"Invalid value for '{text}': {row[1]}")
            
            QMessageBox.information(
                self, 
                "Import Complete", 
                f"Successfully imported {imported_count} entries."
            )
            
            # Refresh the calculator display
            self.refresh_ciphers()
            
        except Exception as e:
            logger.error(f"Error importing CSV: {e}")
            QMessageBox.warning(self, "Import Error", f"Error importing file: {str(e)}")

    def import_excel_file(self, file_path, cipher_type):
        """Import data from Excel file"""
        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
            imported_count = 0
            
            # Skip header row
            rows = list(sheet.rows)[1:]
            
            for row in rows:
                if len(row) >= 2:  # At least text and value
                    text = str(row[0].value).strip()
                    if text and row[1].value is not None:
                        try:
                            value = int(row[1].value)
                            
                            # Save to database
                            if self.word_repository.save_word(text, cipher_type, value):
                                imported_count += 1
                        except ValueError:
                            logger.warning(f"Invalid value for '{text}': {row[1].value}")
            
            QMessageBox.information(
                self, 
                "Import Complete", 
                f"Successfully imported {imported_count} entries."
            )
            
            # Refresh the calculator display
            self.refresh_ciphers()
            
        except Exception as e:
            logger.error(f"Error importing Excel: {e}")
            QMessageBox.warning(self, "Import Error", f"Error importing file: {str(e)}")
