from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QPushButton, QComboBox,
                            QLabel, QDialog, QTextEdit, QMessageBox,
                            QFrame, QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt
from core.database.word_repository import WordRepository

class SearchPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.word_repository = WordRepository()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Gematria Value Search")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """)
        layout.addWidget(header)
        
        # Search panel
        search_panel = QFrame()
        search_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        
        search_layout = QGridLayout(search_panel)
        search_layout.setSpacing(10)
        
        # Value input
        value_label = QLabel("Value:")
        value_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value to search...")
        self.value_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        # Cipher selection
        cipher_label = QLabel("Cipher:")
        cipher_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.cipher_select = QComboBox()
        self.cipher_select.addItems([
            'Global',
            'TQ English',
            'Hebrew Standard',
            'Hebrew Gadol',
            'Greek'
        ])
        self.cipher_select.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #2980b9;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        
        # Add widgets to search layout
        search_layout.addWidget(value_label, 0, 0)
        search_layout.addWidget(self.value_input, 0, 1)
        search_layout.addWidget(cipher_label, 1, 0)
        search_layout.addWidget(self.cipher_select, 1, 1)
        search_layout.addWidget(self.search_button, 2, 0, 1, 2, Qt.AlignCenter)
        
        layout.addWidget(search_panel)
        layout.addStretch()
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
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Results")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel(f"Results for Value: {self.value_input.text()}")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: white;
                border-radius: 5px;
            }
        """)
        layout.addWidget(header)
        
        # Results scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setSpacing(10)
        
        for word, cipher_type in results:
            result_frame = QFrame()
            result_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 5px;
                    border: 1px solid #e0e0e0;
                    padding: 10px;
                }
                QFrame:hover {
                    border-color: #3498db;
                }
            """)
            
            result_layout = QVBoxLayout(result_frame)
            
            word_label = QLabel(word)
            word_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
            word_label.setWordWrap(True)
            
            cipher_label = QLabel(cipher_type)
            cipher_label.setStyleSheet("""
                font-size: 12px;
                color: #16a085;
                background-color: #e8f6f3;
                padding: 4px 8px;
                border-radius: 4px;
            """)
            
            result_layout.addWidget(word_label)
            result_layout.addWidget(cipher_label)
            results_layout.addWidget(result_frame)
        
        scroll.setWidget(results_widget)
        layout.addWidget(scroll)
        
        dialog.setLayout(layout)
        dialog.exec()
