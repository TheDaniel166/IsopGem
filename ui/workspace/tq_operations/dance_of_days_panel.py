from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class DanceOfDaysPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Dance of Days Panel - Coming Soon"))
        self.setLayout(layout) 