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
        # Input section with text area and cipher selection
        input_layout = QHBoxLayout()
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to calculate...")
        self.cipher_select = QComboBox()
        self.cipher_select.addItems([
            'TQ English',
            'Hebrew Standard',
            'Hebrew Gadol',
            'Greek'
        ])
        
        input_layout.addWidget(self.text_input, stretch=3)
        input_layout.addWidget(self.cipher_select, stretch=1)
        
        # Results section
        results_layout = QHBoxLayout()
        self.value_label = QLabel("Value:")
        self.value_display = QLabel("0")
        self.value_display.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.calculate_button = QPushButton("Calculate")
        self.save_button = QPushButton("Save")
        self.import_button = QPushButton("Import File")
        
        results_layout.addWidget(self.value_label)
        results_layout.addWidget(self.value_display)
        results_layout.addStretch()
        results_layout.addWidget(self.calculate_button)
        results_layout.addWidget(self.save_button)
        results_layout.addWidget(self.import_button)
        
        # Add layouts to content_layout once
        self.content_layout.addLayout(input_layout)
        self.content_layout.addLayout(results_layout)


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
        if text.strip():
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
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip header row
                for row in csv_reader:
                    if len(row) >= 2:
                        text = row[0]
                        value = int(row[1])
                        self.word_repository.save_word(text, cipher_type, value)
            QMessageBox.information(self, "Success", "CSV data imported successfully!")
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
