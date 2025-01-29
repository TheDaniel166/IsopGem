from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class SeriesTransitionsPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Series Transitions Panel - Coming Soon"))
        self.setLayout(layout) 