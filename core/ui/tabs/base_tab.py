"""
Base tab implementation
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class BaseTab(QWidget):
    """Base class for all tabs in the application"""
    
    # Tab metadata - override in child classes
    tab_name = "Untitled"  # Display name
    tab_order = 100      # Tab order (lower numbers first)
    tab_icon = None       # Optional icon path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Set up the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tab UI - override in child classes"""
        pass
