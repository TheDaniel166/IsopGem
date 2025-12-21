from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt
from .mindscape_tree import MindscapeTreeWidget
from .mindscape_page import MindscapePageWidget

class MindscapeWindow(QMainWindow):
    """
    Revised Mindscape Window (OneNote Style).
    Splitter: [Tree Navigation] | [Page Editor]
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mindscape: The Knowledge Tree")
        self.resize(1200, 800)
        
        # Central Widget & Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        # Left: Tree
        self.tree = MindscapeTreeWidget()
        self.tree.setMinimumWidth(250) # Prevent sidebar crush
        self.splitter.addWidget(self.tree)
        
        # Right: Page
        self.page = MindscapePageWidget()
        self.splitter.addWidget(self.page)
        
        # Setup Splitter Ratios (Simple and robust)
        self.splitter.setCollapsible(0, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([350, 850])
        
        # Connections
        self.tree.page_selected.connect(self.page.load_node)
        
        # Initial State
        self.page.clear()
