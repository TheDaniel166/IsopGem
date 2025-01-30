from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class KameaCreatorPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Kamea Creator Panel - Coming Soon"))
        self.setLayout(layout) 