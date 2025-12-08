from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QToolBar, QSizePolicy, QFrame, QLabel, QLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction

class RibbonWidget(QTabWidget):
    """
    A unified 'Ribbon' style navigation widget.
    Contains tabs, where each tab is a toolbar-like area grouping actions.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTabWidget::pane {
                border-top: 1px solid #e5e7eb;
                background: #f9fafb;
            }
            QTabBar::tab {
                background: transparent;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 10pt;
            }
            QTabBar::tab:selected {
                background: #f9fafb;
                border-top: 2px solid #0ea5e9;
                font-weight: bold;
                color: #0f172a;
            }
            QTabBar::tab:!selected {
                color: #64748b;
            }
            QTabBar::tab:hover {
                background: #f1f5f9;
            }
        """)
        self.setDocumentMode(True)
        self.setFixedHeight(110) # Enough height for icon + text or rows of controls

    def add_ribbon_tab(self, title: str) -> 'RibbonTab':
        """Create and add a new tab to the ribbon."""
        tab = RibbonTab()
        self.addTab(tab, title)
        return tab

class RibbonTab(QWidget):
    """A single page in the ribbon, containing RibbonGroups."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    def add_group(self, title: str) -> 'RibbonGroup':
        """Add a labeled group of actions to this tab."""
        group = RibbonGroup(title)
        self.layout.addWidget(group)
        return group

class RibbonGroup(QFrame):
    """A visual grouping of controls within a RibbonTab."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("RibbonGroup")
        self.setStyleSheet("""
            RibbonGroup {
                border-right: 1px solid #e5e7eb;
                padding-right: 5px;
            }
        """)
        
        # Main layout: Content on top, label on bottom
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        
        # Content Container (ToolBar-like)
        self.content_container = QWidget()
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)
        
        self.main_layout.addWidget(self.content_container)
        self.main_layout.addStretch()
        
        # Group Label (Bottom center)
        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: #94a3b8; font-size: 8pt;")
        self.main_layout.addWidget(self.label)
        
    def add_widget(self, widget: QWidget):
        """Add a custom widget to the group."""
        self.content_layout.addWidget(widget)
        
    def add_action(self, action: QAction, tool_button_style=Qt.ToolButtonStyle.ToolButtonTextUnderIcon):
        """Add an action as a button."""
        from PyQt6.QtWidgets import QToolButton
        btn = QToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(tool_button_style)
        # Make buttons reasonable size
        btn.setMinimumSize(40, 40)
        btn.setIconSize(QSize(24, 24))
        self.content_layout.addWidget(btn)
        return btn
        
    def add_separator(self):
        """Add a small separator."""
        from PyQt6.QtWidgets import QFrame
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: #e5e7eb;")
        self.content_layout.addWidget(sep)
