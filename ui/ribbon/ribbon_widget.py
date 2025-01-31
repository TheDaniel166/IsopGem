from PyQt5.QtWidgets import QTabWidget
from .home_tab import HomeTab
from .gematria_tab import GematriaTab
from .document_manager_tab import DocumentManagerTab
from .tq_operations_tab import TQOperationsTab

class RibbonWidget(QTabWidget):
    def __init__(self, panel_manager):
        super().__init__()
        self.panel_manager = panel_manager
        self.setTabPosition(QTabWidget.North)
        self.init_ui()

    def init_ui(self):
        # Create and store tab references
        self.home_tab = HomeTab()
        self.gematria_tab = GematriaTab(self.panel_manager)
        self.document_tab = DocumentManagerTab(self.panel_manager)
        
        # Add ribbon tabs
        self.addTab(self.home_tab, "Home")
        self.addTab(self.gematria_tab, "Gematria")
        self.addTab(self.document_tab, "Documents")
        self.addTab(TQOperationsTab(self.panel_manager), "TQ Operations")

