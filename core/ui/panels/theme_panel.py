"""
Theme customization panel
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from ..widgets.theme_customizer import ThemeCustomizer
from .base_panel import BasePanel

class ThemePanel(BasePanel):
    """Panel for theme customization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Customization")
        self._setup_ui()
        
        # Set fixed size and position
        self.setFixedSize(1200, 700)
        self.move(100, 100)
    
    def _setup_ui(self):
        """Set up the panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add theme customizer
        customizer = ThemeCustomizer()
        layout.addWidget(customizer)
    
    def get_title(self) -> str:
        """Get panel title"""
        return "Theme Customization"
    
    def get_preferred_area(self) -> Qt.DockWidgetArea:
        """Get preferred dock area"""
        return Qt.DockWidgetArea.RightDockWidgetArea
    
    def get_preferred_size(self) -> tuple:
        """Get preferred size"""
        return (400, 800)
    
    def on_show(self):
        """Called when panel is shown"""
        pass
    
    def on_hide(self):
        """Called when panel is hidden"""
        pass
