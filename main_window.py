from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt
from ui.ribbon.ribbon_widget import RibbonWidget
from ui.workspace.panel_manager import PanelManager
from ui.actions.gematria_actions import GematriaActions

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ribbon = RibbonWidget()
        self.panel_manager = PanelManager(self)
        
        # Call initialization methods
        self.init_window()
        self.init_ui_components()
        self.init_actions()
        
        # Restore previous layout if exists
        self.panel_manager.restore_layout()

    def init_window(self):
        self.setWindowTitle("IsopGem")
        self.resize(1200, 800)
        self.setDockOptions(
            QMainWindow.AllowTabbedDocks |
            QMainWindow.AllowNestedDocks
        )

    def init_ui_components(self):
        # Initialize ribbon interface
        self.ribbon = RibbonWidget()
        self.setMenuWidget(self.ribbon)

    def init_actions(self):
        self.gematria_actions = GematriaActions(self)
        self.gematria_actions.connect_actions()

    def closeEvent(self, event):
        self.panel_manager.save_layout()
        super().closeEvent(event)
