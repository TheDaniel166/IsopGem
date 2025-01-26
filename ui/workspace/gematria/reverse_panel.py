from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class ReversePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Placeholder header
        header = QLabel("Reverse Calculate")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        layout.addWidget(header)
        self.setLayout(layout)
