from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTextEdit, QFileDialog, QWidget)
import numpy as np
from ui.workspace.gematria.grid.grid_panel import GridPanel

class TextAnalysisRow(QWidget):
    def __init__(self, option_name, text):
        super().__init__()
        self.text = text
        self.char_count = len(text)
        self.option_name = option_name
        self.layout = QHBoxLayout()
        self.grid_windows = []
        
        # Option label and character count
        self.label = QLabel(f"{option_name} ({self.char_count} chars)")
        self.layout.addWidget(self.label)
        
        # Container for grid buttons
        self.button_container = QHBoxLayout()
        self.layout.addLayout(self.button_container)
        
        self.setLayout(self.layout)

    def update_grid_buttons(self, factors):
        # Clear existing buttons
        for i in reversed(range(self.button_container.count())):
            self.button_container.itemAt(i).widget().deleteLater()

        # Create vertical layout to hold rows of buttons
        button_rows_layout = QVBoxLayout()
        current_row_layout = QHBoxLayout()
        button_count = 0
        
        for rows, cols in factors:
            btn = QPushButton(f"{rows}x{cols}")
            if self.is_square_grid(rows, cols):
                btn.setStyleSheet("background-color: #ADD8E6")
            elif self.is_golden_ratio(rows, cols):
                btn.setStyleSheet("background-color: #90EE90")
            btn.clicked.connect(lambda checked, r=rows, c=cols: self.create_grid(r, c))
            
            current_row_layout.addWidget(btn)
            button_count += 1
            
            # Start new row after 10 buttons
            if button_count % 10 == 0:
                button_rows_layout.addLayout(current_row_layout)
                current_row_layout = QHBoxLayout()
        
        # Handle last row
        if button_count % 10 != 0:
            # Center align last row
            current_row_layout.addStretch()
            current_row_layout.addStretch()
            button_rows_layout.addLayout(current_row_layout)
            
        self.button_container.addLayout(button_rows_layout)

            
    def is_square_grid(self, rows, cols):
        return rows == cols
        
    def is_golden_ratio(self, rows, cols):
        ratio = max(rows, cols) / min(rows, cols)
        return abs(ratio - 1.618) < 0.1  # Approximate golden ratio

    def create_grid(self, rows, cols):
        grid_window = GridPanel(self.text, rows, cols, self.option_name)
        self.grid_windows.append(grid_window)
        grid_window.show()

class GridConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Configuration")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        self.setup_ui()

        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)  # Add some padding
        layout.setSpacing(10)  # Space between widgets
        
        # Text input section with controlled height
        self.text_display = QTextEdit()
        self.text_display.setMinimumHeight(150)
        self.text_display.textChanged.connect(self.analyze_text)
        
        # Import button styling
        self.import_button = QPushButton("Import Text")
        self.import_button.setMinimumWidth(120)
        self.import_button.clicked.connect(self.import_text_file)
        
        # Analysis rows container with scroll area potential
        self.analysis_container = QVBoxLayout()
        self.analysis_container.setSpacing(5)
        
        # Add all to main layout
        layout.addWidget(QLabel("Enter or Import Text:"))
        layout.addWidget(self.text_display)
        layout.addWidget(self.import_button)
        layout.addLayout(self.analysis_container)
        
        self.setLayout(layout)

        
    def import_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Import Text File", 
            "", 
            "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        self.text_display.setText(f.read())
                    break
                except UnicodeDecodeError:
                    continue
                
    def analyze_text(self):
        text = self.text_display.toPlainText()
        if not text:
            return
            
        # Clear previous analysis rows
        self.clear_analysis_rows()
        
        # Create analysis rows for each text processing option
        self.add_analysis_row("Keep All", text)
        self.add_analysis_row("No Spaces", text.replace(' ', ''))
        self.add_analysis_row("No Punctuation", 
                            ''.join(c for c in text if c.isalnum() or c.isspace()))
        self.add_analysis_row("No Spaces or Punctuation", 
                            ''.join(c for c in text if c.isalnum()))
                            
    def add_analysis_row(self, option_name, processed_text):
        row = TextAnalysisRow(option_name, processed_text)
        factors = self.calculate_grid_factors(len(processed_text))
        row.update_grid_buttons(factors)
        self.analysis_container.addWidget(row)

    def clear_analysis_rows(self):
        while self.analysis_container.count():
            item = self.analysis_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        
    def calculate_grid_factors(self, text_length):
        factors = []
        sqrt_length = int(np.sqrt(text_length))
        
        # Get all factor pairs
        for i in range(1, sqrt_length + 1):
            if text_length % i == 0:
                rows, cols = i, text_length // i
                factors.append((rows, cols))
                if rows != cols:
                    factors.append((cols, rows))
                    
        # Sort factors by aspect ratio closest to square
        factors.sort(key=lambda x: abs(x[0] - x[1]))
        
        # Check for special arrangements
        if self.is_triangular_number(text_length):
            k = int(np.sqrt(2 * text_length))
            factors.append((k, k+1))  # Triangular arrangement
            
        if self.is_centered_polygonal(text_length, 6):  # Hexagonal check
            factors.append(('hexagonal', text_length))
            
        return factors
        
    def is_triangular_number(self, n):
        k = int(np.sqrt(2 * n))
        return k * (k + 1) // 2 == n
        
    def is_centered_polygonal(self, n, sides):
        k = 1
        while True:
            value = 1 + sides * (k * (k-1) // 2)
            if value == n:
                return True
            if value > n:
                return False
            k += 1