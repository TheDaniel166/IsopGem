from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from core.database.word_repository import WordRepository

class HistoryPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.word_repository = WordRepository()
        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Add header
        header = QLabel("Recent Calculations (Last 20)")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        self.setLayout(layout)

    def load_history(self):
        history = self.word_repository.get_history(limit=20)
        self.history_text.clear()
        
        for text, cipher_type, value, timestamp in history:
            entry = (f"Time: {timestamp}\n"
                    f"Text: {text}\n"
                    f"Cipher: {cipher_type}\n"
                    f"Value: {value}\n"
                    f"{'-' * 40}\n")
            self.history_text.append(entry)
