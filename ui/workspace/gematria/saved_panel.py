from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, 
                            QPushButton, QHBoxLayout, QLabel,
                            QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from core.database.word_repository import WordRepository
from core.gematria.cipher_manager import CipherManager

class SavedPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.word_repository = WordRepository()
        self.cipher_manager = CipherManager()
        self.init_ui()
        self.load_ciphers()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Search Saved Calculations")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        # Search section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter text or value...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        # Add cipher filter dropdown
        self.cipher_filter = QComboBox()
        self.cipher_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 150px;
            }
        """)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.cipher_filter)
        search_layout.addWidget(self.search_btn)
        
        # Add to main layout
        layout.addWidget(header)
        layout.addLayout(search_layout)
        layout.addStretch()
        
        self.setLayout(layout)

    def load_ciphers(self):
        """Load all available ciphers into the filter dropdown"""
        # Clear and add "All Ciphers" option
        self.cipher_filter.clear()
        self.cipher_filter.addItem("All Ciphers")
        
        # Add built-in ciphers
        built_in_ciphers = [
            'TQ English',
            'Hebrew Standard',
            'Hebrew Gadol',
            'Greek'
        ]
        self.cipher_filter.addItems(built_in_ciphers)
        
        # Add separator and custom ciphers
        if self.cipher_manager.get_cipher_names():
            self.cipher_filter.insertSeparator(len(built_in_ciphers) + 1)
            for cipher_name in self.cipher_manager.get_cipher_names():
                self.cipher_filter.addItem(f"Custom: {cipher_name}")

    def perform_search(self):
        search_text = self.search_input.text().strip()
        selected_cipher = self.cipher_filter.currentText()
        
        if not search_text:
            QMessageBox.information(self, "Search", "Please enter a search term")
            return

        # Get search results based on cipher filter
        if selected_cipher == "All Ciphers":
            results = self.word_repository.search_words(search_text)
        else:
            results = self.word_repository.search_words_by_cipher(search_text, selected_cipher)

        print(f"DEBUG: Found {len(results)} results in database")  # Debug print

        if not results:
            QMessageBox.information(self, "Search", "No matching entries found")
            return

        # Find main window
        main_window = None
        widget = self
        while widget.parent():
            widget = widget.parent()
            if hasattr(widget, 'panel_manager'):
                main_window = widget
                break

        if main_window:
            print(f"DEBUG: Found main window, storing results")  # Debug print
            # Store results and create results panel
            main_window.search_results = {
                'results': results,
                'search_term': search_text,
                'cipher_filter': selected_cipher
            }
            panel = main_window.panel_manager.create_panel('search_results')
            print(f"DEBUG: Panel created: {panel is not None}")  # Debug print
        else:
            print("DEBUG: Could not find main window!")  # Debug print
            QMessageBox.warning(self, "Error", "Could not create results panel")