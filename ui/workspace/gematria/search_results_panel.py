from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                            QPushButton, QFrame, QHBoxLayout, QMessageBox,
                            QApplication, QMainWindow)
from PyQt5.QtCore import Qt
from core.document_editor.editor import DocumentEditor

class SearchResultsPanel(QWidget):
    def __init__(self, search_data=None):
        super().__init__()
        print("DEBUG: Initializing SearchResultsPanel")
        
        if search_data:
            print(f"DEBUG: Received search data with {len(search_data['results'])} results")
            self.results = search_data['results']
            self.search_term = search_data['search_term']
            self.init_ui()
        else:
            print("DEBUG: No search data provided")
            self.init_empty_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Add header with result count
        header = QLabel(f"Search Results for '{self.search_term}' ({len(self.results)} found)")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        layout.addWidget(header)
        
        # Add toolbar
        toolbar = QHBoxLayout()
        export_btn = QPushButton("Export to Editor")
        export_btn.clicked.connect(self.export_to_editor)
        toolbar.addWidget(export_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Results area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        results_layout = QVBoxLayout(container)
        results_layout.setSpacing(8)
        
        for text, cipher_type, value in self.results:
            item = self.create_result_item(text, cipher_type, value)
            results_layout.addWidget(item)
            
        results_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
    def create_result_item(self, text, cipher_type, value):
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #3498db;
            }
        """)
        
        layout = QVBoxLayout(item)
        
        # Text row with copy button
        text_row = QHBoxLayout()
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        
        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(30, 30)
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(text))
        
        text_row.addWidget(text_label, stretch=1)
        text_row.addWidget(copy_btn)
        
        # Info row
        info_row = QHBoxLayout()
        value_label = QLabel(f"Value: {value}")
        value_label.setStyleSheet("font-weight: bold;")
        
        cipher_label = QLabel(cipher_type)
        cipher_label.setStyleSheet("""
            background: #e8f6f3;
            color: #16a085;
            padding: 3px 8px;
            border-radius: 3px;
        """)
        
        info_row.addWidget(value_label)
        info_row.addStretch()
        info_row.addWidget(cipher_label)
        
        layout.addLayout(text_row)
        layout.addLayout(info_row)
        return item
        
    def copy_to_clipboard(self, text):
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Text copied to clipboard!")
        
    def export_to_editor(self):
        text = f"Search Results for '{self.search_term}'\n" + "=" * 20 + "\n\n"
        for text_val, cipher, value in self.results:
            text += f"Text: {text_val}\n"
            text += f"Cipher: {cipher}\n"
            text += f"Value: {value}\n"
            text += "-" * 40 + "\n\n"
        
        editor = DocumentEditor()
        editor.editor.setText(text)
        editor.show()

    def init_empty_ui(self):
        """Initialize UI with a message when no results are available"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        message = QLabel("No search results available")
        message.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 20px;
                font-style: italic;
            }
        """)
        message.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(message)
        layout.addStretch() 