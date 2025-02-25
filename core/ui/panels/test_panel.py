"""
Test Panel for development
"""
from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import Qt
from ..base.panel import BasePanel

class TestPanel(BasePanel):
    """A test panel to demonstrate panel functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent, title="Test Panel")
    
    def setup_ui(self):
        """Set up the test panel UI"""
        label = QLabel("This is a test panel!")
        self.layout.addWidget(label)
        
        float_btn = QPushButton("Float Me!")
        float_btn.clicked.connect(self.on_float_clicked)
        self.layout.addWidget(float_btn)
        
        self.layout.addStretch()
    
    def get_preferred_area(self) -> Qt.DockWidgetArea:
        return Qt.DockWidgetArea.LeftDockWidgetArea
    
    def get_preferred_size(self) -> tuple:
        return (250, 300)
    
    def on_float_clicked(self):
        """Handle float button click"""
        if parent := self.parent():
            if hasattr(parent, 'setFloating'):
                parent.setFloating(True)
