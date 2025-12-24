from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize
from pyqtribbon import RibbonBar

class RibbonWidget(RibbonBar):
    """
    A unified 'Ribbon' style navigation widget using pyqtribbon.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # RibbonBar usually sets itself as a menu bar, but here we use it as a widget.
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(125) # Force a reasonable height for widget usage
        
        # Apply comprehensive Office-like styling
        self.setStyleSheet("""
            /* Main Ribbon Bar Background */
            RibbonBar {
                background-color: #f1f5f9;
                border: none;
                border-bottom: 1px solid #cbd5e1;
            }

            /* The Tab Bar Area */
            RibbonTabBar {
                background: transparent;
                margin-left: 5px;
            }

            /* Individual Tabs */
            RibbonTabBar::tab {
                color: #475569;
                border: none;
                background: transparent;
                padding: 6px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 10pt;
                min-width: 60px;
            }

            RibbonTabBar::tab:selected {
                color: #2563eb;
                background: white;
                border: 1px solid #cbd5e1;
                border-bottom: 1px solid white; /* Blend with content */
                font-weight: 600;
            }

            RibbonTabBar::tab:hover:!selected {
                color: #1e293b;
                background: rgba(255, 255, 255, 0.5);
            }

            /* The Content Area for Tabs */
            RibbonStackedWidget {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-top: none; /* Connect with tab */
            }

            /* Panels (Groups) */
            RibbonPanel {
                background-color: transparent;
                border-right: 1px solid #e2e8f0;
            }
            
            RibbonPanelTitle {
                background-color: transparent;
                color: #94a3b8;
                font-size: 8pt;
                padding: 2px;
            }

            /* Buttons inside the ribbon */
            RibbonToolButton {
                background-color: transparent;
                border: none;
                border-radius: 3px;
                color: #334155;
            }

            RibbonToolButton:hover {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                color: #1d4ed8;
            }

            RibbonToolButton:pressed {
                background-color: #dbeafe;
                border: 1px solid #2563eb;
            }
            
            /* Large button text alignment */
            RibbonToolButton[popupMode="1"] {
                padding-right: 10px; /* Space for menu arrow */
            }
            
            /* Separators */
            RibbonSeparator {
                background-color: #cbd5e1;
                width: 1px;
                margin: 4px;
            }
        """)

    def add_ribbon_tab(self, title: str) -> 'RibbonTabWrapper':
        """Create and add a new category (tab) to the ribbon."""
        content = self.addCategory(title)
        return RibbonTabWrapper(content)

class RibbonTabWrapper:
    """Wrapper around pyqtribbon Category to match old RibbonTab API."""
    def __init__(self, category):
        self.category = category

    def add_group(self, title: str) -> 'RibbonGroupWrapper':
        """Add a labeled group (panel) of actions to this tab."""
        panel = self.category.addPanel(title)
        return RibbonGroupWrapper(panel)

class RibbonGroupWrapper:
    """Wrapper around pyqtribbon Panel to match old RibbonGroup API."""
    def __init__(self, panel):
        self.panel = panel

    def add_widget(self, widget: QWidget):
        """Add a custom widget to the group."""
        self.panel.addWidget(widget)
        
    def add_action(self, action: QAction, tool_button_style=Qt.ToolButtonStyle.ToolButtonTextUnderIcon):
        """
        Add an action as a button.
        We map the style to large/small buttons.
        """
        # If the style implies a large icon (under text), usage addLargeButton
        if tool_button_style == Qt.ToolButtonStyle.ToolButtonTextUnderIcon:
            # addLargeButton(self, text, icon=None, slot=None, shortcut=None, tooltip=None, statusTip=None)
            # But the library might return a specific button type.
            # We must verify if the user's QAction is connected.
            
            # The library extracts info from QAction if we just use addAction?
            # pyqtribbon's Panel.addLargeButton usually returns a RibbonButton.
            # Let's see if we can pass the action directly.
            
            # Existing pyqtribbon examples often use specific add methods.
            # We'll try to use the action's properties.
            text = action.text()
            icon = action.icon() if not action.icon().isNull() else None
            
            # We connect the action's trigger to the button click if we create it manually
            # But wait, ribbon buttons *are* tool buttons.
            
            btn = self.panel.addLargeButton(text, icon)
            btn.setDefaultAction(action)
            # Override the text/icon again because setDefaultAction might reset them or sync them
            # Ideally setDefaultAction is enough.
            
            # Ensure the button style is respected if possible, but LargeButton forces text under icon
            return btn
        else:
            # Small button
            btn = self.panel.addSmallButton(action.text(), action.icon())
            btn.setDefaultAction(action)
            return btn
        
    def add_separator(self):
        """Add a separator."""
        self.panel.addSeparator()

