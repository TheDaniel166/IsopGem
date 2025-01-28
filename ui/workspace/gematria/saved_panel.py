from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, 
                            QPushButton, QHBoxLayout, QLabel,
                            QMessageBox)
from PyQt5.QtCore import Qt
from core.database.word_repository import WordRepository

class SavedPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.word_repository = WordRepository()
        self.init_ui()

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
        self.search_input.setPlaceholderText("Enter text, value, or cipher type...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        
        # Add to main layout
        layout.addWidget(header)
        layout.addLayout(search_layout)
        layout.addStretch()
        
        self.setLayout(layout)

    def perform_search(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.information(self, "Search", "Please enter a search term")
            return

        # Get search results
        results = self.word_repository.search_words(search_text)
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
                'search_term': search_text
            }
            panel = main_window.panel_manager.create_panel('search_results')
            print(f"DEBUG: Panel created: {panel is not None}")  # Debug print
        else:
            print("DEBUG: Could not find main window!")  # Debug print
            QMessageBox.warning(self, "Error", "Could not create results panel")