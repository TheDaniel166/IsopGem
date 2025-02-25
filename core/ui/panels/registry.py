"""
Panel registry for managing panel types and factories
"""
from typing import Dict, Callable, Optional
from PyQt6.QtWidgets import QWidget
import logging

logger = logging.getLogger(__name__)

class PanelRegistry:
    """Registry for panel types and their factories"""
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'PanelRegistry':
        if cls._instance is None:
            cls._instance = PanelRegistry()
        return cls._instance
    
    def __init__(self):
        self._factories: Dict[str, Callable[[], QWidget]] = {}
        self._manager = None  # Set by manager during initialization
        logger.debug("=== Panel Registry Initialized ===")
        logger.debug(f"Registered factories: {list(self._factories.keys())}")
        
    def set_manager(self, manager):
        """Set the panel manager reference"""
        self._manager = manager
        
    def register(self, panel_type: str, factory: Callable[[], QWidget]):
        """Register a panel factory"""
        self._factories[panel_type] = factory
        logger.debug(f"[REGISTER] Updated factories: {list(self._factories.keys())}")
        
    def create_panel(self, panel_type: str, panel_id: str = None, **kwargs) -> Optional[QWidget]:
        """Create a panel with optional ID and initialization parameters
        
        Args:
            panel_type: Type of panel to create
            panel_id: Optional unique identifier for the panel
            **kwargs: Additional initialization parameters
        """
        logger.debug(f"[CREATE] Attempting to create panel type: {panel_type}")
        logger.debug(f"[CREATE] Available factories: {list(self._factories.keys())}")
        
        # Check manager first for existing panel
        if panel_id and self._manager:
            if existing := self._manager.get_panel(panel_id):
                logger.debug(f"[CREATE] Found existing panel: {panel_id}")
                return existing.widget()
        
        # Create new panel through factory
        if factory := self._factories.get(panel_type):
            logger.debug(f"[CREATE] Found factory for: {panel_type}")
            panel = factory()
            
            # Set ID if provided
            if panel_id:
                panel.setObjectName(panel_id)
            
            # Initialize with kwargs if supported
            if hasattr(panel, 'initialize'):
                panel.initialize(**kwargs)
            elif kwargs:
                logger.debug(f"[CREATE] Panel does not support initialization parameters")
            
            logger.debug(f"[CREATE] Created panel: {panel.__class__.__name__}")
            return panel
            
        logger.warning(f"[CREATE] No factory found for panel type: {panel_type}")
        return None

    def _cleanup_panel(self, window, panel_id: str):
        """Clean up an existing panel"""
        logger.debug(f"[CLEANUP] Starting cleanup for panel: {panel_id}")
        logger.debug(f"[CLEANUP] Current active panels: {list(self._manager.panels.keys())}")
        logger.debug(f"[CLEANUP] Window panels: {list(window.panel_manager.panels.keys())}")
        
        if panel := window.panel_manager.panels.get(panel_id):
            logger.debug(f"[CLEANUP] Found panel to clean: {panel.__class__.__name__}")
            logger.debug(f"[CLEANUP] Panel parent: {panel.parent().__class__.__name__ if panel.parent() else 'None'}")
            logger.debug(f"[CLEANUP] Panel children: {[c.__class__.__name__ for c in panel.children()]}")
            
            # Remove from window
            window.panel_manager.remove_panel(panel_id)
            # Remove from active panels
            self._manager.panels.pop(panel_id, None)
            # Schedule deletion
            panel.deleteLater()
            
            logger.debug(f"[CLEANUP] After cleanup - Active panels: {list(self._manager.panels.keys())}")
            logger.debug(f"[CLEANUP] After cleanup - Window panels: {list(window.panel_manager.panels.keys())}")
        else:
            logger.debug(f"[CLEANUP] No panel found for cleanup: {panel_id}")
        
    def ensure_panel_exists(self, window, panel_type: str, panel_id: str) -> bool:
        """Ensure a panel exists, create if needed"""
        try:
            logger.debug("\n=== Panel Existence Check ===")
            logger.debug(f"[ENSURE] Checking panel: {panel_type} -> {panel_id}")
            logger.debug(f"[ENSURE] Active panels: {list(self._manager.panels.keys())}")
            logger.debug(f"[ENSURE] Window panels: {list(window.panel_manager.panels.keys())}")
            
            # Check if panel is active and valid
            if panel_id in self._manager.panels:
                panel = self._manager.panels[panel_id]
                logger.debug(f"[ENSURE] Found existing panel: {panel.__class__.__name__}")
                logger.debug(f"[ENSURE] Panel visible: {panel.isVisible()}")
                logger.debug(f"[ENSURE] Panel hidden: {panel.isHidden()}")
                logger.debug(f"[ENSURE] Panel parent: {panel.parent().__class__.__name__ if panel.parent() else 'None'}")
                
                if panel.isVisible() and not panel.isHidden():
                    logger.debug("[ENSURE] Panel is active and visible")
                    window.panel_manager.activate_panel(panel_id)
                    return True
                else:
                    logger.debug("[ENSURE] Panel inactive, cleaning up")
                    self._cleanup_panel(window, panel_id)
            
            # Create new panel
            if factory := self._factories.get(panel_type):
                logger.debug(f"[ENSURE] Creating new panel: {panel_type}")
                panel = factory()
                logger.debug(f"[ENSURE] New panel class: {panel.__class__.__name__}")
                
                # Clean up any existing panel with same ID
                self._cleanup_panel(window, panel_id)
                
                # Store panel before creating dock widget
                window.panel_manager.panels[panel_id] = panel
                self._manager.panels[panel_id] = panel
                logger.debug(f"[ENSURE] Stored panel in registries")
                logger.debug(f"[ENSURE] Updated active panels: {list(self._manager.panels.keys())}")
                
                # Create dock widget
                if window := self.get_main_window():
                    if dock := window.panel_manager.create_panel(panel=panel, panel_type=panel_type):
                        dock.show()
                        logger.debug("[ENSURE] Successfully created dock widget")
                        return True
                    else:
                        logger.error("[ENSURE] Failed to create dock widget")
                        self._cleanup_panel(window, panel_id)
                        return False
            
            logger.warning(f"[ENSURE] No factory found for panel type: {panel_type}")
            return False
            
        except Exception as e:
            logger.error(f"[ENSURE] Error ensuring panel exists: {str(e)}")
            logger.error(f"[ENSURE] Traceback: {traceback.format_exc()}")
            self._cleanup_panel(window, panel_id)
            return False

def get_registry() -> PanelRegistry:
    """Get the global panel registry instance"""
    return PanelRegistry.get_instance()
