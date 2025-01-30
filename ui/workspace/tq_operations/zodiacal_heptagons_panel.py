from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class ZodiacalHeptagonsPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Zodiacal Heptagons Panel - Coming Soon"))
        self.setLayout(layout) 