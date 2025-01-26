from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton


class FileTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # File Operations group
        file_group = QGroupBox("File Operations")
        file_layout = QVBoxLayout()
        file_group.setLayout(file_layout)
        
        # Add buttons
        file_layout.addWidget(QPushButton("New"))
        file_layout.addWidget(QPushButton("Open"))
        file_layout.addWidget(QPushButton("Save"))
        file_layout.addWidget(QPushButton("Save As"))
        file_layout.addWidget(QPushButton("Export"))
        
        layout.addWidget(file_group)
        self.setLayout(layout)
