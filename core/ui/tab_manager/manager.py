"""
Tab Manager implementation for IsopGem
"""
import os
import importlib
import inspect
import logging
from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtGui import QIcon
from ..tabs.base_tab import BaseTab

class TabManager(QTabWidget):
    """Manages application tabs and their interactions"""
    
    def __init__(self, panel_manager=None, parent=None):
        super().__init__(parent)
        self.panel_manager = panel_manager
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setDocumentMode(True)  # Modern look
        self.setMovable(True)  # Allow tab reordering
        
        # Initialize tab registry
        self.tab_registry = []
        
        # Auto-discover and load tabs
        self.discover_tabs()
        self.initialize_tabs()
        
    def discover_tabs(self):
        """Discover all available tabs in the tabs directory"""
        logger = logging.getLogger(__name__)
        tabs_dir = os.path.join(os.path.dirname(__file__), "..", "tabs")
        logger.info(f"Searching for tabs in: {tabs_dir}")
        
        # Get all potential tab modules
        for filename in os.listdir(tabs_dir):
            if filename.endswith("_tab.py") and filename != "base_tab.py":
                module_name = filename[:-3]  # Remove .py
                logger.info(f"Found tab module: {module_name}")
                
                # Import the module
                try:
                    module = importlib.import_module(f"core.ui.tabs.{module_name}")
                    logger.info(f"Imported module: {module}")
                    
                    # Find tab classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseTab) and 
                            obj != BaseTab):
                            logger.info(f"Found tab class: {name}")
                            self.tab_registry.append(obj)
                except Exception as e:
                    logger.error(f"Failed to load tab module {module_name}: {e}")
                    
    def initialize_tabs(self):
        """Initialize all discovered tabs"""
        logger = logging.getLogger(__name__)
        
        # Sort tabs by order
        self.tab_registry.sort(key=lambda x: getattr(x, 'tab_order', 100))
        
        # Create and add each tab
        for tab_class in self.tab_registry:
            logger.info(f"Creating tab: {tab_class.tab_name}")
            tab = tab_class(self)
            self.addTab(tab, tab.tab_name)
            
            # Set icon if specified
            if tab.tab_icon:
                icon_path = os.path.join(os.path.dirname(__file__), 
                                       "..", "icons", tab.tab_icon)
                if os.path.exists(icon_path):
                    self.setTabIcon(self.count() - 1, QIcon(icon_path))
