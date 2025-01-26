from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QComboBox, QPushButton, QSpinBox)

class GridPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Text input area for source text
        self.text_input = QTextEdit()
        
        # Grid control section with horizontal layout
        controls_layout = QHBoxLayout()
        
        # Text format selection dropdown
        self.text_format = QComboBox()
        self.text_format.addItems([
            "Full Text",
            "Without Punctuation",
            "Without Spaces",
            "Without Punctuation and Spaces"
        ])
        
        # Grid size control
        self.grid_size = QSpinBox()
        
        # Grid creation button
        self.create_grid_btn = QPushButton("Create Grid")
        
        # Add controls to horizontal layout
        controls_layout.addWidget(self.text_format)
        controls_layout.addWidget(self.grid_size)
        controls_layout.addWidget(self.create_grid_btn)
        
        # Grid display area
        self.grid_display = QWidget()
        
        # Assemble main layout
        layout.addWidget(self.text_input)
        layout.addLayout(controls_layout)
        layout.addWidget(self.grid_display)
        self.setLayout(layout)
