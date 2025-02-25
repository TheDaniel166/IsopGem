"""
Base panel class with identity support
"""
from PyQt6.QtWidgets import QWidget
from .identity import PanelIdentity

class Panel(QWidget):
    """Base class for all panels"""
    
    def __init__(self, identity: PanelIdentity = None):
        """Initialize panel
        
        Args:
            identity: Optional panel identity. If not provided, will be set by PanelManager
        """
        super().__init__()
        self._identity = identity
        
    @property
    def identity(self) -> PanelIdentity:
        """Get panel identity"""
        return self._identity
        
    @identity.setter
    def identity(self, value: PanelIdentity):
        """Set panel identity"""
        self._identity = value
        if value:
            self.setObjectName(value.unique_id)
    
    def on_show(self):
        """Called when panel becomes visible"""
        pass
        
    def on_hide(self):
        """Called when panel becomes hidden"""
        pass
        
    def on_float(self):
        """Called when panel starts floating"""
        pass
        
    def on_dock(self):
        """Called when panel is docked"""
        pass
        
    def save_state(self) -> dict:
        """Save panel-specific state
        
        Returns:
            Dictionary of state to save
        """
        return {}
        
    def restore_state(self, state: dict):
        """Restore panel-specific state
        
        Args:
            state: Previously saved state
        """
        pass
