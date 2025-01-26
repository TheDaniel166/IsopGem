from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton


class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # View Options group
        view_group = QGroupBox("View")
        view_layout = QVBoxLayout()
        view_group.setLayout(view_layout)
        view_layout.addWidget(QPushButton("Full Screen"))
        view_layout.addWidget(QPushButton("Zoom In"))
        view_layout.addWidget(QPushButton("Zoom Out"))
        
        # Tools group
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout()
        tools_group.setLayout(tools_layout)
        tools_layout.addWidget(QPushButton("Settings"))
        tools_layout.addWidget(QPushButton("Templates"))
        
        # Add groups to layout
        layout.addWidget(view_group)
        layout.addWidget(tools_group)
        self.setLayout(layout)
