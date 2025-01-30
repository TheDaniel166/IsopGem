from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class KameaMautPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Kamea of Ma'ut Panel - Coming Soon"))
        self.setLayout(layout) 