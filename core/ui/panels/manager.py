"""
Panel manager with modern styling support
"""
from typing import Dict, Optional, Type
from PyQt6.QtWidgets import QMainWindow, QDockWidget, QWidget, QApplication
from PyQt6.QtCore import Qt, QPoint, QSize, QByteArray
import os
import json
import logging

from .state import PanelState
from ..widgets.collapsible_dock import CollapsibleDockWidget
from .registry import get_registry
from .base import BasePanel
from .ai_panels.test_panel import AITestPanel
from .ai_panels.chat_panel import ChatPanel

logger = logging.getLogger(__name__)

class PanelManager:
    """Manages all panels in the application"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.state = PanelState()
        self._instance_counters = {}  # Track panel type instances
        self.load_styles()
        
        # Initialize panel tracking
        self.panels = {}  # Dictionary to track panel widgets by unique_id
        self.docks = {}   # Dictionary to track dock widgets by unique_id
        
        # Set manager reference in registry
        registry = get_registry()
        registry.set_manager(self)
        
        self._initialize_default_panels()
        
    def _initialize_default_panels(self):
        """Initialize default panels"""
        self.panels['ai_test'] = AITestPanel()
        self.panels['karnak_chat'] = ChatPanel()
        
    def load_styles(self):
        """Load panel styles from QSS file"""
        try:
            style_dir = os.path.join(os.path.dirname(__file__), "..", "style")
            
            # Load dock style
            with open(os.path.join(style_dir, "dock.qss"), "r") as f:
                self.main_window.setStyleSheet(f.read())
                
        except Exception as e:
            logger.error(f"Error loading styles: {e}")
            
    def _generate_panel_identity(self, panel_type: str) -> str:
        """Generate unique panel identity"""
        count = self._instance_counters.get(panel_type, 0) + 1
        self._instance_counters[panel_type] = count
        return f"{panel_type}_{count}"
    
    def create_panel(self, panel: QWidget, panel_type: str) -> QDockWidget:
        """Create or retrieve a panel and its dock widget
        
        Args:
            panel: The panel widget to create/show
            panel_type: Type identifier for the panel
            
        Returns:
            QDockWidget containing the panel
        """
        logger.debug(f"Creating/retrieving panel: {panel_type}")
        
        # Get panel ID from widget or generate one
        panel_id = panel.objectName() or f"{panel_type.lower().replace(' ', '_')}_{len(self.panels)}"
        logger.debug(f"Using panel ID: {panel_id}")
        
        # Check for existing panel and dock
        existing_panel = self.panels.get(panel_id)
        existing_dock = self.docks.get(panel_id)
        
        # Case 1: Both panel and dock exist
        if existing_panel and existing_dock:
            logger.debug(f"Found existing panel and dock: {panel_id}")
            if panel is not existing_panel:
                existing_dock.setWidget(panel)
                self.panels[panel_id] = panel
            existing_dock.show()
            existing_dock.setFloating(True)
            return existing_dock
            
        # Case 2: Create new dock for panel
        logger.debug(f"Creating new dock for panel: {panel_id}")
        dock = CollapsibleDockWidget(panel_type, self.main_window)
        dock.setObjectName(panel_id)
        dock.setWidget(panel)
        
        # Configure dock widget
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        
        # Store references
        self.panels[panel_id] = panel
        self.docks[panel_id] = dock
        logger.debug(f"Stored panel and dock with ID: {panel_id}")
        
        # Add to main window
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        dock.setFloating(True)
        dock.resize(400, 600)
        dock.show()
        
        logger.debug(f"Panel {panel_id} created and shown as floating")
        return dock

    def get_panel(self, panel_id: str) -> Optional[QWidget]:
        """Get panel widget by ID"""
        return self.panels.get(panel_id)
        
    def get_dock(self, panel_id: str) -> Optional[QDockWidget]:
        """Get dock widget by ID"""
        return self.docks.get(panel_id)

    def remove_panel(self, panel_id: str):
        """Remove panel and its dock widget"""
        if dock := self.docks.pop(panel_id, None):
            dock.close()
        self.panels.pop(panel_id, None)
        
    def activate_panel(self, panel_id: str):
        """Activate and show a panel"""
        logger.debug(f"\n[ACTIVATE] Activating panel: {panel_id}")
        logger.debug(f"[ACTIVATE] Current panels: {list(self.panels.keys())}")
        logger.debug(f"[ACTIVATE] Current docks: {list(self.docks.keys())}")
        
        if dock := self.docks.get(panel_id):
            logger.debug(f"[ACTIVATE] Found dock to activate: {dock.__class__.__name__}")
            logger.debug(f"[ACTIVATE] Dock parent: {dock.parent().__class__.__name__ if dock.parent() else 'None'}")
            logger.debug(f"[ACTIVATE] Dock visibility before: {dock.isVisible()}")
            
            dock.show()
            dock.raise_()
            dock.activateWindow()
            
            logger.debug(f"[ACTIVATE] Dock visibility after: {dock.isVisible()}")
        else:
            logger.debug(f"[ACTIVATE] No dock found to activate: {panel_id}")
            
    def show_panel(self, name: str):
        """Show a panel"""
        if panel := self.get_panel(name):
            panel.show()
            panel.raise_()
            
    def hide_panel(self, name: str):
        """Hide a panel"""
        if panel := self.get_panel(name):
            panel.hide()
            
    def float_panel(self, name: str, pos: QPoint = None):
        """Float a panel"""
        if panel := self.get_panel(name):
            dock = self.get_dock(name)
            dock.setFloating(True)
            if pos:
                dock.move(pos)
            # Save new state
            self.state.save_panel_state(name, dock)
            
    def dock_panel(self, name: str, area=Qt.DockWidgetArea.RightDockWidgetArea):
        """Dock a panel"""
        if panel := self.get_panel(name):
            dock = self.get_dock(name)
            dock.setFloating(False)
            self.main_window.addDockWidget(area, dock)
            # Save new state
            self.state.save_panel_state(name, dock)
            
    def set_panel_size(self, name: str, size: QSize):
        """Set the size of a panel"""
        if name in self.panels:
            panel = self.panels[name]
            panel.resize(size)
            # Save new state
            self.state.save_panel_state(name, panel)
    
    def save_state(self, filename):
        """Save current state of all panels to file"""
        try:
            state = {}
            for panel_id, panel in self.panels.items():
                # Get dock area as integer
                area = self.main_window.dockWidgetArea(panel)
                area_value = int(area.value) if area else int(Qt.DockWidgetArea.RightDockWidgetArea.value)
                
                state[panel_id] = {
                    "geometry": panel.saveGeometry().toHex().data().decode(),
                    "floating": panel.isFloating(),
                    "visible": panel.isVisible(),
                    "area": area_value,
                    "pos": [panel.pos().x(), panel.pos().y()],
                    "size": [panel.size().width(), panel.size().height()]
                }
                
                # Save widget state if available
                widget = panel.widget()
                if hasattr(widget, 'save_state'):
                    state[panel_id]["widget_state"] = widget.save_state()
                    
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            
    def load_state(self, filename):
        """Load panel states from file"""
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
                
            # First ensure all panels exist
            for panel_id in state.keys():
                self._ensure_panel(panel_id)
                
            # Now restore state for existing panels
            for panel_id, panel_state in state.items():
                if panel := self.panels.get(panel_id):
                    # First restore geometry (includes basic position/size)
                    geometry = QByteArray.fromHex(bytes(panel_state["geometry"], "ascii"))
                    panel.restoreGeometry(geometry)
                    
                    # Then restore dock area if not floating
                    if not panel_state["floating"]:
                        area = Qt.DockWidgetArea(panel_state["area"])
                        self.main_window.addDockWidget(area, panel)
                    
                    # For floating panels, set exact position and size
                    if panel_state["floating"]:
                        pos = panel_state.get("pos", [0, 0])
                        size = panel_state.get("size", [200, 200])
                        panel.move(pos[0], pos[1])
                        panel.resize(size[0], size[1])
                    
                    # Set floating state
                    panel.setFloating(panel_state["floating"])
                    
                    # Restore visibility
                    if panel_state["visible"]:
                        panel.show()
                    else:
                        panel.hide()
                    
                    # Restore widget state if available
                    widget = panel.widget()
                    if "widget_state" in panel_state and hasattr(widget, 'restore_state'):
                        widget.restore_state(panel_state["widget_state"])
                        
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            
    def delete_state(self):
        """Delete all saved panel states"""
        self.state.clear_states()
            
    def close_panel(self, panel_id: str):
        """Close panel by ID"""
        if panel_id in self.panels:
            panel = self.panels[panel_id]
            # Save state before closing
            self.state.save_panel_state(panel)
            panel.close()
            del self.panels[panel_id]
            
    def _on_panel_close(self, panel_id: str, event):
        """Handle panel close event"""
        # Save state before closing
        if panel_id in self.panels:
            self.state.save_panel_state(self.panels[panel_id])
            del self.panels[panel_id]
        event.accept()
        
    def get_all_panel_states(self) -> dict:
        """Get states for all panels
        
        Returns:
            Dictionary of panel ID to panel state
        """
        states = {}
        for panel_id, panel in self.panels.items():
            # Get basic state
            state = {
                "geometry": bytes(panel.saveGeometry().toHex()).decode(),
                "floating": panel.isFloating(),
                "visible": panel.isVisible(),
                "area": int(panel.property("default_area").value 
                          if isinstance(panel.property("default_area"), Qt.DockWidgetArea)
                          else Qt.DockWidgetArea.RightDockWidgetArea.value)
            }
            
            # Get widget-specific state
            widget = panel.widget()
            if hasattr(widget, 'save_state'):
                state["widget_state"] = widget.save_state()
                
            states[panel_id] = state
        return states
        
    def restore_panel_states(self, states: dict):
        """Restore panel states
        
        Args:
            states: Dictionary of panel ID to panel state
        """
        for panel_id, state in states.items():
            if panel_id in self.panels:
                panel = self.panels[panel_id]
                
                # Restore geometry
                geometry = QByteArray.fromHex(bytes(state["geometry"], "ascii"))
                panel.restoreGeometry(geometry)
                
                # Restore basic state
                panel.setFloating(state["floating"])
                panel.setVisible(state["visible"])
                
                # Restore dock area
                area = Qt.DockWidgetArea(state["area"])
                self.main_window.addDockWidget(area, panel)
                
                # Restore widget-specific state
                widget = panel.widget()
                if "widget_state" in state and hasattr(widget, 'restore_state'):
                    widget.restore_state(state["widget_state"])

    def _ensure_panel(self, panel_id: str):
        """Recreate a panel if it's missing"""
        if panel_id not in self.panels:
            # Simple mapping of known panel types
            if panel_id.startswith("Properties"):
                from ..panels.common_panels import PropertiesPanel
                self.create_panel(PropertiesPanel(), "Properties")
            elif panel_id.startswith("Console"):
                from ..panels.ai_panels import ConsolePanel
                self.create_panel(ConsolePanel(), "Console")
            elif panel_id.startswith("ai_test"):
                from .ai_panels.test_panel import AITestPanel
                self.create_panel(AITestPanel(), "ai_test")
            elif panel_id.startswith("karnak_chat"):
                from .ai_panels.chat_panel import ChatPanel
                self.create_panel(ChatPanel(), "karnak_chat")
