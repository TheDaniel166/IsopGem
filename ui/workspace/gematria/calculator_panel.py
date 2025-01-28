from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QComboBox, QLabel, QPushButton,
                            QFileDialog, QMessageBox, QDialog)
from core.gematria.calculator import GematriaCalculator
from core.database.word_repository import WordRepository
import csv
import openpyxl

class CalculatorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.calculator = GematriaCalculator()
        self.word_repository = WordRepository()
        self.content_layout = QVBoxLayout(self)
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        # Main layout with spacing and margins
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
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
                color: #2c3e50;
            }
        """)
        
        # Improve text input appearance
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to calculate...")
        self.text_input.setMinimumHeight(100)
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background-color: #ffffff;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        # Cipher selection with label
        cipher_layout = QHBoxLayout()
        cipher_label = QLabel("Select Cipher:")
        self.cipher_select = QComboBox()
        self.cipher_select.addItems([
            'TQ English',
            'Hebrew Standard',
            'Hebrew Gadol',
            'Greek'
        ])
        self.cipher_select.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        cipher_layout.addWidget(cipher_label)
        cipher_layout.addWidget(self.cipher_select)
        cipher_layout.addStretch()
        
        # Results section with better styling
        results_section = QWidget()
        results_section.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        results_layout = QHBoxLayout(results_section)
        
        value_section = QVBoxLayout()
        self.value_label = QLabel("Calculated Value")
        self.value_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.value_display = QLabel("0")
        self.value_display.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2980b9;
            padding: 10px;
        """)
        value_section.addWidget(self.value_label)
        value_section.addWidget(self.value_display)
        
        # Button styling
        button_style = """
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
        """
        
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #2980b9;
                color: white;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        self.import_button = QPushButton("Import")
        self.import_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f39c12;
                color: white;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
        """)
        
        # Add everything to layouts
        input_layout.addWidget(input_header)
        input_layout.addWidget(self.text_input)
        input_layout.addLayout(cipher_layout)
        
        results_layout.addLayout(value_section)
        results_layout.addStretch()
        results_layout.addWidget(self.calculate_button)
        results_layout.addWidget(self.save_button)
        results_layout.addWidget(self.import_button)
        
        self.content_layout.addWidget(input_section)
        self.content_layout.addWidget(results_section)
        self.content_layout.addStretch()

    def connect_signals(self):
        self.calculate_button.clicked.connect(self.calculate_value)
        self.save_button.clicked.connect(self.save_word)
        self.import_button.clicked.connect(self.import_csv)

    def calculate_value(self):
        text = self.text_input.toPlainText()
        cipher = self.cipher_select.currentText()
        value = self.calculator.calculate(text, cipher)
        self.value_display.setText(str(value))
        if text.strip():
            self.word_repository.add_to_history(text, cipher, value)

    def save_word(self):
        text = self.text_input.toPlainText()
        cipher = self.cipher_select.currentText()
        value = int(self.value_display.text())
        
        if not text.strip():
            QMessageBox.warning(self, "Error", "Please enter text to save.")
            return
        
        # Check if word exists
        if self.word_repository.word_exists(text, cipher):
            QMessageBox.information(
                self, 
                "Duplicate Entry", 
                f"'{text}' already exists in the database with cipher {cipher}."
            )
            return
        
        # Save if it's new
        self.word_repository.save_word(text, cipher, value)
        QMessageBox.information(self, "Success", "Word saved successfully!")

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import File", "", "Files (*.csv *.xlsx *.xls)")
        
        if file_path:
            cipher_dialog = QDialog(self)
            cipher_dialog.setWindowTitle("Select Cipher Type")
            layout = QVBoxLayout()
            
            cipher_combo = QComboBox()
            cipher_combo.addItems([
                'TQ English',
                'Hebrew Standard',
                'Hebrew Gadol',
                'Greek'
            ])
            
            confirm_button = QPushButton("Import")
            
            layout.addWidget(QLabel("Select cipher type for import:"))
            layout.addWidget(cipher_combo)
            layout.addWidget(confirm_button)
            
            cipher_dialog.setLayout(layout)
            
            def do_import():
                cipher_type = cipher_combo.currentText()
                if file_path.endswith('.csv'):
                    self.import_csv_file(file_path, cipher_type)
                else:
                    self.import_excel_file(file_path, cipher_type)
                cipher_dialog.accept()
            
            confirm_button.clicked.connect(do_import)
            cipher_dialog.exec()

    def import_csv_file(self, file_path, cipher_type):
        try:
            duplicates = []
            imported = 0
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip header row
                for row in csv_reader:
                    if len(row) >= 2:
                        text = row[0]
                        value = int(row[1])
                        
                        if not self.word_repository.word_exists(text, cipher_type):
                            self.word_repository.save_word(text, cipher_type, value)
                            imported += 1
                        else:
                            duplicates.append(text)
            
            # Show results
            message = f"Successfully imported {imported} entries."
            if duplicates:
                message += f"\n\nSkipped {len(duplicates)} duplicate entries:"
                message += f"\n{', '.join(duplicates[:5])}"
                if len(duplicates) > 5:
                    message += f"... and {len(duplicates) - 5} more"
            
            QMessageBox.information(self, "Import Results", message)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to import CSV: {str(e)}")

    def import_excel_file(self, file_path, cipher_type):
        try:
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            for row in sheet.iter_rows(min_row=2):  # Skip header row
                if len(row) >= 2 and row[0].value and row[1].value:
                    text = str(row[0].value)
                    value = int(float(row[1].value))
                    self.word_repository.save_word(text, cipher_type, value)
            QMessageBox.information(self, "Success", "Excel data imported successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to import Excel: {str(e)}")
