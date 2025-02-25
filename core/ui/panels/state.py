"""
Panel state persistence
"""
from PyQt6.QtCore import QSettings, QPoint, QSize, Qt
from PyQt6.QtWidgets import QDockWidget
from PyQt6.QtCore import QByteArray
from .identity import PanelIdentity
import json

class PanelState:
    """Manages panel state persistence"""
    
    def __init__(self):
        self.settings = QSettings("IsopGem", "Panels")
    
    def save_panel_state(self, panel: QDockWidget):
        """Save panel state"""
        panel_id = panel.objectName()
        widget = panel.widget()
        
        # Get default area, ensuring we get the integer value
        default_area = panel.property("default_area")
        if isinstance(default_area, Qt.DockWidgetArea):
            area_value = int(default_area.value)
        else:
            area_value = int(Qt.DockWidgetArea.RightDockWidgetArea.value)
        
        state = {
            "geometry": bytes(panel.saveGeometry().toHex()).decode(),
            "floating": panel.isFloating(),
            "area": area_value,
            "visible": panel.isVisible()
        }
        
        # Save panel-specific state if available
        if hasattr(widget, 'save_state'):
            state["panel_state"] = widget.save_state()
        
        self.settings.setValue(f"panel_state/{panel_id}", json.dumps(state))
    
    def restore_panel_state(self, panel: QDockWidget, identity: PanelIdentity) -> Qt.DockWidgetArea:
        """Restore panel state"""
        state_str = self.settings.value(f"panel_state/{identity.unique_id}")
        if not state_str:
            return None
            
        try:
            state = json.loads(state_str)
            
            # Restore geometry
            geometry = QByteArray.fromHex(bytes(state["geometry"], "ascii"))
            panel.restoreGeometry(geometry)
            
            # Restore floating state
            panel.setFloating(state["floating"])
            
            # Restore visibility
            if state["visible"]:
                panel.show()
            else:
                panel.hide()
            
            # Restore panel-specific state if available
            widget = panel.widget()
            if "panel_state" in state and hasattr(widget, 'restore_state'):
                widget.restore_state(state["panel_state"])
                
            return Qt.DockWidgetArea(state["area"])
            
        except Exception as e:
            print(f"Error restoring panel state: {e}")
            return None
    
    def save_all_panels(self, panels: dict):
        """Save state for all panels"""
        for panel in panels.values():
            self.save_panel_state(panel)
    
    def clear_states(self):
        """Clear all saved panel states"""
        settings = QSettings()
        settings.beginGroup("panels")
        settings.remove("")  # Remove all keys in this group
        settings.endGroup()
    
    def clear_all_state(self):
        """Clear all saved panel states"""
        self.settings.clear()
