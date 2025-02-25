"""
UI state management system
"""
from PyQt6.QtCore import QSettings
import json

class UIStateManager:
    """Manages saving and loading of UI states"""
    
    def __init__(self):
        self.settings = QSettings("IsopGem", "UIStates")
        
    def save_state(self, name: str, panel_states: dict):
        """Save a named UI state
        
        Args:
            name: Name of the state
            panel_states: Dictionary of panel states
        """
        # Get existing states
        states = self.get_saved_states()
        states[name] = panel_states
        
        # Save updated states
        self.settings.setValue("saved_states", json.dumps(states))
        
    def load_state(self, name: str) -> dict:
        """Load a named UI state
        
        Args:
            name: Name of the state to load
            
        Returns:
            Dictionary of panel states or None if not found
        """
        states = self.get_saved_states()
        return states.get(name)
        
    def delete_state(self, name: str):
        """Delete a named UI state
        
        Args:
            name: Name of the state to delete
        """
        states = self.get_saved_states()
        if name in states:
            del states[name]
            self.settings.setValue("saved_states", json.dumps(states))
            
    def get_saved_states(self) -> dict:
        """Get all saved states
        
        Returns:
            Dictionary of state name to panel states
        """
        states = self.settings.value("saved_states")
        if states:
            return json.loads(states)
        return {}
