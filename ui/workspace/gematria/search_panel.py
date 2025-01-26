from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QPushButton, QComboBox,
                            QLabel, QDialog, QTextEdit, QMessageBox)
from core.database.word_repository import WordRepository

class SearchPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.word_repository = WordRepository()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Search input section with horizontal layout
        search_layout = QHBoxLayout()
        
        # Initialize input widgets
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value to search...")
        
        self.cipher_select = QComboBox()
        self.cipher_select.addItems([
            'Global',
            'TQ English',
            'Hebrew Standard',
            'Hebrew Gadol',
            'Greek'
        ])
        
        self.search_button = QPushButton("Search")
        
        # Add widgets to search layout
        search_layout.addWidget(self.value_input)
        search_layout.addWidget(self.cipher_select)
        search_layout.addWidget(self.search_button)
        
        # Add search layout to main layout
        layout.addLayout(search_layout)
        self.setLayout(layout)

    def connect_signals(self):
        # Connect search button click to search function
        self.search_button.clicked.connect(self.search_value)

    def search_value(self):
        try:
            search_value = int(self.value_input.text())
            selected_cipher = self.cipher_select.currentText()
            
            # Perform search based on cipher selection
            if selected_cipher == 'Global':
                results = self.word_repository.find_by_value_global(search_value)
            else:
                results = self.word_repository.find_by_value(search_value, selected_cipher)
            
            self.show_search_results(results)
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid number")

    def show_search_results(self, results):
        if not results:
            QMessageBox.information(self, "Search Results", "No matches found")
            return
        
        # Create results dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Search Results for Value: {self.value_input.text()}")
        layout = QVBoxLayout()
        
        # Create and configure results display
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        result_text.append(f"Words/Phrases with value {self.value_input.text()}:\n")
        
        # Add results to display
        for word, cipher_type in results:
            result_text.append(f"• {word} ({cipher_type})")
        
        layout.addWidget(result_text)
        dialog.setLayout(layout)
        dialog.exec()
