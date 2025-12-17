from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QToolBar, QSizePolicy, QFrame, QLabel, QLayout, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QColor

class RibbonWidget(QTabWidget):
    """
    A unified 'Ribbon' style navigation widget.
    Contains tabs, where each tab is a toolbar-like area grouping actions.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                border-top: 1px solid #e2e8f0;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.5 #f8fafc, stop:1 #f1f5f9);
            }
            QTabBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #e2e8f0);
            }
            QTabBar::tab {
                background: transparent;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 10pt;
                font-weight: 500;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-top: 3px solid #3b82f6;
                font-weight: 600;
                color: #1e40af;
            }
            QTabBar::tab:!selected {
                color: #64748b;
                margin-top: 3px;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f1f5f9, stop:1 #e2e8f0);
                color: #475569;
            }
            
            /* Style buttons inside ribbon */
            QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 10px;
                color: #334155;
                font-size: 9pt;
            }
            QToolButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #eff6ff, stop:1 #dbeafe);
                border-color: #93c5fd;
                color: #1d4ed8;
            }
            QToolButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dbeafe, stop:1 #bfdbfe);
                border-color: #60a5fa;
            }
            QToolButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dbeafe, stop:1 #bfdbfe);
                border: 2px solid #3b82f6;
                color: #1e40af;
                font-weight: 600;
            }
            QToolButton::menu-indicator {
                image: none;
            }
            
            /* Style combo boxes */
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px 10px;
                color: #334155;
                font-size: 9pt;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #93c5fd;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                selection-background-color: #eff6ff;
                selection-color: #1e40af;
            }
            
            /* Font combo specific */
            QFontComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px 8px;
                min-height: 24px;
            }
            QFontComboBox:hover {
                border-color: #93c5fd;
            }
        """)
        self.setDocumentMode(True)
        self.setFixedHeight(115)
        
        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

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
                background: transparent;
                border-right: 1px solid #e2e8f0;
                margin-right: 8px;
                padding-right: 8px;
            }
        """)
        
        # Main layout: Content on top, label on bottom
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 8, 4)
        self.main_layout.setSpacing(4)
        
        # Content Container (ToolBar-like)
        self.content_container = QWidget()
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)
        
        self.main_layout.addWidget(self.content_container)
        self.main_layout.addStretch()
        
        # Group Label (Bottom center) - styled nicely
        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            color: #64748b;
            font-size: 8pt;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            padding: 2px 4px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f1f5f9, stop:1 #e2e8f0);
            border-radius: 3px;
        """)
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
        btn.setMinimumSize(44, 44)
        btn.setIconSize(QSize(24, 24))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.content_layout.addWidget(btn)
        return btn
        
    def add_separator(self):
        """Add a styled separator."""
        from PyQt6.QtWidgets import QFrame
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 transparent, stop:0.2 #cbd5e1, stop:0.8 #cbd5e1, stop:1 transparent);
        """)
        self.content_layout.addWidget(sep)
