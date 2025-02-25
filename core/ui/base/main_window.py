"""
Main Window implementation for IsopGem
"""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDockWidget
from PyQt6.QtCore import Qt
from ..tab_manager.manager import TabManager
from ..panels.manager import PanelManager
from ..theme.manager import ThemeManager

class MainWindow(QMainWindow):
    """Main application window for IsopGem"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IsopGem")
        
        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Initialize managers
        self.panel_manager = PanelManager(self)
        self.theme_manager = ThemeManager.get_instance()
        
        # Initialize UI components
        self._init_ui()
        
        # Set initial window size
        self.resize(1200, 800)
    
    def _init_ui(self):
        """Initialize all UI components"""
        self._setup_tab_manager()
        self._setup_status_bar()
        
        # No need to manually add tabs - they are auto-discovered
    
    def _setup_tab_manager(self):
        """Set up the tab management system"""
        self.tab_manager = TabManager(panel_manager=self.panel_manager)
        self.main_layout.addWidget(self.tab_manager)
    
    def _setup_status_bar(self):
        """Set up the status bar"""
        status_bar = self.statusBar()
        status_bar.showMessage("Ready")
    
    def create_panel(self, panel: QWidget, name: str) -> QDockWidget:
        """Create and show a panel
        
        Args:
            panel: Panel widget to create
            name: Panel type name
            
        Returns:
            Created dock widget
        """
        dock = self.panel_manager.create_panel(panel=panel, panel_type=name)
        return dock
