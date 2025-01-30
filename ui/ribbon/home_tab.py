from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPushButton
)

class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Main horizontal layout
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # File Operations group
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout()
        file_layout.setSpacing(2)
        file_layout.setContentsMargins(2, 2, 2, 2)
        
        file_layout.addWidget(QPushButton("New"))
        file_layout.addWidget(QPushButton("Open"))
        file_layout.addWidget(QPushButton("Save"))
        file_layout.addWidget(QPushButton("Save As"))
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # View Options group
        view_group = QGroupBox("View")
        view_layout = QVBoxLayout()
        view_layout.setSpacing(2)
        view_layout.setContentsMargins(2, 2, 2, 2)
        
        view_layout.addWidget(QPushButton("Full Screen"))
        view_layout.addWidget(QPushButton("Zoom In"))
        view_layout.addWidget(QPushButton("Zoom Out"))
        view_group.setLayout(view_layout)
        layout.addWidget(view_group)
        
        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(2)
        settings_layout.setContentsMargins(2, 2, 2, 2)
        
        settings_layout.addWidget(QPushButton("Preferences"))
        settings_layout.addWidget(QPushButton("Templates"))
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Add stretch at the end
        layout.addStretch()
        self.setLayout(layout)
