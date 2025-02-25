"""
Base panel class for all panels
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

class BasePanel(QWidget):
    """Base class for all panels"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_floating = False
    
    def get_title(self) -> str:
        """Get panel title"""
        raise NotImplementedError
    
    def get_preferred_area(self) -> Qt.DockWidgetArea:
        """Get preferred dock area"""
        return Qt.DockWidgetArea.RightDockWidgetArea
    
    def get_preferred_size(self) -> tuple:
        """Get preferred size"""
        return (300, 600)
    
    def on_show(self):
        """Called when panel is shown"""
        pass
    
    def on_hide(self):
        """Called when panel is hidden"""
        pass
    
    def on_float(self):
        """Called when panel becomes floating"""
        self._is_floating = True
    
    def on_dock(self):
        """Called when panel is docked"""
        self._is_floating = False
    
    def is_floating(self) -> bool:
        """Check if panel is floating"""
        return self._is_floating
