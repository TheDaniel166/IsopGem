from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class KameaBafometPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Kamea of Bafomet Panel - Coming Soon"))
        self.setLayout(layout) 