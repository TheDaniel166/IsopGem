"""
Base Tab implementation for IsopGem's tab management system
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout

class BaseTab(QWidget):
    """Base class for all application tabs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(4)
        
    def setup_ui(self):
        """Set up the tab's UI components"""
        raise NotImplementedError("Tabs must implement setup_ui method")
