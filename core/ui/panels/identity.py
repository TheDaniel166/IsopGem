"""
Panel identity management
"""

class PanelIdentity:
    """Represents a unique panel identity"""
    
    def __init__(self, panel_type: str, instance_id: str):
        """Initialize panel identity
        
        Args:
            panel_type: Type of panel (e.g. 'theme_customizer')
            instance_id: Unique instance identifier
        """
        self.panel_type = panel_type
        self.instance_id = instance_id
    
    @property
    def unique_id(self) -> str:
        """Get globally unique panel ID"""
        return f"{self.panel_type}_{self.instance_id}"
    
    def __eq__(self, other):
        if not isinstance(other, PanelIdentity):
            return False
        return self.unique_id == other.unique_id
    
    def __hash__(self):
        return hash(self.unique_id)
