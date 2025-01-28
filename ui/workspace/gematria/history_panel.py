from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, 
                            QScrollArea, QFrame, QGridLayout)
from PyQt5.QtCore import Qt
from core.database.word_repository import WordRepository
from datetime import datetime

class HistoryPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.word_repository = WordRepository()
        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        header = QLabel("Calculation History (Last 25)")
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
        
        # Scroll area for history entries
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Container for history entries
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setSpacing(10)
        self.history_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.history_container)
        
        layout.addWidget(scroll)
        self.setLayout(layout)

    def create_entry_widget(self, text, cipher_type, value, timestamp):
        entry = QFrame()
        entry.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 10px;
            }
            QFrame:hover {
                border: 1px solid #3498db;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
        layout = QGridLayout(entry)
        layout.setSpacing(8)
        
        # Format timestamp
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        formatted_time = dt.strftime("%b %d, %Y %I:%M %p")
        
        # Time label with icon-like prefix
        time_label = QLabel(f"🕒 {formatted_time}")
        time_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        
        # Value with highlighted background
        value_widget = QFrame()
        value_widget.setStyleSheet("""
            QFrame {
                background-color: #f0f7ff;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        value_layout = QVBoxLayout(value_widget)
        value_layout.setContentsMargins(5, 5, 5, 5)
        value_label = QLabel(f"Value: {value}")
        value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980b9;")
        value_layout.addWidget(value_label)
        
        # Text content
        text_label = QLabel(f"Text: {text}")
        text_label.setWordWrap(True)
        text_label.setStyleSheet("font-size: 14px;")
        
        # Cipher type with badge-like styling
        cipher_label = QLabel(cipher_type)
        cipher_label.setStyleSheet("""
            QLabel {
                background-color: #e8f6f3;
                color: #16a085;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(time_label, 0, 0, 1, 2)
        layout.addWidget(text_label, 1, 0, 1, 2)
        layout.addWidget(cipher_label, 2, 0)
        layout.addWidget(value_widget, 2, 1)
        
        return entry

    def load_history(self):
        # Clear existing entries
        while self.history_layout.count():
            child = self.history_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Load new entries with limit=25
        history = self.word_repository.get_history(limit=25)
        for text, cipher_type, value, timestamp in history:
            entry_widget = self.create_entry_widget(text, cipher_type, value, timestamp)
            self.history_layout.addWidget(entry_widget)
        
        # Add stretch at the end
        self.history_layout.addStretch()
