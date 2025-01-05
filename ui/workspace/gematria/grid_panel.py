from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                              QTextEdit, QComboBox, QPushButton, QSpinBox)

class GridPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Text input and options
        self.text_input = QTextEdit()
        
        # Grid controls
        controls_layout = QHBoxLayout()
        self.text_format = QComboBox()
        self.text_format.addItems([
            "Full Text",
            "Without Punctuation",
            "Without Spaces",
            "Without Punctuation and Spaces"
        ])
        self.grid_size = QSpinBox()
        self.create_grid_btn = QPushButton("Create Grid")
        
        controls_layout.addWidget(self.text_format)
        controls_layout.addWidget(self.grid_size)
        controls_layout.addWidget(self.create_grid_btn)
        
        # Grid display area
        self.grid_display = QWidget()
        
        layout.addWidget(self.text_input)
        layout.addLayout(controls_layout)
        layout.addWidget(self.grid_display)
        self.setLayout(layout)
