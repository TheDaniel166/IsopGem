from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSizePolicy
from ui.ribbon.ribbon_widget import RibbonWidget
from ui.workspace.panel_manager import PanelManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.search_results = None  # Storage for search results
        self.setWindowTitle("IsopGem")
        self.setup_ui()
    
    def setup_ui(self):
        # Central widget setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create panel workspace with visual properties
        self.workspace = QWidget()
        self.workspace.setStyleSheet("background-color: #ffffff;")
        self.workspace.setMinimumHeight(300)
        self.workspace.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initialize panel manager
        self.panel_manager = PanelManager(self)
        
        # Create ribbon with size constraints
        self.ribbon = RibbonWidget(self.panel_manager)
        self.ribbon.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Add components to layout with proper stretching
        self.layout.addWidget(self.ribbon, 0)
        self.layout.addWidget(self.workspace, 1)
        
        # Set initial window size
        self.setMinimumSize(800, 600)
