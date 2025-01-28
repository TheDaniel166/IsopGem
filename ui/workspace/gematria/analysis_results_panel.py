from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QLabel, 
                            QPushButton, QFrame, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from core.document_editor.editor import DocumentEditor

class AnalysisResultsPanel(QWidget):
    def __init__(self, results_data=None):
        super().__init__()
        print("DEBUG: Initializing AnalysisResultsPanel")
        
        if results_data:
            print(f"DEBUG: Received {len(results_data['results'])} results")
            self.results = results_data['results']
            self.target_value = results_data['target_value']
            self.cipher = results_data['cipher']
            self.mode = results_data['mode']
            self.init_ui()
        else:
            print("DEBUG: No results data provided")
            self.init_empty_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel(f"Analysis Results - {self.mode} Mode")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        layout.addWidget(header)
        
        # Info section
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Target Value: {self.target_value}"))
        info_layout.addWidget(QLabel(f"Cipher: {self.cipher}"))
        info_layout.addWidget(QLabel(f"Found: {len(self.results)} matches"))
        layout.addLayout(info_layout)
        
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
        
        for result in self.results:
            item = self.create_result_item(result)
            results_layout.addWidget(item)
            
        results_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
    def create_result_item(self, result):
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
        text_label = QLabel(result['phrase'])
        text_label.setWordWrap(True)
        
        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(30, 30)
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(result['phrase']))
        
        text_row.addWidget(text_label, stretch=1)
        text_row.addWidget(copy_btn)
        
        layout.addLayout(text_row)
        return item
        
    def copy_to_clipboard(self, text):
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Text copied to clipboard!")
        
    def export_to_editor(self):
        text = f"Analysis Results ({self.mode} Mode)\n" + "=" * 20 + "\n\n"
        text += f"Target Value: {self.target_value}\n"
        text += f"Cipher: {self.cipher}\n"
        text += f"Total Matches: {len(self.results)}\n\n"
        
        for result in self.results:
            text += f"Phrase: {result['phrase']}\n"
            text += f"Value: {result['value']}\n"
            text += "-" * 40 + "\n\n"
        
        editor = DocumentEditor()
        editor.editor.setText(text)
        editor.show()

    def init_empty_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        message = QLabel("No analysis results available")
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