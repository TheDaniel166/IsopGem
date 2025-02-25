"""
Panel state management for tracking panel configurations
"""
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class PanelState:
    """Manages state and configuration for panels"""
    
    def __init__(self):
        self.panel_states: Dict[str, Any] = {}
        
    def save_panel_state(self, panel_id: str, state: Dict[str, Any]):
        """Save state for a panel"""
        try:
            self.panel_states[panel_id] = state
            logger.debug(f"Saved state for panel {panel_id}")
        except Exception as e:
            logger.error(f"Error saving panel state: {e}")
            
    def get_panel_state(self, panel_id: str) -> Dict[str, Any]:
        """Get state for a panel"""
        try:
            return self.panel_states.get(panel_id, {})
        except Exception as e:
            logger.error(f"Error getting panel state: {e}")
            return {}
            
    def clear_panel_state(self, panel_id: str):
        """Clear state for a panel"""
        try:
            self.panel_states.pop(panel_id, None)
            logger.debug(f"Cleared state for panel {panel_id}")
        except Exception as e:
            logger.error(f"Error clearing panel state: {e}")
            
    def clear_all_states(self):
        """Clear all panel states"""
        try:
            self.panel_states.clear()
            logger.debug("Cleared all panel states")
        except Exception as e:
            logger.error(f"Error clearing all panel states: {e}")
            
    def to_json(self) -> str:
        """Convert panel states to JSON"""
        try:
            return json.dumps(self.panel_states)
        except Exception as e:
            logger.error(f"Error converting panel states to JSON: {e}")
            return "{}"
            
    def from_json(self, json_str: str):
        """Load panel states from JSON"""
        try:
            self.panel_states = json.loads(json_str)
            logger.debug("Loaded panel states from JSON")
        except Exception as e:
            logger.error(f"Error loading panel states from JSON: {e}")
            self.panel_states = {}
