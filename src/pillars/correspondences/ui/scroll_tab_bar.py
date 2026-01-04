
"""
Scroll Tab Bar - The Sheet Navigator.
Tab bar widget for navigating between multiple sheets (scrolls) in a spreadsheet.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QToolButton, QTabBar, QMenu
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction

class ScrollTabBar(QWidget):
    """
    The Navigation Bar for Scrolls (Sheets).
    Layout: [ + ] [ ≡ ] [ Tabs ... ] [ < ] [ > ]
    """
    
    # Signals
    tab_added = pyqtSignal()
    tab_changed = pyqtSignal(int)
    tab_renamed = pyqtSignal(int, str) # Not used directly by bar, but good to have context
    show_all_tabs = pyqtSignal() # For the menu
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setFixedHeight(32) # Compact height
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.setSpacing(1)
        
        # 1. Add Button (+)
        self.btn_add = QToolButton()
        self.btn_add.setText("+")
        self.btn_add.setToolTip("Add Scroll")
        self.btn_add.clicked.connect(self.tab_added.emit)
        self.btn_add.setFixedSize(28, 28)
        self.layout.addWidget(self.btn_add)
        
        # 2. Menu Button (≡)
        self.btn_menu = QToolButton()
        self.btn_menu.setText("≡")
        self.btn_menu.setToolTip("All Scrolls")
        self.btn_menu.setFixedSize(28, 28)
        self.btn_menu.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.layout.addWidget(self.btn_menu)
        
        # 3. The Tab Bar
        self.tab_bar = QTabBar()
        self.tab_bar.setDrawBase(False) # Integrated look
        self.tab_bar.setExpanding(False)
        self.tab_bar.setTabsClosable(False) # Can add if needed later
        self.tab_bar.setSelectionBehaviorOnRemove(QTabBar.SelectionBehavior.SelectPreviousTab)
        self.tab_bar.currentChanged.connect(self.tab_changed.emit)
        self.tab_bar.setMovable(True) # Allow dragging tabs
        self.layout.addWidget(self.tab_bar, 1) # Expand to fill space
        
        # 4. Nav Left (<)
        self.btn_prev = QToolButton()
        self.btn_prev.setText("<")
        self.btn_prev.setToolTip("Previous Scroll")
        self.btn_prev.clicked.connect(self._go_prev)
        self.btn_prev.setFixedSize(24, 28)
        self.layout.addWidget(self.btn_prev)
        
        # 5. Nav Right (>)
        self.btn_next = QToolButton()
        self.btn_next.setText(">")
        self.btn_next.setToolTip("Next Scroll")
        self.btn_next.clicked.connect(self._go_next)
        self.btn_next.setFixedSize(24, 28)
        self.layout.addWidget(self.btn_next)

    def add_tab(self, name: str):
        """
        Add tab logic.
        
        Args:
            name: Description of name.
        
        """
        return self.tab_bar.addTab(name)
        
    def set_current_index(self, index: int):
        """
        Configure current index logic.
        
        Args:
            index: Description of index.
        
        """
        self.tab_bar.setCurrentIndex(index)
        
    def count(self):
        """
        Count logic.
        
        """
        return self.tab_bar.count()
        
    def set_tab_text(self, index, text):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
        Configure tab text logic.
        
        Args:
            index: Description of index.
            text: Description of text.
        
        """
        self.tab_bar.setTabText(index, text)
        
    def update_menu(self, names: list):
        """Populate the ≡ menu with actions to jump to tabs."""
        menu = QMenu(self)
        for i, name in enumerate(names):
            action = QAction(name, self)
            # Capture variable i properly in lambda defaults
            action.triggered.connect(lambda checked, idx=i: self.set_current_index(idx))
            menu.addAction(action)
        self.btn_menu.setMenu(menu)

    def _go_prev(self):
        idx = self.tab_bar.currentIndex()
        if idx > 0:
             self.tab_bar.setCurrentIndex(idx - 1)
             
    def _go_next(self):
        idx = self.tab_bar.currentIndex()
        if idx < self.tab_bar.count() - 1:
            self.tab_bar.setCurrentIndex(idx + 1)