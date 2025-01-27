from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QSpinBox, QCheckBox,
                            QColorDialog, QFontDialog, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class GridPanelProperties(QDialog):
    propertiesChanged = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grid Properties")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.setup_connections()
        
        # Initialize with current properties if parent exists
        if parent and hasattr(parent, 'current_properties'):
            self.initialize_values(parent.current_properties)

    def initialize_values(self, current_properties):
        # Set initial values based on current properties
        self.cell_width.setValue(current_properties['cell_width'])
        self.cell_height.setValue(current_properties['cell_height'])
        self.line_thickness.setValue(current_properties['line_thickness'])
        self.line_color = QColor(current_properties['line_color'])
        self.bg_color = QColor(current_properties['bg_color'])
        self.text_color = QColor(current_properties['text_color'])
        self.square_cells.setChecked(current_properties.get('square_cells', False))
        self.auto_fit.setChecked(current_properties.get('auto_fit', False))      

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Cell Size Group
        size_group = QGroupBox("Cell Size")
        cell_size_layout = QHBoxLayout()
        self.cell_width = QSpinBox()
        self.cell_height = QSpinBox()
        self.cell_width.setRange(20, 200)
        self.cell_height.setRange(20, 200)
        cell_size_layout.addWidget(QLabel("Width:"))
        cell_size_layout.addWidget(self.cell_width)
        cell_size_layout.addWidget(QLabel("Height:"))
        cell_size_layout.addWidget(self.cell_height)
        size_group.setLayout(cell_size_layout)
        
        # Visual Properties Group
        visual_group = QGroupBox("Visual Properties")
        visual_layout = QVBoxLayout()
        
        # Line properties
        line_layout = QHBoxLayout()
        self.line_thickness = QSpinBox()
        self.line_thickness.setRange(1, 5)
        line_layout.addWidget(QLabel("Line Thickness:"))
        line_layout.addWidget(self.line_thickness)
        
        # Color buttons
        self.line_color_btn = QPushButton("Grid Line Color")
        self.bg_color_btn = QPushButton("Background Color")
        self.text_color_btn = QPushButton("Text Color")
        
        # Store colors
        self.line_color = QColor(Qt.black)
        self.bg_color = QColor(Qt.white)
        self.text_color = QColor(Qt.black)
        
        visual_layout.addLayout(line_layout)
        visual_layout.addWidget(self.line_color_btn)
        visual_layout.addWidget(self.bg_color_btn)
        visual_layout.addWidget(self.text_color_btn)
        visual_group.setLayout(visual_layout)
        
        # Options Group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        self.square_cells = QCheckBox("Square Cells")
        self.auto_fit = QCheckBox("Auto-fit Content")
        options_layout.addWidget(self.square_cells)
        options_layout.addWidget(self.auto_fit)
        options_group.setLayout(options_layout)
        
        # Add all groups to main layout
        layout.addWidget(size_group)
        layout.addWidget(visual_group)
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def setup_connections(self):
        self.apply_btn.clicked.connect(self.apply_properties)
        self.cancel_btn.clicked.connect(self.reject)
        self.square_cells.toggled.connect(self.handle_square_cells)
        self.line_color_btn.clicked.connect(self.choose_line_color)
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        self.text_color_btn.clicked.connect(self.choose_text_color)
        
    def choose_line_color(self):
        color = QColorDialog.getColor(self.line_color, self)
        if color.isValid():
            self.line_color = color
            
    def choose_bg_color(self):
        color = QColorDialog.getColor(self.bg_color, self)
        if color.isValid():
            self.bg_color = color
            
    def choose_text_color(self):
        color = QColorDialog.getColor(self.text_color, self)
        if color.isValid():
            self.text_color = color
            
    def apply_properties(self):
        properties = {
            'cell_width': self.cell_width.value(),
            'cell_height': self.cell_height.value(),
            'square_cells': self.square_cells.isChecked(),
            'auto_fit': self.auto_fit.isChecked(),
            'line_thickness': self.line_thickness.value(),
            'line_color': self.line_color.name(),
            'bg_color': self.bg_color.name(),
            'text_color': self.text_color.name()
        }
        self.propertiesChanged.emit(properties)
        self.accept()
        
    def handle_square_cells(self, checked):
        if checked:
            self.cell_height.setValue(self.cell_width.value())
            self.cell_height.setEnabled(False)
        else:
            self.cell_height.setEnabled(True)