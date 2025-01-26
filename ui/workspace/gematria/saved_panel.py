from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                              QLabel, QPushButton)
from core.database.word_repository import WordRepository

class SavedPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.word_repository = WordRepository()
        self.init_ui()
        self.load_saved_words()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Saved Calculations")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # Display area
        self.saved_text = QTextEdit()
        self.saved_text.setReadOnly(True)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_saved_words)
        
        layout.addWidget(header)
        layout.addWidget(self.saved_text)
        layout.addWidget(self.refresh_btn)
        self.setLayout(layout)

    def load_saved_words(self):
        saved_words = self.word_repository.get_saved_words()
        self.saved_text.clear()
        
        for text, cipher_type, value in saved_words:
            entry = (f"Text: {text}\n"
                    f"Cipher: {cipher_type}\n"
                    f"Value: {value}\n"
                    f"{'-' * 40}\n")
            self.saved_text.append(entry)